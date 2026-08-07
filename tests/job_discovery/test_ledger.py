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
    data = json.loads((tmp_path / "run.json").read_text())
    assert data["per_source"]["greenhouse"]["status"] == "ok"
    assert data["per_source"]["ashby"]["status"] == "failed"
    assert data["per_source"]["ashby"]["error"] == "HTTP 503"


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
