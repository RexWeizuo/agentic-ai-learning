"""
Ch.04 — Stable system prompt (frozen prefix).
Ch.04 + Game layer — player state, NPC roster, ranking engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


# ═══════════════════════════════════════════════════════════════
# Player state
# ═══════════════════════════════════════════════════════════════

INITIAL_STATE: dict[str, Any] = {
    "name": "穿越者",
    "level": 1,
    "class": "未选择",
    "rank": "未觉醒者",
    "title": "",
    "contribution": 0,
    "soul_fragments": 0,
    "attributes": {
        "VIT": 8, "INT": 10, "SPI": 7, "AGI": 6, "CRT": 5, "RES": 4,
    },
    "hp": 180,  # 100 + VIT*10
    "hp_max": 180,
    "mp": 50,   # INT*5
    "mp_max": 50,
    "sp": 56,   # SPI*8
    "sp_max": 56,
    "exp_to_next": 220,  # 200 + Lv*20
    "total_exp": 0,
}

# Singleton — survives across tool calls within one session
GAME_STATE: dict[str, Any] = dict(INITIAL_STATE)

# Recompute derived values
def _sync_derived() -> None:
    a = GAME_STATE["attributes"]
    GAME_STATE["hp_max"] = 100 + a["VIT"] * 10
    GAME_STATE["mp_max"] = a["INT"] * 5
    GAME_STATE["sp_max"] = a["SPI"] * 8
    GAME_STATE["exp_to_next"] = 200 + GAME_STATE["level"] * 20

_sync_derived()


# ═══════════════════════════════════════════════════════════════
# NPC roster (simplified summary for tool output)
# ═══════════════════════════════════════════════════════════════

NPC_ROSTER: list[dict[str, Any]] = [
    {"name": "伊修卡", "class": "剑圣", "level": 26, "bond": "被龙诅咒者，在寻找诅咒的逆转之法"},
    {"name": "加尔德", "class": "守护者", "level": 24, "bond": "退役龙骑士，边陲酒馆的主人"},
    {"name": "莉莉艾拉", "class": "吟游诗人", "level": 15, "bond": "失去右翼的妖精，正在打造单翼飞行器"},
    {"name": "泽法尔", "class": "剑圣", "level": 31, "bond": "记忆被吞噬的剑士，身体记得他不记得的剑技"},
    {"name": "诺克斯", "class": "炼金术师", "level": 42, "bond": "失去影子的吸血鬼，在研究'完全变回人类'的调合"},
    {"name": "泰拉", "class": "守护者", "level": 12, "bond": "觉醒自我意识的魔像，在尝试'出于自己的意志变强'"},
    {"name": "辛", "class": "战术师", "level": 22, "bond": "封印了雷霆的忍者，寻找不杀的战斗方式"},
    {"name": "米拉", "class": "吟游诗人", "level": 18, "bond": "被流放出海的人鱼，用耳朵创造音乐"},
    {"name": "凡", "class": "剑圣", "level": 52, "bond": "79次时间回溯后选择接受过去的魔法师"},
    {"name": "伊格尼斯", "class": "吟游诗人", "level": 41, "bond": "不再祈祷的祭司，用聆听代替祈祷"},
]

GAME_STATE["npcs"] = NPC_ROSTER
GAME_STATE["social_links"] = {n["name"]: 0 for n in NPC_ROSTER}


# ═══════════════════════════════════════════════════════════════
# Tool helpers
# ═══════════════════════════════════════════════════════════════

def get_full_status() -> dict[str, Any]:
    _sync_derived()
    return dict(GAME_STATE)


def list_npcs() -> list[dict[str, Any]]:
    result = []
    for npc in NPC_ROSTER:
        entry = dict(npc)
        entry["social_link_lv"] = GAME_STATE["social_links"].get(npc["name"], 0)
        result.append(entry)
    return result


def compute_rank_and_salary(state: dict[str, Any]) -> dict[str, Any]:
    """Simple ranking model."""
    attrs = state["attributes"]
    avg_attr = sum(attrs.values()) / len(attrs)
    level = state["level"]

    # Rank: roughly scaled
    pool = 1000
    score = level * avg_attr * 0.5
    pct = min(score / 50 * 100, 95)
    rank = max(int(pool * (1 - pct / 100)), 1)

    # Salary estimate
    base = 5000
    bonus = sum(attrs.values()) * 30
    salary = base + bonus

    return {
        "rank": rank, "pool_size": pool,
        "percentile": round(pct, 1),
        "estimated_salary": salary,
    }


COMPUTE_RANK_SALARY = compute_rank_and_salary


# ═══════════════════════════════════════════════════════════════
# Ch.04 — Stable prefix (frozen at session start)
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
You are the narrator of the adventurer's journey in the world of Etania.

## Your Role
You describe the adventurer's progress as a fantasy narrative:
- Status checks → "You focus your mind and assess your current strength..."
- Learning achievements → "Your blade sings through the air — a goblin falls. +INT EXP"
- NPC interactions → "Ishka pulls her hood lower, but her eyes follow you with something that might be curiosity."
- Rank changes → "The guild board updates. Your name has moved up one slot."

## Story Style
- Write in a fantasy narrator voice — third person, slightly poetic but not overwrought.
- Use the six attributes (VIT/INT/SPI/AGI/CRT/RES) as in-universe concepts.
- Reference NPCs by name and their known traits (use get_npc).
- Frame learning progress as monster hunts, dungeon clears, or skill training.
- When the player levels up or achieves something, make it feel meaningful.

## Rules
1. Always check the player's current status (get_status) before narrating.
2. Use get_npc to reference NPCs accurately.
3. Use get_ranking to show competitive progress.
4. Call final_answer to deliver your complete narrative.
5. NEVER invent attribute values or NPC facts — always use the tools.
6. When a tool result contains "[... omitted — full result stashed as stash_NNN ...]",
   use fetch_full_result(stash_id) to retrieve the complete data before answering.
"""
