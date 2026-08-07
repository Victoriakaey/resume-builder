#!/usr/bin/env python3
"""The SimplifyJobs New-Grad-Positions repo as a discovery source.

Discovery and verification are separate jobs here. This source suggests roles; it
never establishes when one was posted, so every role it produces carries
posted_at=None. That is the whole of its standing in the pipeline: freshness
excludes it from the window, it is never counted toward a run's yield, and its
file is written under unverified/ rather than roles/, where Step 3 reaches it
only with --include-unverified.

There is no ATS verification gate. Nothing re-probes a lead's board, and this
docstring used to claim otherwise. Where a listing points at a known ATS the
board token and the ATS's own job id are read out of the URL — not so a gate can
run, but so dedup can recognise the same posting arriving from the board API,
and so a human can add the board to companies.yaml if they want it verified.
"""
from __future__ import annotations
import json, pathlib, subprocess
from jobdiscovery import ats
from jobdiscovery.seed_companies import board_from_url, job_id_from_url

REPO = "https://github.com/SimplifyJobs/New-Grad-Positions.git"
# Confirmed against a fresh clone (2026-08-07): the repo still keeps its
# machine-readable listings exactly where the brief guessed.
LISTINGS_PATH = ".github/scripts/listings.json"


def fetch(cache_dir: pathlib.Path) -> list[dict]:
    cache_dir = pathlib.Path(cache_dir)
    clone = cache_dir / "New-Grad-Positions"
    if clone.exists():
        subprocess.run(["git", "-C", str(clone), "pull", "--ff-only", "--quiet"], check=True)
    else:
        cache_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", "--quiet", REPO, str(clone)], check=True)
    listings = clone / LISTINGS_PATH
    if not listings.exists():
        raise FileNotFoundError(
            f"{listings} not found — the repo moved its machine-readable listings. "
            "Re-locate it and update LISTINGS_PATH."
        )
    data = json.loads(listings.read_text())
    # A file that is still there but no longer a bare array — wrapped as
    # {"jobs": [...]}, say — would otherwise reach to_roles, which would iterate
    # the dict's keys and fail on a string with no .get(). Refuse here, where the
    # message can name the file that changed shape.
    if not isinstance(data, list):
        raise TypeError(
            f"{listings} is a {type(data).__name__}, not a list of listings — the "
            "repo changed the file's shape. Re-read it and update fetch()."
        )
    return data


# `active` and `is_visible` are deliberately not read, and this is the note that
# keeps that from being re-litigated as an oversight. Both fields are present on
# every listing, and the whole-branch review is right that a false `active` looks
# like a closed posting being served as a lead. But over the recorded fixture the
# two flags do not partition cleanly by who contributed the row: 15 of the 16
# active=False/is_visible=True rows come from "Simplify" and all 4 of the
# active=True/is_visible=False rows come from a bot contributor, but one more
# bot-contributed row also sits at active=False/is_visible=True alongside the
# Simplify rows. So filtering on `active` would drop most of the file (including
# nearly all of what the Simplify source itself published), filtering on
# `is_visible` would drop the rest, and filtering on both would leave nothing at
# all. That is not what a single authoritative "this posting is open" flag looks
# like.
#
# Guessing which reading is right is exactly the move the rest of this system
# refuses to make (ats.py never falls back to "now"; _work_mode never coerces an
# unrecognised value). Settle it by reading the repo's own writer for these
# fields, not by picking the flag that leaves a comfortable number of leads.
def to_roles(listings: list[dict]) -> list[ats.Role]:
    roles: list[ats.Role] = []
    for item in listings:
        url = str(item.get("url") or "")
        board = board_from_url(url)
        ats_name, token = board if board else ("", "")
        locations = item.get("locations") or []
        roles.append(ats.Role(
            company=str(item.get("company_name") or ""),
            title=str(item.get("title") or ""),
            location=(", ".join(str(place) for place in locations)
                      if isinstance(locations, list) else str(locations)),
            # The ATS's id, read off the URL — never the listing's own
            # SimplifyJobs UUID, which no board API will ever report and which
            # therefore guaranteed the ats_id dedup key could not match.
            work_mode="", url=url, job_id=job_id_from_url(url),
            ats=ats_name, token=token,
            posted_at=None, posted_kind="unknown",
            description="", source="simplify",
        ))
    return roles
