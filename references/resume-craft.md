# Resume Craft — formatting · ATS · templates · skills

The craft layer of the skill's knowledge base (2026 web research, sourced below). Companion to
`principles.md` (rubric + bullet checklist), `bullet-writing.md` (elite techniques), and
`market-fit.md` (which roles/companies fit a candidate).

---

## 1. Templates (ATS-safe, one-page, LaTeX)

| Template | Format | ATS-safe | Density | Link |
|---|---|---|---|---|
| **r/EngineeringResumes .tex** ✅ chosen | LaTeX (XCharter) | Yes, single-col | tight, small name | github.com/r-engineeringresumes/resume-templates |
| Jake's Resume | LaTeX | Yes (widely tested) | **airy** (big `\Huge` name, loose `\vspace`) | github.com/jakegut/resume |
| sb2nov/resume | LaTeX | Yes | tighter than Jake's | github.com/sb2nov/resume |
| RenderCV (`engineeringresumes` theme) | YAML→Typst | Yes, 99% parse | tight, minimal | github.com/rendercv/rendercv |
| basic-resume (stuxf) | Typst | Yes | very tight | typst.app/universe/package/basic-resume |
| altacv / two-column | LaTeX | ⚠️ **NO** (columns scramble parsing) | dense | avoid for ATS |
| Awesome-CV / moderncv | LaTeX | icons+color = mild ATS risk | moderate | — |

- **Chosen: r/EngineeringResumes .tex** (XCharter serif, 0.4in margins, `\hfill` right-aligned
  dates, `\pdfgentounicode=1`). Reasons: tight/clean, single-column, stays in Overleaf/LaTeX.
- **Jake's `tabular*` caveat**: the "no tables for ATS" rule targets multi-column BODY layouts;
  a single-row right-aligned-date `tabular*` extracts linearly and is fine. r/EngineeringResumes
  avoids tabular entirely (uses `\hfill`), so it's the safer bet.
- Compaction levers (any template): shrink name (`\Huge`→`\LARGE`), cut margins to ~0.4in, reduce
  `\vspace`, tighten `\titleformat` spacing, `\setlist{itemsep=-2pt}`, 10–11pt body.
- **~one line ≈ 95–100 visible chars** at 11pt XCharter / 0.4in margins (measured). Target ≤100
  visible chars (exclude LaTeX markup) for a one-line bullet; words don't break, so leave margin.

## 2. Formatting & ATS parsing (experience entries)

**Reality check first (2026): the "keyword robot that auto-rejects your resume" is largely a myth
for the ATS tech companies actually use.** Greenhouse does not algorithmically score or auto-reject
(its CEO says so); Lever is human-first. The genuine auto-rejects come from **knockout/screening
questions** in the portal (work authorization, location, min-experience), triggered by *your
answers*, not a secret reading of your resume. Workday/Taleo are stricter parsers but still
auto-reject via those questions, not keyword bots. So:
- **The real failure mode is PARSING CORRUPTION, not rejection.** A multi-column or table layout
  makes the parser attach Company A's title to Company B, or shift your dates a year — and then you
  stop surfacing in recruiter searches. You're not rejected; you're garbled and invisible.
- **Keywords matter for DISCOVERABILITY** (recruiter Boolean search over parsed fields), not as a
  pass/fail gate. Once a human opens it, "they see your resume exactly as you submitted it."
- Ignore the inflated "75% auto-rejected by ATS" / "must use these 3 ATS fonts" SEO folklore. Any
  standard embedded (non-decorative) font parses; a text-based PDF parses fine except the pickiest
  Taleo configs. Avoid *decorative/symbol* fonts and icon glyphs — that's the real rule.

- ATS parses the **whole document** into fields (Title, Company, Dates, Location, Bullets) by
  matching **standard heading keywords**. Skills section is a "concentrated lookup table" but
  bullets are matched too — **keywords in bullets DO count** (no need to duplicate into Skills).
- ~80% of keyword matches come from Skills + Experience combined; spread top keywords 2–3× across
  the doc. Don't keyword-stuff (AI-ATS flags it).
- **Clean experience entry** (title + company on separate lines, then dates, then bullets):
  ```
  Job Title, Company -- City, ST                    Month YYYY -- Present
  - bullet ...
  ```
- **Breaks parsing**: multi-column/tables for the header; **two orgs/titles stacked in one entry**
  (bullets mis-anchor — but two PRODUCTS as bullets under ONE role is fine); non-standard headings
  ("My Journey" → uncategorized; must say "Experience"/"Work Experience", "Projects", "Skills",
  "Education"); company in the title field; icons/graphics; header/footer contact (parsers miss it).
- **Self-employment / founder / open-source**: format like a real job. Company field = a real token
  ("Independent" / "Self-Employed" / the product name). Title = concrete role ("Founder & AI
  Engineer", not bare "Freelancer"). Add GitHub/live URL (verifiability = anti-inflation). 3+
  substantial projects → a "Projects"/"Open Source" section; a single one → a bullet under a job.
- **Dates**: `Month YYYY – Month YYYY`; "Present" parses reliably; avoid 2-digit years / seasons.
- **Contact in the body**, never header/footer. Underlining links is optional (clickability signal);
  keep consistent across the doc or none.

## 3. Skills section

- **Concrete, nameable tools dominate** (languages, frameworks, libraries, DBs, cloud, named AI
  frameworks/vector-DBs/model-APIs/eval-tools). Hard skills = 70–80%.
- **Concepts/methodologies belong in bullets, not Skills** — "RAG", "multi-agent orchestration",
  "prompt engineering", "evals" asserted bare in Skills read as padding and hurt credibility;
  demonstrated in an Experience/Project bullet they earn credit AND get ATS-matched. Rule: a concept
  goes in Skills only if it also appears in a bullet.
- 8–15 items sweet spot; >20 looks unfocused. 4–6 categories × 3–5 items, OR a single line.
- No proficiency ratings ("Python 8/10"), no soft skills, no tables/bars/icons.
- Mirror the JD's exact term (write "LangGraph" if JD says LangGraph; "Google Cloud Platform (GCP)"
  to cover both forms) — but **do exact-matching at the per-JD tailoring step**, keep the master generic.
- **A pattern that works well**: a single line with the **core competencies bolded** as the
  eye-anchor, the rest as breadth — avoids category-label disputes and stays compact.
- For an AI/LLM engineer, legit LISTable AI tools: LangChain, LangGraph, LlamaIndex, AutoGen, CrewAI,
  OpenAI/Anthropic/Gemini APIs, Ollama, Hugging Face, Pinecone/Chroma/Weaviate/pgvector, LangSmith/
  ragas/DeepEval/promptfoo/W&B. SHOW-in-bullets (don't list): RAG, multi-agent, prompt-engineering,
  fine-tuning, function-calling/tool-use, evals.

## 3b. Section order & length (branch by seniority)
- **Standard headings only** ("Skills" / "Experience" or "Work Experience" / "Projects" /
  "Education") — creative headings ("My Journey") parse as uncategorized. Non-negotiable.
- **Early-career / new-grad (thin work history):** Skills → **Education & Projects float UP** →
  Experience. Put whichever of Education/Projects is strongest right after Skills; projects are the
  primary substitute for experience — **link GitHub/live per project** (verifiable = load-bearing for juniors).
- **Experience-strong (real industry / founder / shipped independent work):** Skills → **Experience
  first** → Projects → Education (Education sinks). Lead with present-signal, OSS/independent work —
  AI labs (Anthropic, verbatim) explicitly say to put independent research / OSS / a blog post at the TOP.
  → This is the branch a founder/independent-builder profile takes even when early-career by years.
- **One page:** real and near-mandatory for early/mid-career (new-grad reviewers often stop at page 1);
  flex to two pages only for senior/staff with genuinely substantive content, never as padding. Min 10pt
  for human readability. Don't fight fragile `\vspace` hacks to force one page — compress content instead.

## 4. Bullet writing — basics (elite techniques in `bullet-writing.md`)

- **XYZ (Laszlo Bock, ex-Google — primary source)**: "Accomplished **X** (result) as measured by
  **Y** (a number) by doing **Z** (method)." All three present, order flexible, front-load the metric when strong.
- Verb + object + metric + method; **one idea per bullet** (a stacked business consequence is OK);
  ≤20 words SWE / ≤30 AI; strong SPECIFIC past-tense verb (reuse is fine — flag weak verbs, not repeats).
- **Keep every number**; when no hard number, substitute scope/breadth/comparative (X→Y)/frequency.
- **AI-specific**: name specific models (Claude Sonnet, GPT-4.1), not bare "LLM"; lead with
  production metrics (p95, QPS, **cost-per-call**) > model metrics > framework fluency; ship ≥1 eval
  bullet (a differentiator — only ~52% of teams run offline evals, but screeners weight it);
  agentic+reliability = top differentiator, observability = table stakes.
- **Ban**: responsible for / worked on / helped / leveraged / utilized. Cut filler + vague adjectives.
- **10-point checklist** (in `principles.md`): strong verb · your action · a number · impact-not-task
  · method named · one idea · ≤20–30 words · no filler · AI: metric tied to business · defensible.
- **Two-audience (dual-legible)**: plain-English impact up front for the fast generalist first read,
  specific mechanism as the tail for the engineer + ATS. Not "dumb it down" — see `bullet-writing.md`
  → two-audience problem, and `principles.md` rule 5b.
- **Work authorization** is its own dimension (disclose-vs-omit, dated phrasing, the portal
  "future sponsorship" trap) — see `work-authorization.md`.

## 5. Sources (with confidence)
- **HIGH / primary:** github.com/r-engineeringresumes/resume-templates (live template — XCharter,
  single-col) · Greenhouse-no-algo-scoring via jobscan.co/blog/greenhouse-ats-what-job-seekers-need-to-know ·
  blakecrosley.com/work/ats-insider (parsing-corruption mechanism) · inc.com/LinkedIn (Bock XYZ).
- **MED:** techinterview.org (one-page by seniority) · apply-mate.com/blog/workday-taleo-greenhouse-ats
  (knockout-question auto-reject) · resumegenius/tealhq (self-employment formatting) · docs.rendercv.com.
- **Community rubric:** r/EngineeringResumes wiki + checklist (reddit.com/r/EngineeringResumes/wiki —
  fetch often blocked; corroborate via the community LaTeX template).
- **Mine, don't cite as fact:** resumeoptimizerpro / resumeadapter (AI-engineer playbooks) · resumly.ai ·
  resumeworded. **Related tool:** github.com/ARPeeketi/claude-resume-kit (provenance tags, verb
  discipline, banned-word list, 5-reader critique) — aligns with the integrity bar, worth mining.
