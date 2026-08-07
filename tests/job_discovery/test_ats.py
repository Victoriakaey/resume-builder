"""Every assertion here reads the recorded fixture, so the parser is pinned to
what the API actually returned rather than to what we remember it returning."""
from __future__ import annotations
import json, pathlib, pytest
from jobdiscovery import ats

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _payload(name: str):
    path = FIXTURES / f"{name}_board.json"
    if not path.exists():
        pytest.skip(f"no recorded fixture {path.name}; see Task 3")
    return json.loads(path.read_text())


@pytest.mark.parametrize("name", ["greenhouse", "ashby", "lever"])
def test_every_parsed_role_has_the_identity_fields(name):
    roles = ats.parse_board(name, "probe-token", "Probe Co", _payload(name))
    assert roles, f"{name} fixture parsed to zero roles"
    for role in roles:
        assert role.url.startswith("http")
        assert role.job_id
        assert role.title
        assert role.ats == name


@pytest.mark.parametrize("name", ["greenhouse", "ashby", "lever"])
def test_posting_time_is_parsed_as_an_aware_datetime(name):
    roles = ats.parse_board(name, "probe-token", "Probe Co", _payload(name))
    timed = [r for r in roles if r.posted_at is not None]
    assert timed, f"{name}: no role carried a parseable posting time"
    assert timed[0].posted_at.tzinfo is not None
    assert timed[0].posted_kind in {"published", "updated"}


def test_a_role_with_no_recognisable_timestamp_is_unknown_not_now():
    roles = ats.parse_board("greenhouse", "t", "C", {"jobs": [
        {"id": 1, "title": "AI Engineer", "absolute_url": "https://x/1", "location": {"name": "SF"}}
    ]})
    assert roles[0].posted_at is None
    assert roles[0].posted_kind == "unknown"
