#!/usr/bin/env python3
"""Step 1 — find, verify, dedupe, and write one file per role.

run() is pure with respect to the network: it takes already-fetched roles, so the
whole pipeline is testable without touching Google or an ATS. main() is the thin
shell that does the fetching.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, pathlib, re, sys
from jobdiscovery import ats, dedup, filters, fitscore, freshness, ledger, rolefile

SLUG = re.compile(r"[^a-z0-9]+")


def _slug(role) -> str:
    """One file per posting, not per company-and-title.

    Two real openings at one company with the same title and different locations
    are exactly what dedup's "review" action exists to preserve — and naming the
    files from company and title alone collapsed them onto each other. A live run
    lost four of eight that way. The URL is what distinguishes a posting, so a
    short digest of it ends every name."""
    stem = SLUG.sub("-", f"{role.company} {role.title}".lower()).strip("-")[:70] or "role"
    digest = hashlib.sha1(role.url.encode()).hexdigest()[:8]
    return f"{stem}-{digest}"


def run(*, roles, tracker_rows, run_dir, now, source_results) -> ledger.RunLedger:
    run_dir = pathlib.Path(run_dir)
    # Writing a second run into a directory that already holds one leaves files
    # the new run.json does not account for, which is the same lie by a different
    # route: the ledger would describe a run the disk does not match.
    if (run_dir / "run.json").exists():
        raise FileExistsError(
            f"{run_dir} already holds a run. Pass a different --run-id, or remove it."
        )
    book = ledger.RunLedger()
    for name, count, ok, error in source_results:
        book.record_source(name, count, ok, error)

    kept = []
    for role in roles:
        verdict = filters.verdict(role)
        if not verdict.keep:
            book.record_filtered(role.url, verdict.reason)
            continue
        kept.append(role)

    verified = [r for r in kept if r.posted_at is not None]
    unverified = [r for r in kept if r.posted_at is None]

    # One window. Everything outside it is simply not this run's business — but
    # the ledger says how many there were, so "yield 0" and "found nothing" stay
    # distinguishable.
    fresh = freshness.within_window(verified, now)
    book.stale_verified = len(verified) - len(fresh)

    index = dedup.Index.from_rows(tracker_rows)
    fresh_unique = []
    for role in fresh:
        decision = index.check(role)
        if decision.action == "drop":
            book.record_drop(role.url, decision.key, decision.matched_row)
            continue
        if decision.action == "review":
            book.record_review(role.url, decision.matched_row,
                               "same company and title, different location")
        index.remember(role)
        fresh_unique.append(role)

    # The yield is set after dedup, because a role already in the tracker is not
    # something this run found. It is set once and cannot be revised.
    book.set_yield(len(fresh_unique))

    for role in fresh_unique:
        rolefile.write(
            run_dir / "roles" / f"{_slug(role)}.md", role,
            fit=fitscore.score(role), confidence=freshness.confidence(role),
            age_hours=freshness.age_hours(role, now), run_date=now.date(),
        )
    for role in unverified:
        decision = index.check(role)
        if decision.action == "drop":
            book.record_drop(role.url, decision.key, decision.matched_row)
            continue
        index.remember(role)
        book.record_unverified(role.url, role.company, role.title)
        rolefile.write(
            run_dir / "unverified" / f"{_slug(role)}.md", role,
            fit=fitscore.score(role), confidence="Low", age_hours=None, run_date=now.date(),
        )

    book.write(run_dir / "run.json")
    return book


def _fetch_all(cfg, book_sources: list) -> list:
    """Fetch every configured source, isolating failures per source."""
    import requests, yaml
    from jobdiscovery import simplify
    roles: list = []
    companies = (yaml.safe_load(cfg.companies_path.read_text()) or {}).get("companies", [])
    for entry in companies:
        name = f"{entry['ats']}:{entry['token']}"
        try:
            url = ats.ENDPOINTS[entry["ats"]].format(token=entry["token"])
            response = requests.get(url, timeout=30, headers={"User-Agent": "job-discovery/0.1"})
            response.raise_for_status()
            found = ats.parse_board(entry["ats"], entry["token"], entry["name"], response.json())
            roles.extend(found)
            book_sources.append((name, len(found), True, ""))
        except Exception as exc:                       # noqa: BLE001 — isolation is the point
            book_sources.append((name, 0, False, f"{type(exc).__name__}: {exc}"))
    try:
        listings = simplify.fetch(cfg.runs_dir / "_cache")
        found = simplify.to_roles(listings)
        roles.extend(found)
        book_sources.append(("simplify", len(found), True, ""))
    except Exception as exc:                           # noqa: BLE001
        book_sources.append(("simplify", 0, False, f"{type(exc).__name__}: {exc}"))
    return roles


def main(argv: list[str] | None = None) -> int:
    from jobdiscovery import config, sheets
    ap = argparse.ArgumentParser(description=__doc__)

    ap.add_argument("--run-id", default=None)
    args = ap.parse_args(argv)

    cfg = config.load()
    now = dt.datetime.now(dt.timezone.utc)
    run_id = args.run_id or now.strftime("%Y-%m-%dT%H%M%SZ")
    run_dir = cfg.runs_dir / run_id

    tracker_rows = sheets.TrackerClient(cfg).read_tracker()
    source_results: list = []
    roles = _fetch_all(cfg, source_results)
    book = run(roles=roles, tracker_rows=tracker_rows, run_dir=run_dir, now=now,
               source_results=source_results)

    print(f"run {run_id}", file=sys.stderr)
    print(f"  yield (ATS-verified, inside 24h, new): {book.yield_24h}", file=sys.stderr)
    print(f"  unverified (not counted): {len(book.unverified)}", file=sys.stderr)
    failed = [n for n, s in book.per_source.items() if s["status"] == "failed"]
    if failed:
        print(f"  FAILED sources: {', '.join(failed)}", file=sys.stderr)
    print(f"  role files: {run_dir / 'roles'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
