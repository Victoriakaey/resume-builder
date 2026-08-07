#!/usr/bin/env bash
# Mutation tests for job-discovery's three protected rules.
#
# A test that passes proves nothing about a rule unless breaking the rule makes it
# fail. Each case below edits one line of source, runs the suite, and requires a
# RED result. Every edit is reverted whether or not the case succeeds.
#
# Run from repo root: bash tests/job_discovery/test_mutation.sh
set -uo pipefail
cd "$(dirname "$0")/../../skills/job-discovery" || exit 1
fails=0
MUTATING=""

# If this script is interrupted (Ctrl-C, a killed pytest, anything) while a
# mutation is applied, a plain cp/sed/mv sequence leaves the tracked source
# file mutated and a .bak sitting beside it — a worse state than any failing
# mutation, because a harness whose whole job is proving the tests are real
# must never be the thing that quietly breaks the tree. MUTATING names the
# file with an open edit; the trap only has work to do while it is set.
restore_now() {
  if [ -n "${MUTATING:-}" ] && [ -f "$MUTATING.bak" ]; then
    mv -f "$MUTATING.bak" "$MUTATING"
  fi
  return 0
}
trap restore_now EXIT INT TERM

assert_mutated() {  # assert_mutated <label> <file>
  # A sed expression that matches nothing leaves the file untouched, the suite
  # green, and the case indistinguishable from an unprotected rule. Task 10's
  # implementer hit exactly this: a case-sensitive pattern against prose that
  # capitalised the word deleted nothing and looked like a result. A mutation
  # that did not mutate is a harness failure, and it says so.
  if cmp -s "$1.bak" "$1"; then
    echo "FAIL  $2 — the mutation changed nothing; fix the pattern, not the code"
    return 1
  fi
  return 0
}

mutate() {  # mutate <label> <file> <sed-expression>
  local label="$1" file="$2" expression="$3"
  MUTATING="$file"
  cp "$file" "$file.bak"
  /usr/bin/sed -i '' "$expression" "$file"
  if ! assert_mutated "$file" "$label"; then
    mv "$file.bak" "$file"; MUTATING=""; fails=$((fails + 1)); return
  fi
  if PYTHONPATH=. python3 -m pytest ../../tests/job_discovery -q >/dev/null 2>&1; then
    echo "FAIL  $label — the suite stayed green with the rule broken"
    fails=$((fails + 1))
  else
    echo "PASS  $label — breaking it turns the suite red"
  fi
  mv "$file.bak" "$file"
  MUTATING=""
}

# 1. The 24-hour window must not be quietly loosened.
mutate "freshness: window loosened to a week" \
  jobdiscovery/freshness.py 's/^WINDOW_HOURS = 24$/WINDOW_HOURS = 168/'

# 2. A role with no timestamp must not slip inside the window.
mutate "freshness: missing timestamp treated as fresh" \
  jobdiscovery/freshness.py 's/(age := age_hours(r, now)) is not None and age <= WINDOW_HOURS/True/'

# 3. Dedup must not drop on company+title alone.
mutate "dedup: company+title drops without checking location" \
  jobdiscovery/dedup.py 's/return Decision("review", "company_title", row_number)/return Decision("drop", "company_title", row_number)/'

# 4. Dedup must not drop silently.
mutate "dedup: a drop stops naming its key" \
  jobdiscovery/dedup.py 's/return Decision("drop", "url", self.by_url\[url\])/return Decision("drop", "", None)/'

# 5. The revision cap must hold.
mutate "writing: pass cap raised" \
  jobdiscovery/writing_ledger.py 's/^PASS_CAP = 4$/PASS_CAP = 99/'

# 6. A failed source must not read as an empty one.
mutate "ledger: failure recorded as ok" \
  jobdiscovery/ledger.py 's/"status": "ok" if ok else "failed"/"status": "ok"/'

# 7. A short read must not be accepted.
#
# The brief this harness was written from targeted `if returned_rows < claimed_total:`,
# a line from the service-account-era sheets.py. That design was replaced (see
# commit b5b3d00, "reach the tracker through the web app, not a service account")
# before this task was implemented — sheets.py now checks `returned_rows < expected`
# inside assert_complete_read. Same rule, current line.
mutate "sheets: incomplete read accepted" \
  jobdiscovery/sheets.py 's/if returned_rows < expected:/if False:/'

# 8. An unchecked read must not pass silently.
#
# The brief's pattern (`print("WARNING: no summary_range`) targeted the same
# retired design, where a missing `summary_range` config fell back to an
# unchecked read with only a printed warning. The current design has no such
# fallback — the sheet's own claim about its extent (`lastRow`, `firstDataRow`)
# is read with a hard subscript, so a missing claim already raises KeyError.
# The equivalent current mutation reintroduces exactly the retired failure mode:
# defaulting a missing claim to "already satisfied" instead of raising. See
# tests/job_discovery/test_sheets.py::test_read_tracker_requires_the_sheets_own_claim_of_completeness,
# added in this task because no existing test constructed a payload missing
# those keys.
mutate "sheets: missing claim passes without a word" \
  jobdiscovery/sheets.py 's/payload\["lastRow"\], payload\["firstDataRow"\])/payload.get("lastRow", len(rows)), payload.get("firstDataRow", 1))/'

# --- Documented rules ------------------------------------------------------
#
# The rules Step 2 obeys live in SKILL.md prose, and prose has no compiler. The
# guard for them is tests/test_job_discovery_skill.sh, and a guard whose regex is
# loose enough to match text that no longer states the rule protects nothing —
# two of that file's original six assertions were exactly that. So the same
# discipline applies here: delete the sentence, require the guard to notice.

mutate_doc() {  # mutate_doc <label> <sed-expression>
  local label="$1" expression="$2" file="SKILL.md"
  MUTATING="$file"
  cp "$file" "$file.bak"
  /usr/bin/sed -i '' "$expression" "$file"
  if ! assert_mutated "$file" "$label"; then
    mv "$file.bak" "$file"; MUTATING=""; fails=$((fails + 1)); return
  fi
  if (cd ../.. && bash tests/test_job_discovery_skill.sh >/dev/null 2>&1); then
    echo "FAIL  $label — the skill guard stayed green with the rule deleted"
    fails=$((fails + 1))
  else
    echo "PASS  $label — deleting it turns the skill guard red"
  fi
  mv "$file.bak" "$file"
  MUTATING=""
}

# Patterns are case-correct against the prose as written; assert_mutated catches
# it if that ever stops being true.
mutate_doc "skill: front-matter prohibition deleted"  '/[Nn]ever edit the YAML front matter/d'
mutate_doc "skill: pass-cap rule deleted"             '/counted in code/d'
mutate_doc "skill: best-pass rule deleted"            '/highest-scoring pass/d'
mutate_doc "skill: OPEN rubric marker deleted"        '/OPEN, not yet supplied/d'
mutate_doc "skill: do-not-invent rule deleted"        '/[Dd]o not invent them/d'
mutate_doc "skill: dossier source deleted"            '/dossier\.md/d'
mutate_doc "skill: answer-store source deleted"       '/application-answers\.md/d'
mutate_doc "skill: notes-is-optional rule deleted"    '/the other four sections gate the append/d'
mutate_doc "skill: unverified/ and its flag deleted"  '/only with `--include-unverified`/d'

if [ "$fails" -eq 0 ]; then echo "ALL PASS"; else echo "$fails FAILED"; exit 1; fi
