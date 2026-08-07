#!/usr/bin/env python3
"""Step 3 — append reviewed rows to the tracker.

Two independent locks stop a re-run from writing a row twice: a marker file next
to each role file, and a check of the role's canonical URL against the sheet as
it is right now. Markers are written only after the API call succeeds, so a
failed write leaves the run exactly as re-runnable as it was.
"""
from __future__ import annotations
import argparse, datetime as dt, pathlib, sys
from jobdiscovery import dedup, rolefile

MARKER_SUFFIX = ".appended"

# notes is genuinely optional — a role with nothing worth noting should not be held
# back, and a model padding it to pass a check is worse than a blank cell. The other
# four are the review itself; a row missing one of them is half-written, and a
# half-written role in the sheet is worse than one that waits a round.
REQUIRED_SECTIONS = ("cover_letter", "why_interested", "why_it_fits", "resume_tailoring")


def collect(run_dir, include_unverified: bool = False) -> tuple[list, list[dict]]:
    """Parse every role file, and refuse only the ones that are actually broken.

    A file the parser rejects is one role that cannot be appended, not a run that
    cannot proceed. Letting MalformedRoleFile escape here would mean a single
    hand-edit — a blank fact, a repeated heading — silently costs every other role
    in the run its turn.
    """
    run_dir = pathlib.Path(run_dir)
    # A typo in --run-id would otherwise report "0 rows would be appended", which
    # reads as "nothing to do" rather than "you named a run that does not exist".
    if not run_dir.is_dir():
        raise FileNotFoundError(f"no such run directory: {run_dir}")
    directories = [run_dir / "roles"] + ([run_dir / "unverified"] if include_unverified else [])
    parsed: list[rolefile.RoleFile] = []
    unreadable: list[dict] = []
    for directory in directories:
        for path in sorted(directory.glob("*.md")):
            try:
                parsed.append(rolefile.parse(path))
            except rolefile.MalformedRoleFile as exc:
                unreadable.append({"file": str(path), "reason": str(exc)})
    return parsed, unreadable


def plan(collected: tuple[list, list[dict]], tracker_rows) -> tuple[list, list[dict]]:
    """Decide which parsed roles are ready to append.

    Takes `collect()`'s own return value directly, so a file `rolefile.parse`
    refused is folded into the skip list here rather than by every caller
    re-doing that bookkeeping.
    """
    role_files, unreadable = collected
    seen = {dedup.canonical_url(row.get("B", "")) for row in tracker_rows}
    to_append: list = []
    skipped: list[dict] = list(unreadable)
    for entry in role_files:
        marker = entry.path.with_name(entry.path.name + MARKER_SUFFIX)
        if marker.exists():
            skipped.append({"file": str(entry.path), "reason": "already appended"})
            continue
        url = dedup.canonical_url(entry.fields.get("B", ""))
        if url in seen:
            skipped.append({"file": str(entry.path), "reason": "already in the sheet"})
            continue
        # notes is optional; the other four are the review itself, so only
        # those four gate the append. See REQUIRED_SECTIONS above for why.
        missing = [name for name in REQUIRED_SECTIONS
                   if not entry.sections.get(name, "").strip()]
        if missing:
            skipped.append({"file": str(entry.path),
                            "reason": f"empty prose section(s): {', '.join(missing)}"})
            continue
        to_append.append(entry)
        # Grow the seen-set as the batch grows. Two files in one run directory
        # pointing at the same posting would otherwise both pass every gate, both
        # land in the single append call, and both get a valid marker — so no
        # later run could ever detect the duplicate, let alone undo it. Step 1
        # dedupes within a run, but a hand-copied run directory does not.
        seen.add(url)
    return to_append, skipped


class PartialAppend(RuntimeError):
    """The endpoint reported writing fewer rows than were sent."""


def write_rows(client, role_files) -> int:
    """Append every role in one call, then mark each file done.

    All rows travel together so a run's yield lands in the sheet as one
    contiguous block rather than interleaved with whatever else appends between
    calls. Markers are written only once the call returns without raising, so a
    raised exception here leaves every entry unmarked and re-runnable — the
    live-URL check in `plan()` is what actually protects a re-run in that case,
    since the tracker will already show whichever rows the API call got to
    before it failed.

    A short write — `append_rows` returns without raising, but reports fewer
    rows than were sent — is a different case, and ambiguous on its own terms:
    the count says how many landed, never which. Marking every file appended
    would silently lose whichever one did not; marking none and letting a
    re-run happen would double-append whichever one did. Both are a guess made
    on the human's behalf about their own job applications, so neither marker
    is written — `PartialAppend` is raised instead, and reconciling against the
    sheet is left to a human who can actually see which rows landed.
    """
    if not role_files:
        return 0
    written = client.append_rows([entry.to_row() for entry in role_files])
    if written != len(role_files):
        raise PartialAppend(
            f"sent {len(role_files)} row(s), endpoint reported {written}. No file was "
            "marked appended. Reconcile against the sheet before running this again."
        )
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    for entry in role_files:
        entry.path.with_name(entry.path.name + MARKER_SUFFIX).write_text(stamp + "\n")
    return written


def main(argv: list[str] | None = None) -> int:
    from jobdiscovery import config, sheets
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-unverified", action="store_true")
    args = ap.parse_args(argv)

    cfg = config.load()
    run_dir = cfg.runs_dir / args.run_id
    client = sheets.TrackerClient(cfg)
    tracker_rows = client.read_tracker()
    to_append, skipped = plan(collect(run_dir, args.include_unverified), tracker_rows)

    for entry in skipped:
        print(f"skip  {pathlib.Path(entry['file']).name}: {entry['reason']}", file=sys.stderr)
    for entry in to_append:
        print(f"would append  {entry.fields['F']} — {entry.fields['G']}", file=sys.stderr)

    if args.dry_run:
        print(f"dry run: {len(to_append)} row(s) would be appended", file=sys.stderr)
        return 0
    written = write_rows(client, to_append)
    print(f"appended {written} row(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
