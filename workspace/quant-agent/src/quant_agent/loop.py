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
from typing import Any

from openai import OpenAI

from .tools.registry import TOOLS, Tool

# ── Configuration ────────────────────────────────────────────────

MODEL = "qwen3.7-max"  # Rotate: qwen3.7-max → qwen3.7-max-2026-06-08 → ...
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MAX_STEPS = 20

SYSTEM_PROMPT = """\
You are a quantitative trading analyst assistant.

You have access to market data tools. Your job:
1. When the user asks about a stock or market, fetch the data FIRST.
2. Analyze what the data shows — trends, changes, notable signals.
3. When you have enough information, call final_answer with your analysis.

Rules:
- Always check current price before making any recommendation.
- If a tool fails, read the error and try a different approach.
- Do NOT guess prices or market data — always use tools.
- If the user asks about a stock that's not in A-stock format (6 digits),
  ask them to clarify which market and symbol.
- You support A-stock (6-digit code), crypto (BTC/USDT), and US stocks (AAPL).
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
                result = {"error": f"Unknown tool '{tool_name}'"}
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
                        result = {
                            "error": f"Failed to parse arguments: {e}",
                            "raw_args": tc.function.arguments[:200],
                        }
                except Exception as e:
                    # Ch.01 + Ch.02: wrap exception as tool_result
                    result = {
                        "error": f"Tool execution failed: {e}",
                        "tool": tool_name,
                    }

            # Ch.02: check for final_answer → explicit stop
            if tool_name == "final_answer" and "answer" in result:
                trace.stopped = True
                trace.stop_reason = "final_answer"
                final_text = result["answer"]
                traces.append(trace)
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

            # ── Log: tool result ────────────────────────────────
            _log(f"- **Result** (`{tool_name}`):")
            result_preview = json.dumps(result, ensure_ascii=False)
            _log(f"  ```json\n  {result_preview[:400]}\n  ```\n")

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

