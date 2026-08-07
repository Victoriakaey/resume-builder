#!/usr/bin/env python3
"""run.json — the account of what a run actually did.

Step 1 is its only writer. Step 2 keeps its own file, because a ledger a later
step can revise is not evidence. The run's yield can be set once and then
refuses to change, for the same reason.
"""
from __future__ import annotations
import dataclasses, json, pathlib


class YieldAlreadySet(RuntimeError):
    """The run's yield is written once and never revised."""


@dataclasses.dataclass
class RunLedger:
    yield_24h: int | None = None
    per_source: dict = dataclasses.field(default_factory=dict)
    dedup_drops: list = dataclasses.field(default_factory=list)
    review_flags: list = dataclasses.field(default_factory=list)
    unverified: list = dataclasses.field(default_factory=list)
    filtered_out: list = dataclasses.field(default_factory=list)

    def set_yield(self, count: int) -> None:
        if self.yield_24h is not None:
            raise YieldAlreadySet(
                f"yield already {self.yield_24h}; refusing to rewrite it as {count}"
            )
        self.yield_24h = count

    def record_source(self, name: str, roles: int, ok: bool, error: str = "") -> None:
        self.per_source[name] = {
            "status": "ok" if ok else "failed", "roles": roles, "error": error,
        }

    def record_drop(self, url: str, key: str, matched_row: int | None) -> None:
        self.dedup_drops.append({"url": url, "key": key, "matched_row": matched_row})

    def record_review(self, url: str, matched_row: int | None, why: str) -> None:
        self.review_flags.append({"url": url, "matched_row": matched_row, "why": why})

    def record_unverified(self, url: str, company: str, title: str) -> None:
        self.unverified.append({"url": url, "company": company, "title": title})

    def record_filtered(self, url: str, reason: str) -> None:
        self.filtered_out.append({"url": url, "reason": reason})

    def write(self, path) -> pathlib.Path:
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataclasses.asdict(self), indent=2, sort_keys=True))
        return path
