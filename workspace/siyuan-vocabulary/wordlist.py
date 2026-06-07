"""Split word list into smaller chunks (~250 words each) for Qwen max model."""
import json, re
from pathlib import Path

BASE = Path(__file__).parent
INPUT = BASE / "all_words.json"
OUTDIR = BASE / "wordlist_chunks"

# Clean old chunks
import shutil
if OUTDIR.exists():
    shutil.rmtree(OUTDIR)
OUTDIR.mkdir(exist_ok=True)

def short_meaning(raw):
    if not raw:
        return ''
    text = raw.replace('==', '')
    text = re.sub(r'\\n+', '；', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[[^\]]+\]', '', text)
    first = text.split('；')[0].strip()
    first = re.sub(r'^[a-z]+\.\s*', '', first)
    if len(first) > 20:
        first = first[:18] + '…'
    return first

words = json.loads(INPUT.read_text(encoding='utf-8'))
lines = [f"{w['word']}|{short_meaning(w.get('释义_raw', ''))}" for w in words]

chunk_size = 250
for i in range(0, len(lines), chunk_size):
    chunk = lines[i:i+chunk_size]
    n = i // chunk_size + 1
    f = OUTDIR / f"words_{n:02d}.txt"
    f.write_text('\n'.join(chunk), encoding='utf-8')
    print(f"  {f.name}: {len(chunk)} words")

print(f"\nTotal: {len(lines)} words in {(len(lines) + chunk_size - 1) // chunk_size} chunks")
