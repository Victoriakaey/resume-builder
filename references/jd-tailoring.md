# Per-JD Tailoring — method + a paste-able prompt

The master resume is generic. For each application you fork it and align it to one job
description. Keep this cheap: a shared spine, light per-JD forks — don't rewrite the resume.

## Why bother (and how much)
- A tailored resume out-performs the same resume untailored (directional consensus; the exact
  "40-60% more" figures floating around are content-mill — treat as "meaningfully better", not fact).
- But route effort by CHANNEL: per application a referral is worth ~40 cold applies. Tailoring
  pays off most where a human will actually read it (referral, or a small number of high-fit cold
  apps). Don't spend an hour tailoring for a role you're firing into a portal blind. (See `market-fit.md`.)

## The mechanics (designable, bounded — not "add keywords")
1. **Extract the JD's real requirements.** Pull the must-have skills, the named tools/stack, and the
   headline competency for the target level. Note the JD's EXACT wording ("React.js" vs "React";
   "LLM evaluation" vs "evals") — mirror the employer's term, not your synonym.
2. **Target 65-80% keyword overlap** with the posting. Below that you don't rank in recruiter search;
   above it you look stuffed and modern semantic ATS *penalize* manipulation (they detect repetition
   and cross-reference your LinkedIn). Your master should already sit ~75% before tailoring.
3. **3-location placement rule** — for each missing-but-true requirement, place it in exactly three
   spots: (a) the Skills line, (b) the relevant role's title/summary line, (c) the ONE bullet that
   *proves* it. Proof in the employer's language beats repetition. Never repeat a phrase 5+ times.
4. **Reorder to the target level's headline competency.** Put the bullet that demonstrates the JD's
   #1 ask as the first bullet of the most recent role. Uplevel by leading with scope/ownership;
   avoid downlevel traps (leading with stack; a Projects section past ~4 yrs experience).
5. **Portal answers are part of tailoring.** The genuine ATS auto-rejects are knockout questions
   (work authorization, location, min-experience), not a keyword bot — answer them honestly and
   correctly (see `work-authorization.md` for the "future sponsorship" trap). A perfect resume can't
   fix a wrong portal answer.
6. **Re-check one page + integrity.** Tailoring must not push to a second page or smuggle in a claim
   the base resume didn't defend. Every added keyword must correspond to real, demonstrable work.

## Integrity guardrail
Tailoring mirrors the truth in the employer's vocabulary; it never manufactures fit. If a required
skill isn't real for you, don't insert it — a keyword you can't defend collapses in the screen call.
Tools that give a "match %" (Jobscan, Teal, Simplify) are useful as a *coverage check*, not a target
to game.

## Paste-able tailoring prompt
> You are tailoring my master resume to ONE job description. Do NOT invent or inflate — only surface
> and re-word real experience already in the master.
>
> **Inputs:** [paste MASTER resume] and [paste JOB DESCRIPTION].
>
> **Do this:**
> 1. Extract from the JD: must-have skills, named tools/stack (exact wording), and the single headline
>    competency for the target level.
> 2. List which of those the master ALREADY demonstrates, and where. Estimate current keyword overlap %.
> 3. For each requirement that's TRUE for me but under-surfaced, propose the 3-location placement
>    (Skills line · role title/summary · the one proving bullet), using the JD's exact term. Flag any
>    JD requirement I genuinely lack — do NOT paper over it.
> 4. Propose a bullet re-ORDER so the most-recent role leads with the JD's #1 competency.
> 5. Keep it one page, dual-legible (impact-first), and within 65-80% overlap — warn me if a change
>    would look stuffed or push to a second page.
> 6. Output: (a) the tailored Skills line, (b) the reordered bullets with changes marked, (c) a short
>    "gaps I can't honestly claim" list, (d) the portal work-auth/knockout answers to expect.

## Sources
- 65-80% overlap target + 3-location placement — owlapply.com, scale.jobs, jobscan.co (MED).
- Keyword-stuffing now penalized / manipulation detected by semantic ATS — owlapply.com (HIGH-directional).
- Knockout questions are the real auto-reject, not a keyword bot — jobscan.co, apply-mate.com (HIGH).
- Match-% tools (coverage check, not a target) — jobscan.co, tealhq, simplify.jobs.
