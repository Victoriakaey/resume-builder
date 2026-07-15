---
name: resume-builder
description: >
  Build or rebuild a strong, ATS-safe, one-page technical resume — especially for
  software / AI-agent / LLM engineers. Use when someone wants to write a resume from
  scratch, rebuild an existing one, position for a lane (e.g. AI/Agent vs ML vs
  fullstack), tighten bullets, or tailor to a job description. Runs a research-backed,
  integrity-first, section-by-section process with a writer+critic agent loop per bullet.
---

# resume-builder

A repeatable process for building a top-tier technical resume. Born from rebuilding a
Lane-1 AI/Agent-engineer resume end-to-end. **Core belief: the gap between a weak and a
strong resume is usually packaging & information architecture, not the person's ability.**

## Non-negotiables (read first)
- **Read the dossier first (if it exists).** Before any work, if `docs/dossier.md` exists in the
  user's resume repo, read it — it is this person's accumulated ground truth: project points in
  their words, off-limits claims (guardrails), and register/process preferences. It **overrides
  the generic defaults below.** Missing = a new user; you'll bootstrap it in step 1.
- **Defensibility over modesty (not moral purity).** Push each bullet to the strongest rung
  you can talk about for 5 minutes — round up, frame hard, pick the best honest angle
  (under-selling is the more common failure). But don't cross into what unravels under
  "how did you do X?": invented metrics, unused tools, unbuilt work. In technical/AI lanes
  the interview probes hard — a claim that collapses there is worse than not having it, and
  it taints the whole resume. A critic can approve an overclaim; a human must still catch it.
- **Capability lives in bullets, not in the Skills list.** Concepts (RAG, multi-agent,
  evals) get demonstrated in Experience/Projects; the Skills line is concrete tools only.
- **Dual-legible bullets.** The first pass over a resume is fast and often by a generalist
  screener working from a checklist — not the engineer who reads it later. Lead each bullet with a
  plain-English outcome (what changed, graded in the fast scan); keep the specific mechanism + stack
  as the tail (engineer credibility + ATS keywords). This is NOT "write down to non-technical people";
  it's respecting a fast, cross-audience first read. Never lead with the stack — it fails both readers.
- **Trailer, not documentation.** Show the protagonist, a few great frames, then stop.
  Leave depth for the interview. Reduce what you show at once — that reads as confidence.
- **Discovery, not judgment.** Frame gaps as "here's what's not landing yet", never as a
  scorecard. Don't gatekeep the person by a self-named weakness (e.g. DSA) — it informs
  prep priority, never eligibility.

## The process (section by section, don't rush)

### 1. Intake & positioning
Establish, before writing anything:
- **Lane** — what role family (e.g. LLM/Agent engineer vs Applied ML vs fullstack). Pick
  one; it drives every emphasis. Don't cosplay a lane the person doesn't want.
- **Targeting & constraints** — company tiers, location, level, comp, and **work authorization**.
  For international candidates, work-auth is a real screen that fires *before* bullet quality
  matters (disclose-vs-omit, dated phrasing, the portal "future sponsorship" trap) — decide it
  early; see `references/work-authorization.md`. Also weigh **sourcing**: per application a referral
  is worth ~40 cold applies, so resume-perfection pays off most on the referral channel — route
  effort accordingly (see `references/market-fit.md`).
- **The thesis / throughline** — the one-sentence story a recruiter should remember. A
  narrative arc (a throughline tying the person's background to what they build now) beats a
  pile of projects. Surface its root (a formative prior field, a founding story) rather than burying it.
Record these in a `strategy.md`-style doc so they survive across sessions.

**Dossier (read-first / bootstrap).** Read `docs/dossier.md` in the user's resume repo before
re-asking anything: it already holds the lane, project points, guardrails, and preferences from
prior sessions — do NOT re-derive what's there. Scan its **Guardrails** section before writing any
bullet. If the file is ABSENT (new user), copy `references/dossier-template.md` into the user's repo
as `docs/dossier.md` and fill it during this intake — the dossier grows from session 1, no manual
setup. On read, if a `[durable]` entry looks contradicted by recent work, FLAG it ("this may be
stale — still holds?") rather than silently applying or auto-retiring.

### 2. Deep-read each project/repo for ESSENCE (before writing bullets)
A naive summary ("reviews code", "spec-to-ship workflow") misses what's impressive. Spawn
a subagent to read the real architecture/design docs/source and return: the essence (why
it's non-trivial), the hardest/most novel things, and honest bullet-worthy highlights with
any real numbers. Write bullets FROM this, never from the README top line.

**Point vs mechanism — read the PRODUCT before the code.** Source code gives you *mechanisms*
(there's a separate reviewer, an evidence guard, a git hook); it does NOT give you the *point*
(what the thing is FOR, its one-sentence soul). If you build the resume from mechanisms you'll
keep mistaking a component for the point and churn endlessly. For a **shipped/public product read
its own positioning FIRST** — landing page, docs, how the founder pitches it to users — *that's*
where the throughline lives; read code AFTER, only to make a chosen claim defensible. And when the
project is the **user's own**, the person is the ground truth: get the essence *in their words*
(ask, or read their product's framing) — do NOT reconstruct it via subagents and hand them your
guesses to QA. A wrong essence makes every downstream bullet wrong.

### 3. Template & format (ATS-safe)
- Default: **r/EngineeringResumes LaTeX template** (XCharter, single-column, `\hfill`
  dates, `\pdfgentounicode=1`, ~0.4in margins). Tight, clean, ATS-parsable.
- Single column, standard headings ("Experience"/"Projects"/"Skills"/"Education"), contact
  in the body, `Month YYYY` dates, "Present" ok, no tables/columns/icons.
- One line ≈ 95–100 visible characters at 11pt / 0.4in margins.
- See `references/resume-craft.md` for templates, ATS parsing, self-employment/founder
  entry format, skills-section rules.

### 4. Section order (branch by seniority — see `references/resume-craft.md §3b`)
Experience-strong / founder / shipped-independent-work: Skills → Experience → Projects → Awards &
Publications → Education. Thin work history (new-grad): float Education & Projects UP, right after
Skills. Either way, put the strongest, present-signal, OSS/independent work FIRST (AI labs explicitly say so).

### 5. Write each bullet with the writer+critic loop
Run a **Workflow** (writer→critic, ~4 rounds, parallel across bullets). Each bullet must
pass: fluent · keeps required metrics + tech keywords · keeps essence · **XYZ form**
(X result / Y metric / Z method) · one line (≤~100 visible chars) · specific lead verb
(reuse is fine — flag *weak* verbs, not repetition) · **dual-legible** (plain-English impact
front, mechanism tail) · **defensible**. Build the critic right — it's where loops fail:
**negative criteria** (demerits for jargon-pile-up / buried impact / stack-first / round-number-
no-mechanism) are the anti-sycophancy fix; structured `present/missing/violations` enumeration
*before* a numeric score; derive pass/fail in code, not an LLM boolean; add an explicit
**anti-AI-tell pass** (banned-word list + vary cadence — a same-model loop produces the exact
uniform-rhythm tells recruiters catch). See `references/writer-critic-workflow.md`. **Always
human-review the critic's approvals for integrity** — the critic lacks full ground truth.

**Spine before bullets — and know when the loop is the WRONG tool.** Decide the entry's ONE
throughline FIRST (what should a reader remember about this project?), then write bullets top-down
that ladder off it — never bottom-up, polishing isolated bullets before the story is set. The
writer/critic loop refines **wording only**. If you're several rounds deep and the corrections are
about **facts** ("that's not what it does") or **what to feature** ("that's not the point / feels
off / no focus"), STOP re-wording — the problem is upstream: wrong ground truth (→ go back to step 2,
read the product/ask the person) or wrong altitude/selection (→ re-decide the spine and which facts
earn a bullet). Ten wording passes never fix a bullet that's about the wrong thing. Two failure
smells to catch early: it reads like a **feature list with no point** (missing spine), or like a
**pitch/marketing** (spine carried by adjectives/mission instead of concrete built work).

**Capture durable learnings to the dossier inline.** The moment a durable learning happens — the
person corrects a pattern, decides a guardrail, or nails a project's point in their words — offer a
one-line "record to dossier?". Distinguish durable vs one-off when offering ("a general preference,
or just this bullet?") to set the `[durable]` vs `[context:<scope>]` tag. On yes, append immediately
(dated; guardrails to §1, points to §2, prefs to §3, and log the correction in §4). A new learning
that contradicts an existing entry SUPERSEDES it (mark the old `retired (superseded by <new>, DATE)`),
never silently deletes. All writes are user-approved.

### 6. Bullet craft (the rules the critic enforces)
- XYZ + the "so what?" ladder (task→output→outcome→business); stop at the highest
  DEFENDABLE rung.
- Two-sided metrics (92ms→24ms) > one-sided (−68%); named checkable numbers > round %.
- Lead with the metric when the outcome is the flex; with the problem/system when the HOW
  is the flex; NEVER lead with the stack (downlevels you).
- Ownership verbs (Owned/Drove/Built), not helped/worked-on. Kill nominalizations. Compress
  WORDS not SIGNAL. Skills-buzzwords go in bullets where demonstrated.
- Full depth: `references/bullet-writing.md` (elite techniques) + `references/principles.md`
  (10-point checklist + verb bank).

### 7. Skills section
Concrete tools only (languages/frameworks/DBs/cloud/named AI tools). Concepts → bullets.
A single line with core competencies **bolded** as an eye-anchor works well and dodges
category-label disputes. 8–15 items; mirror JD terms at tailoring time, keep master generic.

### 8. Per-JD tailoring (separate later step)
The master is generic. For each application, swap in the JD's exact keywords (the employer's wording),
use the 3-location placement rule, target 65-80% overlap (don't stuff — modern ATS penalize it),
reorder to hit the target level's headline competency, and re-check one page. A paste-able tailoring
prompt + the full method are in `references/jd-tailoring.md`. For a one-shot invocation, ship the
`commands/tailor-resume.md` slash command (copy it into `.claude/commands/`) — it runs this method on a
pasted JD + master and returns the tailored Skills line, reordered bullets, an honest gaps list, and the
portal knockout answers to expect.

### 9. Close the session — write back to the dossier
Before finishing, sweep the session for durable learnings not already captured inline: new
guardrails decided, project points clarified in the person's words, register/process preferences,
and any corrections. Propose them as a short per-item list ("add these to the dossier?"); on the
user's approval, write each to the right section of `docs/dossier.md` (dated + tagged), append
corrections to §4, and supersede (not delete) anything contradicted. This is what makes the next
session start smarter — never skip it.

> **See it end-to-end:** `references/worked-example.md` traces one bullet through the whole loop on a
> fully-synthetic candidate — writer draft → critic (present/missing/violations/score) → ship-ready,
> plus the cross-bullet AI-tell review. Read it to see the negative criteria and dual-legibility in action.

## Guardrails checklist (run before "done")
one page (early/mid-career) · single column · standard headings · every bullet XYZ + defensible ·
**every bullet dual-legible (impact up front, no bullet 100% jargon)** · ≥1 eval bullet for AI
roles · no unbuilt work / unused tools · specific (not weak) verbs · **no AI-tells (varied cadence,
no banned words, odd true numbers not clean round ones)** · concepts in bullets not Skills · thesis
legible in <10s · strongest/OSS work first · **work-auth strategy decided (if international)**.

## References (each carries sourced findings + confidence tags; 2026 web research)
- `references/principles.md` — the rubric + 10-point bullet checklist + verb bank + editorial axes.
- `references/resume-craft.md` — templates, ATS reality (parsing-corruption not keyword-robot), section
  order by seniority, formatting, skills section.
- `references/bullet-writing.md` — elite bullet techniques (ladder, dual-legible sandwich, AI-lab signals).
- `references/writer-critic-workflow.md` — the reusable writer+critic Workflow + critic design
  (negative criteria, anti-AI-tells) + the accompanying `.js` reference script.
- `references/market-fit.md` — the market-fit research METHOD + 2026 title/tier/signal/referral findings.
- `references/work-authorization.md` — F-1/OPT/STEM-OPT/sponsorship strategy (disclose-vs-omit, the portal trap).
- `references/jd-tailoring.md` — per-JD tailoring method (3-location placement, overlap target) + paste-able prompt.
- `references/cover-letter.md` — whether to write one (conflicting data, by tier + channel) + a non-slop structure, AI-tells to avoid, AI-lab mission-fit, and the work-auth rule.
- `references/worked-example.md` — one bullet start-to-finish on a synthetic candidate (the loop, made concrete).

## Bundled command
- `commands/tailor-resume.md` — a `/tailor-resume` slash command wrapping the per-JD tailoring method.
  Copy it into `.claude/commands/`; invoke with the JD as the argument. Path-agnostic (references the
  skill by name, not a hard path), so it works wherever the skill is installed.
