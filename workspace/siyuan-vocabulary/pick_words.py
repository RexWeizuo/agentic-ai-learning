"""Pick N untracked words: 2 themed groups + random pool. One command."""
import json, glob, random, sys, re
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent
N = int(sys.argv[1]) if len(sys.argv) > 1 else 50

# Load tracked
data = json.load(open(BASE / "memory" / "word_progress.json", encoding="utf-8"))
tracked = set(data["words"].keys())

# Parse group files: words are ## headings
group_words = {}
random_words = []
for f in sorted(BASE.glob("groups/*/*.md")):
    content = f.read_text(encoding="utf-8")
    words = []
    for line in content.split("\n"):
        m = re.match(r"^##\s+(\S.*)$", line.strip())
        if m:
            word = m.group(1).strip()
            if re.search(r"[一-鿿]", word):  # skip Chinese titles
                continue
            if word and word not in tracked:
                words.append(word)
    if not words:
        continue
    if "06-" in str(f):
        random_words.extend(words)
    else:
        group_words[str(f)] = words

# Pick 2 best groups
sorted_groups = sorted(group_words.items(), key=lambda x: len(x[1]), reverse=True)
picked_words = []
for fpath, words in sorted_groups[:2]:
    take = words[: min(8, len(words))]
    picked_words.extend(take)

# Fill from random pool
random.shuffle(random_words)
needed = max(0, N - len(picked_words))
picked_words.extend(random_words[:needed])

# Lookup details
allw_list = json.load(open(BASE / "all_words.json", encoding="utf-8"))
allw = {item["word"]: item for item in allw_list}

output = []
for word in picked_words:
    entry = allw.get(word, {})
    output.append(
        {
            "word": word,
            "root": entry.get("词根词缀", ""),
            "meaning": entry.get("释义_raw", entry.get("释义", "")),
            "example": (entry.get("例句", "") or "").split("\n")[0]
            if entry.get("例句")
            else "",
        }
    )

# Save word list
with open(BASE / "memory" / "next_50.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Init in FSRS
for w in picked_words:
    if w not in data["words"]:
        data["words"][w] = {
            "stability": 1,
            "difficulty": 0.5,
            "state": 0,
            "reviews": 0,
            "next_review": date.today().isoformat(),
            "last_review": None,
            "history": [],
        }
json.dump(
    data,
    open(BASE / "memory" / "word_progress.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2,
)

print(f"OK: {len(picked_words)} words ({len(picked_words)-needed} group + {needed} random)")
for w in output[:5]:
    print(f"  {w['word']}")
if len(output) > 5:
    print(f"  ... and {len(output)-5} more")
