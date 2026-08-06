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
   read (spreadsheet id, tab name, service-account key path) — see
   `jobdiscovery/config.py`. It is found via the `JOB_DISCOVERY_CONFIG`
   environment variable, or the default path that module names. If it is not
   where you expect, ask — do not guess a spreadsheet id.
2. **The private answer store** `job-application` already uses for its settled
   answers — `docs/dossier.md` and `docs/application-answers.md`. This is Step
   2's evidence source. As with that skill's own answer store, look first for a
   recorded path in the standing project instructions this skill can already
   read; if none is recorded, ask, and write the answer back as one line. A
   path asked twice is the record's failure, not the operator's.

## The three steps

1. `python3 -m jobdiscovery.discover` — writes `roles/*.md` and `run.json`.
2. **You**, this skill: fill the prose sections of every `roles/*.md`.
3. `python3 -m jobdiscovery.append` — appends the rows. Only after the human has
   reviewed.

## Your job is Step 2, and only Step 2

Fill five sections per role file: `cover_letter` (250–350 words),
`why_interested` (110–150 words), `why_it_fits`, `resume_tailoring`, and `notes`
(for a YC company, a 60–100 word message to the founders).

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

## The critic's rubric — OPEN, not yet supplied

The seven anti-AI-writing criteria this loop is supposed to score against are
**not yet recorded**. Their original text lives outside both repositories and is
awaiting the owner.

**Do not invent them.** Until they land, score against the two published
references — `references/cover-letter.md` ("Don't write one that screams 'an LLM
wrote this'") and `references/writer-critic-workflow.md` (its AI-tells pass) —
and say plainly in the audit section that the rubric was the fallback, not the
seven criteria.

## Recording what a run cost

Write `writing.json` next to `run.json` via `jobdiscovery.writing_ledger`: passes
and tokens per role. Never edit `run.json`.
