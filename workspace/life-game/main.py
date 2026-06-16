"""
Life Game — Etania (Ch.01-07 full implementation).

Usage: uv run python main.py
"""

from __future__ import annotations

import os, sys
from src.tutor.loop import MODEL, run_loop


def main() -> None:
    if not os.environ.get("DASHSCOPE_API_KEY", os.environ.get("API_KEY", "")):
        print("Set DASHSCOPE_API_KEY or API_KEY"); sys.exit(1)

    print(f"\n  ⚔️  Life Game — Etania ({MODEL})\n")

    result = run_loop(
        "我刚刚在旅店醒来。帮我看看我现在的状态——我的属性、职业、等级。"
        "然后告诉我公会里有哪些同伴（NPC）在。最后给我今天的冒险建议。"
        "用奇幻世界的叙述风格来写。",
        verbose=True, log_dir="logs",
    )

    tag = "⚠️ PARTIAL" if result.get("partial") else "✅"
    print(f"\n  {tag} ({result['total_steps']} steps, {result['total_tokens']} tokens)")
    print(f"\n{result['answer']}")


if __name__ == "__main__":
    main()
