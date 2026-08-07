#!/usr/bin/env python3
"""The SimplifyJobs New-Grad-Positions repo as a discovery source.

Discovery and verification are separate jobs here. This source suggests roles;
it never establishes when one was posted, so everything it produces carries no
timestamp and reaches the ATS verification gate like any other lead. Where its
listing points at a known ATS, the board token is extracted so that gate can
actually run.
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
