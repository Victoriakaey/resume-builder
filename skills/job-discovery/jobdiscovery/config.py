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

# No default into anyone's home directory: the previous one named the author's
# own private repo, which shipped a path to a machine nobody else has, and
# contradicted this module's docstring two lines above. The fallback is a
# conventional per-user location that says nothing about who the user is.
FALLBACK_CONFIG = "~/.config/job-discovery/config.yaml"


@dataclasses.dataclass(frozen=True)
class Config:
    spreadsheet_id: str
    tab_name: str
    first_data_row: int
    header_rows: int
    webapp_credentials: pathlib.Path
    companies_path: pathlib.Path
    runs_dir: pathlib.Path


def load(path: str | None = None) -> Config:
    raw_path = pathlib.Path(
        os.path.expanduser(path or os.environ.get("JOB_DISCOVERY_CONFIG")
                           or FALLBACK_CONFIG)
    )
    if not raw_path.exists():
        raise FileNotFoundError(
            f"job-discovery config not found at {raw_path}. Set JOB_DISCOVERY_CONFIG "
            f"to where yours lives, or put it at {FALLBACK_CONFIG}. It belongs in the "
            "user's own private configuration, outside this repo, with keys: "
            "spreadsheet_id, tab_name, first_data_row, header_rows, webapp_credentials, "
            "companies_path, runs_dir."
        )
    data = yaml.safe_load(raw_path.read_text()) or {}
    missing = [k for k in ("spreadsheet_id", "tab_name", "first_data_row", "header_rows",
                           "webapp_credentials", "companies_path", "runs_dir") if k not in data]
    if missing:
        raise ValueError(f"{raw_path} is missing required keys: {', '.join(missing)}")
    return Config(
        spreadsheet_id=str(data["spreadsheet_id"]),
        tab_name=str(data["tab_name"]),
        first_data_row=int(data["first_data_row"]),
        header_rows=int(data["header_rows"]),
        webapp_credentials=pathlib.Path(os.path.expanduser(data["webapp_credentials"])),
        companies_path=pathlib.Path(os.path.expanduser(data["companies_path"])),
        runs_dir=pathlib.Path(os.path.expanduser(data["runs_dir"])),
    )
