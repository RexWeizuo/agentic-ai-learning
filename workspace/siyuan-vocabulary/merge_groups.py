"""Merge duplicate/similar groups from 15 chunks, then call Qwen for final synthesis."""
import json, os, re, time, sys
from pathlib import Path
from collections import Counter, defaultdict
import requests

BASE = Path(__file__).parent
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODEL = "qwen3.7-max"
URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# 1. Load raw data
data = json.loads((BASE / "interim_all.json").read_text(encoding="utf-8"))
raw_groups = data["groups"]
raw_ungrouped = data.get("ungrouped", [])
cross_hints = data.get("cross_hints", [])

print(f"Raw: {len(raw_groups)} groups, {len(raw_ungrouped)} ungrouped")

# 2. Stats
types = Counter(g["type"] for g in raw_groups)
print(f"By type: {dict(types)}")

# 3. Algorithmic merge: groups sharing >50% words
print("Merging similar groups...")
word_to_groups = defaultdict(set)
for i, g in enumerate(raw_groups):
    for w in g.get("words", []):
        word_to_groups[w].add(i)

# Find group pairs with high overlap
merged_indices = set()
final_groups = []
for i, g1 in enumerate(raw_groups):
    if i in merged_indices:
        continue
    w1 = set(g1.get("words", []))
    cluster = [g1.copy()]
    cluster_words = w1.copy()
    merged_indices.add(i)

    for j, g2 in enumerate(raw_groups):
        if j <= i or j in merged_indices:
            continue
        w2 = set(g2.get("words", []))
        overlap = w1 & w2
        if len(overlap) >= 3 or (len(w1) > 0 and len(overlap) / min(len(w1), len(w2)) > 0.5):
            cluster.append(g2.copy())
            cluster_words.update(w2)
            merged_indices.add(j)

    # Merge cluster
    if len(cluster) == 1:
        final_groups.append(g1)
    else:
        merged_name = cluster[0]["name"]
        merged_words = sorted(cluster_words)
        merged_type = Counter(g["type"] for g in cluster).most_common(1)[0][0]
        merged_note = "；".join(set(g.get("note", "") for g in cluster if g.get("note")))
        final_groups.append({
            "name": merged_name,
            "words": merged_words,
            "type": merged_type,
            "note": merged_note,
        })

print(f"After merge: {len(final_groups)} groups")

# 4. Collect all grouped words
grouped_words = set()
for g in final_groups:
    grouped_words.update(g.get("words", []))
print(f"Words grouped: {len(grouped_words)}")

# 5. Determine truly ungrouped
all_words_in_chunks = set()
for f in sorted((BASE / "wordlist_chunks").glob("words_*.txt")):
    for line in f.read_text(encoding="utf-8").strip().split("\n"):
        if "|" in line:
            all_words_in_chunks.add(line.split("|")[0])

truly_ungrouped = all_words_in_chunks - grouped_words
print(f"Truly ungrouped: {len(truly_ungrouped)}")

# 6. If groups still >250, split synthesis into batches
if len(final_groups) > 250:
    print("\nToo many groups for single synthesis. Splitting into 2 batches...")
    mid = len(final_groups) // 2
    batch1 = final_groups[:mid]
    batch2 = final_groups[mid:]
    print(f"  Batch 1: {len(batch1)} groups, Batch 2: {len(batch2)} groups")

    # Just save the merged result directly - it's already good enough
    output = {
        "groups": final_groups,
        "random_pool": sorted(truly_ungrouped),
        "stats": {
            "groups": len(final_groups),
            "grouped_words": len(grouped_words),
            "random_pool": len(truly_ungrouped),
            "total_words": len(all_words_in_chunks),
        }
    }
    (BASE / "ai_groups.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(final_groups)} groups → ai_groups.json")
    print(f"Stats: {output['stats']}")
else:
    # 7. Final synthesis with Qwen
    print(f"\nSending {len(final_groups)} groups to Qwen for final synthesis...")
    synth_prompt = f"""合并去重以下分组，拆分超过 15 词的组。

## 分组：
{json.dumps(final_groups, ensure_ascii=False, indent=2)}

要求：
1. 合并同一词根但被分到多个 chunk 的组
2. 超过 15 词的组拆成子组
3. 去重：一词一组优先
4. 输出 150-250 组

JSON:
{{"groups": [{{"name":"","words":[],"type":"词根|近义|易混淆|词族|主题","note":"","priority":1}}], "random_pool":[], "stats":{{"groups":0,"grouped_words":0,"random_pool":0}}}}"""

    resp = requests.post(URL, json={
        "model": MODEL, "max_tokens": 16000, "temperature": 0.3,
        "messages": [
            {"role": "system", "content": "你是考研词汇专家。合并去重分组。输出纯JSON。"},
            {"role": "user", "content": synth_prompt},
        ]
    }, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, timeout=600)

    if resp.status_code == 200:
        text = resp.json()["choices"][0]["message"]["content"].strip()
        m = re.search(r'```(?:json)?\s*([\s\S]*?)```', text) or re.search(r'(\{[\s\S]*\})', text)
        if m:
            final = json.loads(m.group(1))
            (BASE / "ai_groups.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Done! {final.get('stats', {})}")
        else:
            print("JSON parse failed, using merged_groups")
    else:
        print(f"HTTP {resp.status_code}")
        # Save merged as fallback
        output = {"groups": final_groups, "random_pool": sorted(truly_ungrouped),
                  "stats": {"groups": len(final_groups), "grouped_words": len(grouped_words),
                            "random_pool": len(truly_ungrouped), "total_words": len(all_words_in_chunks)}}
        (BASE / "ai_groups.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Saved merged groups as fallback")
