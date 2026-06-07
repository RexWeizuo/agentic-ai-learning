"""
词汇分组 — Qwen3.7-max (requests, 250词/块, 600s timeout, 3次重试)
只找出自然成组的词，其余进随机池。
"""
import json, os, re, sys, time
from pathlib import Path
import requests

BASE = Path(__file__).parent
CHUNKS_DIR = BASE / "wordlist_chunks"
OUTPUT = BASE / "ai_groups.json"
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODEL = "qwen3.7-max"
URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

if not API_KEY:
    print("ERROR: DASHSCOPE_API_KEY not set")
    sys.exit(1)

def call_qwen(messages: list, max_tokens: int = 8000, retries: int = 3) -> dict | None:
    """Call Qwen API with retries."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(URL, json=payload, headers=headers, timeout=600)
            if resp.status_code != 200:
                print(f"    HTTP {resp.status_code}: {resp.text[:200]}")
                if attempt < retries:
                    time.sleep(5)
                    continue
                return None

            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()

            # Extract JSON
            m = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
            if m:
                text = m.group(1).strip()
            else:
                start, end = text.find('{'), text.rfind('}')
                if start >= 0 and end > start:
                    text = text[start:end+1]

            result = json.loads(text)
            usage = data.get("usage", {})
            if usage:
                print(f"    Tokens: in={usage.get('prompt_tokens','?')} out={usage.get('completion_tokens','?')}")
            return result
        except json.JSONDecodeError as e:
            print(f"    JSON error (attempt {attempt}): {e}")
            if attempt < retries:
                time.sleep(5)
        except Exception as e:
            print(f"    API error (attempt {attempt}): {e}")
            if attempt < retries:
                time.sleep(10)
    return None


SYSTEM_PROMPT = """你是考研英语词汇专家。从词表中找出能自然成组的词。

重要：只对真正有聚类价值的词分组。无法自然归类的词放入 ungrouped。

分组类型（按优先级）：
1. 词根/词缀相同 — 共享明确词根的词（如 -ceive, -spect, -tain, -mit, -duct 等）
2. 近义词 — 意思非常接近、可互相替换的词
3. 易混淆 — 拼写相近但意思不同，容易看错的词对
4. 词族 — 同一词根派生出的不同词性（如 able/ability/enable/disable）
5. 主题场景 — 同一专业领域的术语（法律、医学、经济等）

每组 4-15 个词。输出纯 JSON。"""


def chunk_prompt(chunk_text: str, chunk_num: int, total: int) -> str:
    return f"""第 {chunk_num}/{total} 个词表。格式：word|中文释义

{chunk_text}

请分组。JSON：
{{
  "groups": [
    {{"name": "组名（中文）", "words": ["word1"], "type": "词根|近义|易混淆|词族|主题", "note": "学习提示"}}
  ],
  "ungrouped": ["无法归类的词"],
  "cross_hints": [{{"my_group": "组名", "likely_in_other_chunks": ["词"]}}],
  "stats": {{"total": 0, "grouped": 0}}
}}
只输出 JSON。"""


def main():
    chunk_files = sorted(CHUNKS_DIR.glob("words_*.txt"))
    total_chunks = len(chunk_files)
    all_groups, all_hints, all_ungrouped = [], [], []

    # ── Phase 1: Group each chunk ──
    print(f"PHASE 1: {total_chunks} chunks → Qwen3.7-max")
    print("=" * 60)

    for i, f in enumerate(chunk_files):
        chunk_num = i + 1
        print(f"\n[{f.name}] ({chunk_num}/{total_chunks})")

        # Skip if already processed
        interim_file = BASE / f"interim_chunk_{chunk_num:02d}.json"
        if interim_file.exists():
            print(f"  Already processed, loading from {interim_file.name}")
            result = json.loads(interim_file.read_text(encoding="utf-8"))
        else:
            text = f.read_text(encoding="utf-8")
            n = len([l for l in text.split("\n") if l.strip()])
            print(f"  {n} words → Qwen...")
            result = call_qwen([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": chunk_prompt(text, chunk_num, total_chunks)},
            ], max_tokens=8000)
            if result:
                interim_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        if result:
            g = result.get("groups", [])
            u = result.get("ungrouped", [])
            h = result.get("cross_hints", [])
            print(f"  → {len(g)} groups, {len(u)} ungrouped")
            all_groups.extend(g)
            all_hints.extend(h)
            all_ungrouped.extend(u)
        else:
            print(f"  → FAILED after retries")

    grouped_words = set()
    for g in all_groups:
        for w in g.get("words", []):
            grouped_words.add(w)

    print(f"\nPhase 1 done: {len(all_groups)} groups, {len(grouped_words)} words grouped, "
          f"{len(all_ungrouped)} ungrouped")

    interim = {"groups": all_groups, "cross_hints": all_hints, "ungrouped": all_ungrouped}
    (BASE / "interim_all.json").write_text(json.dumps(interim, ensure_ascii=False, indent=2), encoding="utf-8")

    if not all_groups:
        print("No groups to synthesize. Exiting.")
        return

    # ── Phase 2: Synthesize ──
    print(f"\nPHASE 2: 合成去重 ({len(all_groups)} groups)...")
    print("=" * 60)

    synth_prompt = f"""合并以下 {total_chunks} 个词表的分组结果，去重、拆分超过 15 词的组。

## 所有分组：
{json.dumps(all_groups, ensure_ascii=False, indent=2)}

## 跨表提示：
{json.dumps(all_hints, ensure_ascii=False)}

要求：
1. 合并跨表重复的组（同名或共享多个词）
2. 超过 15 词的组拆成子组
3. 去重：一词一组优先
4. 输出 150-250 组
5. 未分组词放入 random_pool

JSON:
{{
  "groups": [{{"name": "组名", "words": [], "type": "词根|近义|易混淆|词族|主题", "note": "学习提示", "priority": 1}}],
  "random_pool": [],
  "stats": {{"groups": 0, "grouped_words": 0, "random_pool": 0}}
}}"""

    final = call_qwen([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": synth_prompt},
    ], max_tokens=16000, retries=3)

    if final:
        OUTPUT.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
        s = final.get("stats", {})
        print(f"\nDONE! {s.get('groups','?')} groups, {s.get('grouped_words','?')} grouped, "
              f"{s.get('random_pool','?')} in random pool")
        print(f"Saved → {OUTPUT}")
    else:
        print("Synthesis FAILED, interim saved to interim_all.json")

if __name__ == "__main__":
    main()
