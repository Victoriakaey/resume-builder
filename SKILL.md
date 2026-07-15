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
- **Defensibility over modesty (not moral purity).** Push each bullet to the strongest rung
  you can talk about for 5 minutes — round up, frame hard, pick the best honest angle
  (under-selling is the more common failure). But don't cross into what unravels under
  "how did you do X?": invented metrics, unused tools, unbuilt work. In technical/AI lanes
  the interview probes hard — a claim that collapses there is worse than not having it, and
  it taints the whole resume. A critic can approve an overclaim; a human must still catch it.
- **Capability lives in bullets, not in the Skills list.** Concepts (RAG, multi-agent,
  evals) get demonstrated in Experience/Projects; the Skills line is concrete tools only.
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
- **Targeting & constraints** — company tiers, location, work authorization, level, comp.
- **The thesis / throughline** — the one-sentence story a recruiter should remember. A
  narrative arc (a throughline tying the person's background to what they build now) beats a
  pile of projects. Surface its root (a formative prior field, a founding story) rather than burying it.
Record these in a `strategy.md`-style doc so they survive across sessions.

### 2. Deep-read each project/repo for ESSENCE (before writing bullets)
A naive summary ("reviews code", "spec-to-ship workflow") misses what's impressive. Spawn
a subagent to read the real architecture/design docs/source and return: the essence (why
it's non-trivial), the hardest/most novel things, and honest bullet-worthy highlights with
any real numbers. Write bullets FROM this, never from the README top line.

### 3. Template & format (ATS-safe)
- Default: **r/EngineeringResumes LaTeX template** (XCharter, single-column, `\hfill`
  dates, `\pdfgentounicode=1`, ~0.4in margins). Tight, clean, ATS-parsable.
- Single column, standard headings ("Experience"/"Projects"/"Skills"/"Education"), contact
  in the body, `Month YYYY` dates, "Present" ok, no tables/columns/icons.
- One line ≈ 95–100 visible characters at 11pt / 0.4in margins.
- See `references/resume-craft.md` for templates, ATS parsing, self-employment/founder
  entry format, skills-section rules.

### 4. Section order (new-grad→early-career, experience-strong)
Skills → Experience → Projects → Awards & Publications → Education. Put the strongest,
present-signal, OSS/independent work FIRST (AI labs explicitly say so).

### 5. Write each bullet with the writer+critic loop
Run a **Workflow** (writer→critic, ~4 rounds, parallel across bullets). Each bullet must
pass: fluent · keeps required metrics + tech keywords · keeps essence · **XYZ form**
(X result / Y metric / Z method) · one line (≤~100 visible chars) · varied lead verb
(don't repeat across bullets) · recruiter-skimmable AND engineer-impressive (the
"sandwich": business payload front, mechanism tail) · **defensible**. See the reusable
script pattern in `references/writer-critic-workflow.md`. **Always human-review the
critic's approvals for integrity** — the critic lacks full ground truth.

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
The master is generic. For each application, swap in the JD's exact keywords, reorder to hit
the target level's headline competency, and re-check one page. (A dedicated tailoring
command/prompt can drive this.)

## Guardrails checklist (run before "done")
one page · single column · standard headings · every bullet XYZ + defensible · ≥1 eval
bullet for AI roles · no unbuilt work / unused tools · verbs varied · concepts in bullets
not Skills · thesis legible in <10s · strongest/OSS work first.

## References
- `references/principles.md` — the rubric + 10-point bullet checklist + verb bank.
- `references/resume-craft.md` — templates, ATS parsing, formatting, skills section.
- `references/bullet-writing.md` — elite bullet techniques (ladder, sandwich, AI-lab signals).
- `references/writer-critic-workflow.md` — the reusable writer+critic Workflow script.
- (Populate references/ by copying from the project's `docs/research/*` — kept in sync there.)
