"""SimplifyJobs is a discovery source only: it must never assert freshness."""
from __future__ import annotations
import json, pathlib, re, pytest
from jobdiscovery import simplify

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _listings():
    path = FIXTURES / "simplify_listings.json"
    if not path.exists():
        pytest.skip("no recorded simplify fixture; see Task 7 Step 1")
    return json.loads(path.read_text())


def test_listings_parse_into_roles():
    roles = simplify.to_roles(_listings())
    assert roles
    assert all(r.source == "simplify" for r in roles)


def test_simplify_roles_never_carry_a_posting_time():
    for r in simplify.to_roles(_listings()):
        assert r.posted_at is None and r.posted_kind == "unknown"


def test_an_ats_url_yields_a_board_token_for_verification():
    roles = simplify.to_roles([{"company_name": "Acme", "title": "AI Engineer",
                                "locations": ["San Francisco, CA"],
                                "url": "https://boards.greenhouse.io/acme/jobs/1"}])
    assert roles[0].ats == "greenhouse" and roles[0].token == "acme"


def test_a_non_ats_url_leaves_the_role_unverifiable():
    roles = simplify.to_roles([{"company_name": "Gamma", "title": "AI Engineer",
                                "locations": ["SF"], "url": "https://gamma.com/careers/1"}])
    assert roles[0].ats == "" and roles[0].token == ""


def test_a_listing_whose_locations_hold_a_non_string_still_parses():
    roles = simplify.to_roles([{"company_name": "Delta", "title": "AI Engineer",
                                "locations": ["SF", None], "url": "https://delta.com/1"}])
    assert roles[0].location


def test_fetch_refuses_a_listings_file_that_is_not_a_list(tmp_path, monkeypatch):
    """The guard lives inside fetch(), after the git clone/pull — so exercising it
    honestly means going through fetch() itself, not a hand-rolled isinstance check
    that merely resembles it. No clone is possible in a test (no network), so
    subprocess.run is stubbed to a no-op and the clone's directory tree is built by
    hand instead, with a wrapped ({"jobs": [...]}) payload sitting where the real
    listings.json would be. fetch() then runs its real file-existence check, its
    real json.loads, and its real isinstance guard against that file."""
    monkeypatch.setattr(simplify.subprocess, "run", lambda *a, **k: None)
    listings_dir = tmp_path / "New-Grad-Positions" / ".github" / "scripts"
    listings_dir.mkdir(parents=True)
    listings_path = listings_dir / "listings.json"
    listings_path.write_text(json.dumps({"jobs": []}))

    with pytest.raises(TypeError, match=re.escape(str(listings_path))):
        simplify.fetch(tmp_path)
