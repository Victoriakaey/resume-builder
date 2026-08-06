#!/usr/bin/env bash
# Contract checks for the job-application subskill and its template.
set -uo pipefail
fails=0
note() { echo "FAIL: $1"; fails=$((fails+1)); }

s="skills/job-application/SKILL.md"
t="references/application-answers-template.md"

[ -f "$s" ] || note "missing $s"
[ -f "$t" ] || note "missing $t"

if [ -f "$s" ]; then
  head -1 "$s" | grep -q '^---$'            || note "SKILL.md has no frontmatter"
  grep -q '^name: job-application$' "$s"    || note "frontmatter name is not job-application"
  grep -q '^description: ' "$s"             || note "frontmatter has no description"
  # The four boundaries the design says are non-negotiable.
  grep -qi 'never .*submit'  "$s"           || note "no never-submit rule"
  grep -qi 'never .*upload'  "$s"           || note "no never-upload-resume rule"
  grep -qi 'ats-playbook'    "$s"           || note "does not point at the ATS playbook"
  grep -qi 'answer store'    "$s"           || note "does not mention the answer store"
fi

if [ -f "$t" ]; then
  for h in "## Constants" "## Policies" "## Material blocks"; do
    grep -qF -- "$h" "$t" || note "template missing section: $h"
  done
fi

# Both files must survive the personal-content guard. The guard's exit code
# is meaningful: 1 means it found forbidden content; 2 means it could not
# check at all (e.g. a given path does not exist). Conflating the two would
# send a reader hunting for "personal content" when the real problem is a
# missing file.
guard_out="$(bash scripts/check_no_personal.sh "$s" "$t" 2>&1)"
guard_rc=$?
case "$guard_rc" in
  0) : ;;
  1) note "personal content found: $guard_out" ;;
  2) note "guard could not check (given: $s $t): $guard_out" ;;
  *) note "guard exited unexpectedly ($guard_rc): $guard_out" ;;
esac

[ "$fails" -eq 0 ] && echo "ALL PASS" || exit 1
