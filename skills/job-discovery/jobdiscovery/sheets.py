#!/usr/bin/env python3
"""The only module that talks to the tracker.

Reads and writes go through an Apps Script web app rather than the Sheets API,
because the service-account setup proved more friction than the endpoint is
worth. What decision 2 actually required still holds: this is an authenticated
HTTP call, not browser automation, and it runs unattended.

Two rules are enforced here rather than left to callers. A read is checked
against the sheet's own reported extent, because a silently short read makes
dedup re-report roles that were reported days ago — an export of this very sheet
once returned 115 of its 215 rows and every number the design was reasoned from
came from it. And writes append after the sheet's own last row, so no row index
exists anywhere in this codebase to go stale.
"""
from __future__ import annotations
import json, pathlib
import requests

COLUMNS = [chr(c) for c in range(ord("A"), ord("R") + 1)]  # A..R, 18 columns


class IncompleteReadError(RuntimeError):
    """The read returned fewer rows than the sheet says it has."""


class EndpointError(RuntimeError):
    """The endpoint refused the call or reported a failure."""


def rows_from_values(values: list[list[str]]) -> list[dict[str, str]]:
    """Pad every row to the full A..R shape; trailing empty cells are omitted."""
    out = []
    for row in values:
        padded = list(row) + [""] * (len(COLUMNS) - len(row))
        out.append(dict(zip(COLUMNS, padded[: len(COLUMNS)])))
    return out


def assert_complete_read(returned_rows: int, last_row: int, first_data_row: int) -> None:
    expected = max(0, last_row - first_data_row + 1)
    if returned_rows < expected:
        raise IncompleteReadError(
            f"read {returned_rows} rows but the sheet reports {expected} data rows "
            f"(last row {last_row}, data starts at {first_data_row}). Dedup cannot be "
            "trusted on a partial read; aborting."
        )


class TrackerClient:
    def __init__(self, config, session=None):
        self.config = config
        self._session = session or requests.Session()
        creds = json.loads(pathlib.Path(config.webapp_credentials).read_text())
        self._url, self._token = creds.get("url"), creds.get("token")
        if not self._url or not self._token:
            raise EndpointError(f"{config.webapp_credentials} has no url or no token")

    def _call(self, action: str, **extra):
        response = self._session.post(
            self._url, json={"token": self._token, "action": action, **extra}, timeout=120)
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise EndpointError(f"{action}: {payload.get('error', 'no reason given')}")
        return payload

    def read_tracker(self) -> list[dict[str, str]]:
        payload = self._call("read")
        rows = rows_from_values(payload.get("rows", []))
        # Count first, then drop blanks. The completeness check exists to catch a
        # short read, and the endpoint returns every row in [firstDataRow, lastRow]
        # by construction — so it is the raw count that has to agree with the
        # sheet's extent. The live tracker really does hold two wholly-blank rows
        # inside its range; filtering before counting reported every read of it as
        # truncated, which is the check crying wolf about the sheet's contents
        # rather than about the read.
        assert_complete_read(len(rows), payload["lastRow"], payload["firstDataRow"])
        return [r for r in rows if any(v.strip() for v in r.values())]

    def append_rows(self, rows: list[list[str]]) -> int:
        if not rows:
            return 0
        return int(self._call("append", rows=rows).get("appended", 0))
