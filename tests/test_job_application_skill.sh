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

  # Frontmatter must actually close, and name:/description: must live inside
  # that block — not just be the right line sitting anywhere in the body. A
  # malformed or unclosed block with the right name: line somewhere below it
  # used to pass this check; it shouldn't.
  close_line="$(awk 'NR>1 && /^---$/ { print NR; exit }' "$s")"
  if [ -z "${close_line:-}" ]; then
    note "SKILL.md frontmatter is never closed with a second ---"
  else
    frontmatter="$(sed -n "1,${close_line}p" "$s")"
    echo "$frontmatter" | grep -q '^name: job-application$' || note "frontmatter name is not job-application"
    echo "$frontmatter" | grep -q '^description: '          || note "frontmatter has no description"
  fi

  # The four boundaries the design says are non-negotiable. A loose
  # word-proximity regex passes on a rewrite that inverts the rule, or a
  # sentence that merely mentions submitting in passing. Assert the actual
  # boundary sentence, verbatim, and that it lives in the division-of-labour
  # section where a reader will actually hit it.
  div_section="$(awk '
    $0 == "## Division of labour" { infile=1; next }
    infile && /^## / { exit }
    infile { print }
  ' "$s")"
  echo "$div_section" | grep -qF -- 'Never press Submit.'    || note "no verbatim never-submit boundary in the division-of-labour section"
  echo "$div_section" | grep -qF -- 'Never upload a resume.' || note "no verbatim never-upload-resume boundary in the division-of-labour section"

  grep -qi 'ats-playbook'    "$s"           || note "does not point at the ATS playbook"
  grep -qi 'answer store'    "$s"           || note "does not mention the answer store"

  # Cross-repo contract, SKILL.md side: a checker in the private answer-store
  # repo greps the store byte-for-byte for these five ruling-format markers.
  # SKILL.md's "Recording a ruling" section is what a future agent copies
  # from when writing a new one, so its documented format must carry the
  # identical literal markers — nothing here asserted that before.
  for marker in '### Q:' '**Answer**:' '**Basis**:' '**Overrides**:' '**Decided**:'; do
    grep -qF -- "$marker" "$s" || note "SKILL.md's documented ruling format is missing marker: $marker"
  done

  # SKILL.md depends on the store's three named sections (constants, policy
  # rulings, material blocks) even though its prose bends the words
  # grammatically rather than repeating the headings verbatim ("Policy-level",
  # "material blocks" lowercase) — hence case-insensitive stem matches rather
  # than exact heading text.
  # Attestation precedence. The policy-level question list and stop category 2
  # name four of the same things (background check, export control, non-compete,
  # AI-use attestations) with opposite handling: the stop list says leave them
  # blank, the policy list says auto-answer them on an exact wording match. In
  # the source design that list is NESTED INSIDE stop category 4 — it *defines*
  # the fourth stop category. An earlier SKILL.md promoted it to its own
  # top-level "## Policy-level questions" section, which severed it from the
  # stop list and left it reading as a standing permission; combined with
  # "write the ruling back into the store", that is a path to the agent ticking
  # an attestation box on a real employer's form. Do not re-promote it. If it
  # must live in its own section for readability, the precedence has to travel
  # with it, which is what this asserts: whichever "## " section holds the list
  # must also state that category 2 wins.
  #
  # Anchor on "veteran status", which occurs only inside the list itself — not
  # on "AI-use attestations", which the precedence sentence also names and which
  # would therefore let a re-promoted list anchor onto the section the
  # precedence stayed in. Every "## " section carrying the list must carry the
  # precedence too, so a file-wide grep passing is not enough.
  grep -qF -- 'veteran status' "$s" || note "SKILL.md no longer carries the policy-level question list"
  orphaned="$(awk '
    function flush() {
      if (sect != "" && has_list && !has_prec) print sect
      has_list = 0; has_prec = 0
    }
    /^## / { flush(); sect = $0; next }
    {
      if (index($0, "veteran status")) has_list = 1
      if (index($0, "never auto-answered, whatever the store says")) has_prec = 1
    }
    END { flush() }
  ' "$s")"
  [ -z "$orphaned" ] || note "the policy-level question list appears in a section with no attestation-precedence statement (${orphaned}) — an agent reading it there sees permission to auto-answer an attestation (design §6 step 4: the list IS stop category 4, not a standing permission)"
  # The thing the precedence points at must still be there to point at.
  grep -qF -- 'legal attestations, consents, arbitration agreements' "$s" \
    || note "SKILL.md's stop list no longer carries the legal-attestation category"

  grep -qi 'constants'      "$s" || note "SKILL.md never names the store's Constants section"
  grep -qi 'polic'          "$s" || note "SKILL.md never names the store's Policies section"
  grep -qi 'material block' "$s" || note "SKILL.md never names the store's Material blocks section"
fi

if [ -f "$t" ]; then
  # Whole-line match: a heading substring buried inside a longer line (e.g.
  # "### Constants of the world") would satisfy grep -qF but is not the
  # section header the skill reads by name.
  for h in "## Constants" "## Policies" "## Material blocks"; do
    grep -qxF -- "$h" "$t" || note "template missing section: $h"
  done

  # Cross-repo contract, template side: the same private-repo checker greps
  # a filled-in copy of this template for these five literal markers, so the
  # blank template must offer them for the operator to fill in.
  for marker in '### Q:' '**Answer**:' '**Basis**:' '**Overrides**:' '**Decided**:'; do
    grep -qF -- "$marker" "$t" || note "template missing ruling-format marker: $marker"
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
