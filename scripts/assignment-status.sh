#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "=== QUEUE (non-done) ==="
grep -E '\| A-[0-9]+ \|' docs/assignments/QUEUE.md | grep -vi '| done |' || true
echo
echo "=== SESSION (head) ==="
sed -n '1,40p' docs/SESSION.md
echo
echo "=== git ==="
git status -sb
git log -5 --oneline
