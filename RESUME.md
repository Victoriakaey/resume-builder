# RESUME — resume-builder skill

**Moment:** 2026-07-31, mid-session. Victoria is feeding a series of external references (12 so far,
one per message) for me to evaluate against this skill. Each one gets analyzed, written to the global
references log, and turned into backlog items here. She said: "你可以我发一条你给我写一条 以防写漏"
— log each as it arrives, don't batch.

## Current task
**The reference series is finished** — all eleven are logged and committed. Victoria asked for the
whole thing to be recorded and pushed, and explicitly deferred deciding which backlog items to build:
"我们可以之后再想要不要做的事情".

**Next concrete action:** rewrite the **Tech4Good / Projects / Awards** sections of `~/Documents/resume/resume.tex`.
Do NOT polish the existing wording — it is untouched template-migration text, which reference #8
lists as a red flag in its own right. Atomize the facts first, re-decide section order and grouping,
then write. The old wording's only authority is which facts it contains. Run
`python3 scripts/lint_resume.py resume.tex --dossier docs/dossier.md` after.

A triage of B2–B15 (do / defer / drop, with reasoning) is recorded at the top of `BACKLOG.md` so it
doesn't get re-derived. Short version: B13 and B15 are writing and worth doing; the six
degradation-protection items are speculative until the skill has actually been used enough to break.

## Shipped today (B0/B1 done, both live via the ~/.claude/skills symlink)
- `scripts/lint_resume.py` — the mechanical half of the guardrails checklist. Checks: page count,
  per-bullet rendered line count + near-empty tail lines (measured from PDF geometry via
  `pdftotext -bbox-layout`, never a guessed chars-per-line), weak lead verbs, stack-first openings,
  jargon density, AI-slop wording, **model self-talk leaks (ERROR)**, one-sided round metrics, and
  dossier off-limits phrases. Wired into SKILL.md's Guardrails section.
- `references/bullet-writing.md` — new "Intensity distribution" section: three sameness axes
  (amplitude / length / closing move) + "repair by changing how information enters, never by
  swapping a synonym."
- `SKILL.md` — corrected the wrong "one line ≈ 95–100 chars" claim (her template actually fits ~120;
  capacity is a measurement, not a constant), added the tail-line rule, the intensity rule, and the
  run-the-script-first guardrail block.
- `references/dossier-template.md` + her private `docs/dossier.md` — a hand-curated
  ` ```forbidden-phrases ` block the linter reads.
- Private repo: `resume.tex` got a `\ifdefined\pdfgentounicode` guard so tectonic (XeTeX) can compile
  it locally; Overleaf (pdflatex) behavior unchanged. `tectonic` installed via brew.

## Live findings about her actual resume (not yet acted on)
- **Tech4Good / Projects / Awards are still the original template-migration text** (`929854c` /
  `12dec83`) — never went through spine-first. Reference #8 lists exactly this as a red flag.
  When rewriting: do NOT polish the existing wording; atomize the facts first, re-decide section
  order and grouping, then write. Old wording's only authority is which facts it contains.
- **Six bullets have near-empty tail lines** (`and staff)` at 9% full, `access control` 12%,
  `arXiv:2505.04843` 15%, `at Pearson r ≈ 0.54` 17%) — ~95pt wasted, more than the 48pt of slack the
  page has left. Closing those frees more room than all current whitespace.
- Page currently compiles to 1 page with ~48pt (~3.7 lines) of slack.

## Backlog state
B0 (dossier) and B1 (mechanical guardrails) shipped. Open: B2 slot/patch tailoring → compiled PDF ·
B3 two-tier voice · B4 voice from writing samples · B5 golden set (two layers + anti-theater bad
fixtures) · B6 timing into market-fit, no pipeline · B7 rename (name collides with a published skill)
· B8 role presets · B9 pin prose guardrails with tests · B10 index layer + cap the critic ·
B11 evidence inventory with provenance · B12 rubric hard gates + fairness clause + interview probes ·
B13 claim-layer ladder for AI work · B14 severity tiers (taste tunable, truth not) · B15 US portal
fields an agent must never answer.

**Owed debt:** `lint_resume.py` has no permanent bad-input fixture — its detection was proven once by
hand, which by B5's own anti-theater rule does not count.

## What NOT to retry
- Don't recount motifs with `grep '^- **Tags**:' | grep -c` — returns 0 under the local rtk proxy
  (false negative). Use python.
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
