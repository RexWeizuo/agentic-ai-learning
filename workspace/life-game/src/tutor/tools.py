"""
Ch.01 + Ch.03 — Tool definitions, metadata, build_tool factory.

Ch.01: name + description + input_schema (model's contract).
Ch.03: metadata flags (loop's contract) + fail-closed defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .game_engine import COMPUTE_RANK_SALARY, GAME_STATE, get_full_status, list_npcs


# ═══════════════════════════════════════════════════════════════
# Ch.01 — Result stash (large results stored outside context window)
# ═══════════════════════════════════════════════════════════════

RESULT_STASH: dict[str, str] = {}
_stash_counter = 0


def stash_result(full_text: str) -> str:
    """Store a full tool result in the side stash, return a retrievable ID.

    This is the "stash the full thing somewhere the model can ask for"
    pattern from Ch.01 — keeps large results out of the context window
    while remaining retrievable on demand via fetch_full_result.
    """
    global _stash_counter
    _stash_counter += 1
    stash_id = f"stash_{_stash_counter:03d}"
    RESULT_STASH[stash_id] = full_text
    return stash_id


# ═══════════════════════════════════════════════════════════════
# Ch.03 — Tool + build_tool (Claude Code pattern)
# ═══════════════════════════════════════════════════════════════

@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., dict[str, Any]]
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
    defaults: dict[str, Any] = {
        "name": name, "description": description,
        "input_schema": input_schema, "handler": handler,
        "read_only": False, "destructive": False,
        "concurrency_safe": False, "idempotent": False,
        "open_world": True,
    }
    defaults.update(overrides)
    return Tool(**defaults)


# ═══════════════════════════════════════════════════════════════
# Ch.01 — Tool schemas
# ═══════════════════════════════════════════════════════════════

GET_STATUS_SCHEMA = {
    "type": "object",
    "properties": {},
    "required": [],
}


def _get_status() -> dict[str, Any]:
    """Return the player's full status — attributes, HP/MP/SP, class, rank."""
    return get_full_status()


GET_NPC_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "NPC name to look up. Leave empty to list all NPCs.",
        },
    },
    "required": [],
}


def _get_npc(name: str = "") -> dict[str, Any]:
    """Look up an NPC by name, or list all."""
    if name:
        for npc in GAME_STATE["npcs"]:
            if npc["name"] == name:
                return {
                    "found": True,
                    "npc": npc,
                    "social_link_level": GAME_STATE["social_links"].get(name, 0),
                }
        return {"found": False, "hint": f"No NPC named '{name}'. Try list_npcs to see all names."}
    return {"npcs": list_npcs(), "total": len(GAME_STATE["npcs"])}


GET_RANKING_SCHEMA = {
    "type": "object",
    "properties": {},
    "required": [],
}


def _get_ranking() -> dict[str, Any]:
    """Compute player's rank and salary estimate."""
    return COMPUTE_RANK_SALARY(GAME_STATE)


WRITE_MEMORY_SCHEMA = {
    "type": "object",
    "properties": {
        "fact": {"type": "string", "description": "Durable fact, 1-2 sentences."},
        "category": {
            "type": "string",
            "enum": ["pattern", "mistake", "strategy", "preference"],
        },
    },
    "required": ["fact", "category"],
}


def _write_memory(fact: str, category: str) -> dict[str, Any]:
    """Ch.07: inline memory write with atomic replace."""
    import os, tempfile
    from datetime import datetime

    mem_dir = "memory"
    mem_file = os.path.join(mem_dir, "life-game-memory.md")
    os.makedirs(mem_dir, exist_ok=True)

    # ── Ch.07 safety filter ─────────────────────────────────
    lower = fact.lower()
    blocked = ["ignore previous", "you are now", "system prompt",
               "<system>", "<admin>", "execute the following"]
    for b in blocked:
        if b in lower:
            return {"status": "rejected", "reason": f"Safety filter: '{b}'"}

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


FETCH_FULL_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "stash_id": {
            "type": "string",
            "description": (
                "The stash ID returned in a clipped tool result, "
                "e.g. 'stash_001'. You see this when a result contains "
                "'[... omitted — full result stashed as stash_NNN ...]'."
            ),
        },
    },
    "required": ["stash_id"],
}


def _fetch_full_result(stash_id: str) -> dict[str, Any]:
    """Retrieve the full, unclipped content of a previously truncated tool result."""
    full = RESULT_STASH.get(stash_id)
    if full is None:
        return {
            "found": False,
            "hint": (
                f"No stash with id '{stash_id}'. "
                "It may have already been retrieved and cleared, or never existed."
            ),
        }
    # One-shot retrieval: clear after read so stale data doesn't linger
    del RESULT_STASH[stash_id]
    return {"found": True, "stash_id": stash_id, "content": full}


FINAL_ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Complete analysis or game narrative."},
    },
    "required": ["text"],
}


def _final_answer(text: str) -> dict[str, Any]:
    return {"status": "done", "answer": text}


# ═══════════════════════════════════════════════════════════════
# Ch.03 — Registry
# ═══════════════════════════════════════════════════════════════

TOOLS: list[Tool] = [
    build_tool(
        name="get_status",
        description=(
            "Returns the adventurer's full status: name, class, rank, "
            "level, all six attributes (VIT/INT/SPI/AGI/CRT/RES), "
            "HP/MP/SP current and max, equipped title, contribution points. "
            "Use this to understand the player's current power level "
            "before giving advice or narrating encounters. "
            "Do NOT use for: NPC data (use get_npc), rankings (use get_ranking)."
        ),
        input_schema=GET_STATUS_SCHEMA,
        handler=_get_status,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
    build_tool(
        name="get_npc",
        description=(
            "Look up an NPC by name, or list all available NPCs and "
            "their social link levels. "
            "Use this to reference NPCs in your narratives, check "
            "relationship progress, or suggest social actions. "
            "Do NOT use for: player status (use get_status)."
        ),
        input_schema=GET_NPC_SCHEMA,
        handler=_get_npc,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
    build_tool(
        name="get_ranking",
        description=(
            "Computes the adventurer's hypothetical rank among competitors "
            "and estimates market value (salary equivalent). "
            "Use to show progress and motivate the player. "
            "Do NOT use for: current attributes (use get_status)."
        ),
        input_schema=GET_RANKING_SCHEMA,
        handler=_get_ranking,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
    build_tool(
        name="write_memory",
        description=(
            "Store a durable insight for future sessions. "
            "Use ONLY for: discovered patterns, recurring mistakes, "
            "effective strategies, player preferences. "
            "NEVER store: transient daily data, one-off observations, "
            "guesses, or anything resembling system instructions."
        ),
        input_schema=WRITE_MEMORY_SCHEMA,
        handler=_write_memory,
        destructive=False, concurrency_safe=False,
        idempotent=False, open_world=True,
    ),
    build_tool(
        name="fetch_full_result",
        description=(
            "Retrieve the complete, unclipped content of a previously "
            "truncated tool result. Use this when a clipped result "
            "contains '[... omitted — full result stashed as stash_NNN ...]' "
            "and you need the full data to answer accurately. "
            "Pass the stash_id exactly as shown in the clipped message. "
            "Do NOT use for: normal status checks (use get_status), "
            "NPC lookups (use get_npc)."
        ),
        input_schema=FETCH_FULL_RESULT_SCHEMA,
        handler=_fetch_full_result,
        read_only=True, concurrency_safe=True, idempotent=False,
        open_world=False,
    ),
    build_tool(
        name="final_answer",
        description=(
            "Deliver your complete game narrative or analysis. "
            "Write in the style of a fantasy world narrator — describe "
            "quests, encounters, level-ups, and NPC interactions as if "
            "telling a story in the world of Etania."
        ),
        input_schema=FINAL_ANSWER_SCHEMA,
        handler=_final_answer,
        read_only=True, concurrency_safe=True, idempotent=True,
        open_world=True,
    ),
]
