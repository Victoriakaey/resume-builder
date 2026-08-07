"""The file format between the three steps. A parse failure must be an error,
never a guess, and the eighteen-cell row must always be eighteen cells."""
from __future__ import annotations
import datetime as dt
import pytest
from jobdiscovery import ats, rolefile


def a_role():
    return ats.Role(company="Acme", title="AI Engineer", location="San Francisco, CA",
                    work_mode="Hybrid", url="https://boards.greenhouse.io/acme/jobs/1",
                    job_id="1", ats="greenhouse", token="acme",
                    posted_at=dt.datetime(2026, 8, 5, 6, tzinfo=dt.timezone.utc),
                    posted_kind="published", description="JD text", source="greenhouse")


def written(tmp_path):
    path = tmp_path / "acme-ai-engineer.md"
    rolefile.write(path, a_role(), fit=8, confidence="High", age_hours=30.0,
                   run_date=dt.date(2026, 8, 6))
    return path


def test_round_trip_preserves_the_facts(tmp_path):
    parsed = rolefile.parse(written(tmp_path))
    assert parsed.fields["F"] == "Acme"
    assert parsed.fields["K"] == "High"
    assert parsed.fields["M"] == "8"


def test_a_new_row_is_always_status_discovered(tmp_path):
    assert rolefile.parse(written(tmp_path)).fields["A"] == "Discovered"


def test_date_applied_and_follow_up_are_left_empty(tmp_path):
    parsed = rolefile.parse(written(tmp_path))
    assert parsed.fields["P"] == "" and parsed.fields["Q"] == ""


def test_the_row_has_exactly_eighteen_cells(tmp_path):
    assert len(rolefile.parse(written(tmp_path)).to_row()) == 18


def test_prose_sections_start_empty_and_are_reported(tmp_path):
    parsed = rolefile.parse(written(tmp_path))
    assert set(parsed.empty_sections()) == set(rolefile.PROSE_SECTIONS)


def test_the_jd_is_stored_so_step_two_never_refetches(tmp_path):
    assert "JD text" in rolefile.parse(written(tmp_path)).jd


def test_freshness_is_stated_in_words_a_human_reads(tmp_path):
    parsed = rolefile.parse(written(tmp_path))
    assert "30" in parsed.fields["J"] and "24h" in parsed.fields["J"]


def test_a_malformed_file_raises_rather_than_being_guessed_at(tmp_path):
    bad = tmp_path / "bad.md"
    bad.write_text("no front matter here\n")
    with pytest.raises(rolefile.MalformedRoleFile):
        rolefile.parse(bad)


def test_a_missing_required_field_raises(tmp_path):
    path = written(tmp_path)
    text = path.read_text().replace("company: Acme\n", "")
    path.write_text(text)
    with pytest.raises(rolefile.MalformedRoleFile):
        rolefile.parse(path)


def test_an_unknown_prose_section_raises(tmp_path):
    path = written(tmp_path)
    path.write_text(path.read_text() + "\n## invented_section\n\nhello\n")
    with pytest.raises(rolefile.MalformedRoleFile):
        rolefile.parse(path)
