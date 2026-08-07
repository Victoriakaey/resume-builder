"""The four adversarial cases from the spec, plus the rule that nothing is ever
dropped without a recorded reason."""
from __future__ import annotations
import datetime as dt
import pytest
from jobdiscovery import ats, dedup, sheets


def role(url="https://boards.greenhouse.io/acme/jobs/1", company="Acme",
         title="AI Engineer", job_id="1", location="San Francisco, CA"):
    return ats.Role(company=company, title=title, location=location, work_mode="Hybrid",
                    url=url, job_id=job_id, ats="greenhouse", token="acme",
                    posted_at=dt.datetime(2026, 8, 6, tzinfo=dt.timezone.utc),
                    posted_kind="published", description="", source="greenhouse")


def row(url, company="Acme", title="AI Engineer", location="San Francisco, CA",
        row_number=5, requisition=""):
    base = {c: "" for c in [chr(x) for x in range(ord("A"), ord("R") + 1)]}
    base.update({"B": url, "F": company, "G": title, "H": location, "L": requisition})
    base[sheets.ROW_NUMBER] = row_number
    return base


def test_the_matched_row_is_the_sheet_row_not_a_count():
    """A blank row above the match used to push every row number below it out by
    one. The row carries its own number now, so a gap changes nothing."""
    index = dedup.Index.from_rows([
        row("https://boards.greenhouse.io/acme/jobs/1", row_number=5),
        row("https://boards.greenhouse.io/acme/jobs/2", title="LLM Engineer", row_number=9),
    ])
    assert index.check(role(url="https://boards.greenhouse.io/acme/jobs/2",
                            job_id="2", title="LLM Engineer")).matched_row == 9


def test_a_requisition_id_in_column_l_is_a_dedup_key():
    index = dedup.Index.from_rows([
        row("https://elsewhere.example/1", title="Something Else",
            requisition="greenhouse:acme:1", row_number=7),
    ])
    decision = index.check(role(url="https://boards.greenhouse.io/acme/jobs/1"))
    assert decision.action == "drop" and decision.key == "ats_id"
    assert decision.matched_row == 7


def test_a_bare_requisition_id_is_also_a_dedup_key():
    """Column L holds whatever the tracker's author typed. A raw id matches on its
    own, which is a different branch from the ats:token:id composite above."""
    index = dedup.Index.from_rows([
        row("https://elsewhere.example/1", title="Something Else",
            requisition="12345", row_number=11),
    ])
    decision = index.check(role(url="https://boards.greenhouse.io/acme/jobs/12345",
                                job_id="12345", title="Something Else Entirely"))
    assert decision.action == "drop" and decision.key == "ats_id"
    assert decision.matched_row == 11


def test_two_id_less_postings_at_one_company_are_not_the_same_role():
    """An unresolved job_id collapses the composite key to "ats:token:", which every
    id-less posting at that company would share. Dropping the second one would lose
    a real opening — the failure this module exists to prevent."""
    index = dedup.Index.from_rows([])
    first = role(url="https://boards.greenhouse.io/acme/jobs/a", job_id="", title="Role One")
    second = role(url="https://boards.greenhouse.io/acme/jobs/b", job_id="", title="Role Two")
    assert index.check(first).action == "new"
    index.remember(first)
    assert index.check(second).action == "new"


@pytest.mark.parametrize("variant", [
    "https://boards.greenhouse.io/acme/jobs/1?gh_src=abc123",
    "https://boards.greenhouse.io/acme/jobs/1/",
    "https://job-boards.greenhouse.io/acme/jobs/1",
    "https://BOARDS.greenhouse.io/acme/jobs/1#apply",
])
def test_tracking_parameters_and_host_variants_are_the_same_role(variant):
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1")])
    decision = index.check(role(url=variant))
    assert decision.action == "drop" and decision.key == "url"


def test_the_same_posting_seen_twice_in_one_run_is_dropped_the_second_time():
    index = dedup.Index.from_rows([])
    assert index.check(role()).action == "new"
    index.remember(role())
    assert index.check(role()).action == "drop"


def test_a_repost_under_a_new_requisition_id_is_caught_by_company_and_title():
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1")])
    decision = index.check(role(url="https://boards.greenhouse.io/acme/jobs/999", job_id="999"))
    assert decision.action == "drop" and decision.key == "company_title"


def test_two_real_openings_with_the_same_title_but_different_locations_are_reviewed_not_dropped():
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1",
                                       location="San Francisco, CA")])
    decision = index.check(role(url="https://boards.greenhouse.io/acme/jobs/2",
                                job_id="2", location="Palo Alto, CA"))
    assert decision.action == "review"


def test_status_values_never_affect_the_decision():
    disliked = row("https://boards.greenhouse.io/acme/jobs/1")
    disliked["A"] = "dislike the role"
    index = dedup.Index.from_rows([disliked])
    # A different role at the same company must still be new.
    assert index.check(role(url="https://boards.greenhouse.io/acme/jobs/7",
                            job_id="7", title="LLM Systems Engineer")).action == "new"


def test_every_non_new_decision_names_a_key_and_a_row():
    index = dedup.Index.from_rows([row("https://boards.greenhouse.io/acme/jobs/1")])
    decision = index.check(role())
    assert decision.key and decision.matched_row is not None
