"""Export SiYuan .sy files to markdown, traversing full document tree including child blocks."""
import json, shutil
from pathlib import Path

SIYUAN_DATA = Path(r"C:\Users\scott\SiYuan\data")
PROJECT_DATA = Path(r"D:\learn\agentic-ai-system-course-main\workspace\graduate-exam-agent\data")

NOTEBOOKS = {
    "301": ["20260515155301-wcdv2ip", "20260521212645-teyk23o"],
    "408": ["20260515155307-blvk8ai"],
    "生活": ["20260515105258-6yhxbci"],
}


def extract_markdown(node, level=0):
    parts = []
    if node is None:
        return parts
    node_type = node.get("Type", "")

    if node_type == "NodeText":
        d = node.get("Data", "")
        if d:
            parts.append(d)
    elif node_type == "NodeTextMark":
        c = node.get("TextMarkTextContent", "")
        if c:
            parts.append(c)
    elif node_type == "NodeHeading":
        h_level = min(node.get("HeadingLevel", 1) + level, 6)
        parts.append("\n" + "#" * h_level + " ")
    elif node_type == "NodeListItem":
        parts.append("  - ")
    elif node_type == "NodeParagraph":
        parts.append("\n")
    elif node_type == "NodeCodeBlockCode":
        code = node.get("Data", "")
        if code:
            parts.append("\n```\n" + code + "\n```\n")
    elif node_type == "NodeThematicBreak":
        parts.append("\n---\n")
    elif node_type == "NodeBlockquote":
        parts.append("\n> ")
    elif node_type == "NodeMathBlock":
        content = node.get("Data", "")
        if content:
            parts.append("\n$$\n" + content + "\n$$\n")
    elif node_type == "NodeTable":
        parts.append("\n")

    for child in node.get("Children") or []:
        parts.extend(extract_markdown(child, level))
    return parts


def clean_filename(name):
    invalid = '<>:"/\\|?*'
    for c in invalid:
        name = name.replace(c, "_")
    return name.strip()[:80]


def collect_all_text(doc, base_path):
    """Recursively collect text from a document AND all nested child block .sy files."""
    parts = []
    doc_id = doc.get("ID", "")

    # Main document text
    parts.extend(extract_markdown(doc))

    # Recursively traverse child block directory tree
    _collect_child_blocks(base_path / doc_id, parts)

    return "".join(parts).strip()


def _collect_child_blocks(dir_path, parts):
    """Recursively walk a block directory, extracting text from all .sy files."""
    if not dir_path.exists() or not dir_path.is_dir():
        return
    for child_file in sorted(dir_path.glob("*.sy")):
        try:
            child_doc = json.loads(child_file.read_text(encoding="utf-8"))
            child_text = "".join(extract_markdown(child_doc))
            if child_text.strip():
                parts.append(child_text)
            # Recursively process this child's own subdirectory
            child_id = child_doc.get("ID", "")
            _collect_child_blocks(dir_path / child_id, parts)
        except Exception:
            pass
    # Also check for .sy files in nested subdirectories that aren't block IDs
    for subdir in sorted(dir_path.iterdir()):
        if subdir.is_dir() and not (dir_path / f"{subdir.name}.sy").exists():
            _collect_child_blocks(subdir, parts)


# Clear old
for subject in ["301", "408", "生活"]:
    d = PROJECT_DATA / subject
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True, exist_ok=True)

manifest = {}
total_files = 0

for subject, notebook_ids in NOTEBOOKS.items():
    manifest[subject] = []

    for nb_id in notebook_ids:
        nb_path = SIYUAN_DATA / nb_id
        if not nb_path.exists():
            continue

        for sy_file in sorted(nb_path.glob("*.sy")):
            try:
                doc = json.loads(sy_file.read_text(encoding="utf-8"))
                title = doc.get("Properties", {}).get("title", "untitled")
                updated = doc.get("Properties", {}).get("updated", "")
                text = collect_all_text(doc, nb_path)

                if len(text) < 20:
                    continue

                safe_title = clean_filename(title)
                md_path = PROJECT_DATA / subject / f"{safe_title}.md"

                update_str = ""
                if len(updated) == 14:
                    update_str = f"{updated[:4]}-{updated[4:6]}-{updated[6:8]}"

                full_md = (
                    f"---\n"
                    f"title: {title}\n"
                    f"subject: {subject}\n"
                    f"updated: {update_str}\n"
                    f"source: {nb_id}/{sy_file.stem}\n"
                    f"---\n\n"
                    f"# {title}\n\n{text}"
                )

                md_path.write_text(full_md, encoding="utf-8")
                total_files += 1
                manifest[subject].append({
                    "title": title,
                    "file": f"{safe_title}.md",
                    "updated": update_str,
                    "chars": len(text),
                })
                print(f"  [{subject}] {title} ({len(text):,} chars)")

            except Exception as e:
                print(f"  ERROR: {sy_file.name} - {e}")

(PROJECT_DATA / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)

print(f"\nDone! {total_files} files")
for subject in ["301", "408", "生活"]:
    files = manifest.get(subject, [])
    total_chars = sum(f["chars"] for f in files)
    print(f"  {subject}: {len(files)} files, {total_chars:,} chars")
