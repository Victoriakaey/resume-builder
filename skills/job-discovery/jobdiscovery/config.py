#!/usr/bin/env python3
"""Locates the private configuration this skill needs and refuses to invent it.

The skill's code lives in a public repository; every value that identifies the
account holder or their spreadsheet lives outside it. This module is the single
seam between the two. It never carries a default spreadsheet id, and it fails
loudly rather than continuing with a guess.
"""
from __future__ import annotations
import dataclasses, os, pathlib
import yaml

DEFAULT_CONFIG = "~/Documents/resume/docs/job-discovery/config.yaml"


@dataclasses.dataclass(frozen=True)
class Config:
    spreadsheet_id: str
    tab_name: str
    first_data_row: int
    key_path: pathlib.Path
    companies_path: pathlib.Path
    runs_dir: pathlib.Path
    summary_range: str | None = None
    summary_cell: str | None = None


def load(path: str | None = None) -> Config:
    raw_path = pathlib.Path(
        os.path.expanduser(path or os.environ.get("JOB_DISCOVERY_CONFIG", DEFAULT_CONFIG))
    )
    if not raw_path.exists():
        raise FileNotFoundError(
            f"job-discovery config not found at {raw_path}. It lives in the private "
            "repo; see docs/plans/2026-08-06-job-discovery.md Task 1."
        )
    data = yaml.safe_load(raw_path.read_text()) or {}
    missing = [k for k in ("spreadsheet_id", "tab_name", "first_data_row",
                           "key_path", "companies_path", "runs_dir") if k not in data]
    if missing:
        raise ValueError(f"{raw_path} is missing required keys: {', '.join(missing)}")
    key = pathlib.Path(os.path.expanduser(os.environ.get("JOB_DISCOVERY_SA_KEY", data["key_path"])))
    return Config(
        spreadsheet_id=str(data["spreadsheet_id"]),
        tab_name=str(data["tab_name"]),
        first_data_row=int(data["first_data_row"]),
        key_path=key,
        companies_path=pathlib.Path(os.path.expanduser(data["companies_path"])),
        runs_dir=pathlib.Path(os.path.expanduser(data["runs_dir"])),
        summary_range=data.get("summary_range") or None,
        summary_cell=data.get("summary_cell") or None,
    )
