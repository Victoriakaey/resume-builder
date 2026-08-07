#!/usr/bin/env python3
"""Whether a role qualifies. Every rule here is mechanical and every rejection
carries a reason, because a filter that drops roles without saying why is
indistinguishable from a filter that is broken.

Ambiguity is never a rejection: a role with no usable location signal passes
through and is judged by a human downstream.
"""
from __future__ import annotations
import dataclasses, re

TARGET_TERMS = (
    "ai engineer", "applied ai", "ai systems", "ai runtime", "ai infrastructure",
    "llm", "language model", "agent", "genai", "generative ai",
    "machine learning platform", "ml platform", "developer tools", "devtools",
    "forward deployed", "evaluation", "inference", "rag", "retrieval",
    "software engineer, ai", "full stack", "backend",
)
SENIORITY_CUTS = ("senior", "staff", "principal", "lead ", "manager", "director",
                  "head of", "vp ", "vice president", "architect")
BAY_TERMS = ("san francisco", "sf bay", "bay area", "palo alto", "mountain view",
             "menlo park", "sunnyvale", "santa clara", "san jose", "berkeley",
             "oakland", "redwood city", "cupertino", "south san francisco",
             "san mateo", "burlingame", "emeryville", "california")
# A bare ", ca" substring also matches ", Canada", which kept every Toronto and
# Vancouver posting. The state abbreviation has to end where the word ends.
CA_TAIL = re.compile(r",\s*ca\b", re.I)
# Likewise `us` without boundaries matched the "us" inside "Australia" and inside
# "must relocate". The country is a whole word now — and it has to admit USA as
# well as US, because a boundary tight enough to cut "Australia" also cut
# "Remote, USA" on the first attempt. Dropping a real posting is the worse of the
# two failures: a run that over-reports is visible, one that quietly under-reports
# is not.
CA_REMOTE = re.compile(
    r"remote[^.\n]{0,60}(california|\bca\b|\bu\.?s\.?a?\.?\b|united states)", re.I)
NON_CA_REMOTE = re.compile(r"remote[^.\n]{0,60}(emea|europe|apac|canada|latam|india)", re.I)
CLEARANCE = re.compile(r"(security clearance|ts/sci|top secret|public trust)", re.I)
YEARS = re.compile(r"(\d{1,2})\s*\+?\s*(?:-\s*\d{1,2}\s*)?years?", re.I)
MAX_YEARS = 4


@dataclasses.dataclass(frozen=True)
class Verdict:
    keep: bool
    reason: str


def _title_hits(title: str) -> bool:
    low = title.lower()
    return any(term in low for term in TARGET_TERMS)


def _location_ok(location: str) -> bool:
    low = location.lower()
    if not low.strip():
        return True                       # ambiguous → keep
    if NON_CA_REMOTE.search(low):
        return False
    if CA_REMOTE.search(low):
        return True
    if CA_TAIL.search(low):
        return True
    return any(term in low for term in BAY_TERMS)


def _min_years(description: str) -> int | None:
    hits = [int(m.group(1)) for m in YEARS.finditer(description)]
    return min(hits) if hits else None


def verdict(role) -> Verdict:
    low_title = role.title.lower()
    if any(cut in low_title for cut in SENIORITY_CUTS):
        return Verdict(False, f"seniority: {role.title!r}")
    if not _title_hits(role.title):
        return Verdict(False, f"title off target: {role.title!r}")
    if not _location_ok(role.location):
        return Verdict(False, f"location out of area: {role.location!r}")
    if CLEARANCE.search(role.description):
        return Verdict(False, "clearance required")
    years = _min_years(role.description)
    if years is not None and years > MAX_YEARS:
        return Verdict(False, f"years: requires {years}, cap is {MAX_YEARS}")
    return Verdict(True, "")
