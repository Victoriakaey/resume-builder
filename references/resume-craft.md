# Resume Craft — consolidated research (formatting · ATS · templates · skills)

Distilled from web-research passes run 2026-07-14. Companion to `../research.md`
(market fit + AI-resume craft) and `../principles.md` (rubric + bullet checklist).
This file is knowledge-base material for the future resume-writing **skill**.

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

## 4. Bullet writing — basics (elite techniques in `bullet-writing.md`)

- **XYZ (Google/Bock)**: "Accomplished **X** (result) as measured by **Y** (a number) by doing **Z**
  (method)." All three present, order flexible, front-load the metric when strong.
- Verb + object + metric + method; **one idea per bullet** (a stacked business consequence is OK);
  ≤20 words SWE / ≤30 AI; strong past-tense verb; **don't repeat a verb >2×**.
- **Keep every number**; when no hard number, substitute scope/breadth/comparative (X→Y)/frequency.
- **AI-specific**: name specific models (Claude Sonnet, GPT-4.1) — top resumes do it 3.4×; lead with
  production metrics (p95, QPS, **cost-per-call**) > model metrics > framework fluency; ship ≥1 eval
  bullet (72% of AI resumes have none = 2026 disqualifier); agentic+reliability = top differentiator.
- **Ban**: responsible for / worked on / helped / leveraged / utilized. Cut filler + vague adjectives.
- **10-point checklist** (in `../principles.md`): strong verb · your action · a number · impact-not-task
  · method named · one idea · ≤20–30 words · no filler · AI: metric tied to business · defensible.
- **Two-audience**: bullet must be recruiter-skimmable (≥1 plain value signal) AND engineer-impressive
  (the hard mechanism). Don't make it 100% jargon.

## 5. Sources (strongest, for the skill's reference list)
- r/EngineeringResumes wiki + checklist (community rubric + free reviews) — reddit.com/r/EngineeringResumes/wiki
- Google XYZ — sweresume.app/articles/xyz-method-resume · inc.com (Bock)
- AI-engineer playbook — resumeoptimizerpro.com/blog/ai-engineer-resume-examples · resumeadapter.com/blog/ai-engineer-resume-keywords
- ATS parsing — jobscan.co/blog/resume-tables-columns-ats · atscore.ai/blog/resume-skills-section-ats
- Templates — github.com/jakegut/resume · github.com/r-engineeringresumes/resume-templates · docs.rendercv.com
- Anti-fabrication resume-agent — github.com/ARPeeketi/claude-resume-kit (provenance tags, verb discipline, 5-reader critique)
- Bullet craft — resumly.ai (4-C, ML metrics) · resumeworded.com (quantify, verbs)
