---
description: Tailor a master resume to ONE job description using the resume-builder skill's method — outputs a tailored Skills line, reordered bullets, an honest gaps list, and the portal knockout answers to expect. Surfaces and re-words REAL experience only; never invents or inflates.
argument-hint: [paste the JD, or a path/URL to it]
---

# /tailor-resume

Tailor a master resume to ONE job description. This runs the `resume-builder` skill's
per-JD tailoring method: it surfaces and re-words experience the master ALREADY proves,
in the employer's exact vocabulary. It never manufactures fit — a keyword you can't defend
collapses in the screen call.

## Inputs
- **Job description** — `$ARGUMENTS`: pasted text, a file path, or a URL (fetch it if a URL).
  If empty, ask the user to paste the JD before proceeding.
- **Master resume** — locate it: check the repo for `resume.tex` / `resume.md` / `RESUME.*`,
  else ask the user to paste or point to it. Work from the plain-text content, not a compiled PDF.

## Method — do NOT reimplement from memory
The authoritative method is the resume-builder skill's `jd-tailoring.md` reference (overlap
target, 3-location placement, anti-stuffing, portal knockout handling, integrity guardrail).
Read that reference and follow its 6 steps exactly; the summary below is a checklist, not a substitute.

1. **Extract from the JD** — must-have skills, named tools/stack in the JD's EXACT wording
   ("React.js" vs "React", "LLM evaluation" vs "evals"), and the single headline competency
   for the target level.
2. **Map coverage** — list which of those the master ALREADY demonstrates, and where; estimate
   current keyword overlap %. A strong master should already sit ~75% before tailoring.
3. **3-location placement** — for each requirement that is TRUE but under-surfaced, place it in
   exactly three spots: the Skills line · the relevant role's title/summary · the ONE bullet that
   *proves* it — in the JD's exact term. Flag any requirement genuinely missing; never paper over it.
4. **Re-order** — put the bullet demonstrating the JD's #1 competency first in the most-recent role.
   Uplevel via scope/ownership; avoid downlevel traps (leading with stack; a Projects section past ~4yr).
5. **Constrain** — stay one page, dual-legible (plain-English impact front, mechanism tail), and
   65-80% overlap. Warn the user if a change would look stuffed (modern semantic ATS penalize it) or
   spill to a second page.
6. **Portal answers** — surface the knockout answers to expect (work authorization, location,
   min-experience). These are the real auto-rejects, not a keyword bot — see the skill's
   `work-authorization.md` for the "future sponsorship" trap. A perfect resume can't fix a wrong portal answer.

## Output — exactly these four
1. **Tailored Skills line** — the JD's exact terms, core competencies bolded as the eye-anchor.
2. **Reordered bullets** — changes marked (added / moved / reworded); each still XYZ + defensible + dual-legible.
3. **Gaps I can't honestly claim** — JD requirements not real for this person; listed, never smuggled in.
4. **Portal / knockout answers to expect** — work-auth, location, min-experience.

## Guardrails
- Every added keyword must map to real, demonstrable work.
- Tailoring must not push to a second page or smuggle in a claim the base resume didn't defend.
- Match-% tools (Jobscan, Teal, Simplify) are a *coverage check*, not a target to game.
