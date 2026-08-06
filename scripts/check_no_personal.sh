#!/usr/bin/env bash
# Reject files containing adopter-specific content. This repo is public.
# Usage: scripts/check_no_personal.sh <file>...
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
patterns="$here/personal-patterns.txt"

[ -f "$patterns" ] || { echo "missing pattern file: $patterns" >&2; exit 2; }
[ "$#" -gt 0 ] || { echo "usage: $0 <file>..." >&2; exit 2; }

found=0
while IFS= read -r pat; do
  case "$pat" in ''|'#'*) continue;; esac
  for f in "$@"; do
    [ -f "$f" ] || continue
    while IFS=: read -r lineno _; do
      [ -n "${lineno:-}" ] || continue
      echo "LEAK $f:$lineno: $pat"
      found=1
    done < <(grep -n -i -E -- "$pat" "$f" 2>/dev/null)
  done
done < "$patterns"

exit "$found"
