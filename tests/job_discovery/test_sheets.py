"""The Sheets client's two safety properties: rows come back keyed by column
letter, and a short read is an error rather than a smaller answer."""
from __future__ import annotations
import json, pathlib, pytest
from jobdiscovery import sheets

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _values() -> dict:
    return json.loads((FIXTURES / "sheet_values_small.json").read_text())


def test_rows_are_keyed_by_column_letter():
    rows = sheets.rows_from_values(_values()["values"])
    assert rows[0]["B"] == "https://boards.greenhouse.io/acme/jobs/1"
    assert rows[1]["G"] == "LLM Systems Engineer"
    assert rows[0]["R"] == ""


def test_short_row_is_padded_to_R_not_truncated():
    rows = sheets.rows_from_values([["Discovered", "https://x/1"]])
    assert rows[0]["R"] == ""
    assert len(rows[0]) == 18


def test_read_shorter_than_the_sheet_claims_is_an_error():
    with pytest.raises(sheets.IncompleteReadError):
        sheets.assert_complete_read(returned_rows=115, claimed_total=191)


def test_read_matching_the_claim_is_accepted():
    sheets.assert_complete_read(returned_rows=191, claimed_total=191)


def test_more_rows_than_claimed_is_accepted_because_the_claim_is_hand_maintained():
    sheets.assert_complete_read(returned_rows=200, claimed_total=191)


def test_no_claim_configured_means_no_check_rather_than_a_silent_pass(capsys):
    sheets.assert_complete_read(returned_rows=115, claimed_total=None)
    assert "unchecked" in capsys.readouterr().err.lower()


def test_numbers_in_a_block_are_found_with_their_addresses():
    found = sheets.find_numbers([["Job Tracker", "", "191 roles"],
                                 ["updated 2026", "", ""]], "A1:R4")
    assert ("C1", 191) in found
    assert ("A2", 2026) in found


def test_a_thousands_separator_is_one_number_not_two():
    assert sheets.find_numbers([["1,204 roles"]], "A1:R4") == [("A1", 1204)]


def test_addresses_are_relative_to_the_range_start():
    assert sheets.find_numbers([["7"]], "D2:R4") == [("D2", 7)]
