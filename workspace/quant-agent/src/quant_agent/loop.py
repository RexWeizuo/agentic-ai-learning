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

# ── Error classification (Ch.03: recoverable vs fatal) ───────────

def _classify_error(error_msg: str) -> tuple[bool, str]:
    """
    Classify a tool error as recoverable or fatal.

    Recoverable = retry might work (network blip, timeout, rate limit).
    Fatal = retry will never work (bad symbol, invalid params, auth failure).

    Returns (recoverable: bool, hint: str).
    """
    msg_lower = error_msg.lower()

    # ── Recoverable patterns ──────────────────────────────────
    recoverable_patterns = [
        ("connection", "Network issue — try again in a moment"),
        ("timeout", "Request timed out — retry with fewer symbols if persistent"),
        ("timed out", "Request timed out — retry with fewer symbols if persistent"),
        ("rate limit", "Rate limited — wait a few seconds then retry"),
        ("too many requests", "Rate limited — wait a few seconds then retry"),
        ("remote end closed", "Server closed connection — retry once"),
        ("remote disconnected", "Server disconnected — retry once"),
    ]
    for pattern, hint in recoverable_patterns:
        if pattern in msg_lower:
            return (True, hint)

    # ── Fatal patterns ───────────────────────────────────────
    fatal_patterns = [
        ("not found", "Symbol or resource does not exist — do not retry"),
        ("invalid", "Invalid input — correct the arguments instead of retrying"),
        ("cannot auto-detect", "Unrecognized symbol format — ask user to clarify"),
        ("arrearage", "API quota exhausted — switch model or top up"),
        ("access denied", "Authentication failed — check credentials"),
        ("permission", "Permission denied — cannot fix by retrying"),
    ]
    for pattern, hint in fatal_patterns:
        if pattern in msg_lower:
            return (False, hint)

    # ── Default: assume recoverable (let model decide) ───────
    return (True, "Unknown error — you may retry once or try another approach")


def _make_error_envelope(error_msg: str) -> dict[str, Any]:
    """Wrap an error in Ch.03's result envelope."""
    recoverable, hint = _classify_error(error_msg)
    return {
        "ok": False,
        "error": error_msg,
        "recoverable": recoverable,
        "hint": hint,
    }


# ── Hooks (Ch.03: pre/post dispatch callbacks) ────────────────────
# Each hook is a function (tool_name, args, result) -> result (may modify).
# Pre-hooks run in registration order. Post-hooks run in reverse.
# A hook returning None means "don't modify result".

PRE_HOOKS: list[Callable[[str, dict, dict | None], dict | None]] = []
POST_HOOKS: list[Callable[[str, dict, dict], dict | None]] = []


def _hook_trace_input(tool_name: str, args: dict, _result: dict | None) -> dict | None:
    """Pre-hook: log every tool dispatch with args."""
    # Already logged via _log() in verbose mode — this is the hook version.
    return None  # Don't modify args


def _hook_add_provenance(tool_name: str, _args: dict, result: dict) -> dict | None:
    """Post-hook: stamp result with provenance (Ch.03: output metadata)."""
    result["_provenance"] = {
        "tool": tool_name,
        "timestamp": datetime.now().isoformat(),
    }
    return result


def _hook_scrub_secrets(tool_name: str, _args: dict, result: dict) -> dict | None:
    """Post-hook: redact any leaked secrets from result text."""
    # TODO: add secret patterns when real credentials appear in results
    return None  # Nothing to scrub yet


# Register built-in hooks (order matters!)
POST_HOOKS.append(_hook_add_provenance)
# POST_HOOKS.append(_hook_scrub_secrets)  # TODO: enable when needed


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

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
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
                        f"Tool '{tool_name}' execution failed: {e}"
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
            # Pre-hooks (registration order)
            for hook in PRE_HOOKS:
                modified = hook(tool_name, args, None)
                if modified is not None:
                    args = modified  # Hook transformed the input args

            # Post-hooks (reverse registration order)
            for hook in reversed(POST_HOOKS):
                modified = hook(tool_name, args, result)
                if modified is not None:
                    result = modified  # Hook transformed the output

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

            # ── Reflect: append tool result to messages ──────────
            result_json = json.dumps(result, ensure_ascii=False)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_json,
            })

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

