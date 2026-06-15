"""
Ch.06 — Curated knowledge: read study-progress files as frozen prefix.

Loads real study data from the user's 301/408/Agent progress tracker.
All data is read at session start and frozen per Ch.04 cache rule.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
STUDY_DIR = ROOT / "memory" / "study-progress"
DAILY_DIR = ROOT / "memory" / "daily-sessions"


# ── Data models ─────────────────────────────────────────────────

@dataclass
class ConceptScore:
    name: str
    score: int  # 1-5 stars
    subject: str
    chapter: str


@dataclass
class SubjectSnapshot:
    name: str
    concepts: list[ConceptScore] = field(default_factory=list)
    completed: int = 0
    total: int = 0

    @property
    def mastery_pct(self) -> float:
        if not self.concepts:
            return 0.0
        return sum(c.score for c in self.concepts) / (len(self.concepts) * 5) * 100


@dataclass
class DailyTimeline:
    date: str
    sessions: float  # effective study hours
    tasks_completed: int
    total_tasks: int


# ── Loaders ─────────────────────────────────────────────────────

def _parse_score_table(text: str, default_subject: str = "") -> list[ConceptScore]:
    """Extract concept scores from markdown tables."""
    scores: list[ConceptScore] = []
    subject = default_subject
    chapter = ""

    for line in text.split("\n"):
        stripped = line.strip()

        # Track subject from headings AND filename context
        if stripped.startswith("## "):
            heading = stripped[3:]
            if any(w in heading for w in ("408", "OS", "操作系统")):
                subject = "408-OS"
            elif any(w in heading for w in ("301", "数学", "线代", "高数")):
                subject = "301-数学"
            elif any(w in heading for w in ("Agent", "Ch", "工具", "循环", "函数调用")):
                subject = "Agent"
        if stripped.startswith("### "):
            chapter = stripped[4:]
        # Also detect from frontmatter (title, section, subject)
        if any(stripped.startswith(p) for p in ("title:", "section:", "subject:", "name:")):
            val = stripped.split(":", 1)[1].strip()
            if any(w in val for w in ("408", "OS", "进程", "内存", "文件", "IO", "调度", "死锁", "同步")):
                subject = "408-OS"
            elif any(w in val for w in ("301", "数学", "线代", "高数", "特征", "二次型", "多元")):
                subject = "301-数学"
            elif any(w in val for w in ("Agent", "Ch0", "Ch1", "Ch2", "工具", "循环", "调用")):
                subject = "Agent"

        # Parse table rows with star ratings
        if "★" in stripped and "|" in stripped:
            parts = [p.strip() for p in stripped.split("|")]
            # Find the column that contains stars
            star_col = -1
            name_col = -1
            for i, p in enumerate(parts):
                if "★" in p and star_col < 0:
                    star_col = i
                elif not p or p.startswith("-"):
                    continue
                elif name_col < 0 and not p.startswith("-"):
                    name_col = i
            if star_col >= 0 and name_col >= 0 and star_col != name_col:
                name = parts[name_col].strip()
                stars = parts[star_col].count("★")
                if stars > 0 and name and "---" not in name:
                    scores.append(ConceptScore(
                        name=name, score=min(stars, 5),
                        subject=subject or "Unknown",
                        chapter=chapter or "Unknown",
                    ))

    return scores


def load_all_study_data() -> dict[str, Any]:
    """Ch.06: load curated knowledge into frozen prefix.

    Walks ALL study-progress files recursively, extracts concept
    scores from markdown tables, and compiles subject snapshots.
    """
    subjects: dict[str, SubjectSnapshot] = {}

    if not STUDY_DIR.is_dir():
        return {"subjects": {}, "total_concepts": 0}

    for path in sorted(STUDY_DIR.rglob("*.md")):
        rel = str(path.relative_to(STUDY_DIR))
        # Skip README, 金融知识, and other non-score files
        if path.name in ("README.md", "金融知识.md"):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Detect subject from path (more reliable than parsing)
        path_str = str(rel)
        if "408" in path_str or "OS" in path_str:
            default_subject = "408-OS"
        elif "301" in path_str or "数学" in path_str:
            default_subject = "301-数学"
        elif "agent" in path_str.lower():
            default_subject = "Agent"
        else:
            default_subject = ""

        scores = _parse_score_table(text, default_subject=default_subject)
        for c in scores:
            if c.subject not in subjects:
                subjects[c.subject] = SubjectSnapshot(name=c.subject)
            subjects[c.subject].concepts.append(c)

        # Mark completed from frontmatter status
        if "status: 完成" in text or "status: complete" in text.lower():
            for c in scores:
                if c.subject in subjects:
                    subjects[c.subject].completed += 1
                break  # count chapter completion once per file

    # Count totals
    for s in subjects.values():
        s.total = len(s.concepts)

    return {
        "subjects": {k: {
            "name": v.name,
            "mastery_pct": round(v.mastery_pct, 1),
            "concepts_completed": v.completed,
            "total_concepts": len(v.concepts),
            "top_scores": [c.name for c in v.concepts if c.score >= 4],
            "weak_spots": [c.name for c in v.concepts if c.score <= 2],
        } for k, v in subjects.items()},
        "total_concepts": sum(s.total for s in subjects.values()),
    }


def load_recent_sessions(days: int = 7) -> list[DailyTimeline]:
    """Ch.06: load recent daily timelines for trend analysis."""
    timelines: list[DailyTimeline] = []
    for f in sorted(DAILY_DIR.glob("2026-*.md"), reverse=True)[:days]:
        text = f.read_text(encoding="utf-8")
        date = f.stem
        tasks_done = text.count("[x]") + text.count("[X]")
        tasks_total = text.count("[ ]") + tasks_done
        timelines.append(DailyTimeline(
            date=date,
            sessions=0.0,  # parsed roughly below
            tasks_completed=tasks_done,
            total_tasks=max(tasks_total, 1),
        ))
    return list(reversed(timelines))  # chronological order
