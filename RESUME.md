# RESUME — resume-builder skill

**Moment:** 2026-08-07, mid-session, on branch `feat/job-discovery`. `job-application` shipped as a
symlinked subskill (design doc landed, de-personalised halves built) and the plan moved on to
`job-discovery`: a three-step system (Step 1 `discover.py` finds/verifies roles, Step 2 Claude fills
prose per `SKILL.md`, Step 3 `append.py` appends reviewed rows to a tracker). Task 12 (the last task
on the branch — mutation tests, the critic's own separation test, README mention, install) is
**committed** at `a9b372f`. A post-review finding is being closed right now: `test_mutation.sh`'s
`mutate()`/`mutate_doc()` helpers leave a mutated tracked file + a stray `.bak` behind if interrupted
mid-run (no trap). Adding a `trap ... EXIT INT TERM` restore and verifying it under an actual `TERM`
signal, not just by reasoning about it.

> snapshot: HEAD `a9b372f` · branch `feat/job-discovery` · working tree has one in-progress edit to
> `tests/job_discovery/test_mutation.sh` (the trap fix, not yet committed)

## Next concrete action

Finish the interrupt-safety fix in `tests/job_discovery/test_mutation.sh`: add the `MUTATING` /
`restore_now` trap to both `mutate()` and `mutate_doc()`, rerun the harness to confirm `ALL PASS` +
clean tree, then interrupt it mid-mutation with a real `TERM` and confirm the tracked source file
comes back intact with no `.bak` left over. Append the fix report to
`.superpowers/sdd/2026-08-06-job-discovery/task-12-report.md`, then commit
(`scripts/check_no_personal.sh` on the staged files first — expect it to flag the pre-existing
README `## License` line, which is not new, see Gotchas).

## Shipped previously (this branch, through Task 12 / commit `a9b372f`)

`skills/job-discovery/` — `discover.py`, `dedup.py`, `freshness.py`, `writing_ledger.py`, `ledger.py`,
`sheets.py`, `append.py`, `SKILL.md`. 145 pytest tests + 4 shell suites (`test_check_no_personal.sh`,
`test_job_application_skill.sh`, `test_job_discovery_skill.sh`, `test_mutation.sh`) all green. The
mutation harness proves 15 protected rules (8 code + 7 doc) actually fail the suite when broken — no
holes. Symlinked into `~/.claude/skills/job-discovery`. README now has a `## Subskills` line pointing
at it. The seven anti-AI critic criteria are still OPEN (deferred, not this branch's job) — the two
letter fixtures for `test_critic_separation.md` are deliberately not built until they land.

The `--cli` migration in `scripts/cold_read.py` (older work, `main` branch) is also finished and
committed. `CLI_SHAPES` is wired through `ask_cold_reader()` and a `--cli` argparse option threads
into the run loop. A cold read can now be run by a non-Claude family.

## Design decisions worth not re-deriving (job-application subskill)

- **Public/private split rule:** *would this still be true for a different person using the system?*
  Yes → public repo. No → private repo. Mechanism is shareable; answers are not.
- **Answer store is append-only with an `Overrides` field.** Several rulings contradict the adopter's
  own profile document, and one contradicts `references/work-authorization.md`. Without recorded
  provenance a later reader assumes the assistant decided unilaterally, or re-litigates a settled
  question. Same discipline as `docs/decisions.md`.
- **Store reusable *material blocks*, not answers.** Employers ask the same thing in different words;
  three near-duplicate stored answers rot independently. Trim source material at fill time — with a
  constraint that trimming preserves dates, ownership, metrics, and stated limitations.
- **No fit scoring or success prediction.** Same reasoning as the no-scoring-critic decision below.
- **A submit barrier is required, not a rule against clicking Submit.** Intent already failed once in
  practice: a coordinate click landed on Submit because a browser extension scrolled the page between
  screenshot and click. Rules that depend on care do not survive a moving page.

## Cross-family review, and what it is good for

`codex` reviewed the design blind and returned 12 findings; 9 were folded in. The two most valuable
were structural, not cosmetic: it noticed that the anti-incident rules closed two known paths without
making submission structurally hard, and it caught a contradiction between "stop for legal
attestations" and an appendix that auto-answered several attestation-class questions.

It also correctly cited **this repo's own `references/work-authorization.md`** against the design's
sponsorship ruling. That one was a false positive on the specific case, but only because of adopter
circumstances the reviewer could not see — the general rule it quoted is right, and the design now
records why the case differs. **A blind reviewer citing your own repo against you is the signal to
look for; it means the reference is doing its job.**

## Decisions worth not re-deriving (earlier, still current)

- **No scoring critic, ever.** Recruiter judgement is 55% accurate at Fleiss κ=0.13, and an
  open-sourced ATS scored one unchanged resume 66–99 across 100 runs. A critic asked to predict
  pass/fail simulates a coin, confidently. Comprehension is the part that holds still.
- **Majority-of-three, not one reader.** The first version asked once and reported a concept in one
  run that it missed in the next on a byte-identical file. A lone miss is a minority report.
- **A parse failure counts every concept as unconveyed**, never as a pass — otherwise a broken run is
  indistinguishable from a good resume.
- **`agent` / `model` / `client` / `server` / `browser` are NOT category words**, and are listed as
  explicit false friends in `lint_resume.py`.

## Gotchas

- **This repo is public and the skill is symlinked into `~/.claude`, not bundled.** Personal content
  must never land here. Before every push, grep the outgoing diff for the adopter's name, their
  product names, their email domain and their school. _This rule just caught a whole design document;
  it earns its keep._
- **Cross-family isolation is weaker than Claude's.** Only `claude` accepts `--system-prompt` and
  `--disallowed-tools` as flags. For `codex exec` and `gemini -p` the same instruction must be
  prepended to the user prompt, which a model may weigh differently. Say so when reporting
  cross-family results; never present them as equally isolated.
- **`codex exec` needs `--skip-git-repo-check` and `-s read-only`** for a review run in a repo it did
  not create. Verified working 2026-08-06.
- **Families present on this machine** (checked 2026-08-06): `claude`, `codex`, `gemini`. `qoder`,
  `cursor-agent`, `aider`, `opencode` are absent. (An earlier snapshot also listed `agy` and
  `codebuddy`; not re-verified this session.)
- Don't recount motifs with `grep '^- **Tags**:' | grep -c` — returns 0 under the local rtk proxy
  (false negative). Use python.
- **`scripts/check_no_personal.sh` on `README.md` always flags 3 `LEAK` lines on the `## License`
  line** — that's the account holder's own copyright attribution (three of the name patterns in
  `scripts/personal-patterns.txt`, spelled out there, not repeated here), present since the repo's
  first commit (`b4aeab5`, 2026-07-14), and explicitly called out as intentional in that file's own
  header comment. Not a regression; don't "fix" it without being asked.
- **Task 12's brief had two stale sed patterns** (mutations targeting `claimed_total` / a
  `summary_range` print in `sheets.py`) written against a service-account-era design later replaced
  by the Apps-Script `TrackerClient` (commit `b5b3d00`). A verbatim sed expression that matches
  nothing in the current file is a silent no-op — always check a brief's literal code blocks against
  current source before trusting them, the same discipline the mutation harness enforces on itself.

## Backlog state

B0 (dossier) and B1 (mechanical guardrails) shipped. Open: B2 slot/patch tailoring → compiled PDF ·
B3 two-tier voice · B4 voice from writing samples · B5 golden set (two layers + anti-theater bad
fixtures) · B6 timing into market-fit, no pipeline · B7 rename (name collides with a published skill)
· B8 role presets · B9 pin prose guardrails with tests · B10 index layer + cap the critic ·
B11 evidence inventory with provenance · B12 rubric hard gates + fairness clause + interview probes ·
B13 claim-layer ladder for AI work · B14 severity tiers (taste tunable, truth not) · **B15 US portal
fields an agent must never answer — now directly relevant; the job-application design's
"policy-level questions" list is a first cut at it.**

**Owed debt:** `lint_resume.py` still has no permanent bad-input fixture — `category`'s detection was
proven once by hand against a real prior revision, which by B5's own anti-theater rule does not count
as a test.

## What NOT to retry

- Don't build a job-search pipeline (scan/track/follow-up). career-ops does it at 93k LOC; this
  skill's edge is per-bullet craft. B6 says so explicitly. **The job-application subskill is not a
  pipeline** — it fills forms the human has already chosen, and does not scan, rank, or follow up.
- Don't copy text from the no-license repos (de-AI writing skill, AI-resume-assistant, CareerForge)
  or code from ApplyPilot (AGPL-3.0). This repo is MIT and public. Ideas only.

## Open decision for the repo owner (asked, not yet answered)

Register a new motif `checker-always-passes` in the references log? Four candidate members, four
distinct mechanisms, identical symptom: operator-precedence always-true condition
(AI-Resume-Analyzer) · check scope emptied by gitignore (de-AI `style_audit.js`) · function imported
but never called (ApplyPilot `validate_tailored_resume`) · her own
`project_critic_passive_gate_2026-07-30` (79% of re-reviews got no diff, UI said "Clean sweep").
Plus one positive member (Resume-Matcher, the only one that wrote down the defense). Nuance flagged:
ApplyPilot's symptom is silence, the others emit a false green light. Registering carries a back-tag
obligation, so it's her call.
