"""The one seam between this public repo and the adopter's private setup.

The module's own docstring says it never carries a default and fails loudly
rather than continuing with a guess. It did carry one, and it named a directory
inside the adopter's own private repo — shipped in the public one, and working
on exactly one machine.
"""
from __future__ import annotations
import inspect, pathlib, pytest
from jobdiscovery import config


def test_no_config_anywhere_fails_loudly_and_names_what_to_set(tmp_path, monkeypatch):
    monkeypatch.delenv("JOB_DISCOVERY_CONFIG", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="JOB_DISCOVERY_CONFIG"):
        config.load()


def test_the_environment_variable_is_honoured(tmp_path, monkeypatch):
    written = tmp_path / "elsewhere.yaml"
    written.write_text(
        "spreadsheet_id: sheet-id\ntab_name: Tab\nfirst_data_row: 5\nheader_rows: 4\n"
        f"webapp_credentials: {tmp_path}/creds.json\n"
        f"companies_path: {tmp_path}/companies.yaml\nruns_dir: {tmp_path}/runs\n"
    )
    monkeypatch.setenv("JOB_DISCOVERY_CONFIG", str(written))
    monkeypatch.setenv("HOME", str(tmp_path))
    assert config.load().spreadsheet_id == "sheet-id"


def test_the_fallback_is_a_conventional_per_user_path(tmp_path, monkeypatch):
    """Falling back is allowed; falling back into one named person's project
    directory is not."""
    monkeypatch.delenv("JOB_DISCOVERY_CONFIG", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    fallback = tmp_path / ".config" / "job-discovery" / "config.yaml"
    fallback.parent.mkdir(parents=True)
    fallback.write_text(
        "spreadsheet_id: from-fallback\ntab_name: Tab\nfirst_data_row: 5\nheader_rows: 4\n"
        f"webapp_credentials: {tmp_path}/creds.json\n"
        f"companies_path: {tmp_path}/companies.yaml\nruns_dir: {tmp_path}/runs\n"
    )
    assert config.load().spreadsheet_id == "from-fallback"


def test_the_module_ships_no_path_into_anyone_s_own_repo():
    """A pattern guard cannot catch this: scripts/personal-patterns.txt lives in
    this public repo, so listing the private directory names there would be the
    leak. Assert the shape instead — nothing under a home directory but the
    conventional ~/.config location."""
    source = inspect.getsource(config)
    homes = [line for line in source.splitlines()
             if '"~/' in line or "'~/" in line]
    assert homes == ['FALLBACK_CONFIG = "~/.config/job-discovery/config.yaml"'], homes
