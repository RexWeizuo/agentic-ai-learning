"""
Ch.01 — 一次工具调用 (One Tool Call)

考研 Agent 的第一个原子操作：从思源笔记中搜索知识点。
演示四步循环：发消息+工具定义 → 模型返回 tool_use → 执行 → 返回结果

数据源：C:/Users/scott/SiYuan/data/ 下的 .sy 文件（JSON 树格式）
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic

# ============================================================
# 第 0 步：配置
# ============================================================

SIYUAN_DATA = Path(r"C:\Users\scott\SiYuan\data")

# 笔记本 ID → 科目映射
NOTEBOOK_MAP = {
    "20260515105227-8myszzy": "201",   # 英语词汇 (A-Z)
    "20260515155301-wcdv2ip": "301",   # 数学 - 三大计算/高等数学
    "20260521212645-teyk23o": "301",   # 数学 - 概率统计/线性代数
    "20260515155307-blvk8ai": "408",   # 计算机专业课 - OS
}

SUBJECT_NAMES = {"201": "英语", "301": "数学", "408": "计算机"}

MODEL = "deepseek-v4-pro[1m]"

client = Anthropic(
    api_key="sk-35cdf1877e65407eaf810f0aebd4d78f",
    base_url="https://api.deepseek.com/anthropic",
)

# ============================================================
# .sy 文件解析器 —— 从思源 JSON 树提取纯文本
# ============================================================

def extract_text_from_sy(node: dict) -> str:
    """递归遍历 .sy 的 JSON 树，提取所有文本内容。"""
    parts = []
    node_type = node.get("Type", "")

    if node_type == "NodeText":
        data = node.get("Data", "")
        if data:
            parts.append(data)
    elif node_type == "NodeTextMark":
        content = node.get("TextMarkTextContent", "")
        if content:
            parts.append(content)

    if node_type == "NodeHeading":
        level = node.get("HeadingLevel", 1)
        parts.append(f"\n{'#' * level} ")

    if node_type == "NodeListItem":
        parts.append("  - ")

    if node_type == "NodeParagraph":
        parts.append("\n")

    for child in node.get("Children", []):
        parts.append(extract_text_from_sy(child))

    return "".join(parts)


def get_document_title(doc: dict) -> str:
    return doc.get("Properties", {}).get("title", "无标题")


def get_document_updated(doc: dict) -> str:
    updated = doc.get("Properties", {}).get("updated", "")
    if len(updated) == 14:
        return f"{updated[:4]}-{updated[4:6]}-{updated[6:8]} {updated[8:10]}:{updated[10:12]}"
    return updated


# ============================================================
# 第 1 步：定义工具（schema 就是合同）
# ============================================================

TOOLS = [
    {
        "name": "search_siyuan",
        "description": (
            "在思源讲义中搜索某个知识点的具体说法。"
            "传入简短关键词（如'死锁'、'极限'、'贝叶斯'、'IO管理'），"
            "在数学(301)、计算机(408)两个笔记本中搜索。"
            "返回匹配内容的摘要、文档标题和出处。"
            "用于回答知识点问题或分析错题时，先查阅讲义中的定义和解题方法，"
            "再结合自身知识给出回答。"
            "用户闲聊、提问不涉及考研数学或计算机范围时不要调用。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "要搜索的关键词，支持中文和英文"
                },
                "subject": {
                    "type": "string",
                    "enum": ["301", "408", "201", "all"],
                    "description": "限定搜索范围：301=数学, 408=计算机, 201=英语, all=全部科目"
                }
            },
            "required": ["keyword"]
        }
    }
]


# ============================================================
# 第 2 步：实现工具处理函数（这是你的"厨房"）
# ============================================================

def search_siyuan(keyword: str, subject: str = "all") -> str:
    """在思源 .sy 文件中搜索关键词，返回匹配内容。
    先用完整关键词搜索，无结果时自动拆分为短词重试。
    """

    if subject == "all":
        target_notebooks = list(NOTEBOOK_MAP.keys())
    else:
        target_notebooks = [nb for nb, subj in NOTEBOOK_MAP.items() if subj == subject]

    # 关键词列表：完整词 + 拆分的短词（用于回退）
    import re
    # 按常见分隔符拆词
    short_keywords = [k.strip() for k in re.split(r'[的，、。！？\s]+', keyword) if len(k.strip()) >= 1]
    # 去重，最短的在前
    seen = set()
    keywords_to_try = []
    for k in short_keywords:
        if k not in seen and len(k) >= 1:
            keywords_to_try.append(k)
            seen.add(k)
    # 完整关键词排最前
    if keyword not in keywords_to_try:
        keywords_to_try.insert(0, keyword)

    results = []
    effective_keyword = keyword

    for try_keyword in keywords_to_try:
        results = []
        effective_keyword = try_keyword
        for notebook_id in target_notebooks:
            nb_path = SIYUAN_DATA / notebook_id
            if not nb_path.exists():
                continue

            subject_name = SUBJECT_NAMES.get(NOTEBOOK_MAP[notebook_id], "未知")

            for sy_file in sorted(nb_path.glob("*.sy")):
                try:
                    doc = json.loads(sy_file.read_text(encoding="utf-8"))
                    text = extract_text_from_sy(doc)
                    title = get_document_title(doc)
                    updated = get_document_updated(doc)

                    if try_keyword.lower() not in text.lower():
                        continue

                    lines = text.split("\n")
                    contexts = []
                    for i, line in enumerate(lines):
                        if try_keyword.lower() in line.lower():
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            ctx = "\n".join(lines[start:end]).strip()
                            if ctx:
                                contexts.append(ctx)
                            if len(contexts) >= 3:
                                break

                    if contexts:
                        results.append({
                            "notebook": subject_name,
                            "title": title,
                            "updated": updated,
                            "matches": sum(1 for l in lines if try_keyword.lower() in l.lower()),
                            "snippet": "\n---\n".join(contexts)
                        })

                except Exception:
                    continue

        # 找到结果就停止尝试更短的词
        if results:
            break

    # 如果所有关键词都没结果，报告用的关键词
    if not results:
        return f"在思源笔记中未找到与「{keyword}」相关的内容。"

    results.sort(key=lambda r: r["matches"], reverse=True)

    output_parts = [f"搜索「{effective_keyword}」找到 {len(results)} 个相关文档（最多展示 5 个）：\n"]
    if effective_keyword != keyword:
        output_parts[0] = f"搜索「{keyword}」无结果，改用「{effective_keyword}」找到 {len(results)} 个相关文档（最多展示 5 个）：\n"
    for r in results[:5]:
        snippet = r["snippet"]
        if len(snippet) > 600:
            snippet = snippet[:600] + "\n...(内容过长，已截断)"
        output_parts.append(
            f"【{r['notebook']}】{r['title']}（更新于 {r['updated']}，{r['matches']} 处匹配）\n"
            f"{snippet}"
        )
        output_parts.append("")

    if len(results) > 5:
        output_parts.append(f"...还有 {len(results) - 5} 个文档未展示，可缩小搜索范围。")

    return "\n".join(output_parts)


def execute_tool(name: str, args: dict) -> str:
    """工具调度器：根据名称分发。Ch.03 会深入讲验证和错误分类。"""
    if name == "search_siyuan":
        return search_siyuan(args.get("keyword", ""), args.get("subject", "all"))
    return f"未知工具: {name}"


# ============================================================
# 第 3+4 步：完整的一次工具调用（four-step cycle）
# ============================================================

def one_tool_call(user_message: str) -> str:
    """一次完整的工具调用：发消息 → 收 tool_use → 执行 → 返回结果。"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "你是考研学习助手，专注于数学(301)和计算机专业课(408)。"
            "当用户问到具体知识点或做错题时，先用 search_siyuan 查阅讲义中该知识点的"
            "定义和解题方法，然后将讲义内容与自身知识结合，给出准确回答。"
            "搜索结果中【】内标明了科目和文档名称，回答时引用出处。"
            "用户闲聊或提问不涉及考研数学/计算机范围时，直接回答，不要搜索。"
        ),
        messages=[{"role": "user", "content": user_message}],
        tools=TOOLS,
    )

    # 收集模型返回的所有 content blocks（包括 thinking）
    assistant_blocks = list(response.content)

    for block in assistant_blocks:
        if block.type == "tool_use":
            print(f"\n[工具调用] {block.name}({block.input})")

            result = execute_tool(block.name, dict(block.input))
            print(f"[工具返回] {len(result)} 字符")

            final_response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system="你是考研学习助手。将搜索结果中的讲义内容与自身知识结合，给出完整回答。引用文档标题和科目来源。",
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_blocks},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            }
                        ]
                    }
                ],
            )
            # 取最后一个 text block 作为回答
            for fb in reversed(final_response.content):
                if fb.type == "text":
                    return fb.text
            return "(模型未返回文本回答)"

    # 取最后一个 text block
    for fb in reversed(response.content):
        if fb.type == "text":
            return fb.text
    return "(模型未返回文本回答)"


# ============================================================
# 交互入口
# ============================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("📚 考研助手 > 请问：")

    answer = one_tool_call(question)
    print(f"\n{answer}")
