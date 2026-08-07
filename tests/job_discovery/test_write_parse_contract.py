"""Step 1 writes files Step 3 can read. Nothing else in this suite says so.

`rolefile.write` validated nothing while `rolefile.parse` is strict, so the two
could disagree — and they did. A Greenhouse posting with `location.name: null`
gave `Role.location == ""`, `write` emitted it, `run.json` counted it in
`yield_24h`, Step 2 wrote several hundred words of prose into it, and only then
did `append.collect` refuse it. The loss happened after the ledger was sealed,
nothing revised the ledger, and nothing counted it. The same mechanism killed the
entire `unverified/` directory at once: `simplify.to_roles` states no work mode,
so every SimplifyJobs lead was unreadable and `--include-unverified` was dead code.

145 tests missed all of it because every one of them built its `Role` by hand
with every field populated. So this file builds nothing by hand: the roles come
out of `ats.parse_board` and `simplify.to_roles` over the recorded fixtures, and
the assertion is the round trip through `discover.run` into `append.collect`.
"""
from __future__ import annotations
import copy, dataclasses, datetime as dt, json, pathlib
from jobdiscovery import append, ats, discover, fitscore, freshness, rolefile, simplify

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
NOW = dt.datetime(2026, 8, 6, 12, tzinfo=dt.timezone.utc)
BOARDS = (("greenhouse", "boardtwo", "Board Two"),
          ("ashby", "boardone", "Board One"),
          ("lever", "boardthree", "Board Three"))


def _payload(name: str):
    return json.loads((FIXTURES / f"{name}_board.json").read_text())


def _board_roles() -> list[ats.Role]:
    """Every posting the three recorded boards actually returned.

    Re-dated into the freshness window, and only that: the location, work mode,
    title and JD are whatever the board really said, which is the whole point.
    """
    roles = []
    for name, token, company in BOARDS:
        for role in ats.parse_board(name, token, company, _payload(name)):
            roles.append(dataclasses.replace(role, posted_at=NOW - dt.timedelta(hours=1)))
    return roles


def _simplify_roles() -> list[ats.Role]:
    return simplify.to_roles(json.loads((FIXTURES / "simplify_listings.json").read_text()))


def _lever_posting_with_no_location() -> ats.Role:
    """A real Lever posting whose location the board left null.

    Nulled in the payload rather than on the Role, so `ats.parse_board`'s own
    `str(... or "")` is what produces the empty string — the exact path that
    produced the unreadable files.
    """
    payload = copy.deepcopy(_payload("lever"))
    for posting in payload:
        posting["categories"]["location"] = None
        posting["categories"]["allLocations"] = None
    roles = ats.parse_board("lever", "boardthree", "Board Three", payload)
    kept = [r for r in roles if r.title == "Applied AI Software Engineer"]
    assert kept, "the Lever fixture no longer holds the posting this case is built on"
    return dataclasses.replace(kept[0], posted_at=NOW - dt.timedelta(hours=2),
                               url=kept[0].url + "-no-location", job_id=kept[0].job_id + "-nl")


def _write(tmp_path, role) -> pathlib.Path:
    return rolefile.write(
        tmp_path / "one.md", role, fit=fitscore.score(role),
        confidence=freshness.confidence(role),
        age_hours=freshness.age_hours(role, NOW), run_date=NOW.date())


def test_every_file_a_run_writes_can_be_read_back_by_step_three(tmp_path):
    """The invariant this file exists for. A file Step 1 writes and Step 3
    refuses is a role lost after the ledger already counted it."""
    roles = _board_roles() + _simplify_roles() + [_lever_posting_with_no_location()]
    discover.run(roles=roles, tracker_rows=[], run_dir=tmp_path, now=NOW,
                 source_results=[(name, 0, True, "") for name, _, _ in BOARDS])

    on_disk = sorted((tmp_path / "roles").glob("*.md")) + \
        sorted((tmp_path / "unverified").glob("*.md"))
    parsed, unreadable = append.collect(tmp_path, include_unverified=True)
    assert unreadable == [], f"Step 1 wrote files Step 3 cannot read: {unreadable}"
    assert len(parsed) == len(on_disk)
    # Both halves must be non-empty, or this passes by writing nothing.
    assert list((tmp_path / "roles").glob("*.md"))
    assert list((tmp_path / "unverified").glob("*.md"))


def test_a_run_reports_a_yield_step_three_can_actually_append(tmp_path):
    """run.json's yield and the readable files in roles/ are the same set. The
    old failure was a yield of N and fewer than N appendable files, with nothing
    recording the difference."""
    roles = _board_roles() + [_lever_posting_with_no_location()]
    book = discover.run(roles=roles, tracker_rows=[], run_dir=tmp_path, now=NOW,
                        source_results=[("lever", len(roles), True, "")])
    parsed, unreadable = append.collect(tmp_path)
    assert unreadable == []
    assert book.yield_24h == len(parsed) > 0


def test_a_location_the_board_left_null_is_written_as_unknown_not_blank(tmp_path):
    """Greenhouse states `location: {"name": null}`. `ats.parse_board` turns that
    into "", `parse` refuses a blank required fact, and the role used to die
    between the two."""
    payload = copy.deepcopy(_payload("greenhouse"))
    payload["jobs"][0]["location"]["name"] = None
    role = ats.parse_board("greenhouse", "boardtwo", "Board Two", payload)[0]
    assert role.location == "", "the null no longer reaches Role.location as an empty string"
    parsed = rolefile.parse(_write(tmp_path, dataclasses.replace(
        role, posted_at=NOW - dt.timedelta(hours=1))))
    assert parsed.fields["H"] == "unknown"


def test_every_simplify_lead_round_trips_although_no_work_mode_is_stated(tmp_path):
    """`simplify.to_roles` hardcodes work_mode="". That one blank made every file
    under unverified/ unreadable, which made --include-unverified dead code."""
    leads = _simplify_roles()
    assert leads and all(lead.work_mode == "" for lead in leads)
    for lead in leads:
        parsed = rolefile.parse(_write(tmp_path, lead))
        assert parsed.fields["I"] == "unknown"


def test_a_lead_with_no_jd_gets_unknown_in_the_fit_score_cell_not_a_number(tmp_path):
    """Measured over the recorded fixture, every surviving SimplifyJobs lead
    scored 0 while the one ATS-verified role scored 9 — including a Forward
    Deployed Engineer in SF, squarely on target. The 0 is not a low score, it is
    the absence of a JD to score. Sorting the tracker by Fit Score, the obvious
    use of that column, would bury every discovery lead as "worst fit"."""
    lead = next(r for r in _simplify_roles() if r.title == "Forward Deployed Engineer")
    assert lead.description == ""
    assert rolefile.parse(_write(tmp_path, lead)).fields["M"] == "unknown"


def test_a_role_that_does_carry_a_jd_still_gets_its_number(tmp_path):
    """The rule is "no signal, no number", not "no numbers"."""
    scored = next(r for r in _board_roles() if r.description.strip())
    parsed = rolefile.parse(_write(tmp_path, scored))
    assert parsed.fields["M"] == str(fitscore.score(scored))
    assert parsed.fields["M"] != "unknown"
