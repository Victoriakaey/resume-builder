"""SimplifyJobs is a discovery source only: it must never assert freshness."""
from __future__ import annotations
import json, pathlib, pytest
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
