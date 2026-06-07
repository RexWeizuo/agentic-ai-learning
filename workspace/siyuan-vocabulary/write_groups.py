"""Convert ai_groups.json → organized markdown group files with full word data."""
import json, re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent
GROUPS_DIR = BASE / "groups"
ALL_WORDS = json.loads((BASE / "all_words.json").read_text(encoding="utf-8"))

# Clean old
import shutil
if GROUPS_DIR.exists():
    shutil.rmtree(GROUPS_DIR)

# Word lookup
word_map = {w["word"]: w for w in ALL_WORDS}

# Load AI groups
ai_data = json.loads((BASE / "ai_groups.json").read_text(encoding="utf-8"))
groups = ai_data["groups"]
random_pool = ai_data.get("random_pool", [])

# Organize by type
TYPE_DIRS = {
    "词根": "01-词根聚类",
    "近义": "02-近义词",
    "易混淆": "03-易混淆",
    "词族": "04-词族",
    "主题": "05-主题场景",
}

by_type = defaultdict(list)
for g in groups:
    t = g.get("type", "近义")
    # Normalize type
    if "词根" in t:
        t_key = "词根"
    elif "近义" in t or "同义" in t:
        t_key = "近义"
    elif "混淆" in t:
        t_key = "易混淆"
    elif "词族" in t:
        t_key = "词族"
    elif "主题" in t or "场景" in t or "场景主题" in t:
        t_key = "主题"
    else:
        t_key = "近义"
    by_type[t_key].append(g)

def write_word_md(w: dict) -> str:
    """Write a single word in markdown format (SiYuan-compatible)."""
    lines = [f"## {w['word']}\n"]
    if w.get('音标'):
        lines.append(f"- **音标**: {w['音标']}")
    if w.get('词性'):
        lines.append(f"- **词性**: {w['词性']}")
    if w.get('释义'):
        lines.append(f"- **释义**: {w['释义']}")
    if w.get('英文释义'):
        lines.append(f"- **英文释义**: {w['英文释义']}")
    if w.get('同义词'):
        lines.append(f"- **同义词**: {w['同义词']}")
    if w.get('反义词'):
        lines.append(f"- **反义词**: {w['反义词']}")
    if w.get('词根词缀'):
        lines.append(f"- **词根词缀**: {w['词根词缀']}")
    if w.get('搭配'):
        lines.append(f"- **搭配**: {w['搭配']}")
    if w.get('例句'):
        lines.append(f"- **例句**:\n{w['例句']}")
    if w.get('考频'):
        lines.append(f"- **考频**: {w['考频']}")
    return '\n'.join(lines) + '\n'

# Write group files
readme_lines = [
    "# 考研英语词汇 · AI 智能分组",
    "",
    f"**{len(groups)} 组** | **{ai_data['stats']['grouped_words']} 词已分组** | **{ai_data['stats']['random_pool']} 词随机池**",
    "",
    "> Qwen3.7-max 按词根、近义、易混淆、词族、主题场景智能分组。",
    "> 未分组的词进随机池，每天抽 30 个背。",
    "",
    "## 目录",
    "",
]

for t_key, dir_name in TYPE_DIRS.items():
    gs = by_type.get(t_key, [])
    if not gs:
        continue
    type_dir = GROUPS_DIR / dir_name
    type_dir.mkdir(parents=True, exist_ok=True)
    readme_lines.append(f"\n### {dir_name} ({len(gs)} 组)\n")

    for i, g in enumerate(gs):
        name = g.get("name", f"Group {i+1}")
        words = g.get("words", [])
        note = g.get("note", "")
        gtype = g.get("type", t_key)

        # Safe filename
        safe_name = re.sub(r'[\\/:*?"<>|]', '-', name)[:50]
        fname = f"{i+1:03d}-{safe_name}.md"

        # Build markdown
        md = f"# {name}\n\n"
        md += f"> **类型**: {gtype}\n\n"
        if note:
            md += f"> **学习提示**: {note}\n\n"
        md += f"**{len(words)} 词**\n\n---\n\n"

        found = 0
        for wname in words:
            w = word_map.get(wname)
            if w:
                md += write_word_md(w)
                found += 1
            else:
                md += f"## {wname}\n\n- *(word data not found)*\n\n"

        md += f"\n*({found}/{len(words)} words with full data)*\n"

        (type_dir / fname).write_text(md, encoding="utf-8")

        # Shorten name for index
        short_name = name[:40] + ("..." if len(name) > 40 else "")
        readme_lines.append(f"- [{short_name}]({dir_name}/{fname}) — {len(words)} 词")

# Write random pool
random_dir = GROUPS_DIR / "06-随机池"
random_dir.mkdir(parents=True, exist_ok=True)
random_found = 0
random_md = "# 随机池 — 日常背词\n\n"
random_md += f"> 这些词不便归类，适合每天随机抽取 30 个和分组词混合背诵。\n\n"
random_md += f"**{len(random_pool)} 词**\n\n---\n\n"

for wname in sorted(random_pool):
    w = word_map.get(wname)
    if w:
        random_md += write_word_md(w)
        random_found += 1

(random_dir / "random-pool.md").write_text(random_md, encoding="utf-8")
readme_lines.append(f"\n### 06-随机池 ({random_found} 词)\n")
readme_lines.append(f"- [随机池](06-随机池/random-pool.md) — {random_found} 词，每天随机抽 30 个")

# Stats
readme_lines.extend([
    "",
    "---",
    "",
    "## 统计",
    "",
    f"| 类型 | 组数 |",
    "|---|---|",
])
for t_key, dir_name in TYPE_DIRS.items():
    gs = by_type.get(t_key, [])
    if gs:
        wcount = sum(len(g.get("words", [])) for g in gs)
        readme_lines.append(f"| {dir_name} | {len(gs)} 组 / {wcount} 词 |")
readme_lines.append(f"| 随机池 | — / {random_found} 词 |")
readme_lines.append(f"| **总计** | **{len(groups)} 组 / {ai_data['stats']['grouped_words'] + random_found} 词** |")

(GROUPS_DIR / "README.md").write_text('\n'.join(readme_lines), encoding="utf-8")

print(f"Done! {len(groups)} group files written to {GROUPS_DIR}")
for t_key, dir_name in TYPE_DIRS.items():
    gs = by_type.get(t_key, [])
    if gs:
        print(f"  {dir_name}: {len(gs)} groups")
print(f"  06-随机池: {random_found} words")
