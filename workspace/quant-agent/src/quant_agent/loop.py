"""
Ch.02 — The agent loop: Observe → Plan → Act → Reflect → Stop.

Wraps the Ch.01 tool call inside a loop that lets the model
decide, step by step, what to do next.

Provider: Qwen (DashScope, OpenAI-compatible).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from openai import OpenAI

from .tools.registry import TOOLS, Tool

# ── Memory loading (Ch.06: frozen prefix at session start) ────────

def _load_memory_files(
    base_dir: str = "memory",
    files: tuple[str, ...] = ("user_profile.md", "quant-agent-memory.md"),
) -> str:
    """
    Load curated memory files into the frozen prefix.

    Ch.06: "Markdown files are frozen at session start into the
    system prompt." Ch.04: "the cache wants byte-stable bytes."

    Strips YAML frontmatter (--- ... ---) and wraps content in
    delimited sections the model can identify.
    """
    parts: list[str] = []
    for filename in files:
        path = os.path.join(base_dir, filename)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        # Strip frontmatter
        content = raw
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3:].strip()
        parts.append(f"§ {filename}\n{content}")
    if parts:
        return "\n\n" + "\n\n".join(parts)
    return ""


# ── Error classification (Ch.03: recoverable vs fatal) ───────────

def _classify_error(error_msg: str, exc_type: type | None = None) -> tuple[bool, str]:
    """
    Classify a tool error as recoverable or fatal.

    Prefer exception types over string matching — ConnectionError is
    always recoverable, ValueError is always fatal, etc.

    Returns (recoverable: bool, hint: str).
    """
    # ── Exception-type classification (precise) ──────────────
    if exc_type is not None:
        if issubclass(exc_type, (ConnectionError, TimeoutError)):
            return (True, "Network issue — retry once or try after market reopens")
        if issubclass(exc_type, ValueError):
            return (False, "Invalid data format — check the symbol or parameters")

    # ── String fallback (for errors passed through from tools) ──
    msg_lower = error_msg.lower()

    # Fatal first: things retry can never fix
    for keyword, hint in [
        ("not found", "Resource does not exist — verify the symbol"),
        ("cannot auto-detect", "Unrecognized symbol format — ask the user to clarify"),
        ("arrearage", "API quota exhausted — switch to next model"),
        ("access denied", "Authentication failed — check credentials"),
        ("parse sina response", "Data format unexpected — try again later"),
        ("unexpected response format", "Data format unexpected — try again later"),
    ]:
        if keyword in msg_lower:
            return (False, hint)

    # Recoverable: transient issues
    for keyword, hint in [
        ("connection", "Network issue — retry once"),
        ("timeout", "Request timed out — retry with fewer data points"),
        ("timed out", "Request timed out — retry with fewer data points"),
        ("rate limit", "Rate limited — wait and retry"),
        ("too many requests", "Rate limited — wait and retry"),
        ("remote end closed", "Server disconnected — retry once"),
        ("remote disconnected", "Server disconnected — retry once"),
    ]:
        if keyword in msg_lower:
            return (True, hint)

    # ── Default: assume recoverable ──────────────────────────
    return (True, "Error encountered — retry once or try another approach")


# Error codes (Ch.03: numeric codes model can reason about)
_ERROR_CODES = {
    "unknown_tool": 1,
    "schema_parse": 2,
    "network": 3,
    "not_found": 4,
    "permission": 5,
    "quota": 6,
    "execution": 7,
}


def _error_code_for(recoverable: bool, error_msg: str) -> int:
    """Map error to a numeric code (Claude Code pattern: ValidationResult.errorCode)."""
    msg_lower = error_msg.lower()
    if "not found" in msg_lower or "cannot auto-detect" in msg_lower:
        return _ERROR_CODES["not_found"]
    if any(w in msg_lower for w in ("arrearage", "access denied", "quota")):
        return _ERROR_CODES["quota"]
    if recoverable:
        if any(w in msg_lower for w in ("connection", "timeout", "rate limit", "remote")):
            return _ERROR_CODES["network"]
        return _ERROR_CODES["execution"]
    return _ERROR_CODES["execution"]


def _make_error_envelope(error_msg: str, exc_type: type | None = None) -> dict[str, Any]:
    """Wrap an error in Ch.03's result envelope with error code."""
    recoverable, hint = _classify_error(error_msg, exc_type)
    return {
        "ok": False,
        "error": error_msg,
        "recoverable": recoverable,
        "hint": hint,
        "error_code": _error_code_for(recoverable, error_msg),
    }


# ── Tool output clipping (Ch.05: clip before entering transcript) ──

MAX_RESULT_CHARS = 2_000  # Per Ch.05: cap tool results before model sees them


def _clip_result(result_json: str) -> tuple[str, bool]:
    """
    Clip oversized tool results with a visible omission marker.

    Ch.05: "Silent truncation teaches the model a false view."
    Keep head + tail; insert a marker the model can read.
    Full result stays in the audit log (log file).

    Returns (clipped_str, was_clipped).
    """
    if len(result_json) <= MAX_RESULT_CHARS:
        return result_json, False

    half = MAX_RESULT_CHARS // 2
    head = result_json[:half]
    tail = result_json[-half:]
    omitted = len(result_json) - MAX_RESULT_CHARS

    clipped = (
        f"{head}\n"
        f"[... {omitted} chars omitted — use a more specific query "
        f"or check the full log for details ...]\n"
        f"{tail}"
    )
    return clipped, True


# ── Deduplication (Ch.05: latest-wins for repeated reads) ──────────

def _dedupe_tool_results(
    messages: list[dict[str, Any]], tool_map: dict[str, Tool]
) -> list[dict[str, Any]]:
    """
    Drop earlier duplicates of the same (tool, input) call.

    Ch.05: "latest-wins dedupe — keep only the most recent result
    per (tool, input) pair."

    Skips open_world tools (get_price, get_index) — their results
    change between calls so earlier results are not superseded.
    """
    # ── Find latest index for each (tool, input) pair ──────────
    latest: dict[tuple[str, str], int] = {}
    for i, m in enumerate(messages):
        if m["role"] != "tool":
            continue
        tname = m.get("_tool_name", "")
        targs = m.get("_tool_args", "")
        if not tname:
            continue
        tool = tool_map.get(tname)
        if tool is None or tool.open_world:
            continue  # mutable results: keep all
        latest[(tname, targs)] = i

    # ── Keep latest only ───────────────────────────────────────
    kept: list[dict[str, Any]] = []
    dropped = 0
    for i, m in enumerate(messages):
        if m["role"] != "tool":
            kept.append(m)
            continue
        tname = m.get("_tool_name", "")
        targs = m.get("_tool_args", "")
        tool = tool_map.get(tname)
        if tool is None or tool.open_world:
            kept.append(m)  # always keep mutable results
        else:
            if latest.get((tname, targs)) == i:
                kept.append(m)  # this IS the latest
            else:
                dropped += 1
    if dropped > 0:
        kept.append({
            "role": "user",
            "content": f"[... {dropped} duplicate tool result(s) omitted ...]",
        })
    return kept


# ── Remaining Ch.05 stubs ─────────────────────────────────────────
# TODO: asymmetric reduction — keep head 2 + tail 6 turns verbatim, summarize middle
#   _compact_transcript(messages, keep_head=2, keep_tail=6)
#
# TODO: working memory — small mutable scratchpad for current task
#   working_memory: dict = {"goal": ..., "files_read": [], "open_questions": []}
#
# TODO: mid-turn summarization — auxiliary cheap model compresses middle into reference block
#   summary = await auxiliary_client.summarize(middle_turns)
#
# TODO: compaction trigger — proactive token check before Plan phase
#   if _estimate_tokens(messages) > context_limit - max_output - 4096:
#       messages = _compact_transcript(messages)


# ── Hooks (Ch.03: pre/post dispatch callbacks) ────────────────────
# Claude Code pattern (hooks.ts + toolExecution.ts):
#   Pre-hooks  → execute in registration order
#   Post-hooks → execute in REVERSE registration order (middleware stack)
# Each hook is (tool_name, args, result) -> result (may modify).
# Return None = no modification.

PRE_HOOKS: list[Callable[[str, dict, dict | None], dict | None]] = []
POST_HOOKS: list[Callable[[str, dict, dict], dict | None]] = []


def _hook_scrub_secrets(tool_name: str, _args: dict, result: dict) -> dict | None:
    """Post-hook: redact leaked secrets/keys/tokens from result text."""
    # TODO: enable when tools access authenticated APIs
    return None


# ── Configuration ────────────────────────────────────────────────

MODEL = "qwen3.7-max-2026-06-08"  # Rotate: → 2026-05-20 → 2026-05-17 → preview
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MAX_STEPS = 20

SYSTEM_PROMPT = """\
You are a quantitative trading analyst assistant.

You have four data tools:
- get_price: current real-time price, change%, volume, OHLC
- get_kline: historical candlestick bars (trend + bar details)
- get_financials: PE ratio, market cap, 52-week range
- get_index: SSE Composite / SZSE Component / ChiNext index

Your job:
1. When the user asks about a stock, fetch ALL relevant data in one step
   (price + kline + financials). Use parallel tool calls when possible.
2. If the user asks about market conditions, also call get_index.
3. Analyze across three dimensions:
   - Technical (price trend, support/resistance, volume signals)
   - Fundamental (PE valuation, market cap, 52-week position)
   - Market context (index trend — is the stock leading or following?)
4. Cross-reference: a stock rising while the market falls = strong.
   A stock rising with the market = neutral.
5. When ready, call final_answer with your complete analysis.

Rules:
- NEVER guess prices or data — always use tools first.
- If a tool fails, read the error and try a different approach.
- Use specific numbers from tool results in your analysis (prices, PE, %).
- For non-A-stock symbols, clarify the market with the user.
"""


# ── Step trace (Ch.02 observability hook) ────────────────────────

@dataclass
class StepTrace:
    """One step through the loop — recorded for observability."""
    step: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_calls: list[str] = field(default_factory=list)
    tokens_used: int = 0
    stopped: bool = False
    stop_reason: str = ""


# ── The loop ─────────────────────────────────────────────────────

def run_loop(
    user_message: str,
    model: str = MODEL,
    max_steps: int = MAX_STEPS,
    verbose: bool = True,
    log_dir: str | None = None,
) -> dict[str, Any]:
    """
    Run the agent loop.

    Ch.02 five stages:
      Observe → Plan → Act → Reflect → Stop (check) → loop.

    Args:
        user_message: The user's question or command.
        model: Model name (OpenAI-compatible).
        max_steps: Hard iteration cap.
        verbose: Print step traces if True.
        log_dir: If set, save full run log to this directory.

    Returns:
        Dict with 'answer' (final text) and 'traces' (list of StepTrace).
    """
    # ── Logging setup ────────────────────────────────────────────
    log_lines: list[str] = []
    log_path: str | None = None

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_path = os.path.join(log_dir, f"run-{ts}.md")
        log_lines.append(f"# Agent Run — {datetime.now().isoformat()}\n")
        log_lines.append(f"**Model**: {model} | **Max steps**: {max_steps}\n")
        log_lines.append(f"**User**: {user_message}\n")
        log_lines.append(f"\n**Tools**: {', '.join(t.name for t in TOOLS)}\n")
        log_lines.append(f"\n---\n")
        log_lines.append(f"## System Prompt\n\n```\n{SYSTEM_PROMPT}\n```\n")
        log_lines.append(f"\n---\n")
        log_lines.append(f"## Execution Trace\n")

    def _log(line: str) -> None:
        """Write to both stdout (if verbose) and log file."""
        if verbose:
            print(line)
        if log_dir:
            log_lines.append(line)

    def _save_log() -> None:
        if log_path:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines))

    def _log_step(trace: StepTrace, preview: str | None = None) -> None:
        """Format one step trace and send to both outputs."""
        status = "STOP" if trace.stopped else "CONTINUE"
        tools = ", ".join(trace.tool_calls) if trace.tool_calls else "(text)"
        line = (
            f"  Step {trace.step:2d} | {status:8s} | {tools:30s} | "
            f"{trace.tokens_used:5d} tk | {trace.stop_reason}"
        )
        _log(line)
        if preview:
            _log(f"         └─ {preview}")

    def _log_messages() -> None:
        """Log the full messages array state."""
        _log(f"\n**Messages** ({len(messages)} entries):\n")
        for i, m in enumerate(messages):
            role = m["role"]
            if role == "system":
                _log(f"  [{i}] `system`: (prompt, {len(m['content'])} chars)")
            elif role == "user":
                _log(f"  [{i}] `user`: \"{m['content'][:100]}\"")
            elif role == "assistant":
                tcs = m.get("tool_calls", [])
                if tcs:
                    names = ", ".join(tc["function"]["name"] for tc in tcs)
                    _log(f"  [{i}] `assistant`: tool_calls=[{names}]")
                else:
                    _log(f"  [{i}] `assistant`: \"{m.get('content', '')[:100]}\"")
            elif role == "tool":
                c = m.get("content", "")
                _log(f"  [{i}] `tool` ({m.get('tool_call_id', '?')[:12]}): {c[:120]}")
        _log("")

    # ── Observe: build initial messages ──────────────────────────
    client = OpenAI(
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url=BASE_URL,
    )

    tool_schemas = [t.to_openai_schema() for t in TOOLS]
    tool_map = {t.name: t for t in TOOLS}

    # ── Ch.06: load frozen memory into prefix (session start) ──
    memory_prefix = _load_memory_files()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT + memory_prefix},
        {"role": "user", "content": user_message},
    ]

    traces: list[StepTrace] = []
    final_text: str | None = None
    total_tokens = 0

    # ── Doom-loop state (Ch.02: byte-for-byte check on last 3) ──
    recent_calls: list[tuple[str, str]] = []  # (tool_name, args_json)

    # ── Loop ─────────────────────────────────────────────────────
    for step in range(max_steps):
        trace = StepTrace(step=step + 1)

        # ── Ch.05: dedupe before Plan (collapse phase) ──────────
        messages = _dedupe_tool_results(messages, tool_map)

        # ── Plan: call the model ─────────────────────────────────
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tool_schemas,
            temperature=0.3,  # lower temperature = more consistent analysis
        )

        msg = response.choices[0].message
        usage = response.usage
        if usage:
            total_tokens += usage.total_tokens
            trace.tokens_used = usage.total_tokens

        # ── Log: model's full response ──────────────────────────
        _log(f"\n### Step {step + 1} — Plan (Model Response)")
        if msg.content:
            _log(f"\n> {msg.content[:300]}")
        if msg.tool_calls:
            for tc in msg.tool_calls:
                _log(f"\n- **Tool call**: `{tc.function.name}`")
                _log(f"  - Args: `{tc.function.arguments[:300]}`")
        else:
            _log(f"\n- **No tool calls** → model decided to stop")
        _log("")

        # ── Model-driven stop (no tool calls) ────────────────────
        if not msg.tool_calls:
            trace.stopped = True
            trace.stop_reason = "model_end_turn"
            final_text = msg.content or "(no response)"
            traces.append(trace)
            _log("---")
            _log_messages()
            _log_step(trace, final_text[:200] + "..." if len(final_text) > 200 else final_text)
            _save_log()
            return {
                "answer": final_text,
                "traces": [t.__dict__ for t in traces],
                "total_steps": step + 1,
                "total_tokens": total_tokens,
            }

        # ── Act: dispatch tool calls ─────────────────────────────
        # Append assistant message (with tool_calls) to history
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            trace.tool_calls.append(tool_name)

            # ── Doom-loop detection (Ch.02) ─────────────────────────
            args_str = tc.function.arguments
            recent_calls.append((tool_name, args_str))
            if len(recent_calls) > 3:
                recent_calls.pop(0)

            if (
                len(recent_calls) == 3
                and recent_calls[0] == recent_calls[1] == recent_calls[2]
            ):
                doom_msg = (
                    f"⚠️  Doom-loop detected: '{tool_name}' called 3× "
                    f"with identical arguments. Breaking loop."
                )
                if verbose:
                    _log(f"\n{doom_msg}\n")
                final_text = doom_msg
                trace.stopped = True
                trace.stop_reason = "doom_loop"
                traces.append(trace)
                _log("---")
                _log_messages()
                _log_step(trace)
                _save_log()
                return {
                    "answer": doom_msg,
                    "traces": [t.__dict__ for t in traces],
                    "total_steps": step + 1,
                    "total_tokens": total_tokens,
                    "doom_loop": True,
                }

            tool = tool_map.get(tool_name)
            if tool is None:
                result = _make_error_envelope(f"Unknown tool '{tool_name}'")
            else:
                try:
                    args = json.loads(tc.function.arguments)
                    result = tool.handler(**args)
                except json.JSONDecodeError:
                    # Ch.02: model sometimes emits JSON with control chars.
                    # Try stripping them and parsing again.
                    import re
                    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", tc.function.arguments)
                    try:
                        args = json.loads(cleaned)
                        result = tool.handler(**args)
                    except json.JSONDecodeError as e:
                        result = _make_error_envelope(
                            f"Failed to parse arguments for '{tool_name}': {e}"
                        )
                        result["raw_args"] = tc.function.arguments[:200]
                except Exception as e:
                    # Ch.01 + Ch.02: wrap exception as tool_result
                    result = _make_error_envelope(
                        f"Tool '{tool_name}' execution failed: {e}",
                        exc_type=type(e),
                    )

            # ════════════ Step Boundary (Ch.02) ════════════
            # Act complete, Reflect not yet done.
            # Production capabilities that attach here:

            # TODO: abort_token — check before high-risk dispatch
            #   if abort_token.is_set():
            #       result = {"error": "aborted by user"}
            #       break

            # TODO: grace_call — give model one last turn
            #   if tokens_left < threshold:
            #       messages.append({"role":"system","content":"Last turn"})

            # TODO: provider_fallback — swap model on persistent failure
            #   if consecutive_errors > 3:
            #       model = FALLBACK_MODEL

            # ── Log: tool result ────────────────────────────────
            result_raw = json.dumps(result, ensure_ascii=False)
            _log(f"- **Result** (`{tool_name}`):")
            _log(f"  ```json\n  {result_raw[:400]}\n  ```\n")

            # ════════ Hook pipeline (Ch.03) ════════
            # Claude Code pattern (toolExecution.ts: checkPermissionsAndCallTool):
            #   Pre-hooks → validateInput → Permission → Execute → Post-hooks
            for hook in PRE_HOOKS:
                modified = hook(tool_name, args, None)
                if modified is not None:
                    args = modified

            for hook in reversed(POST_HOOKS):
                modified = hook(tool_name, args, result)
                if modified is not None:
                    result = modified

            # ── Wrap tool-native errors in Ch.03 envelope ───────
            if "error" in result and "ok" not in result:
                result = _make_error_envelope(result["error"])

            # Ch.02: check for final_answer → explicit stop
            if tool_name == "final_answer" and "answer" in result:
                trace.stopped = True
                trace.stop_reason = "final_answer"
                final_text = result["answer"]
                traces.append(trace)
                _log(f"\n### Final Answer\n\n{final_text}\n")
                _log("---")
                _log_messages()
                _log_step(trace, final_text[:200] + "..." if len(final_text) > 200 else final_text)
                _save_log()
                # Return immediately — final_answer means we're done
                return {
                    "answer": final_text,
                    "traces": [t.__dict__ for t in traces],
                    "total_steps": step + 1,
                    "total_tokens": total_tokens,
                }

            # ── Reflect: clip then send to model (Ch.05) ────────
            result_json = json.dumps(result, ensure_ascii=False)
            clipped_json, was_clipped = _clip_result(result_json)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": clipped_json,
                "_tool_name": tool_name,        # for dedupe
                "_tool_args": args_str,          # for dedupe
            })
            if was_clipped and verbose:
                _log(f"         └─ Clipped: {len(result_json)} → {len(clipped_json)} chars")

            if verbose and "error" in result:
                _log(f"         └─ Error: {result['error'][:120]}")

        traces.append(trace)
        _log("---")
        _log_messages()
        _log_step(trace)

    # ── Step cap exhausted ───────────────────────────────────────
    # Ch.02: return partial result, labeled
    _save_log()
    return {
        "answer": final_text or "(step cap reached before final answer)",
        "traces": [t.__dict__ for t in traces],
        "total_steps": max_steps,
        "total_tokens": total_tokens,
        "partial": True,
    }

