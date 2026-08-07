#!/usr/bin/env bash
# Assert the job-discovery skill states the rules that keep Step 2 honest.
# Run from repo root: bash tests/test_job_discovery_skill.sh
set -uo pipefail
SKILL="skills/job-discovery/SKILL.md"
fails=0

want() {  # want <label> <regex>
  if /usr/bin/grep -qiE "$2" "$SKILL"; then
    echo "PASS  $1"
  else
    echo "FAIL  $1  (no match for: $2)"; fails=$((fails + 1))
  fi
}

# Each pattern above must be tight enough that deleting the sentence it guards
# turns this test red. A pattern with a short generic alternative — a bare
# `OPEN`, a bare `prose only` — passes on prose that no longer states the rule,
# which is a guard that guards nothing. Task 12's mutation harness deletes each
# guarded sentence from SKILL.md and requires this file to fail; add a case
# there for every `want` line added here.

want "states the pass cap is counted, not judged"   "cap[^.]*counted in code|counted in code[^.]*not judged"
want "states the best pass ships, not the last"     "highest[- ]scoring pass, not the last"
want "forbids editing the factual front matter"     "never edit[^.]*front matter"
want "names both evidence sources"                  "dossier\.md"
want "names the answer store too"                   "application-answers\.md"
want "marks the seven criteria as still open"       "rubric[^\n]*open, not yet supplied"
want "forbids inventing the criteria"               "do not invent them|never invent them"
want "states which sections gate the append"        "notes. is optional; the other four sections gate the append"
want "names unverified/ and the flag that reads it" "reads .unverified/. only with .--include-unverified."

if [ "$fails" -eq 0 ]; then echo "ALL PASS"; else echo "$fails FAILED"; exit 1; fi
