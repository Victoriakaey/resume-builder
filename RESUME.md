# RESUME — resume-builder skill

**Moment:** 2026-08-02, mid-session. Adding a `--cli` flag to `scripts/cold_read.py` so the
cold-read comprehension test can be run by a model family other than Claude. The edit is
**IN PROGRESS and the file is uncommitted** — `CLI_SHAPES` has been added at module level but
`ask_cold_reader()` has not been switched over to use it, so the script is half-migrated and
will not run correctly until that function is updated.

> snapshot: HEAD `cec5470` · branch `main` · 2026-08-03T01:32:33Z
> Working tree: `scripts/cold_read.py` modified, nothing else.

## Next concrete action

Finish the migration: give `ask_cold_reader()` a `cli` argument, look the shape up in
`CLI_SHAPES`, prepend `SYSTEM_PROMPT` to the user prompt when `inline_system` is true, and build
argv from `shape["argv"](prompt, model)`. Then thread a `--cli` argparse option through `main()`
into the run loop. Verify by reading the same resume with `--cli claude` and `--cli codex` and
comparing which concepts each family retains.

## Shipped this session (both pushed at `cec5470`)

- **`category` check in `lint_resume.py`** — fires when an entry never says what KIND of thing
  the work was (tool / platform / service). Distinct from `stack` (what it was built WITH) and
  `anchor` (does the employer name mean anything). Verified on a real before/after: fires on
  exactly the one entry that had the defect, silent after the fix, zero false positives on the
  other four entries.
- **`scripts/cold_read.py`** — hands the rendered resume to a reader with zero context and asks
  fixed comprehension questions. The model only ever ANSWERS; pass/fail is matched in Python
  against an expectations file the model never sees. Three readers, majority verdict.

## Decisions worth not re-deriving

- **No scoring critic, ever.** Recruiter judgement is 55% accurate at Fleiss κ=0.13, and an
  open-sourced ATS scored one unchanged resume 66–99 across 100 runs. A critic asked to predict
  pass/fail simulates a coin, confidently. Comprehension is the part that holds still.
- **Majority-of-three, not one reader.** The first version asked once and reported a concept in
  one run that it missed in the next on a byte-identical file. A lone miss is a minority report.
- **A parse failure counts every concept as unconveyed**, never as a pass — otherwise a broken
  run is indistinguishable from a good resume.
- **`agent` / `model` / `client` / `server` / `browser` are NOT category words**, and are listed
  as explicit false friends in `lint_resume.py`. Including them made `category` silent on the
  exact entry that prompted it: in this corpus those nouns name the thing the work acts ON.

## Gotchas

- **Cross-family isolation is weaker than Claude's.** Only `claude` accepts `--system-prompt`
  and `--disallowed-tools` as flags. For `codex exec` and `gemini -p` the same instruction must
  be prepended to the user prompt, which a model may weigh differently. Say so when reporting
  cross-family results; never present them as equally isolated.
- **Families present on this machine** (checked 2026-08-02): `claude`, `codex`, `agy`,
  `codebuddy`, `gemini`. `qoder` and `cursor-agent` are absent.
- **This repo is public and the skill is symlinked into `~/.claude`, not bundled.** Personal
  content must never land here. Before every push, grep the outgoing diff for the adopter's
  name, their product names, their email domain and their school — keep that pattern in the
  private repo, not in this one. It caught two leaks in `cold_read.py`'s docstring this
  session: a named private product, and a path into the private repo's research notes.
- Don't recount motifs with `grep '^- **Tags**:' | grep -c` — returns 0 under the local rtk
  proxy (false negative). Use python.

## Backlog state

B0 (dossier) and B1 (mechanical guardrails) shipped. Open: B2 slot/patch tailoring → compiled PDF ·
B3 two-tier voice · B4 voice from writing samples · B5 golden set (two layers + anti-theater bad
fixtures) · B6 timing into market-fit, no pipeline · B7 rename (name collides with a published skill)
· B8 role presets · B9 pin prose guardrails with tests · B10 index layer + cap the critic ·
B11 evidence inventory with provenance · B12 rubric hard gates + fairness clause + interview probes ·
B13 claim-layer ladder for AI work · B14 severity tiers (taste tunable, truth not) · B15 US portal
fields an agent must never answer.

**Owed debt:** `lint_resume.py` still has no permanent bad-input fixture — `category`'s detection
was proven once by hand against a real prior revision, which by B5's own anti-theater rule does
not count as a test.

## What NOT to retry

- Don't build a job-search pipeline (scan/track/follow-up). career-ops does it at 93k LOC; this
  skill's edge is per-bullet craft. B6 says so explicitly.
- Don't copy text from the no-license repos (de-AI writing skill, AI-resume-assistant, CareerForge)
  or code from ApplyPilot (AGPL-3.0). This repo is MIT and public. Ideas only.

## Open decision for Victoria (asked, not yet answered)

Register a new motif `checker-always-passes` in the references log? Four candidate members, four
distinct mechanisms, identical symptom: operator-precedence always-true condition
(AI-Resume-Analyzer) · check scope emptied by gitignore (de-AI `style_audit.js`) · function imported
but never called (ApplyPilot `validate_tailored_resume`) · her own
`project_critic_passive_gate_2026-07-30` (79% of re-reviews got no diff, UI said "Clean sweep").
Plus one positive member (Resume-Matcher, the only one that wrote down the defense). Nuance flagged:
ApplyPilot's symptom is silence, the others emit a false green light. Registering carries a
back-tag obligation, so it's her call.
