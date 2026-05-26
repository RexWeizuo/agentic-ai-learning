"""
Ch.03 — 可信的工具 (Tools the Agent Can Trust)

在 Ch.02 的循环基础上，给每个工具加上完整的契约：
- 元数据标记：read_only, concurrency_safe, idempotent, open_world
- 五阶段验证管线：known → typed → semantic → permission → execute
- 结果信封：{ok, content, hint, meta} 替代裸字符串
- 错误带指引：不只说"没找到"，还告诉模型下一步怎么做
- 溯源信息：每个结果附带文件路径、时间戳、哈希
"""

import json
import re
import sys
import signal
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
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
    timeout=120.0,  # 给 DeepSeek 足够的响应时间
)

MAX_STEPS = 15
TOKEN_BUDGET = 32000
GRACE_STEP = 12


# ============================================================
# Ch.03 核心新增：工具元数据 + 结果信封
# ============================================================

class ToolResult:
    """结果信封 —— 不论成功失败，都走这个形状。"""

    def __init__(self, ok: bool, content: str = "", *,
                 recoverable: bool = True,
                 code: str = "",
                 hint: str = "",
                 meta: Optional[dict] = None):
        self.ok = ok
        self.content = content
        self.recoverable = recoverable
        self.code = code
        self.hint = hint
        self.meta = meta or {}

    def to_api_string(self) -> str:
        """转为发给模型的字符串。失败时附带 hint 指引下一步。"""
        if self.ok:
            parts = [self.content]
            if self.meta:
                parts.append(f"\n[溯源] 文件: {self.meta.get('source', '?')}"
                             f" | 时间: {self.meta.get('timestamp', '?')}"
                             f" | 哈希: {self.meta.get('hash', '?')[:12]}")
            return "".join(parts)
        else:
            parts = [f"[{self.code}] {self.content}"]
            if self.hint:
                parts.append(f"\n[建议] {self.hint}")
            return "".join(parts)


# ============================================================
# 工具注册表 —— 元数据是给循环看的，schema 是给模型看的
# ============================================================

TOOL_REGISTRY = {
    "search_siyuan": {
        # ---- 元数据（循环消费）----
        "version": 1,
        "read_only": True,
        "destructive": False,
        "concurrency_safe": True,    # 纯读，可以并行
        "idempotent": True,          # 相同输入总返回相同结果
        "open_world": False,         # 思源笔记是本地文件，结果可复现
        "max_result_chars": 2000,    # 单次结果上限

        # ---- schema（模型消费）----
        "schema": {
            "name": "search_siyuan",
            "description": (
                "在本地思源笔记中搜索考研知识点。"
                "科目代码: 301=数学(高等数学/概率统计/线性代数), "
                "408=计算机专业课(操作系统), 201=英语词汇(A-Z)。"
                "用简短核心词搜索，如'极限'而非'极限的定义'。"
                "不要用于: 闲聊、通用问答、修改或删除笔记。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "简短搜索词，单个核心词效果最好（如'死锁'、'极限'、'abandon'）"
                    },
                    "subject": {
                        "type": "string",
                        "enum": ["301", "408", "201", "all"],
                        "description": "科目范围: 301=数学, 408=计算机, 201=英语, all=全部"
                    }
                },
                "required": ["keyword"]
            }
        }
    }
}


def get_tool_schemas():
    """提取所有工具的 schema 发给模型。"""
    return [t["schema"] for t in TOOL_REGISTRY.values()]


# ============================================================
# .sy 解析器
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
# Ch.03 核心新增：输入净化 → 五阶段验证 → 执行 → 结果信封
# ============================================================

def sanitize_args(args: dict) -> dict:
    """净化模型输入：去空字符、去 ANSI 转义、裁空白。"""
    cleaned = {}
    for k, v in args.items():
        if isinstance(v, str):
            # 剔除空字节（null byte）
            v = v.replace("\0", "")
            # 剔除 ANSI 转义序列
            v = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', v)
            v = v.strip()
        cleaned[k] = v
    return cleaned


def validate_and_dispatch(tool_name: str, raw_args: dict) -> ToolResult:
    """五阶段验证管线。"""

    # ---- Stage 1: Known tool? ----
    if tool_name not in TOOL_REGISTRY:
        nearby = [n for n in TOOL_REGISTRY if n.startswith(tool_name[:4])]
        hint = f"可用工具: {', '.join(TOOL_REGISTRY.keys())}"
        if nearby:
            hint += f"。你是不是想用: {nearby[0]}？"
        return ToolResult(ok=False, recoverable=False,
                          code="UNKNOWN_TOOL",
                          content=f"未知工具 '{tool_name}'",
                          hint=hint)

    meta = TOOL_REGISTRY[tool_name]

    # ---- Stage 2: Sanitize ----
    args = sanitize_args(raw_args)

    # ---- Stage 3: Schema validation ----
    schema = meta["schema"]["input_schema"]
    required = schema.get("required", [])
    for field in required:
        if field not in args or not args[field]:
            return ToolResult(ok=False, recoverable=True,
                              code="MISSING_ARG",
                              content=f"缺少必要参数 '{field}'",
                              hint=f"请提供 {field} 参数后再试。"
                                   f"例如: search_siyuan(keyword='极限', subject='301')")

    # keyword 合理性检查
    keyword = args.get("keyword", "")
    if len(keyword) > 100:
        return ToolResult(ok=False, recoverable=True,
                          code="ARG_TOO_LONG",
                          content=f"关键词过长 ({len(keyword)} 字符)",
                          hint="请用简短核心词，如'极限'而非完整句子。")

    # subject 枚举检查
    subject = args.get("subject", "all")
    allowed_subjects = schema["properties"]["subject"]["enum"]
    if subject not in allowed_subjects:
        return ToolResult(ok=False, recoverable=True,
                          code="INVALID_ENUM",
                          content=f"'{subject}' 不是有效科目代码",
                          hint=f"可用科目: {', '.join(allowed_subjects)}")

    # ---- Stage 4: Permission ----
    # search_siyuan 是 read_only=True，无需审批。如果是 destructive=True，
    # 这里会触发 Ch.12 的人机审批门。当前直接放行。

    # ---- Stage 5: Execute ----
    try:
        result = _execute_search_siyuan(keyword, subject)
        # 附加溯源
        result.meta["tool_version"] = meta["version"]
        result.meta["tool_name"] = tool_name
        return result
    except Exception as e:
        return ToolResult(ok=False, recoverable=True,
                          code="EXECUTION_ERROR",
                          content=f"工具执行异常: {e}",
                          hint="请尝试换一个关键词或科目。")


def _execute_search_siyuan(keyword: str, subject: str) -> ToolResult:
    """搜索思源笔记的具体实现。"""

    if subject == "all":
        target_notebooks = list(NOTEBOOK_MAP.keys())
    else:
        target_notebooks = [nb for nb, subj in NOTEBOOK_MAP.items() if subj == subject]

    # 关键词回退
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
    meta_info = {}

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
                    raw = sy_file.read_text(encoding="utf-8")
                    doc = json.loads(raw)
                    text = extract_text_from_sy(doc)
                    title = get_document_title(doc)
                    updated = get_document_updated(doc)

                    if try_keyword.lower() not in text.lower():
                        continue

                    # 溯源信息
                    file_hash = hashlib.sha256(raw.encode()).hexdigest()
                    meta_info = {
                        "source": str(sy_file),
                        "title": title,
                        "updated": updated,
                        "hash": file_hash,
                        "notebook": subject_name,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }

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

    # 无结果 → 返回带指引的错误
    if not results:
        notebook_hint = ""
        if subject == "408":
            notebook_hint = "当前408笔记主要包含操作系统(OS)内容，可尝试关键词: IO管理、内存管理、OS概述"
        elif subject == "301":
            notebook_hint = "当前301笔记包含概率统计、线性代数内容，可尝试关键词: 贝叶斯、极限、导数、积分"
        elif subject == "201":
            notebook_hint = "当前201笔记为英语词汇(A-Z)，可尝试搜索具体单词如'abandon'、'abstract'"
        else:
            notebook_hint = "可尝试缩短关键词或切换科目范围(301/408/201)"

        return ToolResult(ok=False, recoverable=True,
                          code="NOT_FOUND",
                          content=f"未找到与「{keyword}」相关的内容",
                          hint=notebook_hint)

    # 有结果 → 组装 + 截断
    results.sort(key=lambda r: r["matches"], reverse=True)
    max_chars = TOOL_REGISTRY["search_siyuan"]["max_result_chars"]

    output_parts = []
    header = f"搜索「{effective_keyword}」找到 {len(results)} 个相关文档：\n"
    if effective_keyword != keyword:
        header = f"「{keyword}」无精确匹配，改用「{effective_keyword}」找到 {len(results)} 个文档：\n"
    output_parts.append(header)

    char_count = 0
    shown = 0
    for r in results[:5]:
        snippet = r["snippet"]
        entry = (f"【{r['notebook']}】{r['title']}（更新于 {r['updated']}，{r['matches']} 处匹配）\n"
                 f"{snippet}\n")
        if char_count + len(entry) > max_chars:
            truncate_point = max_chars - char_count - 50
            entry = entry[:truncate_point] + "\n...(结果过长，已截断。可缩小搜索范围获取更多细节)"
            output_parts.append(entry)
            break
        output_parts.append(entry)
        char_count += len(entry)
        shown += 1

    if len(results) > shown:
        output_parts.append(f"...还有 {len(results) - shown} 个文档未展示。")

    return ToolResult(ok=True,
                      content="".join(output_parts),
                      meta=meta_info)


# ============================================================
# Doom-loop 检测
# ============================================================

def check_doom_loop(recent_calls: list) -> bool:
    if len(recent_calls) < 3:
        return False
    last_three = recent_calls[-3:]
    first = (last_three[0][0], last_three[0][1])
    return all((name, args) == first for name, args in last_three)


# ============================================================
# Agent 循环（基于 Ch.02，增加结果信封处理）
# ============================================================

def agent_loop(user_message: str, abort_flag=None) -> str:

    messages = [{"role": "user", "content": user_message}]
    total_tokens = 0
    step = 0
    recent_calls = []

    system_prompt = (
        "你是考研学习助手，可以搜索本地思源笔记中的知识点。\n"
        "笔记覆盖: 数学(301, 含概率统计/线性代数/高等数学), "
        "计算机专业课(408, 操作系统), 英语词汇(201, A-Z词表)。\n\n"
        "规则:\n"
        "1. 用户问到知识点时，先用 search_siyuan 搜索笔记内容。\n"
        "2. 用简短核心词搜索（'极限'而非'极限的定义'）。\n"
        "3. 搜索无结果时，查看错误消息中的[建议]，换一个关键词或科目重试。\n"
        "4. 基于搜索结果组织回答，引用文档标题和科目来源。\n"
        "5. 用户闲聊时直接回答，不搜索。"
    )

    while step < MAX_STEPS and total_tokens < TOKEN_BUDGET:
        step += 1

        current_system = system_prompt
        if step >= GRACE_STEP:
            current_system = system_prompt + (
                f"\n\n[提示] 第 {step}/{MAX_STEPS} 轮，请尽快给出最终回答。"
            )

        # ---- Observe + Plan ----
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=current_system,
                messages=messages,
                tools=get_tool_schemas(),
            )
        except Exception as e:
            return f"[致命错误] 模型调用失败: {e}"

        if hasattr(response, "usage") and response.usage:
            total_tokens += response.usage.input_tokens + response.usage.output_tokens

        assistant_blocks = list(response.content)
        tool_uses = [b for b in assistant_blocks if b.type == "tool_use"]
        text_blocks = [b for b in assistant_blocks if b.type == "text"]

        # ---- Stop: 模型自己停了 ----
        if not tool_uses:
            for tb in text_blocks:
                return tb.text
            return "(模型未返回文本)"

        # ---- Act: 五阶段验证 + 执行 ----
        tool_results = []
        for block in tool_uses:
            tool_name = block.name
            tool_args = dict(block.input)
            print(f"[Step {step}] {tool_name}({tool_args})")

            # Doom-loop 检测
            recent_calls.append((tool_name, json.dumps(tool_args, sort_keys=True, ensure_ascii=False)))
            if check_doom_loop(recent_calls):
                return f"[警告] 连续 3 次相同调用 {tool_name}，已终止。"

            if abort_flag and abort_flag():
                return "[已取消]"

            # 验证 + 执行
            result = validate_and_dispatch(tool_name, tool_args)
            status = "OK" if result.ok else f"FAIL({result.code})"
            print(f"         -> {status} | {len(result.content)} chars"
                  + (f" | hint: {result.hint[:50]}..." if not result.ok and result.hint else ""))

            tool_results.append((block.id, result))

        # ---- Reflect: 把信封转为模型可读的消息 ----
        messages.append({"role": "assistant", "content": assistant_blocks})

        user_content = []
        for tool_id, result in tool_results:
            user_content.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": result.to_api_string()
            })

            # 不可恢复的错误 → 停止（如未知工具、权限拒绝）
            if not result.ok and not result.recoverable:
                user_content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"[系统] 此错误不可恢复，Agent 将停止。原因: {result.content}"
                })
                messages.append({"role": "user", "content": user_content})
                return f"[不可恢复错误] {result.code}: {result.content}"

        messages.append({"role": "user", "content": user_content})

    if total_tokens >= TOKEN_BUDGET:
        return "[提示] 已达到 token 预算上限。"
    return "[提示] 已达到最大轮次上限。"


# ============================================================
# 交互入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("📚 考研助手 > 请问：")

    cancelled = False

    def on_cancel():
        global cancelled
        cancelled = True

    signal.signal(signal.SIGINT, lambda s, f: on_cancel())

    answer = agent_loop(question, abort_flag=lambda: cancelled)

    output_path = Path(__file__).parent / "last_answer.txt"
    output_path.write_text(answer, encoding="utf-8")
    print(f"\n[回答已写入 {output_path}]")
    try:
        preview = answer[:300]
        print(preview)
        if len(answer) > 300:
            print(f"...(共 {len(answer)} 字符)")
    except UnicodeEncodeError:
        print("(完整内容请查看 last_answer.txt)")
