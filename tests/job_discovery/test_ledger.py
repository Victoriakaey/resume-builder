"""The ledger's job is to make a bad run legible, so its two most important
properties are that a broken source is not a zero-result source, and that
run.json has exactly one writer."""
from __future__ import annotations
import json
from jobdiscovery import ledger


def test_a_failed_source_is_distinguished_from_an_empty_one(tmp_path):
    book = ledger.RunLedger()
    book.record_source("greenhouse", roles=0, ok=True)
    book.record_source("ashby", roles=0, ok=False, error="HTTP 503")
    book.write(tmp_path / "run.json")
    by_name = {s["name"]: s for s in json.loads((tmp_path / "run.json").read_text())["per_source"]}
    assert by_name["greenhouse"]["status"] == "ok"
    assert by_name["ashby"]["status"] == "failed"
    assert by_name["ashby"]["error"] == "HTTP 503"


def test_sources_sharing_a_name_are_counted_separately(tmp_path):
    """Keyed by name, three malformed companies.yaml entries — which discover.py
    used to seed with one shared literal — plus a good source recorded as two,
    and run.json claimed the run consulted 2 sources when it consulted 4. A run
    that under-reports its own failures is the exact class this project exists to
    eliminate; finding it inside the ledger is worse than finding it anywhere
    else."""
    book = ledger.RunLedger()
    for _ in range(3):
        book.record_source("<malformed entry>", roles=0, ok=False, error="KeyError")
    book.record_source("greenhouse:one", roles=4, ok=True)
    book.write(tmp_path / "run.json")
    recorded = json.loads((tmp_path / "run.json").read_text())["per_source"]
    assert len(recorded) == 4
    assert sum(1 for s in recorded if s["status"] == "failed") == 3


def test_every_drop_names_its_key_and_row(tmp_path):
    book = ledger.RunLedger()
    book.record_drop(url="https://x/1", key="url", matched_row=42)
    book.write(tmp_path / "run.json")
    drop = json.loads((tmp_path / "run.json").read_text())["dedup_drops"][0]
    assert drop["key"] == "url" and drop["matched_row"] == 42


def test_the_yield_is_written_once_and_refuses_to_change(tmp_path):
    book = ledger.RunLedger()
    book.set_yield(3)
    try:
        book.set_yield(9)
    except ledger.YieldAlreadySet:
        pass
    else:
        raise AssertionError("the run's yield must not be rewritable")
    book.write(tmp_path / "run.json")
    assert json.loads((tmp_path / "run.json").read_text())["yield_24h"] == 3


def test_a_zero_yield_is_recorded_as_zero_not_omitted(tmp_path):
    book = ledger.RunLedger()
    book.set_yield(0)
    book.write(tmp_path / "run.json")
    assert json.loads((tmp_path / "run.json").read_text())["yield_24h"] == 0
