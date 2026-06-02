"""
批量 OCR 高数章节自测解析 PDF
将 10 个 PDF 每页渲染为 PNG，用 DashScope VL 模型 OCR，输出 markdown
"""
import fitz
import os
import base64
import time
import json
from pathlib import Path
from openai import OpenAI

# --- Config ---
BASE_DIR = Path("D:/study/301/27亲带班课程文件/02 基础阶段/02 基础段章节自测/基础段-01-高数章节自测")
OUTPUT_BASE = BASE_DIR  # 输出到同级子目录
DPI = 200
MATRIX = fitz.Matrix(DPI / 72, DPI / 72)

# DashScope OpenAI-compatible endpoint
client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

MODEL = "qwen-vl-max"

OCR_PROMPT = """请将这张图片中的文字和数学公式完整无误地OCR提取出来，输出为markdown格式。

要求：
1. 所有文字逐字还原，不要省略、概括或改写
2. 数学公式使用 LaTeX 语法，行内公式用 $...$，块级公式用 $$...$$
3. 保留原有的题目编号、选项、解析结构
4. 如果图片中有表格，用 markdown 表格还原
5. 如果图片中有图形/坐标轴，用文字简要描述
6. 不要添加任何额外解释，只输出OCR内容"""

CHAPTER_NAMES = {
    "01": "第一章 函数极限连续",
    "02": "第二章 导数与微分",
    "03": "第三章 一元积分学",
    "04": "第四章 微分方程",
    "05": "第五章 多元函数微分学",
    "06": "第六章 二重积分",
    "07": "第七章 无穷级数",
    "08": "第八章 向量及空间解析几何",
    "09": "第九章 三重积分",
    "10": "第十章 曲线曲面积分",
}


def pdf_to_pages(pdf_path: Path, work_dir: Path):
    """Render PDF pages to PNG, return list of PNG paths"""
    doc = fitz.open(str(pdf_path))
    png_paths = []
    for i in range(doc.page_count):
        page = doc[i]
        pix = page.get_pixmap(matrix=MATRIX)
        png_path = work_dir / f"page_{i+1:02d}.png"
        pix.save(str(png_path))
        png_paths.append(png_path)
    doc.close()
    return png_paths


def ocr_page(image_path: Path, page_num: int) -> str:
    """OCR a single page image using DashScope VL model"""
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                {"type": "text", "text": OCR_PROMPT},
            ],
        }
    ]

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=4096,
                temperature=0.1,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"  Page {page_num} attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    return f"[OCR FAILED for page {page_num}]"


def process_pdf(pdf_path: Path, ch_num: str):
    """Process one PDF: render pages, OCR each, combine to markdown"""
    ch_name = CHAPTER_NAMES[ch_num]
    out_dir = BASE_DIR / f"{ch_num}-{ch_name.split(' ')[-1]}" if " " in ch_name else BASE_DIR / f"{ch_num}-{ch_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    work_dir = out_dir / "_ocr_temp"
    work_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"[{ch_num}/10] {pdf_path.name}")
    print(f"{'='*60}")

    # Render pages
    print("  Rendering pages...")
    png_paths = pdf_to_pages(pdf_path, work_dir)
    total_pages = len(png_paths)
    print(f"  {total_pages} pages rendered")

    # OCR each page
    md_parts = [f"# {ch_name} — 章节测试解析\n\n> OCR from: {pdf_path.name}\n\n---\n\n"]
    for idx, png_path in enumerate(png_paths):
        page_num = idx + 1
        print(f"  OCR page {page_num}/{total_pages}...", end=" ", flush=True)
        start = time.time()
        text = ocr_page(png_path, page_num)
        elapsed = time.time() - start
        print(f"({elapsed:.1f}s, {len(text)} chars)")
        md_parts.append(f"## Page {page_num}\n\n{text}\n\n---\n\n")
        # Small delay between pages to avoid rate limits
        if idx < total_pages - 1:
            time.sleep(1)

    # Write combined markdown
    md_path = out_dir / "章节测试解析.md"
    md_path.write_text("".join(md_parts), encoding="utf-8")
    print(f"  → Saved: {md_path}")

    # Cleanup temp PNGs
    for p in png_paths:
        p.unlink()
    work_dir.rmdir()

    return md_path


def main():
    # Find all 解析 PDFs
    pdfs = sorted([f for f in os.listdir(BASE_DIR) if f.endswith("解析.pdf")])
    print(f"Found {len(pdfs)} PDFs to process\n")

    results = []
    for pdf_name in pdfs:
        # Extract chapter number
        ch_num = pdf_name.split()[0]  # "01", "02", etc.
        pdf_path = BASE_DIR / pdf_name
        try:
            md_path = process_pdf(pdf_path, ch_num)
            results.append((pdf_name, "OK", md_path))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((pdf_name, f"FAIL: {e}", None))
        # Delay between PDFs
        time.sleep(2)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, status, path in results:
        print(f"  {name}: {status}")

    print("\nDone!")


if __name__ == "__main__":
    main()
