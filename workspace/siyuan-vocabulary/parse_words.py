"""
Parse all A-Z vocabulary files into a single structured JSON.
Run: python parse_words.py
Output: all_words.json
"""
import re
import json
import os
from pathlib import Path

AZ_DIR = Path(__file__).parent / "A-Z"
OUTPUT = Path(__file__).parent / "all_words.json"

def parse_word_blocks(text: str, letter: str) -> list[dict]:
    """Parse a markdown file into a list of word dicts."""
    words = []
    # Split on ## headings (words), skip # headings (letter title)
    blocks = re.split(r'\n(?=## )', text)

    for block in blocks:
        # Skip frontmatter and # headings
        if block.startswith('---') or not block.startswith('## '):
            continue

        lines = block.strip().split('\n')
        header = lines[0].strip()
        word_name = header.lstrip('#').strip()

        # Skip if it's the letter heading (e.g., "## A" with no content)
        if word_name == letter or word_name == '':
            continue

        word = {
            "word": word_name,
            "letter": letter,
        }

        # Parse fields
        body = '\n'.join(lines[1:])
        current_field = None
        current_value = []

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # Match field headers: - **音标**: ...
            field_match = re.match(r'- \*\*(.+?)\*\*:\s*(.*)', line)
            if field_match:
                # Save previous field
                if current_field and current_value:
                    word[current_field] = '\n'.join(current_value).strip()

                field_name = field_match.group(1).strip()
                field_value = field_match.group(2).strip()
                current_field = field_name
                current_value = [field_value] if field_value else []
            elif current_field and line.startswith('- '):
                # Continuation of a list field (e.g., 例句 items, 搭配 items)
                current_value.append(line)
            elif current_field:
                # Continuation of previous field
                current_value.append(line)

        # Save last field
        if current_field and current_value:
            word[current_field] = '\n'.join(current_value).strip()

        # Clean up 考频
        if '考频' in word:
            try:
                word['考频'] = int(word['考频'])
            except ValueError:
                word['考频'] = 0

        # Strip == markers from 释义 (keep raw text)
        if '释义' in word:
            # Remove == cloze markers for processing
            word['释义_raw'] = word['释义'].replace('==', '')
        else:
            word['释义_raw'] = ''

        words.append(word)

    return words


def main():
    all_words = []
    stats = {}

    for md_file in sorted(AZ_DIR.glob("*.md")):
        letter = md_file.stem
        text = md_file.read_text(encoding='utf-8')
        words = parse_word_blocks(text, letter)
        all_words.extend(words)
        stats[letter] = len(words)
        print(f"  {letter}: {len(words)} words")

    # Write output
    OUTPUT.write_text(json.dumps(all_words, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\nTotal: {len(all_words)} words from {len(stats)} files")
    print(f"Output: {OUTPUT}")

    # Show available fields
    fields = set()
    for w in all_words:
        fields.update(w.keys())
    print(f"Fields: {sorted(fields)}")

    # Stats
    with_phonetic = sum(1 for w in all_words if w.get('音标'))
    with_synonyms = sum(1 for w in all_words if w.get('同义词'))
    with_antonyms = sum(1 for w in all_words if w.get('反义词'))
    with_root = sum(1 for w in all_words if w.get('词根词缀'))
    with_collocation = sum(1 for w in all_words if w.get('搭配'))
    with_freq = sum(1 for w in all_words if w.get('考频', 0) > 0)

    print(f"\nWith 音标: {with_phonetic}")
    print(f"With 同义词: {with_synonyms}")
    print(f"With 反义词: {with_antonyms}")
    print(f"With 词根词缀: {with_root}")
    print(f"With 搭配: {with_collocation}")
    print(f"With 考频: {with_freq}")

if __name__ == "__main__":
    main()
