"""Deriving an ATS board token from an application URL."""
from __future__ import annotations
import pytest
from jobdiscovery import seed_companies as sc


@pytest.mark.parametrize("url,expected", [
    ("https://boards.greenhouse.io/acme/jobs/4012345", ("greenhouse", "acme")),
    ("https://job-boards.greenhouse.io/acme/jobs/4012345?gh_src=abc", ("greenhouse", "acme")),
    ("https://jobs.lever.co/beta-co/2f1c-uuid", ("lever", "beta-co")),
    ("https://jobs.ashbyhq.com/exampleco/9d0e-uuid/application", ("ashby", "exampleco")),
    ("https://example.com/careers/123", None),
    ("", None),
    # The ATS's own routing sitting where a company slug would. Reading "embed" as
    # a company merged three unrelated employers onto one board.
    ("https://boards.greenhouse.io/embed/job_app?token=4012345", None),
    ("https://boards.greenhouse.io/jobs/4012345", None),
])
def test_board_from_url(url, expected):
    assert sc.board_from_url(url) == expected


def test_entries_are_deduped_and_sorted():
    rows = [
        {"B": "https://boards.greenhouse.io/acme/jobs/1", "F": "Acme"},
        {"B": "https://boards.greenhouse.io/acme/jobs/2", "F": "Acme"},
        {"B": "https://jobs.lever.co/beta-co/x", "F": "Beta Co"},
    ]
    entries = sc.entries_from_rows(rows)
    assert entries == [
        {"name": "Acme", "ats": "greenhouse", "token": "acme", "source": "tracker"},
        {"name": "Beta Co", "ats": "lever", "token": "beta-co", "source": "tracker"},
    ]
