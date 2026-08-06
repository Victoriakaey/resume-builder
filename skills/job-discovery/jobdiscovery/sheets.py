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


CELL = re.compile(r"^([A-Z]+)(\d+)$")


class IncompleteReadError(RuntimeError):
    """The read returned fewer rows than the tracker's own header claims it has."""


class AmbiguousSummaryError(RuntimeError):
    """The configured summary range holds more than one number, so which one
    states the role count is a guess. Set summary_cell instead."""


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


def _column_letters(index: int) -> str:
    letters = ""
    while index >= 0:
        letters = chr(ord("A") + index % 26) + letters
        index = index // 26 - 1
    return letters


def find_numbers(values: list[list[str]], a1_range: str) -> list[tuple[str, int]]:
    """Every number in a block, each with the cell address it came from.

    Returning the addresses is what lets an ambiguous header say which cells it
    is torn between, instead of silently taking the first.
    """
    start = a1_range.split(":")[0].upper()
    match = CELL.match(start)
    first_column, first_row = (match.group(1), int(match.group(2))) if match else ("A", 1)
    column_offset = sum((ord(c) - ord("A") + 1) * 26 ** i
                        for i, c in enumerate(reversed(first_column))) - 1
    found: list[tuple[str, int]] = []
    for row_index, row in enumerate(values):
        for column_index, cell in enumerate(row):
            for number in re.findall(r"\d[\d,]*", str(cell)):
                address = (f"{_column_letters(column_offset + column_index)}"
                           f"{first_row + row_index}")
                found.append((address, int(number.replace(",", ""))))
    return found


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

    def _values(self, a1: str) -> list[list[str]]:
        data = self._get(f"{BASE}/{self.config.spreadsheet_id}/values/"
                         f"'{self.config.tab_name}'!{a1}")
        return data.get("values", [])


    def claimed_total(self) -> int | None:
        """The role count the tracker's header states, if it can be identified.

        An exact cell is read as an exact cell. A range is searched, and finding
        more than one number in it is an error rather than a choice: a header
        block holds dates and other counts, and picking one by position would let
        the check that exists to catch a silently short read be silently wrong
        itself.
        """
        if self.config.summary_cell:
            values = self._values(self.config.summary_cell)
            numbers = [n for row in values for cell in row
                       for n in re.findall(r"\d[\d,]*", str(cell))]
            if len(numbers) != 1:
                raise AmbiguousSummaryError(
                    f"summary_cell {self.config.summary_cell} holds {len(numbers)} "
                    f"numbers ({numbers}); it must hold exactly one."
                )
            return int(numbers[0].replace(",", ""))

        if not self.config.summary_range:
            return None

        candidates = find_numbers(self._values(self.config.summary_range),
                                  self.config.summary_range)
        if not candidates:
            return None
        if len(candidates) > 1:
            listed = ", ".join(f"{addr}={value}" for addr, value in candidates)
            raise AmbiguousSummaryError(
                f"summary_range {self.config.summary_range} holds "
                f"{len(candidates)} numbers ({listed}). Which one is the role "
                "count is not for this code to guess — set summary_cell in the "
                "config to the right address."
            )
        return candidates[0][1]

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
