"""
Split chapter-level 习题/答案 into individual question .md files.
Handles multiple question delimiters: N、 N． N. #### (N) ### N、
"""
import re, shutil
from pathlib import Path

SRC = Path("D:/learn/agentic-ai-system-course-main/knowledge-base")
SUBJECT_MAP = {"301-习题集": "301-数学", "301-讲义": "301-数学", "408-讲义": "408-计算机"}

def clean_text(text):
    """Fix common formatting issues."""
    # Remove duplicate embedded frontmatter
    text = re.sub(r'\n---\ntitle:.*?\n---\n', '\n', text, flags=re.DOTALL)
    # Convert SiYuan colored spans
    text = re.sub(r'<span[^>]*style="color:[^"]*"[^>]*>(.*?)</span>', r'*\1*', text)
    text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text)
    return text.strip()

def split_by_delimiter(text, q_type):
    """
    Split text into individual questions.
    Delimiters: N、 N． N. #### (N) ### (N) #### N. ### N、
    """
    # Try to find the question delimiter pattern
    # Pattern: optional heading markers + number + delimiter + content
    patterns = [
        # #### (N) rest or #### N. rest
        (r'(?:^|\n)(#{3,5})\s*(?:\(|<span[^>]*>)?(\d+)(?:\)|</span>)?\s*', True),
        # N、rest (Chinese enumeration)
        (r'(?:^|\n)(\d+)、', False),
        # N．rest (fullwidth dot)
        (r'(?:^|\n)(\d+)．', False),
        # N. rest (ascii dot with space)
        (r'(?:^|\n)(\d+)\.\s+', False),
    ]

    for pattern, has_heading in patterns:
        matches = list(re.finditer(pattern, text))
        if len(matches) >= 2:  # At least 2 questions found
            result = []
            for i, m in enumerate(matches):
                q_num = int(m.group(2) if has_heading else m.group(1))
                start = m.start()
                end = matches[i+1].start() if i+1 < len(matches) else len(text)
                content = text[start:end].strip()

                # Skip page markers
                if re.match(r'^\d+[、．.]?\s*第\s*\d+\s*页', content):
                    continue
                if re.match(r'^\d+[、．.]?\s*$', content):
                    continue

                result.append({'num': q_num, 'content': content, 'type': q_type})
            return result

    return []

def process_file(md_file):
    """Process one .md file, splitting into questions."""
    text = md_file.read_text(encoding="utf-8")
    text = clean_text(text)

    # Determine type from filename
    fname = md_file.stem
    if '答案' in fname:
        q_type = '答案'
    elif '习题' in fname:
        q_type = '习题'
    else:
        return None, []  # Skip index files

    # Build chapter path from relative path
    try:
        rel = md_file.relative_to(SRC)
    except ValueError:
        return None, []
    parts = list(rel.parts)
    source = parts[0]  # e.g., 301-习题集
    subject = SUBJECT_MAP.get(source, "其他")
    chapter_parts = parts[1:-1]  # between source and filename
    chapter = "/".join(chapter_parts)

    questions = split_by_delimiter(text, q_type)
    return (source, subject, chapter, chapter_parts), questions

# Main
total_files = 0
total_questions = 0

for source_name in ["301-习题集", "301-讲义", "408-讲义"]:
    src_dir = SRC / source_name
    if not src_dir.exists():
        continue

    for md_file in sorted(src_dir.rglob("*.md")):
        fname = md_file.stem
        if fname not in ['习题', '答案']:
            continue  # Skip chapter index files

        meta, questions = process_file(md_file)
        if not questions:
            continue

        source, subject, chapter, chapter_parts = meta

        # Create output directory
        out_dir = SRC / source / "questions"
        for cp in chapter_parts:
            out_dir = out_dir / cp
        out_dir.mkdir(parents=True, exist_ok=True)

        for q in questions:
            q_num = q['num']
            q_type = q['type']
            content = q['content']

            # Build frontmatter
            fm = "---\n"
            fm += f"question_number: {q_num}\n"
            fm += f"chapter: \"{chapter}\"\n"
            fm += f"subject: \"{subject}\"\n"
            fm += f"type: \"{q_type}\"\n"
            fm += "---\n\n"

            (out_dir / f"{q_num:02d}.md").write_text(fm + content, encoding="utf-8")
            total_questions += 1

        print(f"  {chapter}/{fname}: {len(questions)} questions")
        total_files += 1

print(f"\nDone: {total_files} files processed, {total_questions} individual questions")
