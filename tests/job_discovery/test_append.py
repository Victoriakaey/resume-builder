"""Step 3's two locks, and the rule that a run's rows go in one call."""
from __future__ import annotations
import datetime as dt
import pytest
from jobdiscovery import append, ats, rolefile


def a_role(job_id="1", url="https://boards.greenhouse.io/acme/jobs/1"):
    return ats.Role(company="Acme", title="AI Engineer", location="San Francisco, CA",
                    work_mode="Hybrid", url=url, job_id=job_id, ats="greenhouse",
                    token="acme", posted_at=dt.datetime(2026, 8, 5, tzinfo=dt.timezone.utc),
                    posted_kind="published", description="JD", source="greenhouse")


def a_run(tmp_path, prose=True, marker=False):
    path = tmp_path / "roles" / "acme-ai-engineer.md"
    rolefile.write(path, a_role(), fit=8, confidence="High", age_hours=30.0,
                   run_date=dt.date(2026, 8, 6))
    if prose:
        text = path.read_text()
        for name in append.REQUIRED_SECTIONS:
            text = text.replace(f"## {name}\n\n", f"## {name}\n\nreviewed {name}\n")
        path.write_text(text)
    if marker:
        path.with_suffix(".md.appended").write_text("2026-08-06\n")
    return tmp_path


def test_a_role_already_marked_appended_is_skipped(tmp_path):
    to_append, skipped = append.plan(append.collect(a_run(tmp_path, marker=True)), [])
    assert to_append == [] and skipped[0]["reason"] == "already appended"


def test_a_role_whose_url_is_already_in_the_sheet_is_skipped(tmp_path):
    row = {c: "" for c in [chr(x) for x in range(ord("A"), ord("R") + 1)]}
    row["B"] = "https://boards.greenhouse.io/acme/jobs/1?gh_src=x"
    to_append, skipped = append.plan(append.collect(a_run(tmp_path)), [row])
    assert to_append == [] and skipped[0]["reason"] == "already in the sheet"


def test_a_role_with_empty_prose_is_skipped_rather_than_appended_blank(tmp_path):
    to_append, skipped = append.plan(append.collect(a_run(tmp_path, prose=False)), [])
    assert to_append == []
    assert "empty" in skipped[0]["reason"]


def test_a_reviewed_role_is_appended_as_eighteen_cells(tmp_path):
    to_append, skipped = append.plan(append.collect(a_run(tmp_path)), [])
    assert skipped == []
    assert len(to_append[0].to_row()) == 18


def test_all_rows_go_in_a_single_call(tmp_path, monkeypatch):
    calls = []

    class FakeClient:
        def append_rows(self, rows):
            calls.append(rows); return len(rows)

    run_dir = a_run(tmp_path)
    rolefile.write(run_dir / "roles" / "acme-llm-systems-engineer.md",
                   a_role(job_id="2", url="https://boards.greenhouse.io/acme/jobs/2"),
                   fit=7, confidence="High", age_hours=10.0, run_date=dt.date(2026, 8, 6))
    second = run_dir / "roles" / "acme-llm-systems-engineer.md"
    text = second.read_text()
    for name in append.REQUIRED_SECTIONS:
        text = text.replace(f"## {name}\n\n", f"## {name}\n\nreviewed {name}\n")
    second.write_text(text)
    to_append, _ = append.plan(append.collect(run_dir), [])
    append.write_rows(FakeClient(), to_append)
    assert len(calls) == 1 and len(calls[0]) == 2


def test_markers_are_written_only_after_a_successful_write(tmp_path):
    class FailingClient:
        def append_rows(self, rows):
            raise RuntimeError("HTTP 500")

    run_dir = a_run(tmp_path)
    to_append, _ = append.plan(append.collect(run_dir), [])
    with pytest.raises(RuntimeError):
        append.write_rows(FailingClient(), to_append)
    assert not (run_dir / "roles" / "acme-ai-engineer.md.appended").exists()


def test_a_role_with_only_notes_empty_is_still_appended(tmp_path):
    """notes is optional — pins the rule itself, not just REQUIRED_SECTIONS' contents."""
    run_dir = a_run(tmp_path)
    to_append, skipped = append.plan(append.collect(run_dir), [])
    assert skipped == []
    assert to_append[0].sections["notes"].strip() == ""
    for name in append.REQUIRED_SECTIONS:
        assert to_append[0].sections[name].strip()


def test_a_role_missing_one_required_section_is_skipped_by_name(tmp_path):
    run_dir = a_run(tmp_path)
    path = run_dir / "roles" / "acme-ai-engineer.md"
    text = path.read_text().replace(
        "## why_it_fits\n\nreviewed why_it_fits\n", "## why_it_fits\n\n\n")
    path.write_text(text)
    to_append, skipped = append.plan(append.collect(run_dir), [])
    assert to_append == []
    assert "why_it_fits" in skipped[0]["reason"]


def test_a_short_write_raises_partial_append_and_marks_nothing(tmp_path):
    class ShortClient:
        def append_rows(self, rows):
            return len(rows) - 1

    run_dir = a_run(tmp_path)
    to_append, _ = append.plan(append.collect(run_dir), [])
    with pytest.raises(append.PartialAppend):
        append.write_rows(ShortClient(), to_append)
    assert not (run_dir / "roles" / "acme-ai-engineer.md.appended").exists()


def test_a_malformed_file_is_skipped_by_name_while_the_good_one_still_appends(tmp_path):
    run_dir = a_run(tmp_path)
    broken = run_dir / "roles" / "acme-broken-role.md"
    broken.write_text("not a role file at all")
    to_append, skipped = append.plan(append.collect(run_dir), [])
    assert len(to_append) == 1 and to_append[0].path.name == "acme-ai-engineer.md"
    assert any(entry["file"].endswith("acme-broken-role.md") for entry in skipped)


def test_two_role_files_sharing_a_canonical_url_append_once_and_skip_the_second(tmp_path):
    run_dir = a_run(tmp_path)
    # Sorted after "acme-ai-engineer.md" (collect() walks the directory in sorted
    # order), so the original from a_run() is the one that appends and this one
    # is the "second" the rule is meant to catch — not an artifact of glob order.
    dupe_path = run_dir / "roles" / "acme-dupe-posting.md"
    rolefile.write(dupe_path,
                   a_role(job_id="1", url="https://boards.greenhouse.io/acme/jobs/1?gh_src=y"),
                   fit=8, confidence="High", age_hours=30.0, run_date=dt.date(2026, 8, 6))
    text = dupe_path.read_text()
    for name in append.REQUIRED_SECTIONS:
        text = text.replace(f"## {name}\n\n", f"## {name}\n\nreviewed {name}\n")
    dupe_path.write_text(text)
    to_append, skipped = append.plan(append.collect(run_dir), [])
    assert len(to_append) == 1 and to_append[0].path.name == "acme-ai-engineer.md"
    assert any(entry["file"].endswith("acme-dupe-posting.md") and
               entry["reason"] == "already in the sheet" for entry in skipped)


def test_a_run_id_naming_a_missing_directory_raises_rather_than_reports_zero(tmp_path):
    with pytest.raises(FileNotFoundError):
        append.collect(tmp_path / "no-such-run")
