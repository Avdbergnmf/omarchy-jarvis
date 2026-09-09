#!/usr/bin/env bash
# A-006: wipe known one-off scratch artifacts under logs/. Safe to run any time, including
# right before a commit — logs/ is already fully gitignored (nothing here is ever tracked),
# this just keeps the local checkout tidy. Ongoing retention for logs/runs/, logs/debug/
# and logs/journal/archive/ is automatic (see brain/journal.py's prune()); this script only
# removes ad-hoc scrap that isn't part of that rotating set.
set -euo pipefail
cd "$(dirname "$0")/.."

removed=0
for pattern in demo-evidence.json host-evidence.json doctor-final.txt manual-actions.jsonl 'clients-after-*.json' '*.tmp'; do
  for f in logs/$pattern; do
    [[ -e "$f" ]] || continue
    rm -f -- "$f"
    printf 'removed: %s\n' "$f"
    removed=$((removed + 1))
  done
done

while IFS= read -r -d '' dir; do
  rm -rf -- "$dir"
  printf 'removed: %s\n' "$dir"
  removed=$((removed + 1))
done < <(find . -path ./.git -prune -o -name '__pycache__' -type d -print0 2>/dev/null)

if [[ ${1:-} == --profile ]]; then
  if [[ -d logs/overlay-profile ]] && python3 -c "
import sys; sys.path.insert(0, 'actions')
from core import hypr, is_overlay
sys.exit(0 if any(is_overlay(c) for c in hypr('clients')) else 1)
" 2>/dev/null; then
    printf 'SKIP: logs/overlay-profile is in use (overlay running) — close it first\n' >&2
  elif [[ -d logs/overlay-profile ]]; then
    rm -rf -- logs/overlay-profile
    printf 'removed: logs/overlay-profile (will be recreated on next overlay launch)\n'
    removed=$((removed + 1))
  fi
fi

printf 'Temp cleanup done (%s scratch item(s) removed). Pass --profile to also clear the overlay Chromium profile cache.\n' "$removed"
