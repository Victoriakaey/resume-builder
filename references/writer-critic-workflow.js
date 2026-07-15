// Reusable writer+critic Workflow for refining resume bullets.
// Run via the Workflow tool. Edit the BULLETS array for the candidate's real work
// (each bullet's `essence` comes from the project/repo deep-read step), keep the engine.
// The example BULLETS below are GENERIC placeholders showing the shape — replace them.
//
// Critic design matches references/writer-critic-workflow.md:
//   - critic ENUMERATES (present/missing/violations) then emits a numeric SCORE
//   - pass/fail is derived in CODE from the score, never an LLM boolean
//   - NEGATIVE criteria (demerits) counter sycophancy
//   - an explicit anti-AI-tell check (banned words + cadence)
//   - loop guard: MAX_ROUNDS + feedback-dedupe, independent of critic judgment

export const meta = {
  name: 'refine-resume-bullets',
  description: 'Writer+critic loop refining resume bullets to one line each, XYZ, dual-legible, essence-preserving',
  phases: [{ title: 'Refine', detail: 'writer->critic loop per bullet, parallel' }],
}

// ---- Tunables (parameterized so you don't touch the engine) ----
const CHAR_LIMIT = 100   // visible chars (exclude LaTeX markup) => ~one line at 11pt / 0.4in margins
const PASS_SCORE = 4     // critic score (1-4) required to approve; derived in CODE, not by the LLM
const MAX_ROUNDS = 4     // HARD exit independent of critic judgment
// AI-tell words to ban on sight (a same-model loop reaches for these; recruiters spot them):
const BANNED_WORDS = ['delve', 'leverage', 'leveraged', 'spearheaded', 'orchestrated', 'synergized',
  'seamless', 'robust', 'cutting-edge', 'results-driven', 'passionate', 'meticulous', 'tapestry']

// ---- EXAMPLE placeholder bullets (replace with the candidate's real essence) ----
const BULLETS = [
  {
    id: 'example-core',
    leadVerbs: ['Built', 'Shipped', 'Engineered'],
    latexName: '\\href{https://example.com/}{\\underline{ProjectName}}',
    essence: 'PLACEHOLDER: one paragraph of the true, non-trivial essence of this project — what it is, the hard/novel part, and the honest scale/cost/metric — taken from the codebase/project deep-read. Do not invent numbers.',
    mustKeep: ['the primary metric', 'the core technical insight / differentiator'],
    niceToHave: ['scale (LOC / users / hosts)', 'named model or key tech'],
  },
  {
    id: 'example-second',
    leadVerbs: ['Designed', 'Architected', 'Grounded'],
    latexName: null, // null = continues the same entry; don't restate the product name
    essence: 'PLACEHOLDER: the second strongest, honest point about the same role/project — a distinct idea from bullet 1.',
    mustKeep: ['the key mechanism/keyword for this point'],
    niceToHave: [],
  },
]

const BULLET_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['latex', 'visibleChars', 'leadVerb'],
  properties: {
    latex: { type: 'string', description: 'The LaTeX bullet body (what follows \\item), \\textbf{} on key terms/metrics, latexName verbatim for the product name. No leading \\item.' },
    visibleChars: { type: 'integer', description: 'VISIBLE rendered characters, EXCLUDING LaTeX markup (\\textbf{}, \\href{}{}, \\underline{}; $\\sim$ = 1 char, --- = 1 dash).' },
    leadVerb: { type: 'string', description: 'The first word (action verb).' },
  },
}

// Critic ENUMERATES first, then SCORES. No `approved` boolean — the engine derives pass/fail.
// Field ORDER matters: the model fills present/missing/violations BEFORE score, so the score is
// grounded in the enumeration rather than an early guess it then justifies.
const CRITIC_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['present', 'missing', 'violations', 'score', 'feedback'],
  properties: {
    present: { type: 'array', items: { type: 'string' }, description: 'Rubric criteria the draft MEETS (terse tags, not prose).' },
    missing: { type: 'array', items: { type: 'string' }, description: 'Required criteria NOT met (mustKeep gaps, no metric, over char limit, not dual-legible, etc.).' },
    violations: { type: 'array', items: { type: 'string' }, description: 'NEGATIVE hits (demerits): jargon pile-up, buried impact, stack-first, round-number-no-mechanism, passive/no-owner, unfalsifiable claim, AI-tell word, uniform-cadence.' },
    score: { type: 'integer', minimum: 1, maximum: 4, description: '1=broken, 2=weak, 3=solid-minor-fixes, 4=ship-ready. Score from the enumeration above; do NOT reward length.' },
    feedback: { type: 'string', description: 'Specific fix instructions (what to change), only if score < 4.' },
  },
}

function writerPrompt(b, prevLatex, critFeedback) {
  return `You are writing ONE resume bullet for a software/AI engineer (LaTeX, r/EngineeringResumes template).

BULLET ESSENCE (the truth to convey): ${b.essence}
MUST KEEP (all): ${b.mustKeep.map(x => '- ' + x).join('\n')}
NICE TO HAVE (only if space): ${(b.niceToHave || []).join('; ')}

HARD RULES:
- ONE line: <= ${CHAR_LIMIT} VISIBLE characters (exclude LaTeX markup).
- XYZ: accomplished X (result) as measured by Y (a number) by doing Z (method). A metric MUST appear (or honest scope if no hard number exists — never invent one). Prefer the SPECIFIC true number (r$\\sim$0.54, 92ms$\\to$24ms, 1,200 users) over a clean round one (50%, 2x) — round numbers read generated.
- Start with an action verb from: ${b.leadVerbs.join(', ')}.
- DUAL-LEGIBLE (the load-bearing rule): lead with a plain-English outcome a fast, non-specialist screener can grade; put the specific mechanism + stack in the TAIL (engineer credibility + ATS keywords). NEVER lead with the stack.
- Bold key terms/metrics with \\textbf{}. ${b.latexName ? 'Use this product name token verbatim: ' + b.latexName : 'Do NOT restate the product name (continues the same entry).'}
- BANNED words (do not use): ${BANNED_WORDS.join(', ')}. Use a specific verb + concrete noun instead.
- Defensible: only what the essence supports; no overclaim.
- Output ONLY the bullet body (no "\\item"). Use --- for em-dash, $\\sim$ for tilde.
${prevLatex ? `\nPREVIOUS DRAFT (revise): ${prevLatex}\nCRITIC FEEDBACK: ${critFeedback}` : ''}`
}

function criticPrompt(b, draft) {
  return `You are an adversarial resume-bullet critic. ENUMERATE first, then SCORE — do not decide a verdict then justify it.

ESSENCE (ground truth): ${b.essence}
MUST KEEP: ${b.mustKeep.join('; ')}
ALLOWED LEAD VERBS: ${b.leadVerbs.join(', ')}
CHAR LIMIT: ${CHAR_LIMIT} visible chars (exclude LaTeX markup).
BANNED WORDS: ${BANNED_WORDS.join(', ')}

DRAFT: ${draft.latex}
Writer's visible-char count: ${draft.visibleChars} (re-estimate yourself).

POSITIVE criteria (list the ones MET in \`present\`, the required ones NOT met in \`missing\`):
fluent · all must-keeps present · essence preserved (not hollow) · XYZ with a REAL metric (no fabricated number) · within char limit · DUAL-LEGIBLE (plain-English impact up front, not 100% jargon) · lead verb allowed.

NEGATIVE criteria — list every hit in \`violations\` (these are DEMERITS, not neutral):
jargon pile-up with no plain-value signal · buried lede (impact at the end) · leads with the stack · a round % with no mechanism · an unfalsifiable / suspiciously-clean claim · passive voice / "responsible for" / credit-ambiguous ("we/helped") · any BANNED word · a metric with no baseline.
An unfalsifiable or suspiciously-round claim with no mechanism is a demerit, NOT a neutral.

Then SCORE 1-4 from the enumeration (4 only if \`missing\` and \`violations\` are BOTH empty). Do not reward a longer bullet for being longer. Give specific fix feedback only if score < 4.`
}

phase('Refine')

async function refine(b) {
  let draft = await agent(writerPrompt(b), { label: `write:${b.id}`, phase: 'Refine', schema: BULLET_SCHEMA })
  let prevFeedback = null
  for (let round = 1; round <= MAX_ROUNDS; round++) {
    if (!draft) break
    const crit = await agent(criticPrompt(b, draft), { label: `crit:${b.id}:${round}`, phase: 'Refine', schema: CRITIC_SCHEMA })
    if (!crit) break
    const approved = crit.score >= PASS_SCORE   // pass/fail derived in CODE, not by the LLM
    if (approved) return { id: b.id, latex: draft.latex, rounds: round, approved: true, score: crit.score, chars: draft.visibleChars }
    if (crit.feedback && crit.feedback === prevFeedback) break  // dedupe: critic is cycling, stop
    prevFeedback = crit.feedback
    draft = await agent(writerPrompt(b, draft.latex, crit.feedback), { label: `rewrite:${b.id}:${round}`, phase: 'Refine', schema: BULLET_SCHEMA })
  }
  return { id: b.id, latex: draft ? draft.latex : null, rounds: MAX_ROUNDS, approved: false, chars: draft ? draft.visibleChars : null }
}

const results = await parallel(BULLETS.map(b => () => refine(b)))
// IMPORTANT: a human must still verify each approved bullet for integrity — the critic
// lacks full ground truth and may approve an overclaim (negative criteria reduce this but do
// not replace ground truth). Also review the bullets AS A SET for uniform cadence (the AI-tell a
// same-model loop can't see in any single bullet). Reject/rewrite any before use.
return results.filter(Boolean)
