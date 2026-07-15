// Reusable writer+critic Workflow for refining resume bullets.
// Run via the Workflow tool. Edit the BULLETS array for the candidate's real work
// (each bullet's `essence` comes from the project/repo deep-read step), keep the engine.
// The example BULLETS below are GENERIC placeholders showing the shape — replace them.

export const meta = {
  name: 'refine-resume-bullets',
  description: 'Writer+critic loop refining resume bullets to one line each, XYZ, essence-preserving',
  phases: [{ title: 'Refine', detail: 'writer->critic loop per bullet, parallel' }],
}

const CHAR_LIMIT = 100 // visible chars (exclude LaTeX markup) => ~one line at 11pt / 0.4in margins

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

const CRITIC_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['fluent', 'hasRequiredMetricsAndKeywords', 'keepsEssence', 'xyzForm', 'withinCharLimit', 'recruiterSkimmable', 'defensible', 'leadVerbOk', 'approved', 'feedback'],
  properties: {
    fluent: { type: 'boolean' },
    hasRequiredMetricsAndKeywords: { type: 'boolean', description: 'ALL mustKeep present' },
    keepsEssence: { type: 'boolean', description: 'real technical essence survives, not hollow' },
    xyzForm: { type: 'boolean', description: 'X result + Y metric + Z method; a real metric present' },
    withinCharLimit: { type: 'boolean' },
    recruiterSkimmable: { type: 'boolean', description: 'not 100% jargon; >=1 plain value signal' },
    defensible: { type: 'boolean', description: 'no overclaim/fabrication' },
    leadVerbOk: { type: 'boolean', description: 'lead verb in the allowed set' },
    approved: { type: 'boolean', description: 'true only if every other check is true' },
    feedback: { type: 'string', description: 'specific fix instructions if not approved' },
  },
}

function writerPrompt(b, prevLatex, critFeedback) {
  return `You are writing ONE resume bullet for a software/AI engineer (LaTeX, r/EngineeringResumes template).

BULLET ESSENCE (the truth to convey): ${b.essence}
MUST KEEP (all): ${b.mustKeep.map(x => '- ' + x).join('\n')}
NICE TO HAVE (only if space): ${(b.niceToHave || []).join('; ')}

HARD RULES:
- ONE line: <= ${CHAR_LIMIT} VISIBLE characters (exclude LaTeX markup).
- XYZ: accomplished X (result) as measured by Y (a number) by doing Z (method). A metric MUST appear (or honest scope if no hard number exists — never invent one).
- Start with an action verb from: ${b.leadVerbs.join(', ')} (distinct across bullets, no verb repeats).
- Bold key terms/metrics with \\textbf{}. ${b.latexName ? 'Use this product name token verbatim: ' + b.latexName : 'Do NOT restate the product name (continues the same entry).'}
- Fluent natural voice (dodge AI-detector uniformity). Recruiter must grasp >=1 clear value signal; not 100% jargon. Prefer the "sandwich": business payload up front, mechanism in the tail.
- Defensible: only what the essence supports; no overclaim.
- Output ONLY the bullet body (no "\\item"). Use --- for em-dash, $\\sim$ for tilde.
${prevLatex ? `\nPREVIOUS DRAFT (revise): ${prevLatex}\nCRITIC FEEDBACK: ${critFeedback}` : ''}`
}

function criticPrompt(b, draft) {
  return `Adversarial resume-bullet critic. Approve ONLY if ALL criteria pass.

ESSENCE (ground truth): ${b.essence}
MUST KEEP: ${b.mustKeep.join('; ')}
ALLOWED LEAD VERBS: ${b.leadVerbs.join(', ')}
CHAR LIMIT: ${CHAR_LIMIT} visible chars (exclude LaTeX markup).

DRAFT: ${draft.latex}
Writer's visible-char count: ${draft.visibleChars}

Check: fluent; all must-keeps present; essence preserved (not hollow); XYZ (real metric, no fabricated number); within char limit (re-estimate yourself); recruiter-skimmable (not all jargon); defensible (no overclaim); lead verb allowed. Give specific fix feedback if any fail.`
}

phase('Refine')

async function refine(b) {
  let draft = await agent(writerPrompt(b), { label: `write:${b.id}`, phase: 'Refine', schema: BULLET_SCHEMA })
  for (let round = 1; round <= 4; round++) {
    if (!draft) break
    const crit = await agent(criticPrompt(b, draft), { label: `crit:${b.id}:${round}`, phase: 'Refine', schema: CRITIC_SCHEMA })
    if (!crit) break
    if (crit.approved) return { id: b.id, latex: draft.latex, rounds: round, approved: true, chars: draft.visibleChars }
    draft = await agent(writerPrompt(b, draft.latex, crit.feedback), { label: `rewrite:${b.id}:${round}`, phase: 'Refine', schema: BULLET_SCHEMA })
  }
  return { id: b.id, latex: draft ? draft.latex : null, rounds: 4, approved: false, chars: draft ? draft.visibleChars : null }
}

const results = await parallel(BULLETS.map(b => () => refine(b)))
// IMPORTANT: a human must still verify each approved bullet for integrity — the critic
// lacks full ground truth and may approve an overclaim. Reject/rewrite any before use.
return results.filter(Boolean)
