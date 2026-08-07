#!/usr/bin/env python3
"""One-off: derive the initial company list from roles already in the tracker.

The three ATS feeds are per-employer, not a search engine, so the system cannot
find anything until it knows which boards to ask. Every role already in the
tracker carries its application URL, and those URLs name both the ATS and the
board token. This turns history into the seed list. Companies that apply through
their own site produce no token and are skipped — they are added by hand.
"""
from __future__ import annotations
import argparse, pathlib, re, sys
from urllib.parse import urlsplit
import yaml

PATTERNS = [
    ("greenhouse", re.compile(r"^(?:job-)?boards\.greenhouse\.io$"), 1),
    ("lever", re.compile(r"^jobs\.lever\.co$"), 1),
    ("ashby", re.compile(r"^jobs\.ashbyhq\.com$"), 1),
]


# Path segments that sit where a company slug would but are part of the ATS's own
# routing. `boards.greenhouse.io/embed/job_app?token=...` is the live one: 51 URLs
# in the SimplifyJobs listings take that shape, and reading "embed" as the company
# collapsed Chewy, Squarepoint and Cerebras onto a single bogus board. Returning
# None costs one unresolvable lead; guessing costs a dedup key that merges
# unrelated employers. Applied across all three ATS hosts, not just Greenhouse
# where the evidence was found — a company whose slug is literally "jobs" is a
# lead we would rather lose than a collision we would rather not debug.
NON_TOKENS = {"embed", "job_app", "jobs", "job"}


def board_from_url(url: str) -> tuple[str, str] | None:
    if not url:
        return None
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    segments = [s for s in parts.path.split("/") if s]
    for ats, host_re, index in PATTERNS:
        if host_re.match(host) and len(segments) >= index:
            token = segments[index - 1].lower()
            return None if token in NON_TOKENS else (ats, token)
    return None


# Where each ATS puts the posting's own id in the URL path, counted in segments
# after the host: Greenhouse is /<token>/jobs/<id>, Ashby and Lever are
# /<token>/<uuid> with an optional /apply or /application on the end.
ID_INDEX = {"greenhouse": 2, "ashby": 1, "lever": 1}
APPLY_SEGMENTS = {"apply", "application"}


def job_id_from_url(url: str) -> str:
    """The ATS's own id for a posting, read out of its URL.

    SimplifyJobs gives every listing an id of its own that shares nothing with
    the ATS id the board API reports, so the same posting seen through both
    sources produced two ats_id keys that could never match each other. Reading
    the id off the URL gives both sources the same one.

    An id this cannot resolve comes back empty, and dedup's "no id, no key" rule
    then leaves the composite alone — which is correct, because a guessed id is
    a dedup key that merges unrelated postings.
    """
    board = board_from_url(url)
    if board is None:
        return ""
    ats, _ = board
    segments = [s for s in urlsplit(url.strip()).path.split("/") if s]
    while segments and segments[-1].lower() in APPLY_SEGMENTS:
        segments.pop()
    index = ID_INDEX[ats]
    return segments[index] if len(segments) > index else ""


def entries_from_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        board = board_from_url(row.get("B", ""))
        if board is None:
            continue
        ats, token = board
        seen.setdefault((ats, token), {
            "name": row.get("F", "").strip() or token,
            "ats": ats, "token": token, "source": "tracker",
        })
    return [seen[k] for k in sorted(seen)]


def main(argv: list[str] | None = None) -> int:
    from jobdiscovery import config, sheets
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="where to write companies.yaml (default: config's companies_path)")
    args = ap.parse_args(argv)
    cfg = config.load()
    rows = sheets.TrackerClient(cfg).read_tracker()
    entries = entries_from_rows(rows)
    out = pathlib.Path(args.out) if args.out else cfg.companies_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump({"companies": entries}, sort_keys=False, allow_unicode=True))
    print(f"{len(entries)} companies written to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
