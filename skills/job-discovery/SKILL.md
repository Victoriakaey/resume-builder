---
name: job-discovery
description: Find fresh, ATS-verified SWE/AI roles, draft the per-role writing, and append them to a job tracker. Use when someone wants a recurring sweep for new roles rather than help with one application they already chose. Runs in three steps with a human review in the middle; never submits anything.
---

# job-discovery

Companion to `job-application`. That skill fills forms; this one finds roles.

## What this is not

It does not apply to anything. It does not submit, upload, or answer a legal
attestation. It stops at appending rows to a spreadsheet.

## Setup

You need two private inputs, neither of which lives in this repo.

1. **The discovery config** that `jobdiscovery.discover` and `jobdiscovery.append`
   read — see `jobdiscovery/config.py` for the full key list. It holds the
   spreadsheet id, the tab name, where the sheet's data starts, the path to the
   credentials for the web-app endpoint the tracker is reached through
   (`webapp_credentials` — an HTTP endpoint, not a service-account key), the path
   to `companies.yaml`, and where run directories are written. It is found via
   the `JOB_DISCOVERY_CONFIG` environment variable, falling back to
   `~/.config/job-discovery/config.yaml`. There is no other default. If it is not
   where you expect, ask — do not guess a spreadsheet id.
2. **The private answer store** `job-application` already uses for its settled
   answers — `docs/dossier.md` and `docs/application-answers.md`. This is Step
   2's evidence source. As with that skill's own answer store, look first for a
   recorded path in the standing project instructions this skill can already
   read; if none is recorded, ask, and write the answer back as one line. A
   path asked twice is the record's failure, not the operator's.

## The three steps

1. `python3 -m jobdiscovery.discover [--run-id ID]` — writes a run directory.
2. **You**, this skill: fill the prose sections of every `roles/*.md`.
3. `python3 -m jobdiscovery.append --run-id ID` — appends the rows. Only after
   the human has reviewed.

The three steps talk only through files on disk, and each run directory holds:

- `roles/*.md` — one file per role that is ATS-verified, inside the 24-hour
  window, and not already in the tracker. **This is the run's yield, and it is
  what you write.**
- `unverified/*.md` — leads from the public listings repo, which suggests roles
  but never establishes when one was posted. They carry no timestamp, so they are
  not verified, not counted in the yield, and not your job unless the human says
  so. Step 3 reads `unverified/` only with `--include-unverified`.
- `run.json` — the account of what the run did: the yield, every source and
  whether it answered, every role dropped and the key it matched, every role
  filtered out and why, everything verified but outside the window, and every
  role flagged for a human to look at. **Never edit it.** Step 1 is its only
  writer, because a ledger a later step can revise is not evidence.

Step 3 takes two flags worth knowing: `--dry-run`, which prints what would be
appended and writes nothing, and `--include-unverified`. Run `--dry-run` first.

A fact the board did not state is written as the literal `unknown` — in the
front matter and, for a lead with no job description to score, in the Fit Score
cell. That is a gap the human can see, not a mistake to fill in.

## Your job is Step 2, and only Step 2

Fill five sections per role file: `cover_letter` (250–350 words),
`why_interested` (110–150 words), `why_it_fits`, `resume_tailoring`, and `notes`
(for a YC company, a 60–100 word message to the founders).

`notes` is optional; the other four sections gate the append. A role whose
`notes` you leave empty still appends; a role missing any of the other four is
held back and named in Step 3's skip list, because half a review in the tracker
is worse than one that waits a round. Padding `notes` to look complete is worse
than leaving it blank.

**Write prose only. Never edit the YAML front matter.** Those facts came from the
employer's ATS. Restating them is how the previous version of this system was
able to be wrong about freshness for nineteen runs without anyone noticing.

**Fill only empty sections.** If a section already has text, the human wrote or
approved it — leave it alone. Emptying a section is how they ask for a rewrite.

Roles are independent: write them in parallel rather than one after another.

## Evidence boundary

Every claim must be supported by the resume and by the private `docs/dossier.md`
and `docs/application-answers.md`. Do not name a technology that is not on the
resume. Use the applicant name recorded in the private answer store.

## The revision loop

Draft, then critique, then revise. Three rules that are not negotiable:

- **The cap is four passes and it is counted in code, not judged by you.** At the
  cap, ship what you have and state the residual concern in the audit section.
  An unbounded loop whose exit the model judges will eventually declare itself
  clean in order to escape, and the output looks identical either way.
- **Ship the highest-scoring pass, not the last one.** Revision can make writing
  worse.
- **Score each criterion separately, reason before concluding, and let the
  pass/fail come from the scores** — never from a bare judgement.

## The critic's rubric

Score every draft against these seven criteria, in the owner's own words:

1. sentences that could have been written by almost anyone
2. generic summaries or unnecessary conclusions
3. places where my uncertainty was polished away
4. inflated language
5. claims not present in my original notes
6. overly symmetrical or formulaic structure
7. phrases that sound like LinkedIn/AI writing

**Score each criterion 0, 1, or 2** — 0 not triggered, 1 slight, 2 clear — and
sum the seven into a total of **0–14. A lower total means more human-sounding.**
The critic emits all seven sub-scores, not just the total, so it is visible
which criterion cost the points.

**Criterion 5** ("claims not present in my original notes") is judged against `docs/dossier.md` and `docs/application-answers.md`:
does any claim in this letter lack a basis in those two files? This is the
same boundary the evidence rule above already draws, so the two cannot
disagree.

## Recording what a run cost

Write `writing.json` next to `run.json` via `jobdiscovery.writing_ledger`: passes
and tokens per role. Never edit `run.json`.
