# Critic separation test

A critic that cannot tell generated prose from human prose is decoration. Run
this whenever the rubric changes.

0. **Prerequisite:** the seven anti-AI criteria are supplied and `SKILL.md`'s rubric
   no longer says OPEN. Until then this test cannot run, and the two fixtures below
   are deliberately absent — see Task 12 Step 4.
1. Shuffle the twelve letters from `fixtures/letters_ai_sounding.md` and
   `fixtures/letters_human.md` into one unlabelled list. Both fixtures are still to
   be written; build them in the pass that fills in the rubric, from six generated
   letters and six of the account holder's own, stripped of every company name and
   personal detail before they land in a public repo.
2. Have the critic score each one, with no other context.
3. Compute the separation: the lowest human score must exceed the highest
   AI-sounding score.

**Pass:** clean separation. **Fail:** any overlap — the rubric is not
discriminating and must not be trusted to gate a revision loop.

Record the run's scores and verdict in the run report. This test is deliberately
not automated in pytest: it needs a model in the loop, and a hard-coded expected
score would rot the moment the rubric changes.
