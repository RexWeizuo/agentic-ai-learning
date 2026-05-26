"""
Export SiYuan notebooks as folder-md hierarchy, preserving exact document tree.
Each document: folder (if has children) or .md file (if leaf).
"""
import json, shutil, re, os as _os
from pathlib import Path

SIYUAN = Path(r"C:\Users\scott\SiYuan\data")
OUT = Path(r"D:/learn/agentic-ai-system-course-main/knowledge-base")

NOTEBOOKS = {
    "301-讲义": "20260515155301-wcdv2ip",   # 三大计算/高数/线代/概率
    "301-习题集": "20260521212645-teyk23o",  # 概率统计/线代/高数 习题+答案
    "408-讲义": "20260515155307-blvk8ai",    # OS
}

def extract_markdown(node, level=0):
    parts = []
    if node is None: return parts
    t = node.get("Type","")
    children = node.get("Children") or []

    # ---- Inline elements ----
    if t == "NodeText":
        d = node.get("Data","")
        if d: parts.append(d)
    elif t == "NodeTextMark":
        c = node.get("TextMarkTextContent","")
        if c: parts.append(c)
    elif t == "NodeBackslash":
        parts.append("\\")
    elif t == "NodeBackslashContent":
        d = node.get("Data","")
        if d: parts.append(d)
    elif t == "NodeOpenBracket":
        parts.append("{")
    elif t == "NodeCloseBracket":
        parts.append("}")
    elif t == "NodeOpenParen":
        parts.append("(")
    elif t == "NodeCloseParen":
        parts.append(")")
    elif t == "NodeBang":
        parts.append("!")
    elif t == "NodeHTMLEntity":
        d = node.get("Data","")
        if d: parts.append(d)
    elif t == "NodeHardBreak":
        parts.append("  \n")
    elif t == "NodeSoftBreak":
        parts.append("\n")
    elif t == "NodeKramdownSpanIAL":
        pass  # skip kramdown attributes
    elif t == "NodeLinkText":
        pass  # handled by children
    elif t == "NodeLinkDest":
        d = node.get("Data","")
        if d: parts.append(f"]({d})")

    # ---- Block elements ----
    elif t == "NodeHeading":
        parts.append("\n"+"#"*node.get("HeadingLevel",1)+" ")
    elif t == "NodeHeadingC8hMarker":
        pass  # skip
    elif t == "NodeListItem":
        parts.append("- ")
    elif t == "NodeList":
        pass  # structural
    elif t == "NodeParagraph":
        parts.append("\n")
    elif t == "NodeBlockquote":
        parts.append("\n> ")
    elif t == "NodeBlockquoteMarker":
        pass  # skip
    elif t == "NodeThematicBreak":
        parts.append("\n---\n")

    # ---- Code blocks ----
    elif t == "NodeCodeBlock":
        pass  # structural
    elif t == "NodeCodeBlockFenceOpenMarker":
        pass
    elif t == "NodeCodeBlockFenceCloseMarker":
        pass
    elif t == "NodeCodeBlockFenceInfoMarker":
        lang = node.get("Data","")
        parts.append(f"\n```{lang or ''}")
    elif t == "NodeCodeBlockCode":
        c = node.get("Data","")
        if c: parts.append(c + "\n```\n")

    # ---- Math blocks ----
    elif t == "NodeMathBlock":
        pass  # structural
    elif t == "NodeMathBlockOpenMarker":
        parts.append("\n$$\n")
    elif t == "NodeMathBlockCloseMarker":
        parts.append("\n$$\n")
    elif t == "NodeMathBlockContent":
        c = node.get("Data","")
        if c: parts.append(c)

    # ---- Tables ----
    elif t == "NodeTable":
        parts.append("\n")
    elif t == "NodeTableHead":
        pass  # recurse
    elif t == "NodeTableRow":
        parts.append("|")
        for c in children:
            parts.extend(extract_markdown(c, level))
            if c.get("Type") == "NodeTableCell":
                parts.append("|")
        parts.append("\n")
    elif t == "NodeTableCell":
        pass  # recurse children for content

    # ---- Images (extract URL directly, don't recurse children) ----
    elif t == "NodeImage":
        # Image structure: [Bang][OpenBracket][LinkText][CloseBracket][OpenParen][LinkDest][CloseParen]
        img_url = ""
        alt_text = "image"
        for c in children:
            if c.get("Type") == "NodeLinkDest":
                img_url = c.get("Data","")
            elif c.get("Type") == "NodeLinkText":
                alt_text = c.get("Data","") or "image"
        if img_url:
            parts.append(f"![{alt_text}]({img_url})")
        return parts  # Don't recurse

    # ---- Document ----
    elif t == "NodeDocument":
        pass  # root, just recurse

    # Default: recurse for all unhandled types
    for child in children:
        parts.extend(extract_markdown(child, level))
    return parts

def clean(name):
    name = name.replace("\n"," ").replace("\r"," ").replace("\t"," ")
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()[:60]

def get_doc(path):
    """Read a SiYuan document: try path.sy first, then path as .sy file."""
    if path.is_dir():
        sy = path.parent / (path.name + ".sy")
        if sy.exists(): return json.loads(sy.read_text(encoding='utf-8'))
        # Check inside directory for .sy with same name
        inner = path / (path.name + ".sy")
        if inner.exists(): return json.loads(inner.read_text(encoding='utf-8'))
    elif path.suffix == '.sy' and path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return None

def export_node(src_path, out_dir, visited=None):
    """Export a SiYuan document node to folder or .md file."""
    if visited is None: visited = set()

    # Get document info
    doc = get_doc(src_path)
    if not doc: return

    doc_id = doc.get("ID","")
    if doc_id in visited: return
    visited.add(doc_id)

    title = doc.get("Properties",{}).get("title","untitled")
    text = "".join(extract_markdown(doc)).strip()

    # Determine children
    child_items = []
    child_dir = src_path.parent / doc_id if src_path.is_dir() or src_path.suffix == '.sy' else None

    if child_dir and child_dir.exists() and child_dir.is_dir():
        for item in sorted(child_dir.iterdir()):
            if item.name.startswith('.'): continue
            if item.is_dir():
                child_items.append(item)
            elif item.suffix == '.sy' and item.stem != doc_id:
                child_items.append(item)

    # Filter meaningful children
    real_children = []
    for item in child_items:
        cd = get_doc(item)
        if cd:
            ct = "".join(extract_markdown(cd)).strip()
            ctitle = cd.get("Properties",{}).get("title","")
            # Skip empty/trivial
            if ct or ctitle:
                real_children.append(item)

    # Clean text: remove SiYuan metadata code block, fix newlines
    text = re.sub(r'```\n?---\n.*?\n---\n```\n?', '', text, flags=re.DOTALL)
    text = re.sub(r'```---\n.*?\n---\n```\n?', '', text, flags=re.DOTALL)
    # Fix missing newlines before headings
    text = re.sub(r'([^\n])(#{1,6}\s)', r'\1\n\n\2', text)
    text = text.strip()

    if real_children:
        folder = out_dir / clean(title)
        folder.mkdir(parents=True, exist_ok=True)
        if len(text) > 10:
            _write(folder / "README.md", f"---\ntitle: {title}\n---\n\n{text}\n")
        for child in real_children:
            export_node(child, folder, visited)
    else:
        if len(text) > 5:
            fname = clean(title)[:60] + ".md"
            _write(out_dir / fname, f"---\ntitle: {title}\n---\n\n{text}\n")

def _long(path_str):
    if not path_str.startswith("\\\\?\\"):
        return "\\\\?\\" + path_str
    return path_str

def _mkdir(path):
    _os.makedirs(_long(str(path)), exist_ok=True)

def _write(path, content):
    with open(_long(str(path)), "w", encoding="utf-8") as f:
        f.write(content)

# Main
for out_name, nb_id in NOTEBOOKS.items():
    nb_path = SIYUAN / nb_id
    if not nb_path.exists(): continue

    out_dir = OUT / out_name
    if out_dir.exists(): shutil.rmtree(str(out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"{out_name} ({nb_id})")

    file_count = [0]

    # Process top-level .sy files
    for sy_file in sorted(nb_path.glob("*.sy")):
        doc = json.loads(sy_file.read_text(encoding='utf-8'))
        title = doc.get("Properties",{}).get("title","untitled")
        doc_id = doc.get("ID","")

        # Check if this doc has a subdirectory with children
        child_dir = nb_path / doc_id
        has_children = child_dir.exists() and child_dir.is_dir() and len(list(child_dir.iterdir())) > 0

        if has_children:
            export_node(nb_path / doc_id, out_dir)
        else:
            text = "".join(extract_markdown(doc)).strip()
            text = re.sub(r'```\n?---\n.*?\n---\n```\n?', '', text, flags=re.DOTALL)
            text = re.sub(r'```---\n.*?\n---\n```\n?', '', text, flags=re.DOTALL)
            if len(text) > 10:
                fname = clean(title)[:60] + ".md"
                _write(out_dir / fname, f"---\ntitle: {title}\n---\n\n{text}\n")
                file_count[0] += 1

    # Count files
    md = sum(1 for _ in out_dir.rglob("*.md"))
    dirs = sum(1 for _ in out_dir.rglob("*") if _.is_dir())
    print(f"  {dirs} folders, {md} files")

print("\nDone!")
