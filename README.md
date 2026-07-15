# resume-builder

A Claude skill for writing one-page, ATS-friendly technical resumes — aimed at
software / AI / LLM engineers.

## What it does
Builds a resume section by section: pick a target lane, read each project for what's
actually worth saying, drop it into an ATS-safe LaTeX template, and tighten every bullet
with a writer/critic loop until it fits one line.

## Structure
- `SKILL.md` — the process and the rules.
- `references/`
  - `principles.md` — bullet checklist and verb bank
  - `resume-craft.md` — templates, ATS parsing, formatting, skills section
  - `bullet-writing.md` — bullet-writing techniques
  - `market-fit.md` — how to research which roles and companies fit a candidate
  - `writer-critic-workflow.md` + `.js` — the writer/critic bullet workflow

## License
MIT © 2026 Jiaqi (Victoria) Duan
