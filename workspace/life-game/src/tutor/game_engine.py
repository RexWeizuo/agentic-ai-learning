"""
Ch.03 + Ch.04 + Game Layer — ranking engine + salary mapping + prompt.

The game engine converts real study data into:
  - Hypothetical ranking among imaginary competitors
  - Salary premium per skill learned
  - Game-style progress metrics

Ch.04: SYSTEM_PROMPT is the stable prefix — frozen at session start,
       byte-stable across turns for Qwen's automatic cache.
"""

from __future__ import annotations

from typing import Any

# ── Skill → Salary mapping (from Changsha market research) ───────

SKILL_SALARY_MAP: dict[str, dict[str, Any]] = {
    "Python 基础": {
        "base_salary": 6000, "ceiling_salary": 8000,
        "mastery_bonus": 200, "market_weight": 0.8,
    },
    "Agent Loop 设计": {
        "base_salary": 8000, "ceiling_salary": 12000,
        "mastery_bonus": 1000, "market_weight": 1.0,
    },
    "工具验证+元数据": {
        "base_salary": 8000, "ceiling_salary": 11000,
        "mastery_bonus": 800, "market_weight": 0.8,
    },
    "提示词+缓存": {
        "base_salary": 7000, "ceiling_salary": 9000,
        "mastery_bonus": 500, "market_weight": 0.5,
    },
    "记忆系统": {
        "base_salary": 9000, "ceiling_salary": 15000,
        "mastery_bonus": 1500, "market_weight": 0.9,
    },
    "多 Agent 编排": {
        "base_salary": 10000, "ceiling_salary": 18000,
        "mastery_bonus": 2000, "market_weight": 1.0,
    },
    "MCP 连接器": {
        "base_salary": 9000, "ceiling_salary": 15000,
        "mastery_bonus": 1500, "market_weight": 0.8,
    },
    "生产可观测性": {
        "base_salary": 8000, "ceiling_salary": 12000,
        "mastery_bonus": 1000, "market_weight": 0.6,
    },
    "成本优化": {
        "base_salary": 8000, "ceiling_salary": 12000,
        "mastery_bonus": 1000, "market_weight": 0.6,
    },
}


def _match_skill(concept_name: str) -> str | None:
    """Fuzzy-match a concept name to a known skill."""
    mapping = {
        "agent": "Agent Loop 设计",
        "工具": "工具验证+元数据",
        "验证": "工具验证+元数据",
        "提示": "提示词+缓存",
        "缓存": "提示词+缓存",
        "记忆": "记忆系统",
        "编排": "多 Agent 编排",
        "mcp": "MCP 连接器",
        "可观测": "生产可观测性",
        "成本": "成本优化",
    }
    name_lower = concept_name.lower()
    for keyword, skill in mapping.items():
        if keyword in name_lower:
            return skill
    return None


def compute_salary_estimate(study_data: dict[str, Any]) -> dict[str, Any]:
    """Map mastered concepts to estimated market salary."""
    base = 5000  # baseline salary (Changsha junior)
    bonus = 0
    skills_unlocked: list[str] = []

    for subject_name, subject in study_data.get("subjects", {}).items():
        for concept_name in subject.get("top_scores", []):
            skill = _match_skill(concept_name)
            if skill and skill in SKILL_SALARY_MAP:
                info = SKILL_SALARY_MAP[skill]
                bonus += info["mastery_bonus"]
                if skill not in skills_unlocked:
                    skills_unlocked.append(skill)

    estimated = base + bonus
    return {
        "base_salary": base,
        "skill_bonus": bonus,
        "estimated_monthly": estimated,
        "skills_contributing": skills_unlocked,
    }


def compute_hypothetical_ranking(
    study_data: dict[str, Any], pool_size: int = 1000,
) -> dict[str, Any]:
    """
    Compute a hypothetical ranking among imaginary competitors.

    Based on: total concepts mastered, average mastery score,
    and diversity of subjects covered.
    """
    subjects = study_data.get("subjects", {})
    if not subjects:
        return {"rank": pool_size, "pool_size": pool_size, "percentile": 0}

    total_score = 0.0
    max_possible = 0.0

    for s in subjects.values():
        for concept_name in s.get("top_scores", []):
            total_score += 1.0  # each mastered concept = 1 point
        for concept_name in s.get("weak_spots", []):
            total_score += 0.0  # weak concepts contribute nothing
        max_possible += len(s.get("top_scores", [])) + len(s.get("weak_spots", []))

    # Scale to percentile: higher score = higher rank
    # Simple model: your score / hypothetical_max * pool_size
    if max_possible == 0:
        return {"rank": pool_size, "pool_size": pool_size, "percentile": 0}

    # Assume the top competitor has 3x the total concepts
    top_score = max(total_score * 3, 20)
    percentile = min(total_score / top_score * 100, 99.9)
    rank = max(int(pool_size * (1 - percentile / 100)), 1)

    return {
        "rank": rank,
        "pool_size": pool_size,
        "percentile": round(percentile, 1),
        "score": round(total_score, 1),
        "top_score": round(top_score, 1),
    }


# ═════════════════════════════════════════════════════════════════
# Ch.04 — Stable prefix (frozen at session start)
# ═════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
You are a Learning Tutor — a game-style life management agent.

## Your Role
Analyze the user's real study data and produce gamified reports:
- Concept mastery scores → converted to RPG-style levels
- Skill progress → mapped to estimated salary premiums
- Daily activity → ranked against hypothetical competitors

## Data You Have
- Study progress files with concept-level mastery scores (★ to ★★★★★)
- Daily session timelines showing effective study hours
- Salary-skill mapping based on real market data (Changsha AI jobs)

## Reporting Rules
1. Use specific numbers from the data — NEVER invent scores or rankings.
2. Frame progress as a game: levels, achievements, rankings, salary grades.
3. Identify weak spots and suggest focused "quests" to improve them.
4. When asked, call write_memory to persist important insights.
5. Deliver your complete analysis via final_answer.

## Game Mechanics Reference
- Concept scored ★★★★★+ = "Mastered" (max level)
- Concept scored ★★★★  = "Proficient"
- Concept scored ★★ or less = "Weak spot" (needs grinding)
- Every new concept mastered = +ranking boost
- Cross-subject progress (408+301+Agent) = diversity multiplier
"""
