# Resume Principles — the rubric

Distilled from (a) a benchmark resume that landed OpenAI/Anthropic interviews, (b) a strategy
review, and (c) 2026 web research now integrated with sources + confidence (see `## Sources` and
the sourced criteria in `writer-critic-workflow.md`). Scannable rule + one-line why.
**Confidence discipline:** where a widely-repeated number is content-mill and unsourced, it's
replaced or hedged below — say "studies suggest", don't cite fake precision.

## Hierarchy & story

> **0. Know the ceiling before you start.** A resume is a low-signal document and the
> screening of it is close to chance: 76 technical recruiters producing ~2,200 evaluations of
> 1,000+ resumes, scored against those candidates' real interview outcomes, were **55%**
> correct on "would I interview this person" (a companion write-up: **53%**, Fleiss' κ **0.13**);
> two randomly chosen recruiters differ by **41 percentage points** on the SAME resume; the
> median look is **31 seconds**. What the skim rewards is largely unearnable at edit time —
> prior FAANG employment is picked **35%** more often, and the top rejection reasons are
> credential-shaped (no top firm, no top school). *So the honest leverage order is:*
> **(1) referral / direct outreach · (2) a recognisable anchor on the page (rule 10b, awards,
> publications) · (3) bullet craft.** Bullet craft is a floor to clear, not a lever to pull.
> Say this out loud to the person early — it is the difference between a session that ends and
> a session that loops on wording forever. *(interviewing.io, 2024–2026; see `market-fit.md`.)*

1. **Trailer, not documentation.** Show protagonist → why → a few great frames →
   stop. *Why: a reader who already knows everything has no reason to interview you.*
2. **One protagonist.** Recruiter must know which project matters most.
   *Why: no main character = no memory anchor.*
3. **Serve the thesis arc.** Order/phrase every section to make the throughline
   legible (see `strategy.md`). *Why: a story beats a pile; competitors have no thesis.*
4. **Top-load identity.** First signal = "they build AI agents", not "they know React".
   *Why: a fast first scan decides the fate.*

## Bullets
5. **What → Why → How**, in that order. `Built X to improve Y using Z`.
   *Why: leading with "how" (tool soup) buries the point.*
5b. **Dual-legible: lead with a plain-English outcome, keep the mechanism as the tail.** The first
   pass over a resume is fast and often by a generalist screener working from a checklist — not the
   engineer who'll read it later. So the *impact* clause (what changed, in words anyone can grade)
   goes up front; the *mechanism* (specific tech, the hard part) is the tail that earns an engineer's
   trust AND carries the ATS keywords. *Why: leading with the stack fails both readers on the first
   pass — the screener can't evaluate it, the engineer isn't reading yet.* This is NOT "write down to
   non-technical people" — it's respecting a fast, cross-audience first read. When a term must stay,
   expand it once ("Energy Conservation Measures (ECMs)") so it's legible AND searchable.
   *(Well-supported: hiring-side sources + Bock; see Sources.)*
6. **Keep every number.** r≈0.54, 35%, 15%, 120ms/30% — never trim these.
   *Why: quantified results are the single biggest edge over vague competitors. (Numbers-beat-duties
   is strong consensus; specific outperformance percentages floating online are mostly unsourced.)*
7. **Cut adjectives that RATE the work; keep the ones that NAME an architectural choice.**
   Kill "robust", "scalable", "seamless", "pixel-perfect", "highly performant" — self-awarded
   grades, unfalsifiable, padding. Keep "deterministic pipeline", "session-scoped", "centrally
   orchestrated", "until acceptance or a retry limit" — each names a decision that had
   alternatives. *Test: can an interviewer turn the word into a question worth answering?
   "Why deterministic?" is a real question; "why robust?" is not.* *Why: the second kind is the
   cheapest insider signal on the page — that last example tells any agent engineer the writer
   knows a loop needs a hard exit. (Revised 2026-08-01: this rule used to order all three
   keepers killed, which threw away exactly that signal.)*
7b. **Every performance number carries its measurement condition.** `35% in staging tests` ·
   `15% as measured by completion rates` · `120ms (30%) vs unoptimized baselines` · and when a
   correlation is middling, say so — "moderately correlated (r≈0.54)". *Why: the volunteered
   limit is what makes the number credible — it shows the writer knows where it stops being
   true, and it pre-answers the interview follow-up. A bare number is a claim; a bounded number
   is a measurement.* Mechanised as the linter's `measure` check.
7c. **Enumerate to show the system's SHAPE.** "retrieval, structured search, itinerary
   synthesis, critic, and fallback" · "evaluated for factuality, feasibility, constraint
   satisfaction, safety, and currency". *Why: a reader who follows none of the detail still
   sees that the thing has structure — five named parts outperform any adjective at proving the
   work was real.*
7d. **Name the beneficiary.** therapists · 100+ university students · staff, admins and guests.
   *Why: work with nobody on the receiving end is a build; work with someone is a product.*
   Mechanised as the linter's `beneficiary` check.
7e. **One bullet = one DIFFERENT action; an entry's bullets must not be facets of one thing.**
   Five distinct actions (component library · auth/RBAC · caching · API indexing · the product)
   never feel like too many; four facets of one product feel like too many at four. *Why: when
   a reader says "too many bullets", the count is usually innocent and the sameness is the
   defect — cutting one facet just leaves three facets.* NOT mechanisable: it needs the
   entry-level pass in `writer-critic-workflow.md`, because a per-bullet critic sees each facet
   alone and approves every one of them.
8. **Strong past-tense verb; prefer a SPECIFIC verb over a generic one.** "Migrated/Cut/Benchmarked"
   over "Led/Handled/Worked on". Varying verbs across bullets is a nice polish, *but reuse is fine* —
   flag a *weak/vague* verb, not mere repetition. *Why: the myth is "never repeat a verb"; the real
   signal is verb specificity, not novelty (Forbes/TopResume debunk the no-repeat rule).*
9. **Never list unbuilt work.** *Why: collapses in interview; costs integrity.*

## Sections
10. **Skills = keyword footer — lean in PROMINENCE, complete in COVERAGE.** Least visual
    weight on the page, but do not trim the list itself to look tidy: the enumerable part is
    the only part of an automated score that behaves. When one unchanged resume was run 100×
    through HackerRank's open-sourced ATS, the checkbox section (technical skills) scored
    identically in 98 of 100 runs while the judged section (projects) swung across a
    33-point range. *Why: trimming the row costs real matches and buys only tidiness — and
    the earlier framing ("keep minimal") was read as licence to drop live lane vocabulary.*
    Still bounded by rule 11: complete **for your lane**, not for everyone.
10b. **Give an unrecognised employer a few true words of context.** `Ripplet` says nothing;
    `Ripplet (10-person healthtech startup)` gives the skim something to hold. Team size,
    sector, stage, scale — whatever is true. *Why: the 31-second skim hunts for a name it
    knows, and when it finds none the resume is judged at close to chance. This is the one
    lever on that bottleneck that does not require having worked at a famous company.*
    Never invent funding, users or scale to fill it. Flagged by the linter's `anchor` check.
10c. **Fix every typo before touching any wording.** *Why: across ~2,200 recruiter
    evaluations scored against real interview outcomes, the number of typos and grammatical
    errors was the strongest resume-side predictor of an offer — while school, GPA and
    highest degree predicted nothing at all.* This is the highest measured return of any
    edit on the page, and it is the least interesting one to make. Linter: `typo`.
11. **Match skills to the lane, not to everyone.** Copying an ML/CV skill row when
    you're an agent engineer = competing on your weakest turf. *Why: play your board.*
12. **Present signal matters.** Show `Founder — Present`. *Why: "they didn't stop
    after graduating" is a strong, cheap signal.*
13. **Surface third-party validation.** Awards + publication, one line each, not buried.
    *Why: external proof outweighs self-description; don't hide it in comments.*
14. **U.S. work-authorization / clearance up top when relevant** — but as a *strategy
    decision*, not a reflex; for international candidates it can help or hurt. *Why: instant
    screening pass for eligibility-gated roles; but a mishandled visa line/portal answer screens
    you out ahead of the resume read. See `work-authorization.md`.*

## Layout
15. **One page, calm, whitespace** (early/mid-career; senior may flex to two). *Why: dense reads
    as anxious; calm reads as confident — and new-grad reviewers often stop at page 1.*
16. **Don't fight vspace hacks.** Fragile 1-page fits break on one reflow.
    *Why: maintenance tax + risk of ugly overflow — compress content instead.*
17. **Links that prove work** (GitHub, live demos). *Why: an engineer with no visible
    code is a claim without evidence; for juniors, per-project links are load-bearing.*

## AI-engineer specific (from 2026 research — sourced below)
19. **Ship ≥1 eval bullet.** Evals are a genuine differentiator, not a baseline: only ~52% of
    production teams run offline evals (LangChain *State of Agent Engineering* 2025-26), yet
    screeners over-weight them — a resume with no eval mention risks reading as "ships unevaluated
    features." Frame it as an edge, not a universal. Name tool + outcome (ragas / LangSmith /
    Braintrust / DeepEval / promptfoo / custom harness).
20. **Name specific models/versions** (Claude Sonnet, GPT-4.1, Llama 3.3), never bare "LLM".
    *Why: named models read current; generic "LLM" reads 2023.* (Directional; the exact
    "top resumes do it Nx more" figures online are unsourced — don't cite them.)
21. **Lead with production metrics** — p95 latency, QPS, **cost-per-call** > accuracy/F1 >
    framework fluency. *Why: in 2026 the top production blocker teams report is quality/latency,
    not cost, and demos read junior — they want shipped-to-real-users (LangChain survey; Meta's
    stated "ship tools, not demos").* (A per-day inference cost like \$0.04–0.10/day is a strong concrete metric.)
22. **Agentic + reliability is the differentiator** — tool calling, MCP, long-running
    orchestration, retries/fallbacks/guardrails; **observability is table stakes** (94% of
    production agent teams). *Why: it's the scarce, senior signal.*
23. **XYZ every bullet** — "Accomplished X (as measured by Y) by doing Z"; pair a technical metric +
    a business metric. *Why: the dominant, recruiter-trained standard — Laszlo Bock (ex-Google), verbatim.*
24. **Single column, no tables/icons/multi-col, contact in body, full dates, mirror JD
    keywords.** *Why: the real ATS risk is PARSING CORRUPTION (columns/tables shuffle your
    dates & titles), not a keyword robot auto-rejecting you — see `resume-craft.md §2`.*
25. **Vary voice — dodge AI-tells.** A same-model write+critic loop produces uniform cadence + AI
    vocabulary (delve/leverage/spearheaded/orchestrated) that recruiters spot in seconds. *Fix:
    vary sentence length across bullets, kill the banned-word list, prefer odd true numbers over
    clean round ones (see `writer-critic-workflow.md` → AI-tells).*

## Bullet checklist — run EVERY bullet through this (from bullet-craft research)
`1. Strong past-tense verb  2. YOUR action (not team's)  3. A number (%, $, latency,
users, X→Y, or concrete scope if no hard #)  4. Impact not task  5. Method named (Z,
specific enough only you could write it)  6. One idea (a stacked business consequence
is OK; a 2nd unrelated achievement is not)  7. ≤20 words SWE / ≤30 AI  8. No filler /
no vague adjectives / no tech-stack dump  9. AI: model metric tied to a business outcome
10. Defensible in interview.`

- **XYZ:** "Accomplished X (measured by Y) by doing Z." All three present; order flexible
  — front-load the metric when it's strong. (Laszlo Bock, ex-Google — primary source.)
- **Ban verbs:** responsible for · worked on · involved in · helped · leveraged · utilized
  (→ used/applied). Verb variety is a light polish, not a rule — reuse is fine; flag *weak* verbs,
  not mere repetition.
- **Editorial pass (Strunk & White):** omit needless words · active voice / clear owner · concrete >
  abstract (show the action, don't assert the trait) · every word must survive "delete it — is
  meaning lost?". These are the same axes real reviewer rubrics (NACE, Yale OCS, Humboldt) score on.
- **No hard numbers?** substitute scope/breadth (5 hosts, 10k+ users), cost/day,
  comparative (850ms→210ms), frequency. A before/after pair IS a metric.
- **Verb bank:** built/shipped: Built·Engineered·Shipped·Deployed·Integrated·Automated ·
  designed: Architected·Designed·Prototyped · improved: Optimized·Reduced·Cut·Accelerated·
  Scaled·Refactored · led: Led·Spearheaded·Drove·Owned·Mentored · analyzed: Analyzed·
  Benchmarked·Diagnosed·Profiled·Evaluated.
- **Framework spine = XYZ** (metrics-forward). Borrow CAR's "challenge" clause only when a
  bullet needs a problem stated. Don't visibly mix frameworks. STAR is too long → interviews.

## Root cause (meta)
18. **The disease: "I'm so afraid they won't know how strong I am."** Every over-stuff traces
    back to it. *Fix: reduce what you show at once — not your strength. Make them remember you,
    then get curious. Less ≠ weaker. Less = confident.*

## Sources (2026 research, with confidence)
- **XYZ formula** — Laszlo Bock (ex-Google SVP People Ops), "My Personal Formula for a Winning
  Resume" (LinkedIn, 2014) + *Work Rules!*. Primary. **HIGH.** The baseline-comparison rationale
  ("is 12% a big deal? add ($1.2M)") is his own.
- **Recruiter/HR is a fast generalist first reader; jargon density hurts; impact-first resolves it**
  — vmock.com, webuildresumes.com (with before/after), systemdesign.one. **HIGH** (hiring-side consensus).
- **Reviewer rubric axes** (impact/quantified · verb-first · relevant-first · clarity · ownership ·
  scan-legibility · consistency · narrative) — NACE, Yale OCS, Humboldt, Hiration rubrics. **HIGH.**
- **Editorial concision** — Strunk & White, *Elements of Style* (omit needless words; active voice). **HIGH.**
- **AI signals** (evals a differentiator at ~52% adoption; observability table-stakes at 94%; quality/
  latency the top blocker over cost) — LangChain *State of Agent Engineering* 2025-26. **HIGH.**
- **Anthropic "put OSS/independent work at the TOP of your resume"** — anthropic.com/careers, primary. **HIGH.**
- **Myths debunked** — no-repeat-verb & "always one page" (Forbes/TopResume, seniority-gated);
  "6-second scan" is a 2018 7.4s small-n vendor study (Ladders), initial-skim only. **MED–HIGH.**
- Unsourced content-mill figures ("Nx more", "40% more callbacks", "72% of AI resumes") are
  intentionally NOT cited as fact here — the qualitative points stand on the sourced material above.
