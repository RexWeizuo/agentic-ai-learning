"""
Ch.02 — Agent loop: Observe → Plan → Act → Reflect → Stop.

Implements all Ch.02 stop conditions + Ch.03 error envelopes
+ Ch.05 clipping + Ch.05 deduplication + Ch.06 memory prefix
+ Ch.02 step boundary stubs.

Ch.04: Qwen automatic prefix caching — SYSTEM_PROMPT is byte-stable.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from openai import OpenAI

from .game_engine import SYSTEM_PROMPT
from .tools import TOOLS, Tool

# ── Configuration ────────────────────────────────────────────────

MODEL = "qwen3.7-max-2026-05-20"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MAX_STEPS = 15

# ═════════════════════════════════════════════════════════════════
# Ch.03 — Error classification + envelope
# ═════════════════════════════════════════════════════════════════

_ERROR_CODES = {"unknown_tool": 1, "schema": 2, "network": 3,
                "not_found": 4, "execution": 7}


def _classify_error(msg: str) -> tuple[bool, str]:
    m = msg.lower()
    for kw, hint in [("not found", "Resource missing — check path"),
                      ("arrearage", "Quota exhausted — switch model")]:
        if kw in m:
            return (False, hint)
    for kw, hint in [("connection", "Network issue — retry once"),
                      ("timeout", "Timed out — retry")]:
        if kw in m:
            return (True, hint)
    return (True, "Error — retry once or try another approach")


def _make_error_envelope(msg: str) -> dict[str, Any]:
    rec, hint = _classify_error(msg)
    code = _ERROR_CODES["network"] if rec else _ERROR_CODES["execution"]
    m = msg.lower()
    if "not found" in m:
        code = _ERROR_CODES["not_found"]
    return {"ok": False, "error": msg, "recoverable": rec,
            "hint": hint, "error_code": code}


# ═════════════════════════════════════════════════════════════════
# Ch.05 — Clipping + Deduplication
# ═════════════════════════════════════════════════════════════════

MAX_RESULT_CHARS = 2_000


def _clip(text: str) -> tuple[str, bool]:
    """Clip oversized results with visible marker."""
    if len(text) <= MAX_RESULT_CHARS:
        return text, False
    half = MAX_RESULT_CHARS // 2
    omitted = len(text) - MAX_RESULT_CHARS
    return (f"{text[:half]}\n[... {omitted} chars omitted ...]\n{text[-half:]}",
            True)


def _dedupe(msgs: list[dict], tool_map: dict[str, Tool]) -> list[dict]:
    """Ch.05: latest-wins dedupe — skip open_world tools."""
    latest: dict[tuple[str, str], int] = {}
    for i, m in enumerate(msgs):
        if m["role"] != "tool":
            continue
        tname = m.get("_tool_name", "")
        targs = m.get("_tool_args", "")
        if not tname:
            continue
        tool = tool_map.get(tname)
        if tool is None or tool.open_world:
            continue
        latest[(tname, targs)] = i

    kept: list[dict] = []
    dropped = 0
    for i, m in enumerate(msgs):
        if m["role"] != "tool":
            kept.append(m)
            continue
        tname = m.get("_tool_name", "")
        targs = m.get("_tool_args", "")
        tool = tool_map.get(tname)
        if tool is None or tool.open_world:
            kept.append(m)
        elif latest.get((tname, targs)) == i:
            kept.append(m)
        else:
            dropped += 1
    if dropped:
        kept.append({"role": "user",
                      "content": f"[... {dropped} duplicate result(s) omitted ...]"})
    return kept


# ═════════════════════════════════════════════════════════════════
# Ch.02 — Step trace (observability)
# ═════════════════════════════════════════════════════════════════

@dataclass
class StepTrace:
    step: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_calls: list[str] = field(default_factory=list)
    tokens_used: int = 0
    stopped: bool = False
    stop_reason: str = ""


# ═════════════════════════════════════════════════════════════════
# Ch.03 — Hooks
# ═════════════════════════════════════════════════════════════════

PRE_HOOKS: list[Callable] = []
POST_HOOKS: list[Callable] = []


# ═════════════════════════════════════════════════════════════════
# Ch.02 — The loop
# ═════════════════════════════════════════════════════════════════

def run_loop(
    user_message: str,
    model: str = MODEL,
    max_steps: int = MAX_STEPS,
    verbose: bool = True,
    log_dir: str | None = None,
) -> dict[str, Any]:
    client = OpenAI(
        api_key=os.environ.get("DASHSCOPE_API_KEY", os.environ.get("API_KEY", "")),
        base_url=BASE_URL,
    )

    tool_schemas = [t.to_openai_schema() for t in TOOLS]
    tool_map = {t.name: t for t in TOOLS}

    # ── Ch.06: build stable prefix ───────────────────────────
    # Ch.04: SYSTEM_PROMPT is byte-stable → Qwen auto-caches it
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    traces: list[StepTrace] = []
    final_text: str | None = None
    total_tokens = 0
    recent_calls: list[tuple[str, str]] = []

    # ── Logging ──────────────────────────────────────────────
    log_lines: list[str] = []
    log_path: str | None = None

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_path = os.path.join(log_dir, f"run-{ts}.md")

    def _log(line: str) -> None:
        if verbose:
            print(line)
        if log_dir:
            log_lines.append(line)

    def _save_log() -> None:
        if log_path:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines))

    # ── Loop ─────────────────────────────────────────────────
    for step in range(max_steps):
        trace = StepTrace(step=step + 1)

        # Ch.05: dedupe before Plan
        messages = _dedupe(messages, tool_map)

        # Plan
        response = client.chat.completions.create(
            model=model, messages=messages,
            tools=tool_schemas, temperature=0.3,
        )

        msg = response.choices[0].message
        usage = response.usage
        if usage:
            total_tokens += usage.total_tokens
            trace.tokens_used = usage.total_tokens

        # Model-driven stop
        if not msg.tool_calls:
            trace.stopped = True
            trace.stop_reason = "model_end_turn"
            final_text = msg.content or "(no response)"
            traces.append(trace)
            _save_log()
            return {"answer": final_text,
                    "traces": [t.__dict__ for t in traces],
                    "total_steps": step + 1, "total_tokens": total_tokens}

        # Append assistant message
        messages.append({
            "role": "assistant", "content": msg.content,
            "tool_calls": [{
                "id": tc.id, "type": "function",
                "function": {"name": tc.function.name,
                             "arguments": tc.function.arguments},
            } for tc in msg.tool_calls],
        })

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            args_str = tc.function.arguments
            trace.tool_calls.append(tool_name)

            # Doom-loop detection
            recent_calls.append((tool_name, args_str))
            if len(recent_calls) > 3:
                recent_calls.pop(0)
            if len(recent_calls) == 3 and recent_calls[0] == recent_calls[1] == recent_calls[2]:
                doom_msg = f"Doom-loop: '{tool_name}' called 3× identically"
                _log(f"\n{doom_msg}\n")
                _save_log()
                return {"answer": doom_msg, "traces": [],
                        "total_steps": step + 1, "total_tokens": total_tokens,
                        "doom_loop": True}

            # Dispatch
            tool = tool_map.get(tool_name)
            if tool is None:
                result = _make_error_envelope(f"Unknown tool: '{tool_name}'")
            else:
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", args_str)
                    try:
                        args = json.loads(cleaned)
                    except json.JSONDecodeError as e:
                        result = _make_error_envelope(
                            f"Parse error for '{tool_name}': {e}")
                        messages.append({
                            "role": "tool", "tool_call_id": tc.id,
                            "content": json.dumps(result, ensure_ascii=False),
                        })
                        continue
                try:
                    result = tool.handler(**args)
                except Exception as e:
                    result = _make_error_envelope(
                        f"Tool '{tool_name}' failed: {e}")

            # ── Ch.03: Hook pipeline ─────────────────────────
            for hook in PRE_HOOKS:
                modified = hook(tool_name, args, None)
                if modified is not None:
                    args = modified
            for hook in reversed(POST_HOOKS):
                modified = hook(tool_name, args, result)
                if modified is not None:
                    result = modified

            # ── Wrap bare errors ─────────────────────────────
            if "error" in result and "ok" not in result:
                result = _make_error_envelope(result["error"])

            # final_answer check
            if tool_name == "final_answer" and "answer" in result:
                trace.stopped = True
                trace.stop_reason = "final_answer"
                final_text = result["answer"]
                traces.append(trace)
                _save_log()
                return {"answer": final_text,
                        "traces": [t.__dict__ for t in traces],
                        "total_steps": step + 1,
                        "total_tokens": total_tokens}

            # ── Ch.05: clip + Reflect ────────────────────────
            result_json = json.dumps(result, ensure_ascii=False)
            clipped, was_clipped = _clip(result_json)
            messages.append({
                "role": "tool", "tool_call_id": tc.id,
                "content": clipped,
                "_tool_name": tool_name, "_tool_args": args_str,
            })
            if verbose and was_clipped:
                _log(f"         Clipped: {len(result_json)} → {len(clipped)} chars")

        traces.append(trace)

    # Step cap exhausted
    _save_log()
    return {"answer": final_text or "(step cap reached)",
            "traces": [t.__dict__ for t in traces],
            "total_steps": max_steps, "total_tokens": total_tokens,
            "partial": True}
