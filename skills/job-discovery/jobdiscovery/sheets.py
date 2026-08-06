#!/usr/bin/env python3
"""The only module that talks to Google Sheets.

Two rules are enforced here rather than left to callers. Reads are checked
against the sheet's own reported extent, because a silently short read makes
dedup re-report roles that were reported days ago — the tracker's header once
claimed 191 roles while an export returned 115. Writes go through values.append,
which locates the end of the data itself, so no row index exists anywhere in
this codebase to go stale.
"""
from __future__ import annotations
import pathlib, re, sys
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
BASE = "https://sheets.googleapis.com/v4/spreadsheets"
COLUMNS = [chr(c) for c in range(ord("A"), ord("R") + 1)]  # A..R, 18 columns


class IncompleteReadError(RuntimeError):
    """The read returned fewer rows than the tracker's own header claims it has."""


def rows_from_values(values: list[list[str]]) -> list[dict[str, str]]:
    """Sheets omits trailing empty cells; pad every row to the full A..R shape."""
    out = []
    for row in values:
        padded = list(row) + [""] * (len(COLUMNS) - len(row))
        out.append(dict(zip(COLUMNS, padded[: len(COLUMNS)])))
    return out


def assert_complete_read(returned_rows: int, claimed_total: int | None) -> None:
    """Compare the read against the count the tracker's own header claims.

    The sheet's allocated row count is useless for this — it is 1000 rows of
    mostly-empty grid. The only independent statement of how many roles exist is
    the summary cell a human maintains in the header block. When it is not
    configured there is no independent statement at all, and that is said out
    loud rather than passed over: an unchecked read must not look like a checked
    one.
    """
    if claimed_total is None:
        print("WARNING: no summary_range configured — read completeness is unchecked. "
              "Dedup is only as complete as this read.", file=sys.stderr)
        return
    if returned_rows < claimed_total:
        raise IncompleteReadError(
            f"read {returned_rows} rows but the tracker's header claims {claimed_total}. "
            "Dedup cannot be trusted on a partial read; aborting. If the header cell is "
            "simply stale, correct it in the sheet — do not lower this check."
        )


class SheetsClient:
    def __init__(self, config, session: AuthorizedSession | None = None):
        self.config = config
        self._session = session

    @property
    def session(self) -> AuthorizedSession:
        if self._session is None:
            key = pathlib.Path(self.config.key_path)
            if not key.exists():
                raise FileNotFoundError(f"service account key not found at {key}")
            creds = service_account.Credentials.from_service_account_file(str(key), scopes=SCOPES)
            self._session = AuthorizedSession(creds)
        return self._session

    def _get(self, url: str, **params):
        r = self.session.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def claimed_total(self) -> int | None:
        """The role count the tracker's header block states, if one is configured."""
        rng = getattr(self.config, "summary_range", None)
        if not rng:
            return None
        data = self._get(f"{BASE}/{self.config.spreadsheet_id}/values/"
                         f"'{self.config.tab_name}'!{rng}")
        for row in data.get("values", []):
            for cell in row:
                numbers = re.findall(r"\d+", str(cell))
                if numbers:
                    return int(numbers[0])
        return None

    def read_tracker(self) -> list[dict[str, str]]:
        rng = f"'{self.config.tab_name}'!A{self.config.first_data_row}:R"
        data = self._get(f"{BASE}/{self.config.spreadsheet_id}/values/{rng}")
        rows = [r for r in rows_from_values(data.get("values", []))
                if any(v.strip() for v in r.values())]
        assert_complete_read(len(rows), self.claimed_total())
        return rows

    def append_rows(self, rows: list[list[str]]) -> int:
        if not rows:
            return 0
        rng = f"'{self.config.tab_name}'!A{self.config.first_data_row}:R"
        r = self.session.post(
            f"{BASE}/{self.config.spreadsheet_id}/values/{rng}:append",
            params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
            json={"values": rows}, timeout=60,
        )
        r.raise_for_status()
        updated = r.json().get("updates", {}).get("updatedRows", 0)
        return int(updated)
