# Bullet Writing — elite/advanced techniques

Deep research on what separates a good bullet from a top-tier one (senior / AI-lab /
FAANG level). Basics (XYZ, verb bank, one-line, checklist) live in `../principles.md`
and `resume-craft.md §4`. This is the higher-order craft. Skill knowledge-base material.

## The anatomy (elite)
**Scope-verb + owned system + magnitude + Δmetric(baseline→new) + mechanism/tech + 2nd-order impact**, in ≤2 lines.
- Verbatim exemplar: *"Owned redesign of payment routing service handling 80K RPS, reducing p99 latency from 92ms to 24ms via Go circuit breakers; eliminated $620K of annual over-provisioning."*

## The "so what?" impact ladder — climb, stop at the highest DEFENDABLE rung
`task → output(+scale) → outcome(+Δmetric) → business/mission impact`
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

## The two-audience problem — recruiter-skimmable AND engineer-impressive
- Recruiters grade business impact + scope (and "get lost in technical details"); engineers want to see real craft.
- **The "sandwich"**: FRONT = recruiter payload (scope verb + owned system + magnitude/metric, business-legible); TAIL = engineer payload (mechanism + specific tech + the hard part).
  - *"…reducing p99 from 92ms to 24ms [front] by introducing connection pooling and a Go circuit breaker [tail]."*
- Keep the impressive HOW to a **short named mechanism**, not a paragraph, so it enriches without breaking the 6–10s skim.

## Reverse-engineer from JD / leveling rubric
- Recruiters anchor **level-fit → impact-density → stack-match** in ~10s.
- Pull the JD/leveling rubric → list the target level's competencies → ensure each has ≥1 bullet that DEMONSTRATES (not asserts) it → order so the recent role's top bullet hits the headline competency.
- Map to Amazon Leadership Principles / JD competencies; each bullet should yield a 5-min STAR story.
- **Uplevel levers:** lead recent role with cross-team scope, add a mentorship bullet, quantify $/headcount. **Downlevel traps:** leading with stack, a Projects section past ~4yr experience, omitting ownership verbs.

## "Almost-good" failure modes (the subtle ones)
buried lede (payoff at line-2 end) · metric with no baseline · feature-scoped-as-initiative (verb↔scope mismatch) · tool-dump without engineering reasoning · credit ambiguity ("helped/we") · task-only/process-focused · claim with no number AND no proxy · unparseable jargon/codenames · the un-defendable bullet (can't narrate 5 min).

## Sources
resumeoptimizerpro.com/blog/faang-resume-guide · dev.to/mihaig04 (200 FAANG resumes) ·
sweresume.app (bullet + senior guides) · formation.dev (ex-Meta recruiter) ·
theinterviewguys.com/the-so-what-test · simpliresy.com (5 metric dimensions) ·
ai-engineering-trend.medium.com (Anthropic 1,680 resumes) · sundeepteki.org (OpenAI/Anthropic/DeepMind 2026) ·
wordvice/wordrake/4syllables (nominalizations) · Harvard FAS action verbs.
