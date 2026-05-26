"""
Reorganize FlowUs 301quiz exports into structured knowledge-base.
Handles BOTH:
  - Separated: 函数-极限-连续/习题/...md + 错题/...md
  - Combined: 函数+极限+连续/...md (single file)
"""
import zipfile, os, re, json, shutil
from pathlib import Path

BASE = Path(r"C:/Users/scott/OneDrive/桌面/301quiz")
OUT = Path(r"D:/learn/agentic-ai-system-course-main/knowledge-base/301-数学")

if OUT.exists():
    shutil.rmtree(OUT)

def extract_zips(root):
    """Recursively extract all zips under root."""
    for zp in sorted(root.rglob("*.zip")):
        dest = zp.parent / zp.stem
        if not dest.exists():
            with zipfile.ZipFile(zp, 'r') as z:
                z.extractall(dest)

extract_zips(BASE)

# ================================================================
# Parser
# ================================================================

def parse_flowus_md(md_path):
    """Parse FlowUs bullet-list markdown into structured sections."""
    text = md_path.read_text(encoding='utf-8')
    lines = text.split('\n')

    sections = []
    cur_section = None
    cur_q = None
    image_dir = md_path.parent  # images relative to .md file

    for line in lines:
        # Section: "- <title>" (1 indent level = leading "- ")
        if re.match(r'^- .+$', line) and not re.match(r'^    ', line):
            title = line[2:].strip()
            if title and not title[0].isdigit():
                cur_section = {'title': title, 'questions': []}
                sections.append(cur_section)
                cur_q = None
                continue

        # Question: "    - <num> <annotation>"
        qm = re.match(r'^    - (\d+)\s*(.*)$', line)
        if qm and cur_section:
            cur_q = {
                'num': int(qm.group(1)),
                'annotation': qm.group(2).strip(),
                'images': [],
                'notes': []
            }
            cur_section['questions'].append(cur_q)
            continue

        # Image: "        ![image](path)"
        im = re.match(r'^\s*!\[image.*\]\((.+)\)$', line)
        if im and cur_q:
            cur_q['images'].append(im.group(1))
            continue

        # Text note: "        <text>"
        tm = re.match(r'^        (.+)$', line)
        if tm and cur_q:
            txt = tm.group(1).strip()
            if txt and not txt.startswith('![') and not txt.startswith('['):
                cur_q['notes'].append(txt)

    return sections

# ================================================================
# Writer
# ================================================================

def clean_fn(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()[:60]

def write_question(q, section_title, topic_name, folder_type, src_dir, out_base):
    """Write a single question as a markdown file with images."""
    q_num = q['num']
    annotation = q['annotation']
    sec_dir = out_base / clean_fn(section_title)
    sec_dir.mkdir(parents=True, exist_ok=True)

    # Filename
    fname = f"{q_num:02d}"
    if annotation:
        fname += f"-{clean_fn(annotation)[:40]}"
    fname += ".md"

    # Copy images
    img_dir = sec_dir / f"images/{q_num:02d}"
    img_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for i, img_path in enumerate(q.get('images', [])):
        src = src_dir / img_path
        if src.exists():
            ext = src.suffix
            new = f"img-{i+1}{ext}"
            shutil.copy2(src, img_dir / new)
            copied.append(new)
        else:
            copied.append(f"MISSING:{img_path}")

    # Build markdown
    md = []
    md.append('---')
    md.append(f'question_number: {q_num}')
    md.append(f'section: "{section_title}"')
    md.append(f'topic: "{topic_name}"')
    md.append(f'type: "{folder_type}"')
    if annotation:
        md.append(f'annotation: "{annotation}"')
    md.append(f'images: {len(copied)}')
    md.append('---')
    md.append('')
    md.append(f'# {section_title} · 题{q_num}')
    md.append('')

    if annotation:
        md.append(f'> {annotation}')
        md.append('')

    if q.get('notes'):
        for note in q['notes']:
            md.append(f'- {note}')
        md.append('')

    for i, img in enumerate(copied):
        label = ["题目", "解答", "批注", "补充"][i] if i < 4 else f"图{i+1}"
        md.append(f'![{label}](images/{q_num:02d}/{img})')
        md.append('')

    (sec_dir / fname).write_text('\n'.join(md), encoding='utf-8')
    return section_title, q_num, annotation

# ================================================================
# Process all
# ================================================================

stats = {}

for md_file in sorted(BASE.rglob("*.md")):
    rel = md_file.relative_to(BASE)
    parts = rel.parts
    md_name = md_file.stem  # e.g., "习题+uuid" or "函数+极限+连续+uuid"

    # Determine topic name and type
    folder_type = "unknown"
    topic_name = parts[0] if len(parts) > 1 else "未分类"

    # Heuristic: parent dir or filename prefix indicates type
    parent = md_file.parent.name
    if '习题' in parent or '习题' in md_name:
        folder_type = '习题'
    elif '错题' in parent or '错题' in md_name:
        folder_type = '错题'
    elif '导学' in parent or '导学' in topic_name or 'Intro' in md_name:
        folder_type = '导学'
    elif 'test' in md_name.lower():
        folder_type = '测试'
    else:
        # If filename starts with topic name, it's likely a combined file
        folder_type = '综合'

    topic_name = topic_name.replace('+', '-')

    print(f"\n=== {topic_name}/{folder_type} ({md_name[:50]}...) ===")
    sections = parse_flowus_md(md_file)
    out_base = OUT / topic_name / folder_type

    q_count = 0
    for sec in sections:
        for q in sec['questions']:
            s, n, a = write_question(q, sec['title'], topic_name, folder_type, md_file.parent, out_base)
            note = a[:50] if a else '(无注释)'
            print(f"  [{s}] Q{n}: {note}")
            q_count += 1

    if q_count == 0:
        print(f"  (no questions found)")

    stats[f"{topic_name}/{folder_type}"] = q_count

# ================================================================
# README
# ================================================================
lines = ['# 301 数学', '', '## 目录', '']
for topic_dir in sorted(OUT.glob("*/")):
    tn = topic_dir.name
    lines.append(f'### {tn}')
    for sub_dir in sorted(topic_dir.glob("*/")):
        ft = sub_dir.name
        count = sum(1 for _ in sub_dir.rglob("*.md"))
        img_count = sum(1 for _ in sub_dir.rglob("*.png"))
        lines.append(f'- [{ft}]({tn}/{ft}/) — {count} 题, {img_count} 图片')
    lines.append('')

(OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')

print("\n" + "="*50)
print("SUMMARY:")
for k, v in stats.items():
    print(f"  {k}: {v} questions")
print(f"  Total: {sum(stats.values())} questions")
print(f"  Output: {OUT}")
