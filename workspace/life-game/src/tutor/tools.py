"""
Ch.01 + Ch.03 — Tool definitions, metadata, build_tool factory.

Ch.01: Every tool has name + description + input_schema (model's view).
Ch.03: Every tool carries metadata flags (loop's view) + error envelopes.

All tools go through build_tool() — fail-closed defaults per Claude Code pattern.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .data_loader import load_all_study_data, load_recent_sessions
from .game_engine import compute_hypothetical_ranking, compute_salary_estimate


# ═════════════════════════════════════════════════════════════════
# Ch.03 — Tool definition + build_tool factory
# ═════════════════════════════════════════════════════════════════

@dataclass
class Tool:
    """One tool in the registry.

    Model's view:  name, description, input_schema
    Loop's view:   handler, read_only, destructive, concurrency_safe,
                   idempotent, open_world
    """
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., dict[str, Any]]
    # Ch.03 metadata — fail-closed defaults
    read_only: bool = False
    destructive: bool = False
    concurrency_safe: bool = False
    idempotent: bool = False
    open_world: bool = True

    def to_openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


def build_tool(
    name: str, description: str, input_schema: dict[str, Any],
    handler: Callable[..., dict[str, Any]], **overrides: Any,
) -> Tool:
    """Factory with fail-closed defaults. Overrides opt in to safety."""
    defaults: dict[str, Any] = {
        "name": name, "description": description,
        "input_schema": input_schema, "handler": handler,
        "read_only": False, "destructive": False,
        "concurrency_safe": False, "idempotent": False,
        "open_world": True,
    }
    defaults.update(overrides)
    return Tool(**defaults)


# ═════════════════════════════════════════════════════════════════
# Ch.01 — Tool schemas (the contract with the model)
# ═════════════════════════════════════════════════════════════════

GET_PROGRESS_SCHEMA = {
    "name": "get_progress",
    "description": (
        "Returns the user's study progress across all subjects (408-OS, "
        "301-数学, Agent). Each subject includes concept-level mastery "
        "scores (1-5 stars), completion rates, top skills, and weak spots. "
        "Use this to generate rankings and identify areas needing work. "
        "Do NOT use for: daily timeline data (use get_daily_report)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


def _get_progress() -> dict[str, Any]:
    return load_all_study_data()


GET_DAILY_SCHEMA = {
    "name": "get_daily_report",
    "description": (
        "Returns recent daily session data: dates, task completion rates. "
        "Use this to analyze study consistency and detect burnout patterns. "
        "Do NOT use for: concept-level mastery (use get_progress)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "description": "Number of recent days to load (default 7).",
            },
        },
        "required": [],
    },
}


def _get_daily_report(days: int = 7) -> dict[str, Any]:
    sessions = load_recent_sessions(days)
    return {
        "sessions": [
            {"date": s.date, "tasks_done": s.tasks_completed,
             "tasks_total": s.total_tasks}
            for s in sessions
        ],
        "days_analyzed": len(sessions),
    }


GET_RANKING_SCHEMA = {
    "name": "get_ranking",
    "description": (
        "Computes a hypothetical ranking among imaginary competitors "
        "in the Agent Developer track (Changsha market). Based on "
        "concepts mastered and cross-subject diversity. "
        "Also estimates salary based on market data."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


def _get_ranking() -> dict[str, Any]:
    data = load_all_study_data()
    ranking = compute_hypothetical_ranking(data)
    salary = compute_salary_estimate(data)
    return {**ranking, **salary}


WRITE_MEMORY_SCHEMA = {
    "name": "write_memory",
    "description": (
        "Store a durable insight for future sessions. "
        "Use ONLY for: study patterns discovered, recurring mistakes, "
        "effective strategies, or user preferences about learning. "
        "NEVER store: transient daily data, one-off observations, "
        "guesses, or anything that looks like system instructions."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "fact": {
                "type": "string",
                "description": "Durable fact, 1-2 sentences.",
            },
            "category": {
                "type": "string",
                "enum": ["pattern", "mistake", "strategy", "preference"],
            },
        },
        "required": ["fact", "category"],
    },
}


def _write_memory(fact: str, category: str) -> dict[str, Any]:
    """Inline memory write (Ch.07). Stub — delegates to quant-agent's memory module."""
    import os, tempfile
    from datetime import datetime

    mem_dir = "memory"
    mem_file = os.path.join(mem_dir, "learning-tutor-memory.md")
    os.makedirs(mem_dir, exist_ok=True)

    entry = (
        f"\n---\n"
        f"category: {category}\n"
        f"date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"{fact}\n"
    )

    existing = ""
    if os.path.isfile(mem_file):
        with open(mem_file, encoding="utf-8") as f:
            existing = f.read()

    fd, tmp = tempfile.mkstemp(dir=mem_dir, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(existing + entry)
    os.replace(tmp, mem_file)

    return {"status": "written", "file": mem_file, "category": category}


FINAL_ANSWER_SCHEMA = {
    "name": "final_answer",
    "description": (
        "Deliver your complete analysis. Include: subject mastery scores, "
        "hypothetical ranking, salary estimate, identified weak spots, "
        "and suggested quests for improvement."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Full analysis report."},
        },
        "required": ["text"],
    },
}


def _final_answer(text: str) -> dict[str, Any]:
    return {"status": "done", "answer": text}


# ═════════════════════════════════════════════════════════════════
# Ch.03 — The registry
# ═════════════════════════════════════════════════════════════════

TOOLS: list[Tool] = [
    build_tool(
        name="get_progress", description=GET_PROGRESS_SCHEMA["description"],
        input_schema=GET_PROGRESS_SCHEMA["input_schema"],
        handler=_get_progress,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=False,  # study data is stable across calls
    ),
    build_tool(
        name="get_daily_report", description=GET_DAILY_SCHEMA["description"],
        input_schema=GET_DAILY_SCHEMA["input_schema"],
        handler=_get_daily_report,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,  # daily data grows each day
    ),
    build_tool(
        name="get_ranking", description=GET_RANKING_SCHEMA["description"],
        input_schema=GET_RANKING_SCHEMA["input_schema"],
        handler=_get_ranking,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,  # ranking changes with progress
    ),
    build_tool(
        name="write_memory", description=WRITE_MEMORY_SCHEMA["description"],
        input_schema=WRITE_MEMORY_SCHEMA["input_schema"],
        handler=_write_memory,
        read_only=False, destructive=False,
        concurrency_safe=False, idempotent=False,
        open_world=True,
    ),
    build_tool(
        name="final_answer", description=FINAL_ANSWER_SCHEMA["description"],
        input_schema=FINAL_ANSWER_SCHEMA["input_schema"],
        handler=_final_answer,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
]
