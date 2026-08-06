from __future__ import annotations
import json
from jobdiscovery import writing_ledger


def test_writing_json_is_separate_from_run_json(tmp_path):
    book = writing_ledger.WritingLedger()
    book.record("acme-ai-engineer", passes=2, tokens_in=8000, tokens_out=1200, residual="")
    book.write(tmp_path / "writing.json")
    assert (tmp_path / "writing.json").exists()
    assert not (tmp_path / "run.json").exists()


def test_totals_let_one_run_answer_the_cost_question(tmp_path):
    book = writing_ledger.WritingLedger()
    book.record("a", passes=4, tokens_in=10_000, tokens_out=1_500, residual="hedged opening")
    book.record("b", passes=1, tokens_in=6_000, tokens_out=900, residual="")
    book.write(tmp_path / "writing.json")
    data = json.loads((tmp_path / "writing.json").read_text())
    assert data["totals"]["roles"] == 2
    assert data["totals"]["tokens_in"] == 16_000
    assert data["totals"]["tokens_out"] == 2_400
    assert data["totals"]["passes"] == 5


def test_a_role_that_hit_the_cap_records_its_residual(tmp_path):
    book = writing_ledger.WritingLedger()
    book.record("a", passes=4, tokens_in=1, tokens_out=1, residual="cadence still even")
    book.write(tmp_path / "writing.json")
    entry = json.loads((tmp_path / "writing.json").read_text())["roles"]["a"]
    assert entry["hit_cap"] is True and entry["residual"] == "cadence still even"
