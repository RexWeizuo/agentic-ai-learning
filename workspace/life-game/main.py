"""
Life Game — Learning Tutor Agent (Ch.01-07 implementation).

Usage:
    uv run python main.py
"""

from __future__ import annotations

import os
import sys

from src.tutor.loop import MODEL, run_loop


def main() -> None:
    key = os.environ.get("DASHSCOPE_API_KEY", os.environ.get("API_KEY", ""))
    if not key:
        print("Set DASHSCOPE_API_KEY or API_KEY")
        sys.exit(1)

    print(f"Life Game — Learning Tutor ({MODEL})")

    result = run_loop(
        "Analyze my current study progress across all subjects (408-OS, 301-数学, Agent). "
        "Show me: 1) mastery levels and weak spots, 2) hypothetical ranking among "
        "1000 competitors, 3) estimated salary based on skills mastered, "
        "4) a game-style daily quest. Use get_progress, get_daily_report, and get_ranking.",
        verbose=True, log_dir="logs",
    )

    print(f"\n{'⚠️ PARTIAL' if result.get('partial') else '✅'} "
          f"({result['total_steps']} steps, {result['total_tokens']} tokens)")
    print(f"\n{result['answer']}")


if __name__ == "__main__":
    main()
