#!/usr/bin/env bash
# Test the personal-content guard. Run from repo root: bash tests/test_check_no_personal.sh
set -uo pipefail
GUARD="scripts/check_no_personal.sh"
fails=0

check() {  # check <label> <expected-exit> <file>...
  local label="$1" want="$2"; shift 2
  bash "$GUARD" "$@" >/dev/null 2>&1
  local got=$?
  if [ "$got" -ne "$want" ]; then
    echo "FAIL: $label — expected exit $want, got $got"
    fails=$((fails+1))
  else
    echo "ok: $label"
  fi
}

check "clean file passes"        0 tests/fixtures/clean.md
check "leaky file is rejected"   1 tests/fixtures/leaky.md
check "nonexistent path fails closed, not clean"  2 tests/fixtures/does-not-exist.md
check "one missing path among real ones still fails closed" 2 \
  tests/fixtures/clean.md tests/fixtures/does-not-exist.md

# The guard must name the missing path, not just refuse silently.
out=$(bash "$GUARD" tests/fixtures/does-not-exist.md 2>&1 || true)
if ! grep -q "tests/fixtures/does-not-exist.md" <<<"$out"; then
  echo "FAIL: missing-path output does not name the offending path"; fails=$((fails+1))
else
  echo "ok: missing-path output names the offending path"
fi

# The guard must name the file and the term it matched.
out=$(bash "$GUARD" tests/fixtures/leaky.md 2>&1 || true)
if ! grep -q "LEAK tests/fixtures/leaky.md" <<<"$out"; then
  echo "FAIL: output does not name the offending file"; fails=$((fails+1))
else
  echo "ok: output names the offending file"
fi

# Every pattern in the list must actually be detectable, or the list is decorative.
while IFS= read -r pat; do
  case "$pat" in ''|'#'*) continue;; esac
  probe=$(mktemp); printf 'lorem %s ipsum\n' "$(sed 's/[\\^$.|?*+()]//g' <<<"$pat")" > "$probe"
  if bash "$GUARD" "$probe" >/dev/null 2>&1; then
    echo "FAIL: pattern never fires: $pat"; fails=$((fails+1))
  fi
  rm -f "$probe"
done < scripts/personal-patterns.txt

[ "$fails" -eq 0 ] && echo "ALL PASS" || { echo "$fails failure(s)"; exit 1; }
