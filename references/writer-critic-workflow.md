# Writer + Critic Workflow — reusable pattern

The engine of the skill: refine each resume bullet with a **writer→critic loop** until it
passes every rubric criterion (or a round cap). Runs via the `Workflow` tool, parallel
across bullets. This is what turns "good enough" bullets into tight, defensible, one-line ones.

## When to use
Any time you have the ESSENCE of an experience/project (from the deep-read step) and need to
turn it into 1–3 polished bullets. Also for re-polishing a section that reads flabby.

## Inputs per bullet
- `essence` — the ground-truth of what the work IS and why it's non-trivial (from the codebase/
  project deep-read). The critic checks the draft against this so it stays honest and doesn't go hollow.
- `mustKeep` — required metrics + tech keywords that cannot be dropped.
- `leadVerbs` — an allowed set of first-word verbs, DISTINCT per bullet, so verbs don't repeat
  across the entry.
- `latexName` — the exact `\href{}{\underline{...}}` product token (or null if the bullet
  continues an entry and shouldn't restate the name).
- `charLimit` — ~100 visible chars (exclude LaTeX markup) = one line at 11pt / 0.4in margins.

## The loop (per bullet, parallel across bullets)
```
draft = writer(essence, mustKeep, leadVerbs, charLimit)
for round in 1..4:
  crit = critic(draft, essence, rubric)
  if crit.approved: return draft
  draft = writer(..., prevDraft=draft, feedback=crit.feedback)
return draft   // best effort if not approved in 4 rounds
```

## Critic rubric (approve ONLY if all true)
fluent · hasRequiredMetricsAndKeywords (all mustKeep present) · keepsEssence (not hollow) ·
xyzForm (X result + Y metric + Z method; a real metric present) · withinCharLimit ·
recruiterSkimmable (≥1 plain value signal, not 100% jargon) · defensible (no overclaim) ·
leadVerbOk (verb in the allowed set).

Also fold in the elite techniques (see `bullet-writing.md`): "so what?" ladder to the highest
defendable rung · two-sided metrics > one-sided · lead with metric-or-problem, never stack ·
sandwich (business front, mechanism tail) · ownership verbs · kill nominalizations · compress
words not signal.

## CRITICAL: human-verify the critic's approvals
The critic lacks full ground truth. It once approved a "verified 100%" claim that was a real
overclaim (the system honestly abstains). **After the workflow returns, a human (or the main
agent with the deep-read context) must sanity-check each approved bullet for integrity and
reject/rewrite any overclaim.** Integrity is not delegable to the critic.

## Reference implementation
A working script (schemas for BULLET/CRITIC, the writer/critic prompts, the parallel refine
loop) ships alongside this file: **`writer-critic-workflow.js`**. To reuse: edit the `BULLETS`
array (each with essence/mustKeep/leadVerbs/latexName — essence comes from the project
deep-read), keep the schemas + loop, re-run via `Workflow({ script })`. Char limit and rubric
are parameterized at the top.
