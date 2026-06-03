"""
批量 OCR 线代 + 概统 章节自测解析 PDF → qwen3.6-plus → markdown
"""
import fitz, base64, os, time
from pathlib import Path
from openai import OpenAI

API_KEY = "sk-4880953c556543bfa87a8d45f91aa95c"
MODEL = "qwen3.6-plus"
DPI = 200

client = OpenAI(api_key=API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

CONFIG = [
    {
        "src": "D:/study/301/27亲带班课程文件/02 基础阶段/02 基础段章节自测/基础段-02-线代章节自测",
        "out": "D:/learn/agentic-ai-system-course-main/knowledge-base/301-习题集/线性代数/章节自测解析",
        "chapters": {
            "01": "第一章 行列式", "02": "第二章 矩阵", "03": "第三章 向量组",
            "04": "第四章 方程组", "05": "第五章 特征值", "06": "第六章 二次型",
        }
    },
    {
        "src": "D:/study/301/27亲带班课程文件/02 基础阶段/02 基础段章节自测/基础段-03-概统章节自测",
        "out": "D:/learn/agentic-ai-system-course-main/knowledge-base/301-习题集/概率统计/章节自测解析",
        "chapters": {
            "01": "第一章 随机事件与概率", "02": "第二章 一维随机变量",
            "03": "第三章 多维随机变量", "04": "第四章 随机变量数字特征",
            "05": "第五章 数理统计", "06": "第六章 参数估计",
        }
    },
]

PROMPT = """OCR提取图片中所有文字和数学公式。要求逐字还原，不要省略、概括或改写。
- 数学公式用LaTeX：行内$...$，块级$$...$$
- 保留题目编号、选项(A)(B)(C)(D)、答案、解析结构
- 如果图片中有表格，用markdown表格还原
只输出OCR内容，不要加任何解释。"""


def ocr_page(img_b64, page_num):
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
            if any(w in err for w in ["Arrearage", "Free", "quota"]):
                raise RuntimeError(f"额度耗尽: {err}")
            if attempt < 2:
                print(f"\n    p{page_num} retry {attempt+1}: {err[:80]}")
                time.sleep(10 * (attempt + 1))
    return f"[OCR FAILED page {page_num}]"


def process_subject(cfg):
    src, out_base = Path(cfg["src"]), Path(cfg["out"])
    out_base.mkdir(parents=True, exist_ok=True)
    matrix = fitz.Matrix(DPI / 72, DPI / 72)

    pdfs = sorted([f for f in os.listdir(src) if "解析" in f and f.endswith(".pdf")])
    print(f"\n{'='*50}\n{src.name}\n{'='*50}")

    for pdf_name in pdfs:
        ch_num = pdf_name.split()[0]
        ch_name = cfg["chapters"][ch_num]
        out_dir = out_base / ch_name
        out_dir.mkdir(parents=True, exist_ok=True)
        md_file = out_dir / "章节测试解析.md"
        if md_file.exists():
            print(f"  [{ch_num}] {pdf_name[:45]:<47} skip (exists)")
            continue

        pdf_path = src / pdf_name
        doc = fitz.open(str(pdf_path))
        imgs = [base64.b64encode(doc[i].get_pixmap(matrix=matrix).tobytes("png")).decode()
                for i in range(doc.page_count)]
        doc.close()

        print(f"  [{ch_num}] {pdf_name[:45]:<47} {len(imgs)}p ", end="", flush=True)

        md = [f"# {ch_name} — 章节测试解析\n\n> 来源: {pdf_name}  |  OCR: {MODEL}\n\n---\n"]
        for i, img in enumerate(imgs):
            print(f"{i+1}", end="", flush=True)
            md.append(f"\n## 第{i+1}页\n\n")
            md.append(ocr_page(img, i + 1))
            md.append("\n\n---\n")
            if i < len(imgs) - 1:
                time.sleep(0.5)

        (out_dir / "章节测试解析.md").write_text("".join(md), encoding="utf-8")
        print(" OK")


def main():
    for cfg in CONFIG:
        try:
            process_subject(cfg)
        except RuntimeError as e:
            print(f"\n!!! {e}")
            break
    print("\nDone!")


if __name__ == "__main__":
    main()
