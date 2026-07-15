# resume-builder

A Claude skill for writing one-page, ATS-friendly technical resumes — aimed at
software / AI / LLM engineers.

## What it does
Builds a resume section by section: pick a target lane, read each project for what's
actually worth saying, drop it into an ATS-safe LaTeX template, and tighten every bullet
with a writer/critic loop until it fits one line. Each bullet leads with a plain-English
outcome (the first reader is a fast, non-specialist screener) and keeps the mechanism as a
tail. The rules are backed by 2026 research with sources and confidence tags, and the
writer/critic loop is built to resist its own failure modes — rubber-stamping overclaims,
and the uniform-cadence "AI tells" a same-model loop tends to produce.

## Structure
- `SKILL.md` — the process and the rules.
- `references/`
  - `principles.md` — the rubric, bullet checklist, verb bank, editorial axes
  - `resume-craft.md` — templates, ATS reality (parsing, not a keyword robot), section order, skills
  - `bullet-writing.md` — elite bullet techniques (impact ladder, dual-legible sandwich, AI-lab signals)
  - `market-fit.md` — how to research which roles/companies fit a candidate (+ 2026 title/tier findings)
  - `work-authorization.md` — F-1/OPT/sponsorship strategy on a resume (disclose vs omit, the portal trap)
  - `jd-tailoring.md` — per-JD tailoring method + a paste-able prompt
  - `cover-letter.md` — when a cover letter is worth writing (and when it isn't) + a non-AI-slop structure
  - `writer-critic-workflow.md` + `.js` — the writer/critic bullet workflow and critic design
  - `worked-example.md` — one bullet start-to-finish on a synthetic candidate
- `commands/`
  - `tailor-resume.md` — a `/tailor-resume` slash command that runs the per-JD tailoring
    method on a pasted JD + master resume. Copy it into `.claude/commands/` to use it.

## License
MIT © 2026 Jiaqi (Victoria) Duan
