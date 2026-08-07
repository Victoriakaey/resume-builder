#!/usr/bin/env python3
"""Column M, computed by a fixed formula rather than by a model.

A model-assigned score drifts between runs, so two identical roles found a week
apart would not compare. This rubric is boring on purpose: the same role always
scores the same number, and explain() shows where every point came from.
"""
from __future__ import annotations

PRIORITY_TOPICS = (
    "agent architecture", "agent orchestration", "orchestration",
    "llm evaluation", "evaluation", "judge", "critic",
    "prompt optimisation", "prompt optimization", "context engineering",
    "retrieval", "tool use", "distributed systems", "developer tools",
    "production", "inference", "fine-tun",
)
CORE_TITLES = ("llm", "agent", "applied ai", "ai systems", "ai runtime", "ai engineer")
TITLE_POINTS, TOPIC_POINTS, TOPIC_CAP, LOCATION_POINTS, ENTRY_POINTS = 4, 1, 4, 1, 1


def explain(role) -> dict[str, int]:
    low_title = role.title.lower()
    blob = f"{role.title} {role.description}".lower()
    topic_hits = sum(1 for topic in PRIORITY_TOPICS if topic in blob)
    return {
        "title": TITLE_POINTS if any(t in low_title for t in CORE_TITLES) else 0,
        "topics": min(topic_hits * TOPIC_POINTS, TOPIC_CAP),
        # work_mode, not the location string: ats.py already resolved this from
        # what the board states, and re-reading the prose here would score the
        # same role differently depending on how its location happens to be
        # written. The Lever posting whose location says "San Francisco, CA /
        # Remote" while the board says hybrid is exactly that role.
        # A stated Hybrid or On-site earns the point. Remote does not, and neither
        # does an unknown — a role from a discovery source carries work_mode="" until
        # the ATS gate replaces it, and "not Remote" would have handed every one of
        # those a free point for a fact nobody had established yet. Same rule as
        # freshness: no signal, no credit.
        "location": LOCATION_POINTS if role.work_mode in ("Hybrid", "On-site") else 0,
        "entry_level": ENTRY_POINTS if any(
            k in blob for k in ("new grad", "entry level", "early career", "university")
        ) else 0,
    }


def score(role) -> int:
    return min(10, sum(explain(role).values()))
