"""
批量 OCR 高数章节自测解析 PDF → qwen3.6-plus → markdown
"""
import fitz, base64, os, time, json
from pathlib import Path
from openai import OpenAI

API_KEY = "sk-4880953c556543bfa87a8d45f91aa95c"
MODEL = "qwen3.6-plus"

client = OpenAI(api_key=API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

SRC = Path("D:/study/301/27亲带班课程文件/02 基础阶段/02 基础段章节自测/基础段-01-高数章节自测")
OUT = Path("D:/learn/agentic-ai-system-course-main/knowledge-base/301-习题集/高等数学/章节自测解析")
DPI = 200

CHAPTERS = {
    "01": "第一章 函数极限连续",
    "02": "第二章 导数与微分", "03": "第三章 一元积分学",
    "04": "第四章 微分方程", "05": "第五章 多元函数微分学",
    "06": "第六章 二重积分", "07": "第七章 无穷级数",
    "08": "第八章 向量及空间解析几何", "09": "第九章 三重积分",
    "10": "第十章 曲线曲面积分",
}

PROMPT = """OCR提取图片中所有文字和数学公式。要求逐字还原，不要省略、概括或改写。
- 数学公式用LaTeX：行内$...$，块级$$...$$
- 保留题目编号、选项(A)(B)(C)(D)、答案、解析结构
- 如果图片中有表格，用markdown表格还原
只输出OCR内容，不要加任何解释。"""


def ocr_page(img_b64: str, page_num: int) -> str:
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    {"type": "text", "text": PROMPT},
                ]}],
                max_tokens=8192, temperature=0.1,
            )
            return resp.choices[0].message.content
        except Exception as e:
            err = str(e)
            if "Arrearage" in err or "Free" in err or "quota" in err.lower():
                raise RuntimeError(f"额度耗尽: {err}")
            print(f"  p{page_num} retry {attempt+1}: {err[:100]}")
            if attempt < 2:
                time.sleep(10 * (attempt + 1))
    return f"[OCR FAILED page {page_num}]"


def process_pdf(pdf_path: Path, ch_num: str):
    ch_name = CHAPTERS[ch_num]
    out_dir = OUT / ch_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Render
    doc = fitz.open(str(pdf_path))
    matrix = fitz.Matrix(DPI / 72, DPI / 72)
    imgs = []
    for i in range(doc.page_count):
        b64 = base64.b64encode(doc[i].get_pixmap(matrix=matrix).tobytes("png")).decode()
        imgs.append(b64)
    doc.close()

    print(f"[{ch_num}/10] {pdf_path.name}  {len(imgs)}p ", end="", flush=True)

    # OCR
    md = [f"# {ch_name} — 章节测试解析\n\n> 来源: {pdf_path.name}  |  OCR: {MODEL}\n\n---\n"]
    for i, img in enumerate(imgs):
        print(f"{i+1}", end="", flush=True)
        md.append(f"\n## 第{i+1}页\n\n")
        md.append(ocr_page(img, i + 1))
        md.append("\n\n---\n")
        if i < len(imgs) - 1:
            time.sleep(0.5)

    md_path = out_dir / "章节测试解析.md"
    md_path.write_text("".join(md), encoding="utf-8")
    print(f"  → {md_path}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pdfs = sorted([f for f in os.listdir(SRC) if "解析" in f and f.endswith(".pdf")])
    print(f"共 {len(pdfs)} 个PDF\n")

    for pdf_name in pdfs:
        ch_num = pdf_name.split()[0]
        try:
            process_pdf(SRC / pdf_name, ch_num)
        except RuntimeError as e:
            print(f"\n!!! {e}")
            break
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(1)

    print("\nDone!")


if __name__ == "__main__":
    main()
