"""End-to-end over fake sources: no network, no sheet."""
from __future__ import annotations
import datetime as dt, json, pathlib
from jobdiscovery import ats, discover, rolefile, sheets

NOW = dt.datetime(2026, 8, 6, 12, tzinfo=dt.timezone.utc)


def role(hours, title="AI Engineer", url="https://boards.greenhouse.io/acme/jobs/1", job_id="1"):
    return ats.Role(company="Acme", title=title, location="San Francisco, CA",
                    work_mode="Hybrid", url=url, job_id=job_id, ats="greenhouse",
                    token="acme", posted_at=NOW - dt.timedelta(hours=hours),
                    posted_kind="published", description="agent orchestration work",
                    source="greenhouse")


def test_a_run_writes_role_files_and_a_ledger(tmp_path):
    # The second role needs its own title, not just its own url/job_id — same
    # company + title + location is what dedup treats as the same posting
    # reposted, and the brief's original fixture (identical title and location)
    # collided under that rule, collapsing 2 roles to 1 survivor.
    result = discover.run(
        roles=[role(2), role(30, title="LLM Engineer",
                    url="https://boards.greenhouse.io/acme/jobs/2", job_id="2")],
        tracker_rows=[], run_dir=tmp_path, now=NOW,
        source_results=[("greenhouse", 2, True, "")],
    )
    assert (tmp_path / "run.json").exists()
    files = sorted((tmp_path / "roles").glob("*.md"))
    assert len(files) == 2
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
