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


def collect(run_dir, include_unverified: bool = False) -> tuple[list, list[dict]]:
    """Parse every role file, and refuse only the ones that are actually broken.

    A file the parser rejects is one role that cannot be appended, not a run that
    cannot proceed. Letting MalformedRoleFile escape here would mean a single
    hand-edit — a blank fact, a repeated heading — silently costs every other role
    in the run its turn.
    """
    run_dir = pathlib.Path(run_dir)
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
    re-doing that bookkeeping. Note this does not dedupe two role files in the
    same run against each other — `seen` is built once from `tracker_rows` and
    never grows as `to_append` does, so two role files sharing a canonical URL
    in the same run both pass and both get appended. Deliberately left as-is
    rather than fixed here: Step 1 already dedupes by URL before writing role
    files, so this path is not expected to fire in practice, and closing it
    blind is a decision for whoever reviews this, not a silent addition.
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
        if dedup.canonical_url(entry.fields.get("B", "")) in seen:
            skipped.append({"file": str(entry.path), "reason": "already in the sheet"})
            continue
        # "Empty" means Step 2 never touched this role at all: every prose
        # section is still exactly as Step 1 left it. A role Step 2 wrote
        # something for — even only one section — is reviewed, not blank; a
        # role file where every one of the five is untouched is the one that
        # would land as a wholly blank prose row.
        empty = entry.empty_sections()
        if len(empty) == len(rolefile.PROSE_SECTIONS):
            skipped.append({"file": str(entry.path),
                            "reason": f"empty prose section(s): {', '.join(empty)}"})
            continue
        to_append.append(entry)
    return to_append, skipped


def write_rows(client, role_files) -> int:
    """Append every role in one call, then mark each file done.

    All rows travel together so a run's yield lands in the sheet as one
    contiguous block rather than interleaved with whatever else appends between
    calls. Markers are written only once the call returns without raising, so a
    raised exception here leaves every entry unmarked and re-runnable — the
    live-URL check in `plan()` is what actually protects a re-run in that case,
    since the tracker will already show whichever rows the API call got to
    before it failed. `append_rows` returning a *count lower than len(rows)*
    without raising is a different, unhandled case: every entry here still gets
    a marker regardless of what `written` says, so a silent partial write on the
    endpoint's side would mark a role "appended" that never actually landed.
    """
    if not role_files:
        return 0
    written = client.append_rows([entry.to_row() for entry in role_files])
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
