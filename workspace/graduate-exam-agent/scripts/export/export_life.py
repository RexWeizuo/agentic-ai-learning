"""
Export SiYuan life management notebook preserving FILESYSTEM hierarchy.
SiYuan stores document hierarchies in the directory structure, not in JSON.
"""
import json, shutil, re
from pathlib import Path

SIYUAN = Path(r"C:\Users\scott\SiYuan\data")
NB_ID = "20260515105258-6yhxbci"
OUT = Path(r"D:/learn/agentic-ai-system-course-main/knowledge-base/生活")

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)

def extract_markdown(node, level=0):
    parts = []
    if node is None: return parts
    t = node.get("Type","")
    if t == "NodeText":
        d = node.get("Data","")
        if d: parts.append(d)
    elif t == "NodeTextMark":
        c = node.get("TextMarkTextContent","")
        if c: parts.append(c)
    elif t == "NodeHeading":
        h = min(node.get("HeadingLevel",1)+level, 6)
        parts.append("\n"+"#"*h+" ")
    elif t == "NodeListItem":
        parts.append("  - ")
    elif t == "NodeParagraph":
        parts.append("\n")
    elif t == "NodeCodeBlockCode":
        c = node.get("Data","")
        if c: parts.append("\n```\n"+c+"\n```\n")
    elif t == "NodeThematicBreak":
        parts.append("\n---\n")
    for child in node.get("Children") or []:
        parts.extend(extract_markdown(child, level))
    return parts

def clean(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()[:80]

def get_doc_info(path):
    """Read a .sy file or directory and return (title, text)."""
    # Find matching .sy file
    sy_file = path.parent / (path.name + ".sy")
    if not sy_file.exists():
        sy_file = path
    if not sy_file.exists() or not sy_file.is_file():
        return None, ""

    try:
        doc = json.loads(sy_file.read_text(encoding='utf-8'))
        title = doc.get("Properties",{}).get("title","untitled")
        text = "".join(extract_markdown(doc)).strip()
        return title, text
    except Exception:
        return None, ""

def export_dir(src_dir, out_dir):
    """Export a SiYuan directory tree to markdown folders."""
    out_dir.mkdir(parents=True, exist_ok=True)

    for item in sorted(src_dir.iterdir()):
        if item.name.startswith('.'): continue

        if item.is_dir():
            # Collect sub-items
            sub_dirs = [d for d in item.iterdir()
                       if d.is_dir() and not d.name.startswith('.')]
            sub_sy = [f for f in item.iterdir()
                     if f.suffix == '.sy' and f.stem != item.name]

            # Try to get document info (may not exist for organizational folders)
            title, text = get_doc_info(item)
            if not title:
                # Organizational folder (e.g., 一/, 二/) — use dir name
                title = item.name

            if sub_dirs or sub_sy:
                # Container: create folder and recurse
                folder = out_dir / clean(title)
                folder.mkdir(parents=True, exist_ok=True)
                if len(text) > 20:
                    (folder / "README.md").write_text(
                        f"---\ntitle: {title}\n---\n\n# {title}\n\n{text}",
                        encoding='utf-8')
                for sub in sub_dirs:
                    export_dir(sub, folder)
                for s in sub_sy:
                    stitle, stext = get_doc_info(s)
                    if stitle and stext and len(stext) > 10:
                        fname = clean(stitle) + ".md"
                        (folder / fname).write_text(
                            f"---\ntitle: {stitle}\n---\n\n# {stitle}\n\n{stext}",
                            encoding='utf-8')
            else:
                # Leaf document
                if len(text) > 10:
                    fname = clean(title) + ".md"
                    (out_dir / fname).write_text(
                        f"---\ntitle: {title}\n---\n\n# {title}\n\n{text}",
                        encoding='utf-8')

        elif item.suffix == '.sy':
            doc_id = item.stem
            matching_dir = item.parent / doc_id
            if not matching_dir.exists():
                try:
                    doc = json.loads(item.read_text(encoding='utf-8'))
                    title = doc.get("Properties",{}).get("title","untitled")
                    text = "".join(extract_markdown(doc)).strip()
                    if len(text) > 10:
                        fname = clean(title) + ".md"
                        (out_dir / fname).write_text(
                            f"---\ntitle: {title}\n---\n\n# {title}\n\n{text}",
                            encoding='utf-8')
                except Exception:
                    pass

# Process the notebook directory
nb_path = SIYUAN / NB_ID
export_dir(nb_path, OUT)

# Stats
md_count = sum(1 for _ in OUT.rglob("*.md"))
print(f"Exported {md_count} files to {OUT}")

def show(path, indent=0, max_items=40):
    items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    count = 0
    for item in items:
        if item.name.startswith('.'): continue
        count += 1
        if count > max_items:
            print("  "*indent + f"... ({len(items)-max_items} more)")
            break
        if item.is_dir():
            md_count = sum(1 for _ in item.rglob("*.md"))
            print("  "*indent + f"{item.name}/ ({md_count} files)")
            show(item, indent+1, max_items)
        else:
            size = item.stat().st_size
            print(f"  "*indent + f"{item.name} ({size:,}B)")

show(OUT)
