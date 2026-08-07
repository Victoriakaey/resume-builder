"""The tracker client's safety properties: rows come back keyed by column
letter, a short read is an error rather than a smaller answer, the endpoint's
own failure is surfaced rather than swallowed, and nothing touches the network
without an injected fake session."""
from __future__ import annotations
import json, pathlib, types, pytest
from jobdiscovery import sheets

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _values() -> dict:
    return json.loads((FIXTURES / "sheet_values_small.json").read_text())


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


class _FakeSession:
    """Records every call made through it; a test asserting `calls == []`
    is asserting the network was never touched."""

    def __init__(self, payload: dict):
        self._payload = payload
        self.calls: list[tuple[str, dict, int]] = []

    def post(self, url, json, timeout):
        self.calls.append((url, json, timeout))
        return _FakeResponse(self._payload)


def _credentials(tmp_path: pathlib.Path, url="https://example.test/exec", token="tok") -> types.SimpleNamespace:
    creds_path = tmp_path / "webapp.json"
    creds_path.write_text(json.dumps({"url": url, "token": token}))
    return types.SimpleNamespace(webapp_credentials=str(creds_path))


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
        sheets.assert_complete_read(returned_rows=115, last_row=195, first_data_row=5)


def test_read_matching_the_sheets_own_extent_is_accepted():
    sheets.assert_complete_read(returned_rows=191, last_row=195, first_data_row=5)


def test_more_rows_than_the_extent_implies_is_accepted():
    sheets.assert_complete_read(returned_rows=200, last_row=195, first_data_row=5)


def test_call_raises_endpoint_error_when_the_endpoint_reports_failure(tmp_path):
    session = _FakeSession({"ok": False, "error": "bad token"})
    client = sheets.TrackerClient(_credentials(tmp_path), session=session)
    with pytest.raises(sheets.EndpointError, match="bad token"):
        client._call("read")


@pytest.mark.parametrize("url,token", [("", "tok"), ("https://example.test/exec", "")])
def test_missing_url_or_token_in_credentials_raises_endpoint_error(tmp_path, url, token):
    creds = _credentials(tmp_path, url=url, token=token)
    with pytest.raises(sheets.EndpointError):
        sheets.TrackerClient(creds, session=_FakeSession({}))


def test_missing_url_or_token_key_entirely_raises_endpoint_error(tmp_path):
    creds_path = tmp_path / "webapp.json"
    creds_path.write_text(json.dumps({"token": "tok"}))  # no "url" key at all
    cfg = types.SimpleNamespace(webapp_credentials=str(creds_path))
    with pytest.raises(sheets.EndpointError):
        sheets.TrackerClient(cfg, session=_FakeSession({}))


def test_read_tracker_counts_the_raw_read_before_dropping_blank_rows(tmp_path):
    """The live tracker's exact shape: the endpoint's raw row count matches its
    stated extent exactly, but two of those rows are wholly blank. Counting
    after filtering would misread that as a short read — this is the bug the
    live check actually hit. Counting the raw read first, then dropping blanks
    from what's returned, reads it clean.

    If the completeness check ran on the filtered count instead, this payload
    would raise IncompleteReadError (2 real rows < 3 expected) instead of
    returning 2 rows cleanly — that's the behaviour this test pins.

    The blank row sits between the two real ones (sheet row 6 of firstDataRow=5),
    so a stamp computed by enumerating the *filtered* list would read 5, 6 — a
    consecutive count that happens to look plausible. The real sheet rows are
    5 and 7. Only stamping before the filter runs gets this right."""
    payload = {
        "ok": True,
        "rows": [
            ["Discovered", "https://x/1"] + [""] * 16,
            [""] * 18,
            ["Applied", "https://x/2"] + [""] * 16,
        ],
        "lastRow": 7,
        "firstDataRow": 5,
    }
    client = sheets.TrackerClient(_credentials(tmp_path), session=_FakeSession(payload))
    rows = client.read_tracker()  # must not raise
    assert len(rows) == 2
    assert rows[0]["B"] == "https://x/1"
    assert rows[1]["B"] == "https://x/2"
    assert rows[0][sheets.ROW_NUMBER] == 5
    assert rows[1][sheets.ROW_NUMBER] == 7


def test_append_rows_with_empty_list_returns_zero_without_calling_the_endpoint(tmp_path):
    session = _FakeSession({"ok": True, "appended": 99})
    client = sheets.TrackerClient(_credentials(tmp_path), session=session)
    assert client.append_rows([]) == 0
    assert session.calls == []


def test_append_rows_posts_and_returns_the_appended_count(tmp_path):
    session = _FakeSession({"ok": True, "appended": 2, "firstRow": 216})
    client = sheets.TrackerClient(_credentials(tmp_path), session=session)
    appended = client.append_rows([["a"] * 18, ["b"] * 18])
    assert appended == 2
    assert len(session.calls) == 1
    url, body, timeout = session.calls[0]
    assert body["action"] == "append"
    assert body["rows"] == [["a"] * 18, ["b"] * 18]
    assert body["token"] == "tok"
