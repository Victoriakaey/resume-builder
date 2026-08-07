"""End-to-end over fake sources: no network, no sheet."""
from __future__ import annotations
import datetime as dt, json, pathlib
from types import SimpleNamespace
from jobdiscovery import ats, discover, rolefile, sheets

NOW = dt.datetime(2026, 8, 6, 12, tzinfo=dt.timezone.utc)


def role(hours, title="AI Engineer", url="https://boards.greenhouse.io/acme/jobs/1", job_id="1",
         location="San Francisco, CA"):
    return ats.Role(company="Acme", title=title, location=location,
                    work_mode="Hybrid", url=url, job_id=job_id, ats="greenhouse",
                    token="acme", posted_at=NOW - dt.timedelta(hours=hours),
                    posted_kind="published", description="agent orchestration work",
                    source="greenhouse")


def test_a_run_writes_role_files_and_a_ledger(tmp_path):
    # role(30) is outside the 24h window. roles/ is the in-window set — a
    # verified-but-stale role gets no file, only a count in stale_verified (see
    # test_the_yield_is_exactly_the_files_in_roles_and_stale_verified_accounts_for_the_rest).
    # Only the fresh role produces a file here.
    result = discover.run(
        roles=[role(2), role(30, url="https://boards.greenhouse.io/acme/jobs/2", job_id="2")],
        tracker_rows=[], run_dir=tmp_path, now=NOW,
        source_results=[("greenhouse", 2, True, "")],
    )
    assert (tmp_path / "run.json").exists()
    files = sorted((tmp_path / "roles").glob("*.md"))
    assert len(files) == 1
    assert rolefile.parse(files[0]).fields["A"] == "Discovered"


def test_only_roles_inside_24h_are_reported(tmp_path):
    discover.run(roles=[role(2), role(30, url="https://x/2", job_id="2")],
                 tracker_rows=[], run_dir=tmp_path, now=NOW,
                 source_results=[("greenhouse", 2, True, "")])
    assert json.loads((tmp_path / "run.json").read_text())["yield_24h"] == 1


def test_roles_without_an_ats_timestamp_go_to_unverified_and_are_not_counted(tmp_path):
    unverifiable = ats.Role(company="Gamma", title="AI Engineer", location="San Francisco, CA",
                            work_mode="", url="https://gamma.com/careers/1", job_id="",
                            ats="", token="", posted_at=None, posted_kind="unknown",
                            description="", source="simplify")
    discover.run(roles=[role(2), unverifiable], tracker_rows=[], run_dir=tmp_path,
                 now=NOW, source_results=[("simplify", 1, True, "")])
    assert len(list((tmp_path / "unverified").glob("*.md"))) == 1
    assert len(list((tmp_path / "roles").glob("*.md"))) == 1
    assert json.loads((tmp_path / "run.json").read_text())["yield_24h"] == 1


def test_a_role_already_in_the_tracker_is_dropped_and_logged(tmp_path):
    row = {c: "" for c in [chr(x) for x in range(ord("A"), ord("R") + 1)]}
    row.update({"B": "https://boards.greenhouse.io/acme/jobs/1", "F": "Acme", "G": "AI Engineer"})
    # dedup.Index.from_rows reads the sheet row number off the row itself
    # (sheets.ROW_NUMBER); the brief's row literal predates that interface and
    # would KeyError without it.
    row[sheets.ROW_NUMBER] = 5
    discover.run(roles=[role(2)], tracker_rows=[row], run_dir=tmp_path, now=NOW,
                 source_results=[("greenhouse", 1, True, "")])
    data = json.loads((tmp_path / "run.json").read_text())
    assert len(list((tmp_path / "roles").glob("*.md"))) == 0
    assert data["dedup_drops"][0]["key"] == "url"


def test_the_yield_is_exactly_the_files_in_roles_and_stale_verified_accounts_for_the_rest(tmp_path):
    """run.json and roles/ are the same set by design. A run that reports a yield
    of N but leaves other verified roles' files on disk lets Step 2 and Step 3 act
    on postings the ledger never admitted — the precise failure this system exists
    to prevent. Two roles inside the window, one outside it: the yield and the
    file count must both be 2, and the one left out must be counted, not silent."""
    fresh_a = role(2)
    fresh_b = role(5, title="LLM Engineer", url="https://boards.greenhouse.io/acme/jobs/2",
                   job_id="2")
    stale = role(30, title="ML Platform Engineer", url="https://boards.greenhouse.io/acme/jobs/3",
                job_id="3")
    discover.run(roles=[fresh_a, fresh_b, stale], tracker_rows=[], run_dir=tmp_path, now=NOW,
                source_results=[("greenhouse", 3, True, "")])
    data = json.loads((tmp_path / "run.json").read_text())
    files = list((tmp_path / "roles").glob("*.md"))
    assert data["yield_24h"] == len(files) == 2
    assert data["stale_verified"] == 1


def test_two_roles_at_the_same_company_and_title_but_different_locations_each_get_a_file(tmp_path):
    """dedup's "review" action keeps both of these — same company and title, but
    different locations means they are not the same posting. Naming files from
    company and title alone (dropped in a prior version of this fix) collapsed
    them onto one file; the filename must be able to tell them apart."""
    here = role(2, location="San Francisco, CA")
    there = role(3, url="https://boards.greenhouse.io/acme/jobs/2", job_id="2",
                location="Palo Alto, CA")
    discover.run(roles=[here, there], tracker_rows=[], run_dir=tmp_path, now=NOW,
                source_results=[("greenhouse", 2, True, "")])
    assert len(list((tmp_path / "roles").glob("*.md"))) == 2


def test_a_second_run_into_the_same_directory_is_refused(tmp_path):
    """A rerun that overwrites some files and leaves others from the first run
    would leave run.json describing a directory that no longer matches it — the
    same lie by a different route. The directory is refused outright."""
    discover.run(roles=[role(2)], tracker_rows=[], run_dir=tmp_path, now=NOW,
                source_results=[("greenhouse", 1, True, "")])
    try:
        discover.run(roles=[role(2)], tracker_rows=[], run_dir=tmp_path, now=NOW,
                    source_results=[("greenhouse", 1, True, "")])
    except FileExistsError:
        pass
    else:
        raise AssertionError("a second run into an already-written directory must be refused")


def test_a_non_empty_run_dir_without_a_ledger_is_still_refused(tmp_path):
    """A run that crashed partway through writing role files never reached
    book.write(run_dir / "run.json") — a guard that only checks for run.json
    would wave the next run straight in, and the new ledger would then describe
    a disk that still has the crashed run's leftover files on it."""
    (tmp_path / "roles").mkdir()
    (tmp_path / "roles" / "leftover.md").write_text("stale from a crashed run")
    assert not (tmp_path / "run.json").exists()
    try:
        discover.run(roles=[role(2)], tracker_rows=[], run_dir=tmp_path, now=NOW,
                    source_results=[("greenhouse", 1, True, "")])
    except FileExistsError:
        pass
    else:
        raise AssertionError(
            "a non-empty run directory without a ledger must still be refused")


def test_a_malformed_companies_entry_is_one_failed_source_not_a_crash(tmp_path, monkeypatch):
    """_fetch_all's docstring promises isolation per source. Building the source's
    display name from entry['ats']/entry['token'] before the try turned a missing
    key into an uncaught KeyError that took the whole run down with it — the
    opposite of that promise."""
    from jobdiscovery import simplify
    monkeypatch.setattr(simplify, "fetch", lambda cache_dir: [])
    companies_path = tmp_path / "companies.yaml"
    companies_path.write_text("companies:\n  - name: Bad\n    ats: greenhouse\n    source: test\n")
    cfg = SimpleNamespace(companies_path=companies_path, runs_dir=tmp_path)
    book_sources = []
    roles = discover._fetch_all(cfg, book_sources)
    assert roles == []
    # The malformed entry plus simplify (stubbed to succeed with zero roles).
    assert len(book_sources) == 2
    name, count, ok, error = book_sources[0]
    assert name == "<malformed entry>"
    assert count == 0 and ok is False
    assert "KeyError" in error
