#!/usr/bin/env python3
"""Step 1 — find, verify, dedupe, and write one file per role.

run() is pure with respect to the network: it takes already-fetched roles, so the
whole pipeline is testable without touching Google or an ATS. main() is the thin
shell that does the fetching.
"""
from __future__ import annotations
import argparse, datetime as dt, pathlib, re, sys
from jobdiscovery import ats, dedup, filters, fitscore, freshness, ledger, rolefile

SLUG = re.compile(r"[^a-z0-9]+")


def _slug(*parts: str) -> str:
    return SLUG.sub("-", " ".join(parts).lower()).strip("-")[:80] or "role"


def run(*, roles, tracker_rows, run_dir, now, source_results) -> ledger.RunLedger:
    run_dir = pathlib.Path(run_dir)
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

    # Dedup runs over every verified, filtered role regardless of age — matching
    # against the tracker is freshness-independent, and a genuinely new opening
    # still deserves a file even if it is older than the window. The window only
    # decides what counts toward the reported yield, below.
    index = dedup.Index.from_rows(tracker_rows)
    verified_unique = []
    for role in verified:
        decision = index.check(role)
        if decision.action == "drop":
            book.record_drop(role.url, decision.key, decision.matched_row)
            continue
        if decision.action == "review":
            book.record_review(role.url, decision.matched_row,
                               "same company and title, different location")
        index.remember(role)
        verified_unique.append(role)

    # One window. The yield is set after dedup, because a role already in the
    # tracker is not something this run found. It is set once and cannot be
    # revised.
    book.set_yield(len(freshness.within_window(verified_unique, now)))

    for role in verified_unique:
        rolefile.write(
            run_dir / "roles" / f"{_slug(role.company, role.title)}.md", role,
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
            run_dir / "unverified" / f"{_slug(role.company, role.title)}.md", role,
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
