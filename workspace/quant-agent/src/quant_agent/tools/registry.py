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

from .prices import GET_PRICE_SCHEMA, get_price


# ── Tool definition ──────────────────────────────────────────────

@dataclass
class Tool:
    """One tool in the registry.

    Ch.01: "schema and handler must move together."
    Ch.02: "concurrency_safe marks tools that can run in parallel."
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., dict[str, Any]]
    concurrency_safe: bool = True  # True for read-only tools

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
    Tool(
        name=GET_PRICE_SCHEMA["name"],
        description=GET_PRICE_SCHEMA["description"],
        input_schema=GET_PRICE_SCHEMA["input_schema"],
        handler=get_price,
        concurrency_safe=True,
    ),
    Tool(
        name="final_answer",
        description=(
            "Call this when you have gathered sufficient data to answer "
            "the user's question. Use text to deliver your complete analysis. "
            "Do NOT call this if you still need more data from other tools."
        ),
        input_schema=FINAL_ANSWER_SCHEMA,
        handler=final_answer,
        concurrency_safe=True,
    ),
    # ── Reserved slots ─────────────────────────────────────────
    # Tool(name="get_kline",        ...)  # K-line / candlestick history
    # Tool(name="get_financials",   ...)  # Fundamental data (PE, revenue)
    # Tool(name="get_index",        ...)  # Market index (上证指数 etc.)
    # Tool(name="search_news",      ...)  # Sentiment / news search
    # Tool(name="run_backtest",     ...)  # Strategy backtest engine
]
