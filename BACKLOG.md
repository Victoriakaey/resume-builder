# Backlog

Ideas not yet built. Each is a design sketch, not a commitment — brainstorm before building.

## Per-user dossier — "the skill gets better the more you use it"

**Problem.** The skill re-learns the person every session: re-derives their projects' *points*,
re-asks positioning, and re-makes mistakes it already made (re-proposing a claim that was killed,
mischaracterizing a project, using a register the person dislikes). A single hard session can burn
20+ rounds rediscovering things that were true the whole time.

**Mechanism (not model fine-tuning — a persistent read-first/write-back profile).** A structured
per-user dossier the skill **reads FIRST every session and appends to at the end**. Over sessions it
converges: session 2 onward the skill writes in the person's register, avoids their known landmines,
and applies their decided guardrails from word one — so each session needs less correction. Difference
between a new collaborator (explain everything) and a year-in one (already knows the taste).

**What the dossier holds** (the four things that cause the most churn when missing):
1. **Project points, in the person's own words** — the one-sentence soul of each project (NOT its
   mechanisms). Stored once, reused forever. For shipped/public products this comes from the product's
   own positioning, not the source code.
2. **Positioning** — lane, targeting, constraints, the throughline.
3. **Decisions + guardrails** — what to feature, and an explicit **OFF-LIMITS-claims list** (things
   that are undefendable, mischaracterized, or already rejected). Read before every bullet so a killed
   claim is never re-proposed.
4. **Preferences + corrections log** — register/voice, style, process preferences, and an append-only
   log of "when the person corrected a pattern, and what the durable lesson was."

**The loop.** Read at session start → don't re-ask/re-derive/re-mistake. Append what was learned at
session end → next session is closer to the person's real preference and needs.

**Design cautions (so it doesn't over-fit):**
- Distinguish **durable preferences** from **one-off, project-specific** ones — don't promote a single
  instance to a rule.
- Keep every entry **overridable** — the person can always contradict the dossier.
- **Stale preferences must be refreshable/retirable** — supersede, don't cargo-cult old taste.
  (Same discipline as good long-term memory systems: supersession + honest provenance.)
- Skill body stays **generic**; the dossier is **per-user and private** (lives with the user's own
  resume repo, like a `docs/dossier.md`), never baked into the published skill.

**Status:** designed at the sketch level; not built. Next step = a proper brainstorm on the schema,
the read-first hook, and the write-back discipline.
