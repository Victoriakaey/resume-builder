#!/usr/bin/env python3
"""Age, confidence, and one window.

There is no target and no widening. A run reports the ATS-verified roles posted
inside twenty-four hours, and however many that is, is the answer.

The graded 24/48/72-hour passes this module used to have existed to reach ten
roles per run. Measurement killed that number: this supply supports about three,
and most of what the previous system counted toward ten had either never been
verified or was already past the freshness rule. A target a system cannot hit is
not a goal, it is a pressure to fabricate — so the target went, and the machinery
for stretching to meet it went with it.
"""
from __future__ import annotations
import datetime as dt

WINDOW_HOURS = 24


def age_hours(role, now: dt.datetime) -> float | None:
    if role.posted_at is None:
        return None
    return (now - role.posted_at).total_seconds() / 3600.0


def confidence(role) -> str:
    if role.posted_at is None:
        return "Low"
    return "High" if role.posted_kind == "published" else "Medium"


def within_window(roles, now: dt.datetime) -> list:
    """The roles this run may report. No timestamp means not inside the window."""
    return [r for r in roles
            if (age := age_hours(r, now)) is not None and age <= WINDOW_HOURS]


def yield_24h(roles, now: dt.datetime) -> int:
    """The run's yield. Zero is a real answer and means the supply was zero."""
    return len(within_window(roles, now))
