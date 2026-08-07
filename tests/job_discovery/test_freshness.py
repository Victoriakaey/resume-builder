"""Freshness is the rule the previous system broke silently, so it is tested
by behaviour, not by inspection."""
from __future__ import annotations
import datetime as dt
import pytest
from jobdiscovery import ats, freshness

NOW = dt.datetime(2026, 8, 6, 12, 0, tzinfo=dt.timezone.utc)


def role(hours_ago: float | None, kind: str = "published"):
    posted = None if hours_ago is None else NOW - dt.timedelta(hours=hours_ago)
    return ats.Role(company="C", title="AI Engineer", location="SF", work_mode="Hybrid",
                    url="https://x/1", job_id="1", ats="greenhouse", token="t",
                    posted_at=posted, posted_kind=kind if posted else "unknown",
                    description="", source="greenhouse")


def test_age_is_measured_from_the_ats_timestamp():
    assert freshness.age_hours(role(31), NOW) == pytest.approx(31.0)


def test_missing_timestamp_has_no_age():
    assert freshness.age_hours(role(None), NOW) is None


def test_confidence_high_only_for_an_unambiguous_publish_time():
    assert freshness.confidence(role(5, "published")) == "High"
    assert freshness.confidence(role(5, "updated")) == "Medium"
    assert freshness.confidence(role(None)) == "Low"


def test_the_window_is_twenty_four_hours_and_there_is_only_one():
    assert freshness.WINDOW_HOURS == 24
    assert not hasattr(freshness, "WINDOWS"), "the graded windows went with the target"
    assert not hasattr(freshness, "select"), "there is no target to select against"


def test_only_roles_inside_the_window_are_returned():
    roles = [role(3), role(23.9), role(24.1), role(30), role(60)]
    assert len(freshness.within_window(roles, NOW)) == 2


def test_a_role_with_no_timestamp_is_not_inside_the_window():
    assert freshness.within_window([role(None)], NOW) == []


def test_the_yield_is_the_count_and_zero_is_a_real_answer():
    assert freshness.yield_24h([role(30), role(60)], NOW) == 0
    assert freshness.yield_24h([role(3), role(10)], NOW) == 2
