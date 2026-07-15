# Market-Fit Research — the method

How to figure out which companies, roles, and titles best fit a given candidate — and how
the hiring bar differs across tiers — so the resume can be positioned for the highest-yield
lane. This is a reusable RESEARCH METHOD, not any one person's results. Run it per candidate.

## Inputs to gather first (the profile)
- **Lane** the person wants (e.g. LLM/Agent engineer vs Applied ML vs fullstack vs infra).
- **Strongest real signals** — shipped systems, founding/ownership experience, awards, OSS,
  publications, standout projects (with any concrete scale/metrics).
- **Constraints** — location, work authorization / sponsorship need, level target, comp goal.
- **Self-named weak spots** (e.g. DSA) — for prep prioritization only, never to narrow scope.

## The research (spawn a web-research pass; 5–8 searches)
Ask, concretely:
1. **Which role titles fit this profile and are actively hiring** — and what each title really
   wants day-to-day (e.g. AI Engineer, Applied AI Engineer, Member of Technical Staff,
   Founding Engineer, Product/Agent Engineer, Forward-Deployed Engineer). Titles are not
   interchangeable; map each to the competencies it screens for.
2. **What each company TIER screens for at top-of-funnel, and how loops differ** — frontier
   labs vs AI startups vs big tech. (Frame interview-bar differences as prep-prioritization,
   never as eligibility gating.)
3. **Which company TYPES give this profile the best yield/fit** — and why (e.g. a founding-
   engineer track record is a rare credential for seed/Series-A roles; a regulated-vertical
   background is a reusable wedge only if it's a genuine, defensible strength).
4. **Named companies actually hiring** in the target location + lane (application-layer / agent
   startups / product companies / labs), with sources.
5. **Realistic level + comp bands** for that profile in that market.
6. **Where to source roles continuously** (e.g. YC Work-at-a-Startup, Simplify, Wellfound,
   Built In, curated new-grad GitHub lists, company career pages).

## Turning research into positioning
- **Rank lanes by yield/fit**, not prestige. Pick a PRIMARY lane; the resume's master version
  targets it. Other lanes become light variants at tailoring time (shared spine → cheap forks).
- **Match the resume's emphasis to what the top lane screens for** (e.g. AI labs weight
  reliability / production scale / infra cost and say to put OSS/independent work at the top;
  startups weight shipped, real-user projects and ownership).
- **Don't over-anchor on a thin credential.** If a "differentiating" background turns out to be
  shallow or undefendable on closer questioning, dial it back — an overclaim that collapses in
  interview costs more than a narrower, honest positioning.
- **Respect the person's stated preferences** — don't push them toward a lane/title they've said
  they don't want, even if the market data favors it.

## Integrity note
Everything surfaced here is input to HONEST positioning. Never invent fit, inflate a credential,
or list a target the person can't credibly pursue. Market fit sharpens the truth; it doesn't
manufacture one.

## Freshness
The AI-engineering hiring bar shifts fast — re-run the research per candidate rather than trust
stale numbers. Strong source types: engineering-resume communities, ex-recruiter writeups, AI-lab
hiring analyses, YC/startup job boards, comp-data aggregators.

---

## 2026 reusable findings (re-verify per candidate — these age fast)

**Title → what it screens for** (titles are NOT interchangeable; match the *work*, not the label):
- **Member of Technical Staff (MoTS)** — frontier-lab flat title (Anthropic/OpenAI) that collapses
  research + eng; screens for depth, ownership, ability to cross research↔engineering. Tells you little
  about level (huge bands). Title-matching a lab resume is futile — match the work.
- **AI Engineer** — application layer: LLMs, APIs, RAG, orchestration, deployment. NOT model training.
- **Applied AI Engineer** — takes big models → scalable internal products; ML-adjacent depth + eval suites.
- **Forward-Deployed Engineer (FDE)** — customer-embedded builder, no sales quota, ships on customer
  infra; screens for SWE fundamentals + extreme-ambiguity comfort + end-to-end ownership + customer
  aptitude. Exploding demand. Shares FDE↔Applied-AI mission (make model capability work in a real env).
- **Founding Engineer (AI startup)** — broadest bar: full-stack + LLM integration + eval-framework
  design + fast shipping + inference-cost management + product instinct; must show 0-1/1-5 ownership.
- **Research/ML Engineer** — model-centric (PyTorch, scaling, CUDA). Conflating this with "AI Engineer"
  is a fast rejection in 2026 — recruiters are strict about the split.

**Bar by tier (top-of-funnel):** frontier labs weight demonstrated ability over credentials —
**Anthropic's careers page literally says to put OSS / independent research / a blog post at the TOP
of your resume**, and ~half their technical staff had no prior ML experience (so "need a PhD" is a
myth). Funded startups weight shipped agentic systems + eval discipline + 0-1 ownership + cost
awareness. Big tech weights production-at-scale + standard DSA screen.

**AI-lane signals that generic SWE advice misses (LangChain State of Agent Engineering 2025-26):**
observability is table-stakes (94% of production teams); evals are the *differentiator* but only ~52%
run offline evals (so it's an edge, not a baseline); quality/latency are the top production blockers,
NOT cost (leading a resume with fine-tuning/cost-cutting can mis-signal); most teams don't fine-tune
(57% rely on base models + prompt eng + RAG). Must-have: a shipped LLM/agent system + evals-with-a-metric
+ RAG/agent orchestration in bullets + a public artifact.

**Sourcing leverage (this changes where resume-perfection pays off):** per application, a referral is
worth roughly *40 cold applications* (referred candidates ~4-5× more likely to be hired) — yet by
*volume* cold-apply is still the #1 source of offers because far more people do it. Implication: resume
perfection has sharply diminishing returns on the cold-apply channel (you're one of hundreds) and high
leverage on the referral channel (a human already sponsors and reads it). A resume skill that ignores
sourcing over-optimizes the low-yield channel. Boards current in 2026: HN "Who is Hiring", Wellfound,
ai-jobs.net, Simplify.jobs curated lists, YC Work-at-a-Startup, RemoteOK (AI/ML).

**Cover letters** still expected more often than not (even when "optional") for competitive/eng/AI
roles — and are the natural home for work-auth context under the omit-from-resume strategy.

### Sources (confidence)
- **HIGH / primary:** anthropic.com/careers (OSS-at-top; ~half staff no prior ML) · LangChain *State of
  Agent Engineering* 2025-26 (eval/observability/blocker data).
- **MED:** dataexec.io (per-tier bar) · newsletter.pragmaticengineer.com (FDE) ·
  fde.academy (FDE vs Applied-AI) · recruitingfromscratch.com (founding-engineer bar) ·
  cnbc.com 2026-01-12 (cold-apply still #1 by volume) · refer.me / mylivecv (referral per-attempt lift).
- **LOW (directional):** interviewquery, resumeoptimizerpro, ai-jobs board aggregators.
