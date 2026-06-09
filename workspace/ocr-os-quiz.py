"""
OCR 408 OS 习题图片 → qwen3.7-plus → markdown
处理 knowledge-base/408-计算机-quiz/OS/ 下所有习题图片
"""
import base64, os, time, json
from pathlib import Path
from openai import OpenAI

API_KEY = "sk-9980a81fba7f4d948c30a04100e27e8c"
MODEL = "qwen3.7-plus"

client = OpenAI(api_key=API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

SRC = Path(r"D:\learn\agentic-ai-system-course-main\knowledge-base\408-计算机-quiz\OS")

PROMPT = """OCR提取图片中的所有文字和数学公式。要求逐字还原，不要省略、概括或改写。
- 数学公式用LaTeX：行内用 $...$，块级公式用 $$...$$
- 保留题目编号、选项标注(A)(B)(C)(D)、答案、解析等全部结构
- 如果图片中有表格，用markdown表格还原
- 注意识别中文、英文、数字混合内容
只输出OCR内容，不要加任何解释。"""

def ocr_image(img_path: Path) -> str:
    """OCR a single image file, returns text."""
    # Read and encode image
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode()

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    {"type": "text", "text": PROMPT},
                ]}],
                max_tokens=4096,
                temperature=0.1,
            )
            text = resp.choices[0].message.content
            return text
        except Exception as e:
            err = str(e)
            if "Arrearage" in err or "Free" in err or "quota" in err.lower():
                raise RuntimeError(f"额度耗尽: {err}")
            print(f"    retry {attempt+1}: {err[:120]}")
            if attempt < 2:
                time.sleep(10 * (attempt + 1))
    return f"[OCR FAILED: {img_path.name}]"


def process_section(section_dir: Path, section_name: str) -> str:
    """Process all images in a section, returning combined markdown."""
    # section_dir is e.g.: .../1.1+OS概述+89a31fd9-18/images/
    images_dir = section_dir / "images"
    if not images_dir.exists():
        return ""

    # Collect images grouped by question number
    questions = {}
    for img_path in sorted(images_dir.rglob("img-*.png")):
        q_num = img_path.parent.name  # e.g., "01", "02"
        if q_num not in questions:
            questions[q_num] = []
        questions[q_num].append(img_path)

    print(f"  {section_name}: {len(questions)} questions, {sum(len(v) for v in questions.values())} images")

    md_parts = []
    for q_num in sorted(questions.keys()):
        imgs = questions[q_num]
        md_parts.append(f"\n## 第{q_num}题\n")
        for img_path in imgs:
            img_label = img_path.stem  # e.g., "img-1"
            print(f"    OCR: {section_name}/{q_num}/{img_label}...", end=" ", flush=True)
            text = ocr_image(img_path)
            md_parts.append(f"\n### {img_label}\n\n{text}\n")
            print(f"{len(text)} chars")
            time.sleep(0.3)  # rate limit

    return "\n".join(md_parts)


def main():
    # Walk through the OS directory structure
    chapters = sorted([d for d in SRC.iterdir() if d.is_dir()])
    total_images = 0
    total_success = 0

    for chapter_dir in chapters:
        chapter_name = chapter_dir.name
        print(f"\n{'='*60}")
        print(f"Chapter: {chapter_name}")
        print(f"{'='*60}")

        # Find 习题 directories
        xiti_dir = chapter_dir / "习题"
        if not xiti_dir.exists():
            print(f"  No 习题 dir, skipping")
            continue

        for section_dir in sorted(xiti_dir.iterdir()):
            if not section_dir.is_dir():
                continue
            section_name = section_dir.name  # e.g., "1.1+OS概述+89a31fd9-18"
            images_dir = section_dir / "images"

            if not images_dir.exists():
                continue

            # Count images
            img_count = len(list(images_dir.rglob("img-*.png")))
            if img_count == 0:
                continue

            try:
                md_content = process_section(section_dir, section_name)
                if md_content:
                    # Build markdown header
                    header = f"# {section_name}\n\n> OCR: {MODEL}  |  日期: {time.strftime('%Y-%m-%d')}\n\n---\n"
                    full_md = header + md_content

                    # Save alongside images
                    out_path = section_dir / "ocr_result.md"
                    out_path.write_text(full_md, encoding="utf-8")
                    print(f"  → Saved: {out_path}")
            except RuntimeError as e:
                print(f"\n!!! 额度耗尽: {e}")
                return
            except Exception as e:
                print(f"  ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"Done!")


if __name__ == "__main__":
    main()
