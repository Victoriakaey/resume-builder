#!/usr/bin/env python3
"""writing.json — Step 2's own account of what the prose cost.

Kept apart from run.json on purpose: one file, one writer. If the writing step
could edit the discovery ledger, the 24-hour baseline in it would stop being
evidence.
"""
from __future__ import annotations
import dataclasses, json, pathlib

PASS_CAP = 4


@dataclasses.dataclass
class WritingLedger:
    pass_cap: int = PASS_CAP
    roles: dict = dataclasses.field(default_factory=dict)

    def record(self, role_slug: str, *, passes: int, tokens_in: int, tokens_out: int,
               residual: str = "") -> None:
        self.roles[role_slug] = {
            "passes": passes, "tokens_in": tokens_in, "tokens_out": tokens_out,
            "residual": residual, "hit_cap": passes >= self.pass_cap,
        }

    def write(self, path) -> pathlib.Path:
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        totals = {
            "roles": len(self.roles),
            "passes": sum(r["passes"] for r in self.roles.values()),
            "tokens_in": sum(r["tokens_in"] for r in self.roles.values()),
            "tokens_out": sum(r["tokens_out"] for r in self.roles.values()),
            "hit_cap": sum(1 for r in self.roles.values() if r["hit_cap"]),
        }
        path.write_text(json.dumps(
            {"pass_cap": self.pass_cap, "roles": self.roles, "totals": totals},
            indent=2, sort_keys=True))
        return path
