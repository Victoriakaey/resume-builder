"""The four adversarial cases from the spec, plus the rule that nothing is ever
dropped without a recorded reason."""
from __future__ import annotations
import datetime as dt
import pytest
from jobdiscovery import ats, dedup


def role(url="https://boards.greenhouse.io/acme/jobs/1", company="Acme",
         title="AI Engineer", job_id="1", location="San Francisco, CA"):
    return ats.Role(company=company, title=title, location=location, work_mode="Hybrid",
                    url=url, job_id=job_id, ats="greenhouse", token="acme",
                    posted_at=dt.datetime(2026, 8, 6, tzinfo=dt.timezone.utc),
                    posted_kind="published", description="", source="greenhouse")


def row(url, company="Acme", title="AI Engineer", location="San Francisco, CA"):
    base = {c: "" for c in [chr(x) for x in range(ord("A"), ord("R") + 1)]}
    base.update({"B": url, "F": company, "G": title, "H": location})
    return base


@pytest.mark.parametrize("variant", [
    "https://boards.greenhouse.io/acme/jobs/1?gh_src=abc123",
    "https://boards.greenhouse.io/acme/jobs/1/",
    "https://job-boards.greenhouse.io/acme/jobs/1",
    "https://BOARDS.greenhouse.io/acme/jobs/1#apply",
])
def test_tracking_parameters_and_host_variants_are_the_same_role(variant):
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1")], 5)
    decision = index.check(role(url=variant))
    assert decision.action == "drop" and decision.key == "url"


def test_the_same_posting_seen_twice_in_one_run_is_dropped_the_second_time():
    index = dedup.Index.from_rows([], 5)
    assert index.check(role()).action == "new"
    index.remember(role())
    assert index.check(role()).action == "drop"


def test_a_repost_under_a_new_requisition_id_is_caught_by_company_and_title():
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1")], 5)
    decision = index.check(role(url="https://boards.greenhouse.io/acme/jobs/999", job_id="999"))
    assert decision.action == "drop" and decision.key == "company_title"


def test_two_real_openings_with_the_same_title_but_different_locations_are_reviewed_not_dropped():
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1",
                                       location="San Francisco, CA")], 5)
    decision = index.check(role(url="https://boards.greenhouse.io/acme/jobs/2",
                                job_id="2", location="Palo Alto, CA"))
    assert decision.action == "review"


def test_status_values_never_affect_the_decision():
    disliked = row("https://boards.greenhouse.io/acme/jobs/1")
    disliked["A"] = "dislike the role"
    index = dedup.Index.from_rows([disliked], 5)
    # A different role at the same company must still be new.
    assert index.check(role(url="https://boards.greenhouse.io/acme/jobs/7",
                            job_id="7", title="LLM Systems Engineer")).action == "new"


def test_every_non_new_decision_names_a_key_and_a_row():
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1")], 5)
    decision = index.check(role())
    assert decision.key and decision.matched_row is not None
