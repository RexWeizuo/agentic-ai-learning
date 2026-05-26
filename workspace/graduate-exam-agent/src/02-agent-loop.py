"""
Ch.02 — Agent 循环 (The Agent Loop)

在 Ch.01 的单次工具调用外面包一层循环。
模型每轮可以决定：继续调工具，还是给出最终回答。

新增：
- 五阶段循环：Observe → Plan → Act → Reflect → Stop
- 五层停止条件：模型自己停 / step cap / token cap / doom-loop / user cancel
- 错误分类：transient（重试）vs permanent（立即报错）
- 模型可以多轮优化搜索词：搜"极限的定义"无果 → 搜"极限" → 搜"ε-δ"

数据源：C:/Users/scott/SiYuan/data/ 下的 .sy 文件（JSON 树格式）
"""

import json
import re
import sys
import signal
from pathlib import Path
from anthropic import Anthropic

# ============================================================
# 第 0 步：配置
# ============================================================

SIYUAN_DATA = Path(r"C:\Users\scott\SiYuan\data")

NOTEBOOK_MAP = {
    "20260515105227-8myszzy": "201",
    "20260515155301-wcdv2ip": "301",
    "20260521212645-teyk23o": "301",
    "20260515155307-blvk8ai": "408",
}

SUBJECT_NAMES = {"201": "英语", "301": "数学", "408": "计算机"}

MODEL = "deepseek-v4-pro[1m]"

client = Anthropic(
    api_key="sk-35cdf1877e65407eaf810f0aebd4d78f",
    base_url="https://api.deepseek.com/anthropic",
)

# ============================================================
# 停止条件配置（Ch.02：五层，从软到硬）
# ============================================================

MAX_STEPS = 15          # 硬上限：防止无限循环
TOKEN_BUDGET = 32000    # token 预算
GRACE_STEP = 12         # 还剩几步时提醒模型"该收尾了"


# ============================================================
# .sy 解析器（同 Ch.01）
# ============================================================

def extract_text_from_sy(node: dict) -> str:
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
# 第 1 步：工具定义
# ============================================================

TOOLS = [
    {
        "name": "search_siyuan",
        "description": (
            "搜索思源笔记中的考研知识点。"
            "传入简短关键词（如'死锁'、'极限'、'贝叶斯'、'IO管理'、'abandon'），"
            "在数学(301)、计算机(408)、英语(201)三个笔记本中搜索。"
            "返回匹配文档的内容摘要。"
            "提示：用单个核心词搜索效果最好，如搜'极限'而不是'极限的定义是什么'。"
            "如果搜索结果不理想，可以用不同的关键词再搜一次。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "要搜索的简短关键词，如'极限'、'死锁'、'贝叶斯'"
                },
                "subject": {
                    "type": "string",
                    "enum": ["301", "408", "201", "all"],
                    "description": "限定搜索范围：301=数学, 408=计算机, 201=英语, all=全部"
                }
            },
            "required": ["keyword"]
        }
    }
]


# ============================================================
# 第 2 步：工具实现
# ============================================================

def search_siyuan(keyword: str, subject: str = "all") -> str:
    if subject == "all":
        target_notebooks = list(NOTEBOOK_MAP.keys())
    else:
        target_notebooks = [nb for nb, subj in NOTEBOOK_MAP.items() if subj == subject]

    # 关键词回退：完整词搜不到，用短词重试
    short_keywords = [k.strip() for k in re.split(r'[的，、。！？\s]+', keyword) if len(k.strip()) >= 1]
    seen = set()
    keywords_to_try = []
    for k in short_keywords:
        if k not in seen and len(k) >= 1:
            keywords_to_try.append(k)
            seen.add(k)
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
        if results:
            break

    if not results:
        return f"[无结果] 在思源笔记中未找到与「{keyword}」相关的内容。建议：换个更简短的关键词重试。"

    results.sort(key=lambda r: r["matches"], reverse=True)
    output_parts = []
    if effective_keyword != keyword:
        output_parts.append(f"「{keyword}」无结果，改用「{effective_keyword}」找到 {len(results)} 个文档：\n")
    else:
        output_parts.append(f"搜索「{effective_keyword}」找到 {len(results)} 个文档：\n")

    for r in results[:5]:
        snippet = r["snippet"]
        if len(snippet) > 600:
            snippet = snippet[:600] + "\n...(内容过长，已截断)"
        output_parts.append(
            f"【{r['notebook']}】{r['title']}（{r['updated']}，{r['matches']} 处匹配）\n{snippet}"
        )
        output_parts.append("")

    if len(results) > 5:
        output_parts.append(f"...还有 {len(results) - 5} 个文档未展示，可缩小搜索范围。")
    return "\n".join(output_parts)


# ============================================================
# 错误分类（Ch.02：transient → 重试，permanent → 立即报错）
# ============================================================

def classify_error(err: Exception) -> str:
    """将异常分为 transient（可重试）或 permanent（立即停止）。"""
    msg = str(err).lower()
    # Transient: 网络问题、服务端过载、速率限制
    if any(kw in msg for kw in ["timeout", "rate", "overloaded", "server error", "503", "502", "429"]):
        return "transient"
    # Permanent: 认证、权限、参数错误
    if any(kw in msg for kw in ["401", "403", "400", "invalid", "auth", "not found"]):
        return "permanent"
    return "permanent"  # 未知错误保守处理


def execute_tool(name: str, args: dict) -> str:
    if name == "search_siyuan":
        return search_siyuan(args.get("keyword", ""), args.get("subject", "all"))
    return f"[错误] 未知工具: {name}"


# ============================================================
# Doom-loop 检测（Ch.02：连续三次相同调用 → 卡住了）
# ============================================================

def check_doom_loop(recent_calls: list) -> bool:
    """最近三次调用名称和参数完全相同时，判定为 doom loop。"""
    if len(recent_calls) < 3:
        return False
    last_three = recent_calls[-3:]
    first = (last_three[0][0], last_three[0][1])  # (name, args)
    return all((name, args) == first for name, args in last_three)


# ============================================================
# 第 3+4+5 步：Agent 循环（五阶段）
# ============================================================

def agent_loop(user_message: str, abort_flag=None) -> str:
    """
    Agent 循环：重复 Observe → Plan → Act → Reflect → Stop 直到模型认为自己完成。
    返回模型的最终文本回答，或在预算耗尽时返回部分结果。
    """

    # ---- 状态初始化 ----
    messages = [{"role": "user", "content": user_message}]
    total_tokens = 0
    step = 0
    recent_calls = []  # 用于 doom-loop 检测

    system_prompt = (
        "你是考研学习助手。你可以在用户的思源笔记中搜索知识点。"
        "用户笔记包含三门科目：数学(301)、计算机专业课(408)、英语词汇(201)。"
        "重要规则：\n"
        "1. 用简短的核心词搜索（如'极限'而非'极限的定义是什么'）。\n"
        "2. 如果一次搜索无结果，换一个更简短的关键词再搜。\n"
        "3. 收到足够信息后直接给出最终答案，不要再搜索。\n"
        "4. 回答时引用具体的文档标题和科目来源。"
    )

    # ---- 主循环 ----
    while step < MAX_STEPS and total_tokens < TOKEN_BUDGET:
        step += 1

        # Grace call: 接近预算时提醒模型收尾
        current_system = system_prompt
        if step >= GRACE_STEP:
            current_system = system_prompt + (
                f"\n\n[系统提示] 这是第 {step} 轮，即将达到最大轮次({MAX_STEPS})。"
                "如果还需要更多信息，请给出你目前能给出的最佳回答。"
            )

        # ---- Observe + Plan: 调用模型 ----
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=current_system,
                messages=messages,
                tools=TOOLS,
            )
        except Exception as e:
            error_class = classify_error(e)
            if error_class == "transient":
                print(f"  [transient error, retrying] {e}")
                continue
            else:
                return f"[错误] 模型调用失败: {e}"

        # 累计 token
        if hasattr(response, "usage") and response.usage:
            total_tokens += response.usage.input_tokens + response.usage.output_tokens

        # 收集模型返回的所有 blocks
        assistant_blocks = list(response.content)

        # 检查是否有 tool_use
        tool_uses = [b for b in assistant_blocks if b.type == "tool_use"]
        text_blocks = [b for b in assistant_blocks if b.type == "text"]

        # ---- Stop 条件 1: 模型自己停了（没有 tool_use）----
        if not tool_uses:
            for tb in text_blocks:
                return tb.text
            return "(模型未返回文本回答)"

        # ---- Act: 执行工具 ----
        tool_results = []
        for block in tool_uses:
            print(f"\n[Step {step}] {block.name}({block.input})")

            # Doom-loop 检测
            recent_calls.append((block.name, json.dumps(dict(block.input), sort_keys=True, ensure_ascii=False)))
            if check_doom_loop(recent_calls):
                return (
                    f"[警告] 检测到重复调用 {block.name} 已达 3 次，可能是搜索方向有误。"
                    f"建议换个关键词或科目重试。最后一次搜索参数: {dict(block.input)}"
                )

            # 检查 abort
            if abort_flag and abort_flag():
                return "[已取消] 用户中断了 Agent。"

            result = execute_tool(block.name, dict(block.input))
            print(f"         → {len(result)} 字符")
            tool_results.append((block.id, result))

        # ---- Reflect: 把结果追加到消息列表 ----
        # 注意：所有 assistant blocks（含 thinking）都要回传（DeepSeek 要求）
        messages.append({"role": "assistant", "content": assistant_blocks})

        user_content = []
        for tool_id, result in tool_results:
            user_content.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": result
            })
        messages.append({"role": "user", "content": user_content})

        # ---- 循环回到 Observe ----

    # ---- 预算耗尽 ----
    if total_tokens >= TOKEN_BUDGET:
        return "[提示] 已达到 token 预算上限，回答可能不完整。"
    return "[提示] 已达到最大轮次上限，回答可能不完整。"


# ============================================================
# 交互入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("📚 考研助手 > 请问：")

    # 简单的 Ctrl-C 处理
    cancelled = False

    def on_cancel():
        global cancelled
        cancelled = True

    original_handler = signal.signal(signal.SIGINT, lambda s, f: on_cancel())

    answer = agent_loop(question, abort_flag=lambda: cancelled)
    # 写入文件避免终端 GBK 编码问题
    output_path = Path(__file__).parent / "last_answer.txt"
    output_path.write_text(answer, encoding="utf-8")
    print(f"\n[回答已写入 {output_path}]")
    # 尝试打印前 200 字符预览
    try:
        preview = answer[:200]
        print(preview)
        if len(answer) > 200:
            print(f"...(共 {len(answer)} 字符)")
    except UnicodeEncodeError:
        print("(回答含特殊 Unicode 字符，完整内容请查看 last_answer.txt)")
