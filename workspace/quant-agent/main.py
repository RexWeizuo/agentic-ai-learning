"""
Quant Agent — entry point.

Usage:
    uv run python main.py

Environment:
    DASHSCOPE_API_KEY — your DashScope API key (required)
"""

from __future__ import annotations

import os
import sys

from src.quant_agent.loop import run_loop


def main() -> None:
    # ── Check API key ────────────────────────────────────────────
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("Error: DASHSCOPE_API_KEY environment variable not set.")
        print("Set it with: $env:DASHSCOPE_API_KEY='your-key'  (PowerShell)")
        print("       or: export DASHSCOPE_API_KEY='your-key'   (bash)")
        sys.exit(1)

    print("=" * 60)
    print("Quant Agent — Ch.02 Agent Loop")
    print("Model: qwen-max (DashScope)")
    print("=" * 60)

    # ── Demo: ask about a stock ──────────────────────────────────
    user_message = "贵州茅台现在什么价格？最近走势怎么样，值得买吗？"

    print(f"\nUser: {user_message}\n")
    print("-" * 60)

    result = run_loop(user_message, verbose=True)

    print("-" * 60)
    print(f"\n{'⚠️  PARTIAL ' if result.get('partial') else '✅'} "
          f"Answer ({result['total_steps']} steps, "
          f"{result['total_tokens']} tokens):\n")
    print(result["answer"])


if __name__ == "__main__":
    main()
