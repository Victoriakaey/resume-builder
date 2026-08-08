# Critic separation test

A critic that cannot tell generated prose from human prose is decoration. Run
this whenever the rubric changes.

1. Shuffle the twelve letters from `fixtures/letters_ai_sounding.md` and
   `fixtures/letters_human.md` into one unlabelled list. Both fixtures are still to
   be written — six generated letters and six of the account holder's own, one per
   `##` heading in each file, stripped of every company name and personal detail
   before they land in this public repo.
2. Have the critic score each one, with no other context.
3. Compute the separation: **the highest human score must be below the lowest
   AI-sounding score** — lower totals mean more human-sounding under this rubric,
   so "more human" reads as a lower number, not a higher one.

**Pass:** clean separation. **Fail:** any overlap — the rubric is not
discriminating and must not be trusted to gate a revision loop.

Record the run's scores and verdict in the run report. This test is deliberately
not automated in pytest: it needs a model in the loop, and a hard-coded expected
score would rot the moment the rubric changes.
