# Writer + Critic Workflow — reusable pattern

The engine of the skill: refine each resume bullet with a **writer→critic loop** until it
passes every rubric criterion (or a round cap). Runs via the `Workflow` tool, parallel
across bullets. This is what turns "good enough" bullets into tight, defensible, one-line ones.

## When to use
Any time you have the ESSENCE of an experience/project (from the deep-read step) and need to
turn it into 1–3 polished bullets. Also for re-polishing a section that reads flabby.

## Inputs per bullet
- `essence` — the ground-truth of what the work IS and why it's non-trivial (from the codebase/
  project deep-read). The critic checks the draft against this so it stays honest and doesn't go hollow.
- `mustKeep` — required metrics + tech keywords that cannot be dropped.
- `leadVerbs` — an allowed set of first-word verbs, DISTINCT per bullet, so verbs don't repeat
  across the entry. (Verb *variety* is a low-priority polish, not a hard gate — see the note under
  the critic rubric. The set exists to nudge, not to fail an otherwise-strong bullet.)
- `latexName` — the exact `\href{}{\underline{...}}` product token (or null if the bullet
  continues an entry and shouldn't restate the name).
- `charLimit` — ~100 visible chars (exclude LaTeX markup) = one line at 11pt / 0.4in margins.

## The loop (per bullet, parallel across bullets)
```
draft = writer(essence, mustKeep, leadVerbs, charLimit)
for round in 1..MAX_ROUNDS:      // MAX_ROUNDS is a HARD exit, independent of critic judgment
  crit = critic(draft, essence, rubric)
  if crit.score >= PASS: return draft   // PASS derived in CODE from the score, not an LLM bool
  if crit.feedback == prevFeedback: return draft   // dedupe: critic is cycling, stop
  draft = writer(..., prevDraft=draft, feedback=crit.feedback)
return draft   // best effort if not approved in MAX_ROUNDS
```

## How to build the CRITIC (this is where loops fail)
The critic is the load-bearing component. A weak critic rubber-stamps plausible-but-wrong bullets.
Design rules (from LLM-as-judge / critic-design research — see Sources):

1. **One job.** The critic *judges*; it does not also rewrite. Rewriting is the writer's turn.
   Mixing judge + generate in one call degrades the judgment. If feedback needs to be rich, that's
   still fine as a short note — but the verdict comes from scoring, not from drafting a fix.
2. **Structured enumeration BEFORE the verdict — but terse, not prose.** The critic's output schema
   lists, in order: `present` (which rubric criteria are met), `missing`, `violations`, THEN a
   numeric `score`, THEN nothing else. Enumerating first stops the model from committing to a verdict
   and back-filling justification. **But keep it mechanical** — a list, not an essay. A long free-form
   rationale before the verdict re-introduces early-token anchoring (the very bug enumeration avoids).
   Enumerate, don't monologue.
3. **Score → pass/fail in CODE, never an LLM boolean.** Use a small integer scale (e.g. 1–4 coverage)
   and derive `approved = score >= 3` in the routing code. LLM-generated `approved: true` booleans are
   unreliable and sycophantic.
4. **Rubric criteria are OBSERVABLE behaviors, not adjectives.** "Directly states a measured outcome
   with a baseline" — not "high quality". Replace every "use your judgment" with a mechanical test:
   *"if a claim has no metric AND no verifiable artifact, mark it undefendable."*
5. **Include NEGATIVE criteria — this is the anti-sycophancy fix.** With only positive criteria, the
   model strains to make sense of the input and marks things MET for bullets of any quality. Adding
   explicit *demerits* (jargon pile-up · buried impact · stack-first · round number with no mechanism ·
   passive/no-owner · unfalsifiable claim) counteracts the rubber-stamp. An unfalsifiable or
   suspiciously-round claim with no mechanism is a **demerit, not a neutral**.
6. **Length-neutrality.** Instruct the critic not to reward a longer bullet for being longer. Signal
   density, not word count.
7. **Loop guard.** A hard `MAX_ROUNDS` exit and feedback-dedupe (above) live in the routing code, never
   in the critic's prompt. The loop must terminate even if the critic never says "approved".

## Critic rubric (the criteria — derive score from these)
Per-bullet criteria the critic checks (each maps to a real reviewer rubric axis — see `principles.md`):
- **fluent** — reads cleanly, no grammar/tense errors.
- **hasRequiredMetricsAndKeywords** — all `mustKeep` present.
- **keepsEssence** — still true to the deep-read; not hollowed out.
- **xyzForm** — X result + Y metric + Z method; a real metric (or honest scope proxy) present.
- **withinCharLimit** — one line.
- **dualLegible** — the impact is legible to a fast, non-specialist first reader (plain-English
  outcome up front), AND the mechanism is credible to an engineer (specific tech as the tail). See the
  legibility principle in `principles.md` — this is NOT "dumb it down"; it's "lead with the outcome
  because the first pass is fast and cross-audience."
- **defensible** — no overclaim; the candidate could talk about it for 5 minutes.
- **leadVerbOk** — verb in the allowed set (soft; don't fail an otherwise-strong bullet on this alone).

NEGATIVE checks (any hit is a demerit): jargon pile-up with no plain-value signal · buried lede ·
leads with the stack · metric with no baseline · round % with no mechanism · passive / "responsible
for" / credit-ambiguous ("we/helped") · unfalsifiable claim · **AI-tell tics** (see next section).

Also fold in the elite techniques (see `bullet-writing.md`): "so what?" ladder to the highest
defendable rung · two-sided metrics > one-sided · lead with metric-or-problem, never stack ·
sandwich (business front, mechanism tail) · ownership verbs · kill nominalizations · compress
words not signal.

## The self-inflicted failure: AI-tells (add an explicit pass)
A writer+critic loop where the SAME model writes and reviews has a structural blind spot: it produces
**uniform bullet cadence** (every bullet the same Action+Result rhythm and length) and reaches for a
recognizable **AI vocabulary** — and a critic from the same model won't flag its own rhythm as odd.
Recruiters spot exactly these tells in seconds. Defend against it explicitly:
- **Banned/over-used words** (hard list, don't trust the LLM to notice): delve · leverage · spearheaded ·
  orchestrated · synergized · seamless · robust · cutting-edge · results-driven · passionate about ·
  meticulous · tapestry · "in the realm of". (Kill on sight; swap for a specific verb + concrete noun.)
- **Cadence variation** — after the loop, review the bullets AS A SET: if every bullet is the same
  length and Verb-…-metric shape, deliberately vary sentence structure and length. Uniformity is the
  tell, not any single bullet.
- **Suspiciously clean numbers** — a column of round numbers (50%, 100%, 2x, 10k) reads generated. Real
  work has odd numbers (r≈0.54, 92ms→24ms, 1,200 merchants); prefer the specific true figure.
- Inject **only-you-could-know specifics** (exact tool name, team size, the actual bug) — these are both
  more defensible AND the strongest anti-AI-tell signal.

## CRITICAL: human-verify the critic's approvals
The critic lacks full ground truth. It once approved a "verified 100%" claim that was a real
overclaim (the system honestly abstains). **After the workflow returns, a human (or the main
agent with the deep-read context) must sanity-check each approved bullet for integrity and
reject/rewrite any overclaim.** Integrity is not delegable to the critic — the negative criteria
above reduce sycophancy but do not replace ground truth.

## Reference implementation
A working script (schemas for BULLET/CRITIC, the writer/critic prompts, the parallel refine
loop) lives alongside this file: `writer-critic-workflow.js`. To reuse: edit the `BULLETS`
array (each with essence/mustKeep/leadVerbs/latexName), keep the schemas + loop, re-run via
`Workflow({ script })`. Char limit, PASS threshold, MAX_ROUNDS, and the rubric are parameterized
at the top.

## Sources
- Critic/judge design — build-reliable-agents `critic-judge-design` skill (one-job, structured
  reasoning-before-verdict, score→derived-binary, loop guard).
- LLM-as-judge rubric best practices, incl. **negative criteria to counter sycophancy** and
  length-neutrality — galtea.ai/blog/llm-as-a-judge-prompts-templates-rubrics-and-best-practices.
- AI-tell detection (uniform cadence + AI vocabulary as the recruiter-visible tells) —
  jobscan.co/blog/can-ats-detect-ai-resume.
