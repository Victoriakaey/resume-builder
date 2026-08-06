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

  # ── The attestation safety property ──────────────────────────────────────
  #
  # THE INVARIANT IS NOT A LAYOUT. What must hold is: no reading of this file
  # permits the agent to auto-answer a legal attestation. The layout is only
  # one of the facts that carries it.
  #
  # Why the file is like this. The policy-level question list and stop category
  # 2 name four of the same things (background check, export control,
  # non-compete, AI-use attestations) with opposite handling: the stop list says
  # leave them blank, the policy list says auto-answer on an exact wording
  # match. In the source design the list is NESTED INSIDE stop category 4 — it
  # *defines* the fourth stop category. An earlier SKILL.md promoted it to its
  # own top-level "## Policy-level questions" section, which severed it from the
  # stop list and left it reading as a standing permission; combined with "write
  # the ruling back into the store", that is a path to the agent ticking an
  # "I did not use AI" box on a real employer's form. Do not re-promote it.
  #
  # An earlier version of this check asserted only "the list sits in a section
  # that also contains one anchor string". Six reversions of the repair were
  # built against it and five passed: narrowing the precedence so it no longer
  # covers attestations, deleting the frontmatter promise, reverting the
  # division-of-labour caveat, hoisting the list above the first heading (where
  # a section-scoped awk cannot see it), and inverting the precedence's meaning
  # with an appended exception. Structural containment was never the property.
  # The checks below assert the facts that actually carry the invariant, and
  # end with a stated limit on what a text test can reach at all.

  # (1) The promise the skill makes about itself, where a caller reads it.
  #     Deleting this leaves the body rules intact but removes the one
  #     statement anyone reads before invoking the skill.
  if [ -n "${frontmatter:-}" ]; then
    echo "$frontmatter" | grep -qF -- 'never answers a legal attestation' \
      || note "frontmatter no longer promises the skill never answers a legal attestation"
  fi

  # (2) The division-of-labour row that grants store-settled answers must carry
  #     the attestation carve-out. Without it that row reads as blanket
  #     permission and contradicts stop category 2.
  echo "$div_section" | grep -qF -- 'never an attestation' \
    || note "the division-of-labour row for store-settled answers no longer excepts attestations"

  # (3) The stop category the precedence points at must exist to be pointed at.
  grep -qF -- 'legal attestations, consents, arbitration agreements' "$s" \
    || note "SKILL.md's stop list no longer carries the legal-attestation category"

  # (4) Position, asserted as line ranges rather than as section nesting. Stop
  #     category 2, the policy-level list and the precedence must all sit inside
  #     numbered step 4 — which is precisely what the design says (the list IS
  #     stop category 4). Line position is defined everywhere in the file;
  #     section membership is not, which is why a section-scoped scan could not
  #     see a list hoisted above the first "## " heading.
  #
  #     Anchor the list on "veteran status", which occurs only inside the list
  #     itself, not on "AI-use attestations", which the precedence sentence also
  #     names and which would let a re-promoted list anchor onto the section the
  #     precedence stayed behind in.
  grep -qF -- 'veteran status' "$s" || note "SKILL.md no longer carries the policy-level question list"
  line_of() { grep -nF -- "$1" "$s" | head -1 | cut -d: -f1; }
  l_stop2="$(line_of 'legal attestations, consents, arbitration agreements')"
  l_list="$(line_of 'veteran status')"
  l_prec="$(line_of 'Categories 2 and 3 outrank this list')"
  l_step4="$(grep -nE '^4\. \*\*Stop for four categories' "$s" | head -1 | cut -d: -f1)"
  eof="$(( $(wc -l < "$s") + 1 ))"
  # End of step 4: the next unindented numbered step, else the end of the "## "
  # section, else EOF. Bounding at the next step keeps steps 5 and 6 out of the
  # region checks below, so editing the handoff wording does not trip them.
  l_bound="$(awk -v n="${l_step4:-0}" 'NR>n && /^[0-9]+\. / { print NR; exit }' "$s")"
  [ -n "${l_bound:-}" ] || l_bound="$(awk -v n="${l_step4:-0}" 'NR>n && /^## / { print NR; exit }' "$s")"
  [ -n "${l_bound:-}" ] || l_bound="$eof"

  if [ -z "${l_step4:-}" ]; then
    note "SKILL.md no longer has a numbered step 4 'Stop for four categories' — the whole stop-category structure the attestation rules hang off is gone"
  else
    in_step4() { [ -n "${1:-}" ] && [ "$1" -gt "$l_step4" ] && [ "$1" -lt "$l_bound" ]; }
    in_step4 "${l_stop2:-}" \
      || note "stop category 2 (legal attestations) is not inside step 4 (lines $l_step4-$((l_bound-1)))"
    [ -z "${l_list:-}" ] || in_step4 "$l_list" \
      || note "the policy-level question list (line $l_list) is no longer inside step 4 (lines $l_step4-$((l_bound-1))) — read where it now sits it is a standing permission to auto-answer an attestation, not stop category 4 (design §6 step 4)"
    if [ -z "${l_prec:-}" ]; then
      note "SKILL.md no longer states that categories 2 and 3 outrank the policy-level list"
    else
      in_step4 "$l_prec" \
        || note "the attestation-precedence statement (line $l_prec) is no longer inside step 4 (lines $l_step4-$((l_bound-1))) — an agent standing at the list does not reach it"
    fi
  fi

  # (5) The precedence paragraph itself, pinned verbatim modulo whitespace.
  #
  #     THIS ONE IS DELIBERATELY BRITTLE, and the brittleness is the point. A
  #     keyword assertion cannot tell "category 2 wins" from "category 2 wins —
  #     unless the store has an explicit ruling, in which case tick the box":
  #     grep matches strings, not meaning, and every anchor phrase survives that
  #     edit intact. No grep/awk assertion can catch an arbitrary semantic
  #     inversion. Pinning the reviewed text is the closest a text test gets:
  #     any reword — safe or not — fails here, which forces the change through
  #     review instead of letting it through silently. If you are rewording this
  #     paragraph on purpose, update prec_expected in the same commit and say in
  #     the message why the new wording still forbids auto-answering.
  #
  #     Compared whitespace-normalised so reflowing the paragraph is free.
  prec_expected='**Categories 2 and 3 outrank this list.** An item here that is also an attestation, a consent, or an authorisation — background check, export control, non-compete, AI-use attestations — is never auto-answered, whatever the store says: category 2 wins. Criminal history is category 3 as well. A stored ruling on any of them records what the applicant has decided to enter, for them to enter; it never authorises this skill to tick the box on their behalf. Only the person applying attests.'
  prec_actual="$(awk '
    /^[[:space:]]*$/ { if (hit) exit; buf = ""; next }
    { buf = buf " " $0; if (index($0, "Categories 2 and 3 outrank this list")) hit = 1 }
    END { if (hit) print buf }
  ' "$s" | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
  [ "$prec_actual" = "$prec_expected" ] \
    || note "the attestation-precedence paragraph is not the reviewed text (see prec_expected above; whitespace is ignored, wording is not). Got: ${prec_actual:-<not found>}"

  step4_region="$(awk -v a="${l_step4:-1}" -v b="$l_bound" 'NR>=a && NR<b' "$s")"

  # (6) Nothing inside step 4 may carve an exception. Categories 2 and 3 are
  #     absolute; the words below are how an exception gets written. This
  #     catches an exception bolted on as a separate paragraph, which (5) — a
  #     single-paragraph pin — does not read.
  if echo "$step4_region" | grep -qiE '(^|[^[:alnum:]])(unless|except|exception|save for|other than|provided that)([^[:alnum:]]|$)'; then
    note "step 4 now carves an exception ($(echo "$step4_region" | grep -inE '(^|[^[:alnum:]])(unless|except|exception|save for|other than|provided that)([^[:alnum:]]|$)' | head -1)) — categories 2 and 3 are absolute; an exception here is the bug this section exists to prevent"
  fi

  # (6b) The paragraph inventory of step 4, pinned. (5) pins the precedence
  #      paragraph and (6) catches exception wording, but an inversion can also
  #      arrive as a NEW paragraph beside them, phrased without any exception
  #      keyword — "Where the store holds an explicit ruling on that exact
  #      wording, tick the box on the applicant's behalf." Neither of the two
  #      above reads it. Pinning how many paragraphs step 4 has and how each one
  #      opens makes any such insertion fail.
  #
  #      Only the opening of each paragraph is pinned, so editing a paragraph's
  #      body stays free (the precedence paragraph is separately pinned in full
  #      by (5)). Adding or removing a paragraph in step 4 is a safety-relevant
  #      change: update step4_expected in the same commit and say why the new
  #      text still forbids auto-answering.
  #      Pinned as the first five whitespace-separated words of each paragraph:
  #      word boundaries, not a byte count, so nothing can be truncated through
  #      the middle of a multi-byte character.
  step4_expected='4. **Stop for four categories.**
1. the employer forbids AI-assisted
**Policy-level questions** are the fourth
work authorization · sponsorship ·
**Categories 2 and 3 outrank
When a policy-level question has'
  step4_actual="$(echo "$step4_region" | awk '
    /^[[:space:]]*$/ { seen = 0; next }
    {
      if (seen) next
      seen = 1
      n = (NF < 5 ? NF : 5); out = $1
      for (i = 2; i <= n; i++) out = out " " $i
      print out
    }
  ')"
  if [ "$step4_actual" != "$step4_expected" ]; then
    note "step 4's paragraph inventory changed (a paragraph was added, removed or reopened). Expected openings:
$step4_expected
Got:
$step4_actual"
  fi

  # (7) The write-back paragraph, pinned in full for the same reason as (5).
  #     Write-back is what turned the contradiction into a live failure — ask
  #     once, store a ruling, auto-answer forever — so this is the second of the
  #     two paragraphs where a sentence appended to the tail would grant exactly
  #     what the section forbids. (6b) pins each paragraph's opening; these two
  #     are pinned end to end.
  wb_expected='When a policy-level question has no stored answer: ask, then **write the ruling back into the store**, with its basis and the date. A question asked twice means the store failed, not that the operator was forgetful. Writing a ruling back never converts a category-2 item into an auto-answerable one.'
  wb_actual="$(echo "$step4_region" | awk '
    /^[[:space:]]*$/ { if (hit) exit; buf = ""; next }
    { buf = buf " " $0; if (index($0, "write the ruling back into the")) hit = 1 }
    END { if (hit) print buf }
  ' | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
  [ "$wb_actual" = "$wb_expected" ] \
    || note "the write-back paragraph is not the reviewed text — it is the path from 'operator answered once' to 'agent ticks the box', so its wording is pinned (whitespace ignored). Got: ${wb_actual:-<not found>}"

  # KNOWN LIMIT, stated so nobody reads the checks above as complete. grep and
  # awk match strings; they cannot evaluate meaning. What still gets through:
  # a sentence appended to the TAIL of the policy-level intro paragraph or of
  # the category list itself — the two paragraphs that are not pinned end to
  # end — phrased without any of the exception words in (6) and without opening
  # a new paragraph. "…near-matches get raised. A stored ruling is sufficient
  # authority to enter any of them:" passes everything here. Closing that would
  # mean pinning all of step 4 verbatim, which buys little: at that point the
  # test is a copy of the prose and a future editor updates it by pasting. The
  # two paragraphs that grant or deny — the precedence and the write-back — are
  # the ones pinned in full, deliberately.

  # SKILL.md depends on the store's three named sections (constants, policy
  # rulings, material blocks) even though its prose bends the words
  # grammatically rather than repeating the headings verbatim ("Policy-level",
  # "material blocks" lowercase) — hence case-insensitive stem matches rather
  # than exact heading text.
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
