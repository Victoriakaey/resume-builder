from __future__ import annotations
import datetime as dt
from jobdiscovery import ats, fitscore


def role(title, description="", location="San Francisco, CA", work_mode="Hybrid"):
    return ats.Role(company="C", title=title, location=location, work_mode=work_mode,
                    url="https://x/1", job_id="1", ats="greenhouse", token="t",
                    posted_at=dt.datetime(2026, 8, 6, tzinfo=dt.timezone.utc),
                    posted_kind="published", description=description, source="greenhouse")


def test_the_location_point_follows_the_work_mode_not_the_location_text():
    """The real Lever posting: the board says hybrid, the location string says
    Remote. The point follows the board."""
    hybrid = role("AI Engineer", location="San Francisco, CA / Remote", work_mode="Hybrid")
    remote = role("AI Engineer", location="San Francisco, CA", work_mode="Remote")
    assert fitscore.explain(hybrid)["location"] == 1
    assert fitscore.explain(remote)["location"] == 0


def test_score_is_bounded():
    for r in [role("AI Engineer"), role("Sales Rep", "cold calling", "New York")]:
        assert 0 <= fitscore.score(r) <= 10


def test_priority_topics_score_above_a_bare_title_match():
    bare = fitscore.score(role("AI Engineer"))
    rich = fitscore.score(role(
        "AI Engineer",
        "You will work on agent orchestration, LLM evaluation, retrieval and tool use.",
    ))
    assert rich > bare


def test_the_same_role_always_scores_the_same():
    r = role("LLM Systems Engineer", "evaluation harnesses and prompt optimisation")
    assert fitscore.score(r) == fitscore.score(r)


def test_explain_components_sum_to_the_score():
    r = role("Agent Infrastructure Engineer", "context engineering and retrieval")
    assert sum(fitscore.explain(r).values()) == fitscore.score(r)
