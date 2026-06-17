"""
Ch.02 — Agent loop: Observe→Plan→Act→Reflect→Stop.
Ch.03 — Error envelopes + hooks + step boundary.
Ch.05 — Clipping + deduplication.
Ch.06 — Auto Qwen prefix cache (stable SYSTEM_PROMPT).
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
from .tools import TOOLS, Tool, stash_result

MODEL = "qwen3.7-max-2026-05-17"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MAX_STEPS = 12

# ═══════════════════════════════════════════════════════════════
# Ch.03 — Error classification
# ═══════════════════════════════════════════════════════════════

def _classify_error(msg: str) -> tuple[bool, str]:
    m = msg.lower()
    for kw, hint in [("not found", "NotFound"), ("arrearage", "QuotaExhausted"),
                      ("access denied", "AuthFailed")]:
        if kw in m: return (False, hint)
    for kw, hint in [("connection", "NetworkIssue"), ("timeout", "Timeout")]:
        if kw in m: return (True, hint)
    return (True, "RetryableError")


_ERROR_CODES = {"unknown_tool": 1, "parse": 2, "network": 3, "not_found": 4, "quota": 6, "exec": 7}


def _make_error_envelope(msg: str) -> dict[str, Any]:
    rec, _ = _classify_error(msg)
    code = _ERROR_CODES["network"] if rec else _ERROR_CODES["exec"]
    if "not found" in msg.lower(): code = _ERROR_CODES["not_found"]
    if "arrearage" in msg.lower(): code = _ERROR_CODES["quota"]
    return {"ok": False, "error": msg, "recoverable": rec, "error_code": code}


# ═══════════════════════════════════════════════════════════════
# Ch.05 — Clipping + Deduplication
# ═══════════════════════════════════════════════════════════════

MAX_RESULT = 2_000

def _clip(text: str) -> tuple[str, bool, str | None]:
    """Clip oversized results. Returns (clipped_text, was_clipped, stash_id_or_none).

    When clipping occurs, the full text is stashed via stash_result() and a
    pointer is embedded in the clipped message so the model can retrieve it
    on demand with fetch_full_result(stash_id).
    """
    if len(text) <= MAX_RESULT: return text, False, None
    half = MAX_RESULT // 2
    omitted = len(text) - MAX_RESULT
    sid = stash_result(text)
    return (
        f"{text[:half]}\n"
        f"[... {omitted} chars omitted — full result stashed as '{sid}', "
        f"use fetch_full_result('{sid}') to retrieve ...]\n"
        f"{text[-half:]}",
        True, sid,
    )


def _dedupe(msgs: list[dict], tool_map: dict[str, Tool]) -> list[dict]:
    latest: dict[tuple[str, str], int] = {}
    for i, m in enumerate(msgs):
        if m["role"] != "tool": continue
        tn = m.get("_tn", ""); ta = m.get("_ta", "")
        if not tn: continue
        t = tool_map.get(tn)
        if t is None or t.open_world: continue
        latest[(tn, ta)] = i

    kept: list[dict] = []; dropped = 0
    for i, m in enumerate(msgs):
        if m["role"] != "tool":
            kept.append(m); continue
        tn = m.get("_tn", ""); ta = m.get("_ta", "")
        t = tool_map.get(tn)
        if t is None or t.open_world: kept.append(m)
        elif latest.get((tn, ta)) == i: kept.append(m)
        else: dropped += 1
    if dropped:
        kept.append({"role": "user", "content": f"[... {dropped} duplicate tool result(s) omitted ...]"})
    return kept


# ═══════════════════════════════════════════════════════════════
# Ch.02 — Step trace
# ═══════════════════════════════════════════════════════════════

@dataclass
class StepTrace:
    step: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_calls: list[str] = field(default_factory=list)
    tokens_used: int = 0
    stopped: bool = False
    stop_reason: str = ""


# ═══════════════════════════════════════════════════════════════
# Ch.03 — Hooks
# ═══════════════════════════════════════════════════════════════

PRE_HOOKS: list[Callable] = []
POST_HOOKS: list[Callable] = []


# ═══════════════════════════════════════════════════════════════
# Ch.02 — The loop
# ═══════════════════════════════════════════════════════════════

def run_loop(
    user_message: str,
    model: str = MODEL,
    max_steps: int = MAX_STEPS,
    verbose: bool = True,
    log_dir: str | None = None,
) -> dict[str, Any]:
    key = os.environ.get("DASHSCOPE_API_KEY", os.environ.get("API_KEY", ""))
    client = OpenAI(api_key=key, base_url=BASE_URL)

    tool_schemas = [t.to_openai_schema() for t in TOOLS]
    tool_map = {t.name: t for t in TOOLS}

    # ── Ch.04 stable prefix ─────────────────────────────────
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    traces: list[StepTrace] = []
    final_text: str | None = None
    total_tokens = 0
    recent_calls: list[tuple[str, str]] = []

    # ── Logging ──────────────────────────────────────────────
    log_lines: list[str] = []; log_path: str | None = None
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md")

    def _log(line: str) -> None:
        if verbose: print(line)
        if log_dir: log_lines.append(line)

    def _save_log() -> None:
        if log_path:
            with open(log_path, "w", encoding="utf-8") as f: f.write("\n".join(log_lines))

    # ── Loop ─────────────────────────────────────────────────
    for step in range(max_steps):
        trace = StepTrace(step=step + 1)

        # Ch.05: dedupe before Plan
        messages = _dedupe(messages, tool_map)

        # Plan
        response = client.chat.completions.create(
            model=model, messages=messages, tools=tool_schemas, temperature=0.7,
        )

        msg = response.choices[0].message
        usage = response.usage
        if usage:
            total_tokens += usage.total_tokens
            trace.tokens_used = usage.total_tokens

        # Model-driven stop
        if not msg.tool_calls:
            final_text = msg.content or "(silence)"
            traces.append(trace)
            _log(f"\nStep {step+1}: [END] model_end_turn\n{final_text[:200]}")
            _save_log()
            return {"answer": final_text, "traces": [t.__dict__ for t in traces],
                    "total_steps": step + 1, "total_tokens": total_tokens}

        # Append assistant
        messages.append({
            "role": "assistant", "content": msg.content,
            "tool_calls": [{
                "id": tc.id, "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            } for tc in msg.tool_calls],
        })

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            args_str = tc.function.arguments
            trace.tool_calls.append(tool_name)
            _log(f"Step {step+1}: [{tool_name}] {args_str[:120]}")

            # Doom-loop
            recent_calls.append((tool_name, args_str))
            if len(recent_calls) > 3: recent_calls.pop(0)
            if len(recent_calls) == 3 and recent_calls[0] == recent_calls[1] == recent_calls[2]:
                _log("DOOM-LOOP DETECTED"); _save_log()
                return {"answer": "Doom-loop detected", "traces": [],
                        "total_steps": step + 1, "total_tokens": total_tokens, "doom_loop": True}

            # Dispatch
            tool = tool_map.get(tool_name)
            if tool is None:
                result = _make_error_envelope(f"Unknown: {tool_name}")
            else:
                try: args = json.loads(args_str)
                except json.JSONDecodeError:
                    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", args_str)
                    try: args = json.loads(cleaned)
                    except json.JSONDecodeError as e:
                        result = _make_error_envelope(f"Parse error: {e}")
                        messages.append({"role": "tool", "tool_call_id": tc.id,
                                         "content": json.dumps(result, ensure_ascii=False)})
                        continue
                try: result = tool.handler(**args)
                except Exception as e: result = _make_error_envelope(f"Tool fail: {e}")

            # Hooks
            for hook in PRE_HOOKS:
                m = hook(tool_name, args, None)
                if m is not None: args = m
            for hook in reversed(POST_HOOKS):
                m = hook(tool_name, args, result)
                if m is not None: result = m

            # Wrap bare error
            if "error" in result and "ok" not in result:
                result = _make_error_envelope(result["error"])

            # Ch.02 step boundary stubs
            # TODO: abort_token check, grace_call, provider_fallback

            # final_answer
            if tool_name == "final_answer" and "answer" in result:
                final_text = result["answer"]
                traces.append(trace)
                _log(f"Step {step+1}: [FINAL] {final_text[:200]}")
                _save_log()
                return {"answer": final_text, "traces": [t.__dict__ for t in traces],
                        "total_steps": step + 1, "total_tokens": total_tokens}

            # Ch.05 — clip + Reflect
            result_json = json.dumps(result, ensure_ascii=False)
            clipped, was, _sid = _clip(result_json)
            messages.append({
                "role": "tool", "tool_call_id": tc.id,
                "content": clipped, "_tn": tool_name, "_ta": args_str,
            })

        traces.append(trace)

    _save_log()
    return {"answer": final_text or "(step cap)", "traces": [t.__dict__ for t in traces],
            "total_steps": max_steps, "total_tokens": total_tokens, "partial": True}
