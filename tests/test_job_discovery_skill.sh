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

want "states the pass cap is counted, not judged"   "counted in code|not.*model.*decide|never asks the model"
want "states the best pass ships, not the last"     "highest[- ]scoring|best.*not the last"
want "forbids editing the factual front matter"     "never.*front matter|prose only"
want "names the evidence sources"                   "dossier|application-answers"
want "marks the seven criteria as still open"       "OPEN|not yet supplied|awaiting"
want "forbids inventing the criteria"               "do not invent|never invent"

if [ "$fails" -eq 0 ]; then echo "ALL PASS"; else echo "$fails FAILED"; exit 1; fi
