#!/usr/bin/env python3
"""Per-ATS adapters that flatten a public job board into one Role shape.

The field paths in FIELDS are transcribed from the recorded board fixtures in
tests/job_discovery/fixtures/. If an adapter stops finding a timestamp, the
fix is to re-probe and update these paths — never to fall back to "now",
which would turn a stale posting into a fresh one.
"""
from __future__ import annotations
import dataclasses, datetime as dt
from typing import Any


@dataclasses.dataclass(frozen=True)
class Role:
    company: str
    title: str
    location: str
    work_mode: str
    url: str
    job_id: str
    ats: str
    token: str
    posted_at: dt.datetime | None
    posted_kind: str          # "published" | "updated" | "unknown"
    description: str
    source: str


# Transcribed from the recorded fixtures. list_path: where the postings live in
# the payload ("" means the payload is itself the list). Each *_path is a
# dotted path inside one posting; "" means this ATS has no such field. Ashby
# has no updatedAt field at all — its updated_path is "" on purpose, not a
# placeholder.
FIELDS: dict[str, dict[str, Any]] = {
    "greenhouse": {
        "list_path": "jobs",
        "id_path": "id", "title_path": "title", "url_path": "absolute_url",
        "location_path": "location.name", "description_path": "content",
        "published_path": "first_published", "updated_path": "updated_at",
        "workplace_path": "",          # Greenhouse states no workplace type
    },
    "ashby": {
        "list_path": "jobs",
        "id_path": "id", "title_path": "title", "url_path": "jobUrl",
        "location_path": "location", "description_path": "descriptionPlain",
        "published_path": "publishedAt", "updated_path": "",
        "workplace_path": "workplaceType",     # "OnSite" | "Hybrid" | "Remote"
    },
    "lever": {
        "list_path": "",
        "id_path": "id", "title_path": "text", "url_path": "hostedUrl",
        "location_path": "categories.location", "description_path": "descriptionPlain",
        "published_path": "createdAt", "updated_path": "",
        "workplace_path": "workplaceType",     # "onsite" | "hybrid" | "remote"
    },
}

# The three values I may hold, keyed by the lowercased form of whatever the ATS
# states. An unrecognised value is not coerced — it falls through to the text
# reading, so a new vocabulary shows up as a wrong guess to fix rather than as
# a silent "On-site".
WORKPLACE = {"onsite": "On-site", "on-site": "On-site", "hybrid": "Hybrid", "remote": "Remote"}

# Each board's public listings endpoint, keyed by the same ats name used in
# FIELDS above. Verified 2026-08-07 against a real token for each (Figma,
# Alembic, Canvas Medical from the seeded companies.yaml): all three returned
# HTTP 200.
ENDPOINTS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{token}",
    "lever": "https://api.lever.co/v0/postings/{token}?mode=json",
}


def _dig(obj: Any, path: str) -> Any:
    if not path:
        return None
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _parse_time(value: Any) -> dt.datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):          # epoch millis or seconds
        seconds = value / 1000 if value > 1e11 else value
        return dt.datetime.fromtimestamp(seconds, tz=dt.timezone.utc)
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def _work_mode(stated: Any, location: str, description: str) -> str:
    """What the board says, and only failing that, what its prose suggests.

    Ashby and Lever state the workplace type outright — 63 of the 70 boards — so
    reading it out of the location string there would be guessing past a real
    signal, the same mistake `freshness` refuses to make with timestamps. A Lever
    posting really does carry `workplaceType: "hybrid"` alongside the location
    `"San Francisco, CA / Remote"`, and the text reading gets it wrong. Greenhouse
    states nothing, so there the text is all there is.
    """
    if stated:
        resolved = WORKPLACE.get(str(stated).strip().lower())
        if resolved:
            return resolved
    blob = f"{location} {description}".lower()
    if "remote" in blob and "hybrid" not in blob:
        return "Remote"
    if "hybrid" in blob:
        return "Hybrid"
    return "On-site"


def parse_board(ats_name: str, token: str, company: str, payload: Any) -> list[Role]:
    spec = FIELDS[ats_name]
    raw = _dig(payload, spec["list_path"]) if spec["list_path"] else payload
    postings = raw if isinstance(raw, list) else []
    roles: list[Role] = []
    for posting in postings:
        published = _parse_time(_dig(posting, spec["published_path"]))
        updated = _parse_time(_dig(posting, spec["updated_path"]))
        if published is not None:
            posted_at, kind = published, "published"
        elif updated is not None:
            posted_at, kind = updated, "updated"
        else:
            posted_at, kind = None, "unknown"
        location = str(_dig(posting, spec["location_path"]) or "")
        description = str(_dig(posting, spec["description_path"]) or "")
        stated_mode = _dig(posting, spec["workplace_path"])
        roles.append(Role(
            company=company, title=str(_dig(posting, spec["title_path"]) or ""),
            location=location, work_mode=_work_mode(stated_mode, location, description),
            url=str(_dig(posting, spec["url_path"]) or ""),
            job_id=str(_dig(posting, spec["id_path"]) or ""),
            ats=ats_name, token=token, posted_at=posted_at, posted_kind=kind,
            description=description, source=ats_name,
        ))
    return roles
