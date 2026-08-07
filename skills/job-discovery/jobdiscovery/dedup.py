#!/usr/bin/env python3
"""What "previously unreported" means.

Three keys, checked strongest first. The third — company plus title — is the
only one that can be wrong about a genuinely new opening, so it never drops on
its own: it must agree on location, and otherwise the role is flagged for a
human rather than discarded. Nothing is dropped without a recorded key and the
tracker row it matched; the previous system's failures survived nineteen runs
precisely because its process left nothing to audit.

Status values are deliberately not consulted. "dislike the role" is information
the operator is giving the system, not a company-level exclusion.
"""
from __future__ import annotations
import dataclasses, re
from urllib.parse import urlsplit

LOCATION_NOISE = re.compile(r"\((?:[^)]*)\)|[-–—]\s*(remote|hybrid|on-?site).*$", re.I)
PUNCT = re.compile(r"[^a-z0-9 ]+")
SPACES = re.compile(r"\s+")
GREENHOUSE_HOST = re.compile(r"^(?:job-)?boards\.greenhouse\.io$", re.I)


@dataclasses.dataclass(frozen=True)
class Decision:
    action: str                 # "new" | "drop" | "review"
    key: str = ""               # "url" | "ats_id" | "company_title"
    matched_row: int | None = None


def canonical_url(url: str) -> str:
    if not url:
        return ""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    if GREENHOUSE_HOST.match(host):
        host = "boards.greenhouse.io"
    path = parts.path.rstrip("/").lower()
    return f"{host}{path}"


def _norm(text: str) -> str:
    text = LOCATION_NOISE.sub(" ", text.lower())
    return SPACES.sub(" ", PUNCT.sub(" ", text)).strip()


def title_key(company: str, title: str) -> str:
    return f"{_norm(company)}|{_norm(title)}"


def location_key(location: str) -> str:
    return _norm(location)


class Index:
    def __init__(self):
        self.by_url: dict[str, int] = {}
        self.by_ats_id: dict[str, int] = {}
        self.by_title: dict[str, tuple[int, str]] = {}

    @classmethod
    def from_rows(cls, rows: list[dict[str, str]], first_data_row: int) -> "Index":
        """first_data_row is required on purpose. It carried a default of 6 while
        the sheet's data actually starts at row 5, and every matched_row this
        index reported was off by one for two days before anyone noticed. The
        caller holds the config; a default here can only ever disagree with it."""
        index = cls()
        for offset, row in enumerate(rows):
            row_number = first_data_row + offset
            url = canonical_url(row.get("B", ""))
            if url:
                index.by_url.setdefault(url, row_number)
            req = row.get("L", "").strip()
            if req:
                index.by_ats_id.setdefault(req.lower(), row_number)
            key = title_key(row.get("F", ""), row.get("G", ""))
            if key.strip("|"):
                index.by_title.setdefault(key, (row_number, location_key(row.get("H", ""))))
        return index

    def remember(self, role, row_number: int = -1) -> None:
        url = canonical_url(role.url)
        if url:
            self.by_url.setdefault(url, row_number)
        ats_id = f"{role.ats}:{role.token}:{role.job_id}".lower()
        self.by_ats_id.setdefault(ats_id, row_number)
        self.by_title.setdefault(title_key(role.company, role.title),
                                 (row_number, location_key(role.location)))

    def check(self, role) -> Decision:
        url = canonical_url(role.url)
        if url in self.by_url:
            return Decision("drop", "url", self.by_url[url])
        ats_id = f"{role.ats}:{role.token}:{role.job_id}".lower()
        if ats_id in self.by_ats_id:
            return Decision("drop", "ats_id", self.by_ats_id[ats_id])
        if role.job_id and role.job_id.lower() in self.by_ats_id:
            return Decision("drop", "ats_id", self.by_ats_id[role.job_id.lower()])
        key = title_key(role.company, role.title)
        if key in self.by_title:
            row_number, seen_location = self.by_title[key]
            if seen_location == location_key(role.location):
                return Decision("drop", "company_title", row_number)
            return Decision("review", "company_title", row_number)
        return Decision("new")
