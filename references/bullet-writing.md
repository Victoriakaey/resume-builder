# Bullet Writing — elite/advanced techniques

Deep research on what separates a good bullet from a top-tier one (senior / AI-lab /
FAANG level). Basics (XYZ, verb bank, one-line, checklist) live in `principles.md`
and `resume-craft.md §4`. This is the higher-order craft. Skill knowledge-base material.

## The anatomy (elite)
**Scope-verb + owned system + magnitude + Δmetric(baseline→new) + mechanism/tech + 2nd-order impact**, in ≤2 lines.
- Verbatim exemplar: *"Owned redesign of payment routing service handling 80K RPS, reducing p99 latency from 92ms to 24ms via Go circuit breakers; eliminated $620K of annual over-provisioning."*

## The "so what?" impact ladder — climb, stop at the highest DEFENDABLE rung
`task → output(+scale) → outcome(+Δmetric) → business/mission impact`
*("So-what ladder" is our working label, not a canonical named framework — but the underlying
escalation is well-attested: Bock's X-vs-Y separates the accomplishment from its measured impact;
systemdesign.one frames it as "show what changed because you existed, not what you did.")*
- Formula: **Action verb + task + quantifiable result + impact**. The `for [users/team]` slot forces the top rung.
- Audit each accomplishment across 5 dimensions — **volume · speed · quality · cost · revenue** — take the strongest REAL one.
- **Litmus (ex-Meta recruiter Selena Ma):** never write a bullet you can't talk about for 5 minutes. If you can't trace the chain to revenue, drop to the outcome rung (latency/reliability/incidents). Honesty = stopping at the defendable rung.

## Scale without inflation ("signal density")
- Real scope levers when no hard metric: RPS/QPS, req·day, PB/rows/events·sec, MAU/tenants/merchants, $ spend/saved, # services/teams/engineers, migration size, on-call/blast radius, incident count.
- **Named checkable numbers ("1,200 merchants", "18 months", "14 services") read as MORE credible than round percentages** ("improved 50%").
- **Two-sided metrics (92ms→24ms) beat one-sided (−68%)** — they encode the baseline. A baseline-less "improved 50%" is unfalsifiable.

## Leading — result vs method
- Lead with the **metric** when the OUTCOME is the flex.
- Lead with the **problem / owned system** when the HOW is the flex (novel architecture, hard debug) — reveal the mechanism as the payoff (Amazon "Dive Deep": *"traced to a kernel-level TCP retransmit setting"*).
- **NEVER lead with the stack** ("Using Kafka and Go, I…") — reads junior, downlevels you.

## Compression — 2 lines → 1, without losing signal
- **Verb first, subject implied** (drop "I"). Power verb must be the first word.
- **Kill nominalizations** — `-tion/-ment/-ance/-ing` nouns hide a stronger verb: "responsible for the implementation of" → "Implemented"; "performed an optimization of" → "Optimized"; "led the migration of" → "Migrated".
- Cut hedges/connectors: "helped, worked on, responsible for, involved in, in order to", most articles, "that/which" clauses.
- **Semicolon-chain** the second-order impact instead of a new sentence: "…cut deploy time to 3 min; unblocked 6 teams."
- **Compress WORDS, not SIGNAL.** Over-compression strips scope outsiders need — "Built distributed scheduler using Go" is short but empty; "…handling 10K concurrent jobs, cutting completion time 43%" is longer AND denser.

## Seniority + AI-lab signals (what juniors miss)
- Every bullet answers: **"What changed because you were there?"** — Owned / Drove / Set direction, NOT helped / contributed / was part of.
- Show **trade-offs made, ambiguity resolved, cross-team blast radius, mentorship, judgment (what you deliberately CUT).**
- **AI labs (Anthropic/OpenAI/DeepMind) read like elite INFRA resumes, not research resumes:**
  - Emphasize **reliability (uptime, incident reduction, on-call), production scale, infra cost, outage handling** — these punch above feature bullets. (Anthropic posts a "SWE, AI Reliability" req; median hire ≈12yr, ~40% infra, pedigree from Stripe/Databricks/Palantir.)
  - **Anthropic verbatim:** *"If you have done interesting independent research, written an insightful blog post, or made substantial contributions to open-source software, put that at the TOP of your resume."*
  - **Anti-pattern:** don't sound academic; generic "passion for LLMs" underperforms concrete system-building. Production skills > credentials, depth > breadth.
  - → **Implication for an AI-infra/agent candidate:** lead with shipped OSS + reliability engineering; frame the reliability/cost/determinism work as the flex, not as research.

## The two-audience problem — recruiter-legible AND engineer-impressive
- **The first reader is usually a fast, non-specialist screener working from a checklist**, not the
  engineer who'll read it later (hiring-side consensus — vmock, webuildresumes). Jargon density
  measurably hurts *because the first decision-maker can't parse it*. This is NOT a knock on
  recruiters and NOT "dumb it down" — it's respecting a fast, cross-audience first pass.
- **The "sandwich" resolves it**: FRONT = recruiter payload (scope verb + owned system +
  magnitude/metric, in plain-English business/user/perf terms); TAIL = engineer payload (mechanism +
  specific tech + the hard part). The front is graded in the fast scan; the tail earns the engineer's
  trust later AND carries the ATS keywords.
  - *"…reducing p99 from 92ms to 24ms [front] by introducing connection pooling and a Go circuit breaker [tail]."*
  - Hiring-side before/after: *"Engineered a multi-phase, six-sigma compliant process optimization"* →
    *"Developed a process improvement strategy that reduced production errors by 20%."* (impact a
    generalist can grade, up front.)
- When a technical term must stay, **expand it once** — "Energy Conservation Measures (ECMs)" — so it's
  both recruiter-legible AND keyword-searchable. Don't just delete jargon; translate it.
- Keep the impressive HOW to a **short named mechanism**, not a paragraph, so it enriches without
  breaking the ~7-second first skim (Ladders eye-tracking; small-n vendor study, treat as directional).

## Reverse-engineer from JD / leveling rubric
- Recruiters anchor **level-fit → impact-density → stack-match** in ~10s.
- Pull the JD/leveling rubric → list the target level's competencies → ensure each has ≥1 bullet that DEMONSTRATES (not asserts) it → order so the recent role's top bullet hits the headline competency.
- Map to Amazon Leadership Principles / JD competencies; each bullet should yield a 5-min STAR story.
- **Uplevel levers:** lead recent role with cross-team scope, add a mentorship bullet, quantify $/headcount. **Downlevel traps:** leading with stack, a Projects section past ~4yr experience, omitting ownership verbs.

## "Almost-good" failure modes (the subtle ones)
buried lede (payoff at line-2 end) · metric with no baseline · feature-scoped-as-initiative (verb↔scope mismatch) · tool-dump without engineering reasoning · credit ambiguity ("helped/we") · task-only/process-focused · claim with no number AND no proxy · unparseable jargon/codenames · the un-defendable bullet (can't narrate 5 min).

## Sources
**Primary / HIGH:** Laszlo Bock — linkedin.com/pulse/20140929001534-24454816 (XYZ formula +
baseline-comparison rationale) · anthropic.com/careers (put OSS/independent work at the top) ·
Strunk & White *Elements of Style* (concision/active-voice) · theladders eye-tracking PDF (7.4s scan).
**Hiring-side / MED-HIGH:** systemdesign.one/p/software-engineer-resume (impact-first, "delivered
[value] using [tech]") · vmock.com/1216-2 (expand-don't-drop jargon, checklist screening) ·
webuildresumes.com (business-value-first before/after) · formation.dev (ex-Meta recruiter, 5-min litmus).
**Directional / LOW (use, don't cite as fact):** resumeoptimizerpro.com/blog/faang-resume-guide ·
dev.to/mihaig04 (200 FAANG resumes) · sweresume.app · ai-engineering-trend.medium.com ·
sundeepteki.org · Harvard FAS action verbs · wordvice/wordrake (nominalizations).
