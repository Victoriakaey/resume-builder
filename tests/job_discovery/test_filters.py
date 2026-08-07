from __future__ import annotations
import datetime as dt
import pytest
from jobdiscovery import ats, filters


def role(title="AI Engineer", location="San Francisco, CA", description=""):
    return ats.Role(company="C", title=title, location=location, work_mode="Hybrid",
                    url="https://x/1", job_id="1", ats="greenhouse", token="t",
                    posted_at=dt.datetime(2026, 8, 6, tzinfo=dt.timezone.utc),
                    posted_kind="published", description=description, source="greenhouse")


@pytest.mark.parametrize("title", [
    "AI Engineer", "LLM Systems Engineer", "Agent Infrastructure Engineer",
    "Applied AI Engineer", "Developer Tools Engineer", "Machine Learning Platform Engineer",
])
def test_target_titles_are_kept(title):
    assert filters.verdict(role(title=title)).keep


@pytest.mark.parametrize("title", [
    "Senior AI Engineer", "Staff LLM Engineer", "Principal Applied AI Engineer",
    "Engineering Manager, AI", "Director of AI",
])
def test_seniority_is_cut(title):
    v = filters.verdict(role(title=title))
    assert not v.keep and "seniority" in v.reason


def test_off_target_title_is_cut():
    v = filters.verdict(role(title="Sales Development Representative"))
    assert not v.keep and "title" in v.reason


@pytest.mark.parametrize("location", [
    "San Francisco, CA", "Palo Alto", "Mountain View, California",
    "Remote - US (CA eligible)", "South San Francisco",
])
def test_bay_area_and_ca_eligible_remote_are_kept(location):
    assert filters.verdict(role(location=location)).keep


@pytest.mark.parametrize("location", ["New York, NY", "London, UK", "Remote - EMEA"])
def test_out_of_area_is_cut(location):
    v = filters.verdict(role(location=location))
    assert not v.keep and "location" in v.reason


@pytest.mark.parametrize("location", [
    "Toronto, Canada",                       # ", ca" once matched ", Canada"
    "Vancouver, Canada",
    "Remote - Australia",                    # the "us" inside "Australia"
    "Remote (must relocate within 90 days)",  # the "us" inside "must"
])
def test_a_substring_of_another_word_is_not_a_location_match(location):
    v = filters.verdict(role(location=location))
    assert not v.keep and "location" in v.reason


@pytest.mark.parametrize("location", [
    "Remote, US", "Remote, USA", "Remote - USA", "Remote (USA only)",
    "Remote - U.S.", "Remote - United States", "Foster City, CA",
])
def test_the_tightened_rules_still_keep_what_they_should(location):
    """The boundary that cuts "Australia" must not also cut "USA" — a filter that
    quietly eats real postings fails invisibly, which is worse than one that lets
    a few through."""
    assert filters.verdict(role(location=location)).keep


def test_hard_years_requirement_above_four_is_cut():
    v = filters.verdict(role(description="We require 8+ years of production experience."))
    assert not v.keep and "years" in v.reason


def test_four_years_or_fewer_is_kept():
    assert filters.verdict(role(description="3+ years of experience preferred.")).keep


def test_clearance_is_cut():
    v = filters.verdict(role(description="Must hold an active TS/SCI security clearance."))
    assert not v.keep and "clearance" in v.reason


def test_ambiguity_is_kept_not_dropped():
    # No location signal at all: the spec says ambiguous cases pass through.
    assert filters.verdict(role(location="")).keep


@pytest.mark.parametrize("location", [
    "SF", "SF, CA", "San Francisco (SF)", "SF Bay Area", "Hybrid — SF office",
])
def test_sf_is_a_bay_location(location):
    """The most common Bay abbreviation on the discovery source. Two of twenty
    recorded listings were dropped as "location out of area: 'SF'"."""
    assert filters.verdict(role(location=location)).keep


@pytest.mark.parametrize("location", [
    "Sfax, Tunisia",                  # "sf" inside a city name
    "Berlin — Transformation Office",  # "sf" inside "transformation"
])
def test_sf_matches_on_a_word_boundary_not_as_a_substring(location):
    """BAY_TERMS is substring-matched, so a bare "sf" in that tuple would fire
    inside unrelated words. This is why it has a boundary of its own."""
    v = filters.verdict(role(location=location))
    assert not v.keep and "location" in v.reason


@pytest.mark.parametrize("location", [
    "Remote (US or Canada)", "Remote - Canada or United States", "Remote — USA/EMEA",
])
def test_a_remote_posting_the_us_half_makes_eligible_is_kept(location):
    """NON_CA_REMOTE was checked before CA_REMOTE, so a posting open to the US
    was cut for also naming somewhere else. Dropping a real posting is the worse
    of the two failures: a run that over-reports is visible, one that quietly
    under-reports is not."""
    assert filters.verdict(role(location=location)).keep


@pytest.mark.parametrize("location", ["Remote - Canada", "Remote (EMEA only)",
                                      "Remote — APAC", "Remote, India"])
def test_a_remote_posting_with_no_us_half_is_still_cut(location):
    """Re-ordering the two patterns must not turn the exclusion off."""
    v = filters.verdict(role(location=location))
    assert not v.keep and "location" in v.reason
