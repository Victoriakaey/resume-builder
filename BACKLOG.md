# Backlog

Ideas not yet built. Each is a design sketch, not a commitment — brainstorm before building.
Items carry stable `B#` ids so external notes (e.g. a references log) can cite them.

---

## Triage — 2026-07-31

Everything below B1 came out of a single session reading eleven external references. Recorded here so
the judgement doesn't have to be re-derived, **not** as a decision — Victoria explicitly deferred
choosing.

**The context that makes the sorting mean anything:** this skill has one user writing one resume for
one lane. Most of the open items are engineering against *repeat use by many people over time* —
real problems, but ones neither of those conditions has produced yet. Building them now costs a
session and buys protection against a failure that hasn't happened. The honest split is by **who the
work is for**, not by how good the idea is; every item below is a decent idea.

| Verdict | Items | Reasoning |
|---|---|---|
| **Do — improves this resume** | B13 (claim-layer ladder, ~20 lines) · B15 (US portal fields an agent must never answer, ~10 lines) | Both are *writing*, not building. B13 gives Lane-1 positive vocabulary the dossier lacks (it only says what not to claim) and is useful in interviews too. B15 covers real legal exposure on the sponsorship question. |
| **Do — inside B12, when the rubric is next touched** | the interview-probe procedure | Turns "defensible for five minutes" from an assertion into something testable. Cheap, and immediately useful before an actual interview. |
| **Defer — needs usage evidence first** | B2 · B5 · B9 · B10 · B11 · B14 | Each solves a real degradation problem: prompt edits regressing silently, prose guardrails being deleted by a tidy-up, an uncapped critic, a linter with no permanent bad-input fixture. All of it is speculative until the skill has been used to tailor five or six times and something has actually broken. Revisit then — the breakage will say which of the six mattered. |
| **Drop unless something changes** | B4 · B6 · B7 · B8 | B4: the hand-built dossier already beats sample extraction for this user. B6: worth *reading* the timing argument, not worth writing it in — and cold outreach comes after the resume is finished. B7: the name collision only bites on public promotion. B8: single lane, so per-role presets have nobody to serve. |

**Standing debt, unaffected by the above:** `lint_resume.py` (B1, shipped) has no permanent bad-input
fixture — its detection was proven once by hand, which by B5's own anti-theater rule does not count.
Three of the eleven references were repositories whose checks silently never ran; this is the same
hole, and it is ours.

**The other honest note.** The session that produced B2–B15 moved the resume itself by two lines of
LaTeX compatibility guard. The linter earned its keep — it caught that the skill's stated ~95–100
characters-per-line was wrong for the actual template (~120, so bullets had been trimmed to a target
20% too small) and that six bullets waste ~95pt on near-empty tail lines, more room than the page has
left. Neither was visible by eye. **That is the argument for the tooling that exists and the argument
against adding more of it right now.**

---

## ✅ Shipped

### B0 — Per-user dossier ("the skill gets better the more you use it")
**Shipped 2026-07-15.** `references/dossier-template.md` + read-first/write-back wiring in the
Non-negotiables and steps 1 / 5 / 9. The companion `references/candidate-profile-template.md`
(SUBSTANCE: facts + a STAR bank) shipped alongside it — profile = WHAT, dossier = HOW.

**The original problem, kept for context.** The skill re-learned the person every session:
re-derived their projects' *points*, re-asked positioning, re-made mistakes it had already made
(re-proposing a killed claim, using a disliked register). A single hard session could burn 20+
rounds rediscovering things that were true the whole time. The fix was a persistent
read-first / write-back profile, not model fine-tuning: read at session start so nothing is
re-asked; append what was learned at session end so the next session starts closer.

**Design cautions that survived into the shipped version:** distinguish `[durable]` from
`[context:<scope>]` so one instance never becomes a rule · every entry stays overridable ·
stale entries are SUPERSEDED (marked `retired (superseded by <new>, DATE)`), never silently
deleted · the skill body stays generic, the dossier is per-user and lives in the user's own
private resume repo.

### B1 — Mechanical guardrails as a script, not a reading
**Shipped 2026-07-31.** `scripts/lint_resume.py` + the "run the mechanical half first" block in
the Guardrails checklist. The skill's own critic doctrine already said *derive pass/fail in code,
not an LLM boolean* — the checklist itself was still being eyeballed. Now page count, per-bullet
rendered line count, near-empty tail lines, weak lead verbs, stack-first openings, jargon density,
AI-slop wording, one-sided round metrics and dossier off-limits phrases are all decided by a script.

Two findings worth remembering from building it: (a) **line capacity is a measurement, not a
constant** — the skill had been asserting ~95–100 chars/line, but a 0.4in-margin letterpaper page at
11pt XCharter actually fits ~120, so bullets were being trimmed against a target that was wrong by
20%; (b) **the expensive defect is the tail line, not the character count** — a wrapped bullet whose
last line holds two words spends a whole line to buy them, and six of those cost more room than the
page had left.

---

## 🔜 Open

### B2 — Slot-and-patch tailoring: make `/tailor-resume` produce a compiled PDF
**Source:** the `latex-tex` mode in santifer/career-ops.

Today `/tailor-resume` returns *advice* — swap these keywords, reorder these bullets — and the
person hand-edits their `.tex`. career-ops solves the same problem mechanically: one script reads
the user's own `.tex` and extracts the **editable prose slots** into JSON (document body only;
preamble macro definitions and commented-out bullets are skipped so a stale bullet never becomes an
editable slot), the model rewrites only `slots[].text`, a second script patches them back and
compiles. The preamble, macros, spacing and colors are never touched.

Why it fits here: with `tectonic` already required by B1, the compile step is free, and the output
becomes a real tailored PDF instead of a to-do list. Their layout-detection table (a `resumeSubheading`
macro family vs a plain `tabularx`+`itemize` family, anything else → refuse with a clear error) is the
right amount of scope for v1 — refusing an unknown layout beats silently mangling it.

Carry over their ethics wording verbatim in spirit: keywords are **reformulated, never fabricated**;
never add a tool, skill or metric absent from the source; cross-check against the candidate profile
and omit anything not backed by it.

**Give it a mechanical acceptance gate** (from Resume-Matcher's structural scorers — see B5): the
tailored `.tex` must introduce **no employer, company or project name absent from the master**, and
the contact/identity block must be byte-for-byte unchanged. That turns part of "never fabricate"
from a human read into a check that can't be forgotten. It does not cover invented *narrative*
inside a real role — that stays human, and B9 says to write that limit down.

### B3 — Split voice into two tiers (anti-slop everywhere, conversational only in letters)
**Source:** `modes/_writing.md` in santifer/career-ops.

The dossier holds register/voice preferences and applies them to everything the skill writes. That
is a latent bug: the register that makes a **cover letter** sound like the person (contractions,
sentence-opening "And/But", hedges, parenthetical asides) is wrong for a **resume bullet**, which
wants a formal, keyword-dense, ATS-legible line.

career-ops splits them explicitly. Tier 1 — the anti-AI-slop rules (banned words, dead phrases,
cadence) — are HARD and apply to all generated text including bullets. Tier 2 — conversational voice
— applies **only** to letters, outreach and follow-up emails, and is forbidden in CV text. Their
precedence rule is also worth copying: the person's own stated style beats the generic anti-slop
guardrail wherever the two conflict, and accuracy beats both (never soften a real metric for rhythm).

**The same boundary, said a second way** (OUBIGFA's de-AI writing skill): *"this is a de-AI-ify patch,
it does not prescribe a new style — whatever register the original was in, it stays in after the
edit."* De-slopping must not sand off the person's voice along with the tells. Two independent
sources landing on the same line is worth treating as settled.

Work: add the tier distinction to `references/dossier-template.md` §3 (tag each preference with where
it applies), and teach step 5 + the cover-letter reference to respect it.

### B4 — Bootstrap voice from writing samples instead of asking
**Source:** the `## Writing Style` extraction in career-ops' `_writing.md`.

Session 1 currently *asks* about register. Better: read what the person has already written — an old
cover letter, a LinkedIn About, any professional prose they'll hand over — and extract tone, average
sentence length, opening patterns, punctuation habits, preferred verbs, and the words they never use.
Cache the result in the dossier so later sessions skip the scan.

Their guardrails are the load-bearing part and should be copied as-is: extract **style only**, never
import content, claims, metrics or personal identifiers from samples; store abstract descriptors, not
verbatim sentences; treat idiosyncratic punctuation as intentional voice rather than error; and only
extract what is demonstrably present in more than one sample.

### B5 — A golden set so critic-rubric edits can't silently regress
**Sources:** `evals/` in santifer/career-ops; `apps/backend/tests/evals/` in srbhr/Resume-Matcher
(the stronger of the two — take its structure, take career-ops' provenance discipline).

Every edit to the critic's rubric is an experiment with no control. A golden set fixes that, in
**two deliberately separate layers**:

**Layer 1 — structural scorers. Pure functions: no LLM, no network, no disk.** They assert the
invariants that must hold however the model worded things, so they run free on every change and
catch most "a prompt edit broke something" regressions. Resume-Matcher's set maps almost directly
onto ours: no populated section vanishes · **no employer, company or project name appears that
wasn't in the master** (a set difference — zero model involved) · the identity/contact block is
byte-for-byte unchanged · the output still parses · **JD-keyword coverage as a fraction**, which is
what finally makes `jd-tailoring.md`'s "65–80% overlap" a number instead of a vibe.

**Layer 2 — LLM-as-judge.** Marked, run on demand, uses the developer's own key, **skips cleanly
when no key is configured, and never sits in a keyless gate.** You cannot answer "did this prompt
change help?" with a deterministic test; you must also never block on a non-deterministic one.

**The anti-theater rule — this is the part that is easy to skip and shouldn't be.** Every golden
case ships a `good` AND a `bad` variant, and the tests assert that each scorer actually **fires** on
the bad one (drop a section → False; invent a company → it comes back in the list; change the name →
False). A checker that always says OK is worse than no checker: it costs attention and blocks
nothing. *(Applies retroactively to `lint_resume.py` from B1 — its violation detection was proven
once by hand, which does not count. It owes a permanent bad-input fixture.)*

**This is not hygiene theater — here is the accident it prevents.** `deepakpadhi986/AI-Resume-Analyzer`
(889 stars, 250 forks) scores resumes with lines like `if 'Objective' or 'Summary' in resume_text:`.
Python reads that as `if ('Objective') or ('Summary' in resume_text)`, and a non-empty string literal
is always truthy — so the branch **can never be false**. Two such lines hand 18 of 100 points to every
resume, including a blank one, and print a green "Awesome! You have added Objective/Summary" while the
`else` arms sit there as dead code. It shipped that way for four years. Nobody noticed, and that is the
whole point: **a checker that always passes emits only good news, so no feedback signal ever exposes
it.** One known-bad fixture — feed the empty string, assert the points are *not* awarded — catches it
on day one.

From career-ops, keep two discipline choices the above doesn't cover: **synthetic candidates only**,
so the set can live in the public repo with no real person's data in it; and **labels carrying a
`provenance` field**, so hand-curated ground truth can replace a frozen reference later without
touching the harness. Weight the cases toward **ambiguous/edge inputs** rather than easy wins.

### B9 — Pin the prose guardrails with tests, and write down what the machine can't catch
**Source:** `tests/unit/test_prompt_guardrails.py` in srbhr/Resume-Matcher.

Every integrity rule this skill has lives in prose — the Non-negotiables in `SKILL.md`, the
guardrails in the user's dossier. **Nothing currently stops a future "let's tighten SKILL.md" edit
from quietly deleting "never list unbuilt work" or the defensibility clause.** Prose guardrails are
load-bearing and completely unprotected.

Resume-Matcher's fix is blunt and good: a test that asserts the anti-fabrication clauses are still
**literally present** in the prompt text, so an edit that drops one fails loudly. Their docstring
does the harder half — it states exactly which fabrications the mechanical layer misses (an invented
*narrative*, e.g. "led 12 engineers", slips past both their verifiers because one's metric regex
ignores bare counts and the other only checks skills/certs/companies) and concludes that the prose
clause is therefore *the only guard*.

Copy both halves: assert the key phrases survive, and keep a written, honest list of what only a
human can catch. The second half matters more — a mechanical layer whose blind spots are undocumented
quietly reads as full coverage.

### B6 — Fold job-search *timing* into `market-fit.md`; do not build the pipeline
**Sources:** a Xiaohongshu post on pre-JD outreach; santifer/career-ops (which automates all of it).

`market-fit.md` already argues about channel (a referral is worth ~40 cold applies). It says nothing
about **when**. The missing idea: companies decide to hire 1–2 months before the JD posts, and
showing up inside that window makes you the person helping scope the role instead of one of 200
applicants. The concrete moves are cheap to write down — read the company newsroom for funding /
launch / partnership signals and infer which team is about to expand; ask which *title* owns the
problem and search that title plus the company; track sends → replies → interviews so a dead script
gets changed instead of repeated.

One more line belongs in the same edit, from a different source (the AnySearch search skill, which was
evaluated and rejected as a dependency): **when you don't know which class of source holds the answer,
query several classes in parallel instead of betting on one.** Researching a company, the signal might
be in the newsroom, a funding database, or an employee's LinkedIn — `cover-letter.md`'s existing
"Fast company-research (by company type)" teaches how to *pick* a source class but not what to do when
the class is genuinely ambiguous. Coverage beats guessing, and it costs nothing beyond the tools
already installed.

Two honesty notes to write in alongside it: the popularized version of this tactic reports ~7 sends
with 3 replies and calls it a 3× lift — that is anecdote at noise scale, so take the mechanism and
drop the number. And it only works where there IS a newsroom, which excludes many of the small AI
startups that are the likeliest targets.

**Explicitly NOT in scope:** scanning portals, an application tracker, a dashboard, follow-up
automation. career-ops does all of that at ~93k lines with a contributor community; this skill's
edge is per-bullet craft (spine, writer/critic loop, defensibility, dual-legibility), which career-ops
does not have. Adopt theirs for pipeline if that layer is ever wanted — don't rebuild it here.

### B7 — Rename: `resume-builder` collides with a published skill of the same name
`cosen1024/resume-builder-skill` publishes a skill whose frontmatter `name:` is also `resume-builder`,
promoted on Xiaohongshu, aimed at the Chinese market (five templates, ID-photo support, campus-vs-
experienced-hire presets). Different market, no functional overlap worth worrying about — but a
name collision matters the moment either is installed alongside the other or either is promoted.

Renaming is nearly free today (a frontmatter `name:`, the two slash commands' skill reference, README
headings) and gets expensive once anyone has it installed. Decide before any public promotion.

### B10 — An index layer for SKILL.md, and a cap on what the critic reports
**Source:** the three-tier read strategy in OUBIGFA's de-AI writing skill. *(That repo carries no
license — all rights reserved — so this borrows the architecture, never its text.)*

`SKILL.md` is 261 lines and grew again today; eleven references sit behind it with no routing. Theirs
keeps the entry file at 81 lines, puts a **51-line index between it and the detail**, and reads the
640-line reference **by section, located via keywords from the index** — never end to end. Two output
rules travel with it and are worth taking as-is: **never dump a reference file at the user** (it is
for judging and patching, not for reciting), and on a review pass **report at most the top 5–10
problems**. Our critic currently has no cap, and an uncapped critic reports lint instead of the
things that decide the page.

Sketch: `references/index.md` mapping task → which sections of which reference to read, with locator
keywords. Whether the whole skill needs it or only the bulkier references is the open question.

### B11 — An evidence inventory with provenance, and no structural inheritance
**Source:** redmaplewww/AI-resume-assistant. *(No license — architecture and ideas only, no text.)*

Two moves, one principle: **an existing resume has content-source authority only.** It carries no
automatic authority over section order, project grouping, titles, bullet boundaries, page allocation,
or wording. Their non-negotiable is to never start by polishing the old document in place — first
atomize it into an evidence inventory that is independent of the old layout, and treat old wording as
possibly templated or model-generated until the person deliberately reuses and confirms it. Their red
flag list names the failure directly: *a new resume that preserves the old section order, project
grouping, or bullet boundaries without an explicit reason.*

**Tag every atom** `verified` / `user-stated` / `inferred` / `missing` / `contradictory`, and force
five separations that bullets routinely blur: team outcome vs personal contribution · product function
vs technical mechanism · project purpose vs framework capability · total experience vs
target-specialty experience · verified evidence vs claims awaiting confirmation. The candidate profile
has a STAR bank but no confidence marking on any single fact; the dossier's guardrails are effectively
a hand-maintained "this one isn't defensible" list, which is the same information caught much later.

They also rank what earns a bullet: `relevance × evidence strength × distinctiveness × recency`. This
skill tells the writer to make that selection and never says how.

**Authorship provenance** is the part worth taking without taking their absolute no-drafting rule:
track each final line as `user-written` / `user-confirmed-local-edit` / `model-drafted-user-approved`,
and make "no line ships without provenance" a release check. Their stance is structural (never
generate); ours is procedural (a human reviews). Theirs is more robust, ours is more usable — the
provenance ledger is what makes ours honest about which is which.

### B12 — Hard gates, a fairness clause, and interview probes in the rubric
**Source:** `references/quality-rubric.md` in redmaplewww/AI-resume-assistant.

Three things our guardrails don't have:

**A hard gate independent of the aggregate.** *"Do not treat the total as scientific. A score of 0 in
metric integrity or interview defensibility is a release blocker even when the total is high."* Same
doctrine as deriving pass/fail in code rather than from one LLM-produced number, applied to a resume
rubric.

**A fairness clause.** *Do not lower quality for protected characteristics, school prestige alone,
email provider, photo style, or a missing salary expectation* — and, separately, *keep JD mismatch out
of the integrity score unless the resume falsely relabels the background.* **Being a bad fit is not
being dishonest**, and this skill currently lets the two bleed together. It matters most for exactly
the candidates who already absorb the most noise.

**Defensibility as a procedure, not a slogan.** *Generate interview probes for the three strongest
bullets; weaken or qualify any claim the candidate cannot defend.* We assert the five-minute standard
and never say how to test it. This is how.

**Ground the probes in retrieved reality, not model priors.** CareerForge's mock-interview searches
the web for real interview reports about the target employer *before* writing any question — its
author's stated reason is so it isn't running on the model's own corpus and hallucinations. It then
drills 2–3 follow-ups deep on one project and withholds all feedback until the end. Two things worth
copying: **probes should come from what that employer actually asks**, and **a probe only tests
defensibility if it keeps going after the first answer** — one question is a prompt, three is a test.

**Not optional — a second rubric shows what its absence costs.** CareerForge ships the same shape of
weighted six-dimension rubric (hard skills 25 / experience 25 / soft skills 15 / education 10 /
keyword coverage 15 / resume quality 10, summed and rounded to an integer) with **no gate of any
kind**. A resume whose numbers are invented scores an A and gets "recommended, apply" as long as the
skills line up and keyword coverage is high — nothing in the rubric can stop it. Its B band's
prescribed action is literally "repackage the experience", with no defensibility clause attached.
Two takeaways: **treat the fairness clause as settled** (CareerForge independently states the same
thing — overseas and domestic degrees weigh equally, no credit or penalty for school prestige, and a
career-changer is not marked down merely for a different industry), and **never let the word
"repackage" appear without "and it has to survive the interview question" in the same breath.**

One positive detail worth copying from CareerForge's rubric: **the anti-keyword-stuffing rule lives
inside the rubric**, as a scoring instruction — *keyword coverage corroborates the other dimensions
and never earns a high score on its own.* Ours warns about stuffing in `jd-tailoring.md` prose, where
nothing enforces it at scoring time.

### B13 — A claim-layer ladder for AI/ML work
**Source:** the "API or low-code work presented as model engineering" section of their anti-patterns.

Six distinct layers, all legitimate, routinely collapsed into one another: calling a hosted model API ·
configuring an orchestration or low-code product · building RAG or agent application logic · training
or fine-tuning a model · serving and optimizing inference · operating a production system. The rule
that makes it useful: **use the accurate layer, and never inherit the capabilities of the platform
underneath you.**

This gives a Lane-1 candidate positive vocabulary instead of only a prohibition — a dossier guardrail
that bans fine-tuning claims says what not to write; this says what the honest rung is called. Ship it
alongside two companions from the same file: **demo-as-enterprise-production** (require at least two
project-relevant lifecycle signals and one concrete operating constraint before any "enterprise-grade"
/ "high concurrency" / "production-ready" wording) and **fashionable-but-shallow** (RAG, Agent, MCP,
tool calling, reranking, multimodal appearing with no parameters, selection rationale, evaluation,
failures or tradeoffs — the repair is fewer terms each attached to a real constraint, never invented
parameters to look deep).

### B14 — Severity tiers in the linter: taste is tunable, truth is not
**Source:** the strict/normal/lenient modes in Pickle-Pixel/ApplyPilot's `scoring/validator.py`.
*(AGPL-3.0 — ideas only, no code.)*

Their validator runs the same checks at three strictness levels: banned filler words are hard errors
that trigger a retry in `strict`, warnings in `normal`, ignored in `lenient` — **but the fabrication
and structure checks are enforced at every level.** That is the right axis to make configurable.
`lint_resume.py` currently fixes one severity per check, which means the only way to quiet a stylistic
nag is to disable the check with `--only`, and that same switch would also disable a truth check.

Split it: **taste tier** (AI-slop wording, jargon density, one-sided round metrics, stack-first
openings) becomes tunable; **truth tier** (dossier off-limits phrases, model self-talk leaks, and the
fabrication checks B5 will add) stays ERROR at every level, with no flag that can soften it.

Two more from the same file worth folding into B5:

**Preservation runs in both directions.** Resume-Matcher checks that tailoring invents no employer;
ApplyPilot checks that tailoring hasn't *dropped* one — `preserved_companies` and `preserved_school`
must still be present, and a missing one is an error. Adding a fake job and deleting a real one are
both tailoring failures, and each source only guards one of them.

**Auto-fix what is deterministically fixable; fail only on what needs judgment.** Their
`sanitize_text` rewrites em dashes and smart quotes on the way through rather than rejecting the
output and spending a retry on it. Cheap normalization belongs in the pipeline, not in the verdict.

**And one anti-pattern to avoid.** Their fabrication check runs off a hardcoded watchlist of
"languages with zero relation to the candidate's stack" — which includes Django, Vue, Rails, Go and
Rust. That list is tuned to one person and would flag a Django developer's true skill as a lie. Their
own module docstring promises "all validation is profile-driven, no hardcoded personal data", and they
even wrote the `_build_skills_set()` helper to do it — it is dead code, called from nowhere. **Derive
the allowed set from the person's profile; never ship a hardcoded blacklist of technologies.**

### B8 — Role presets (low priority)
`cosen1024/resume-builder-skill` ships a per-role table driving section order, emphasis and a sample
skills line, kept explicitly orthogonal to the visual template. This skill branches section order by
*seniority* (step 4) but not by *role*. Useful for a multi-lane user; irrelevant to a single-lane one.
Small, do it only if a second lane ever shows up.
