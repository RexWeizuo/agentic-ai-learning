"""
Ch.02 — Tool registry: the contract between model and code.

Every tool the agent can call is registered here.
The model sees name + description + input_schema.
Your code sees handler + concurrency_safe.

Reserved slots for future tools:
  - get_kline      (historical candlestick data)
  - get_financials (PE ratio, revenue, profit, etc.)
  - get_index      (market index like SSE Composite)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .memory import WRITE_MEMORY_SCHEMA, write_memory
from .prices import (
    GET_FINANCIALS_SCHEMA,
    GET_INDEX_SCHEMA,
    GET_KLINE_SCHEMA,
    GET_PRICE_SCHEMA,
    get_financials,
    get_index,
    get_kline,
    get_price,
)


# ── Tool definition ──────────────────────────────────────────────

@dataclass
class Tool:
    """One tool in the registry.

    Ch.01: "schema and handler must move together."
    Ch.02: "concurrency_safe marks tools that can run in parallel."
    Ch.03: metadata flags the loop reads before dispatching.

    Fields the MODEL sees (via to_openai_schema):
      - name, description, input_schema

    Fields the LOOP reads (the metadata contract):
      - handler, read_only, destructive, concurrency_safe,
        idempotent, open_world
    """

    # ── Model's view ───────────────────────────────────────────
    name: str
    description: str
    input_schema: dict[str, Any]

    # ── Loop's view (Ch.03 metadata) ───────────────────────────
    # Defaults are FAIL-CLOSED (Claude Code pattern):
    #   assume write, assume unsafe, need explicit override.
    handler: Callable[..., dict[str, Any]]
    read_only: bool = False          # default: assume can mutate
    destructive: bool = False        # default: not destructive
    concurrency_safe: bool = False   # default: assume NOT safe
    idempotent: bool = False         # default: assume NOT idempotent
    open_world: bool = True          # default: assume result varies

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI-compatible tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


def build_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    handler: Callable[..., dict[str, Any]],
    **overrides: Any,
) -> Tool:
    """
    Build a Tool with safe defaults. `overrides` explicitly opt in.

    Claude Code pattern (Tool.ts:757-792): all tools go through
    a factory that applies fail-closed defaults — no tool ships
    with undefined safety flags. Each tool that IS safe must
    explicitly declare it.
    """
    defaults: dict[str, Any] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "handler": handler,
        # fail-closed: assume unsafe unless explicitly overridden
        "read_only": False,
        "destructive": False,
        "concurrency_safe": False,
        "idempotent": False,
        "open_world": True,
    }
    defaults.update(overrides)
    return Tool(**defaults)


# ── final_answer — the explicit stop tool ────────────────────────

FINAL_ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {
            "type": "string",
            "description": (
                "Your final answer or analysis to the user. "
                "Include all relevant data, reasoning, and conclusions."
            ),
        },
    },
    "required": ["text"],
}


def final_answer(text: str) -> dict[str, Any]:
    """Explicit stop — model declares it is done."""
    return {"status": "done", "answer": text}


# ── The registry ─────────────────────────────────────────────────

TOOLS: list[Tool] = [
    build_tool(
        name=GET_PRICE_SCHEMA["name"],
        description=GET_PRICE_SCHEMA["description"],
        input_schema=GET_PRICE_SCHEMA["input_schema"],
        handler=get_price,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
    build_tool(
        name=GET_KLINE_SCHEMA["name"],
        description=GET_KLINE_SCHEMA["description"],
        input_schema=GET_KLINE_SCHEMA["input_schema"],
        handler=get_kline,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=False,
    ),
    build_tool(
        name=GET_INDEX_SCHEMA["name"],
        description=GET_INDEX_SCHEMA["description"],
        input_schema=GET_INDEX_SCHEMA["input_schema"],
        handler=get_index,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
    build_tool(
        name=GET_FINANCIALS_SCHEMA["name"],
        description=GET_FINANCIALS_SCHEMA["description"],
        input_schema=GET_FINANCIALS_SCHEMA["input_schema"],
        handler=get_financials,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=False,
    ),
    build_tool(
        name=WRITE_MEMORY_SCHEMA["name"],
        description=WRITE_MEMORY_SCHEMA["description"],
        input_schema=WRITE_MEMORY_SCHEMA["input_schema"],
        handler=write_memory,
        # NOT read_only — writes to disk!
        destructive=False,
        concurrency_safe=False,
        idempotent=False,
        open_world=True,
    ),
    build_tool(
        name="final_answer",
        description=(
            "Call this when you have gathered sufficient data to answer "
            "the user's question. Use text to deliver your complete analysis. "
            "Do NOT call this if you still need more data from other tools."
        ),
        input_schema=FINAL_ANSWER_SCHEMA,
        handler=final_answer,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
    # ── Reserved slots ─────────────────────────────────────────
    # build_tool(name="get_kline", ...)
    # build_tool(name="get_financials", ...)
    # build_tool(name="get_index", ...)
    # build_tool(name="search_news", ...)
    # build_tool(name="run_backtest", ...)
]
