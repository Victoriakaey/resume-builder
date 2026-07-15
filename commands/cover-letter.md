---
description: Draft a cover letter for ONE job description using the resume-builder skill's method — runs the whether-to-write gate first, then generates a letter from the person's REAL material (resume + dossier + strategy), and returns the letter + why-this-shape rationale + honest gaps + a format/AI-tell check. Never invents metrics or fit.
argument-hint: [paste the JD, or a path/URL to it]
---

# /cover-letter

Draft a cover letter for ONE job description. This runs the `resume-builder` skill's
cover-letter method: it decides whether a letter is even worth writing, then builds one from
experience the person can actually defend — one angle, one company artifact, real numbers. It
never manufactures fit; a claim you can't say in an interview is worse than no letter at all.

## Inputs
- **Job description** — `$ARGUMENTS`: pasted text, a file path, or a URL (fetch it if a URL).
  If empty, ask the user to paste the JD before proceeding.
- **The person's material** — read, in this order:
  - `docs/dossier.md` if it exists — **read FIRST.** It sets the register/voice and the off-limits
    guardrails the letter MUST honor (don't re-propose a killed claim; keep the person's own cadence).
  - `resume.tex` / `resume.md` / `RESUME.*` — the proven experience + metrics the letter draws from.
    Work from the plain-text content, not a compiled PDF.
  - `strategy.md` / `profile.md` — lane + throughline + the work-auth strategy (decides whether work-auth
    is mentioned at all — default OUT unless the posting explicitly raises it; see `work-authorization.md`).
  - `candidate-profile.md` **if it exists** — the reusable substance / STAR story bank; when present,
    prefer its quantified stories as the achievement source.

## Method — do NOT reimplement from memory
The authoritative method is the resume-builder skill's `references/cover-letter.md` (the ordered
generation pipeline, hook patterns, fast company-research, match-without-mirroring, format-by-channel,
anti-slop). Read it and follow its pipeline; the checklist below is a reminder, not a substitute.

1. **Triage first — should this letter exist?** Apply the reference's channel/tier gate: referral /
   small team / career-changer / mission-lab = worth it; blind big-tech portal = usually unread. If it
   reads low-ROI, say so plainly + the reason, and write only if the user still wants it.
2. **Research the company (~10 min).** Find ONE concrete recent artifact (shipped feature, eng-blog post,
   OSS PR, paper, changelog) — see the reference's by-company-type guide + fast-find queries.
3. **Pick the ONE angle** — the strongest overlap between that artifact and one thing the person built.
   Decide it BEFORE drafting.
4. **Draft** — hook (one of the 4 patterns) → map 1–2 real achievements → company-knowledge paragraph →
   forward-looking close. Real material only; never invent a metric.
5. **De-slop pass** — vary sentence length, one specificity anchor per paragraph, kill the tricolon, read
   aloud, strip banned vocab and clichéd openers.

## Output — exactly these four
1. **The letter** — 250–400 words (or the channel-appropriate length), ready to send.
2. **Why this shape** — the ONE angle chosen, the hook type, which 1–2 achievements were pulled, and the
   specific company artifact referenced.
3. **Gaps I can't honestly claim** — where the fit is thin or a requirement isn't real for this person;
   surfaced, never smuggled into the prose.
4. **Format + AI-tell check** — the de-slop result, the channel/format recommendation (email body vs PDF
   vs portal free-text), and how work-auth was handled (and why).

## Guardrails
- Only real, defensible experience (from the resume / candidate-profile). Never invent a metric or a fit.
- Enforce the dossier's guardrails and register — the letter must not re-propose an off-limits claim, and
  must sound like the person, not like an LLM.
- Specificity over adjectives: one concrete detail no other applicant could write, per paragraph.
- Never mirror JD language verbatim — demonstrate the keyword, don't repeat it (the resume is the ATS
  surface, not the letter).
- One angle, one thesis. Don't try to cover the whole JD.
