#!/usr/bin/env bash
# Show queue, in-progress work, and a naive claimability hint for new agents.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Who is working (SESSION) ==="
if [[ -f docs/SESSION.md ]]; then
  sed -n '/^## Active goal/,/^## Checklist/p' docs/SESSION.md | sed '$d'
  echo
  sed -n '/^## Next action/,/^## Parallel/p' docs/SESSION.md | sed '$d'
else
  echo "(no docs/SESSION.md)"
fi

echo
echo "=== QUEUE (open rows) ==="
mapfile -t ROWS < <(grep -E '^\| A-[0-9]+ \|' docs/assignments/QUEUE.md || true)
if ((${#ROWS[@]} == 0)); then
  echo "(queue empty of open A-### rows)"
else
  printf '%s\n' "${ROWS[@]}"
fi

echo
echo "=== in_progress ==="
IN_PROG=()
for row in "${ROWS[@]+"${ROWS[@]}"}"; do
  if echo "$row" | grep -qi '| in_progress |'; then
    echo "$row"
    IN_PROG+=("$row")
  fi
done
if ((${#IN_PROG[@]} == 0)); then
  echo "(none)"
fi

echo
echo "=== Claim hint (new / parallel agent) ==="
if ((${#ROWS[@]} == 0)); then
  echo "No assignment in queue is possible right now. The queue is empty."
  exit 0
fi

if ((${#IN_PROG[@]} == 0)); then
  # top queued
  for row in "${ROWS[@]}"; do
    if echo "$row" | grep -qi '| queued |'; then
      echo "Nothing in progress — claim first queued row:"
      echo "$row"
      exit 0
    fi
  done
  echo "No assignment in queue is possible right now. (No queued rows; only in_progress/other?)"
  printf '%s\n' "${ROWS[@]}"
  exit 0
fi

echo "Something is already in_progress. You may only claim queued + parallel-ok: YES with disjoint area/paths."
FOUND=0
for row in "${ROWS[@]}"; do
  if echo "$row" | grep -qi '| queued |' && echo "$row" | grep -qi '| YES |'; then
    echo "Candidate (verify paths in its active/*.md before claiming):"
    echo "$row"
    FOUND=1
  fi
done
if ((FOUND == 0)); then
  echo "No assignment in queue is possible right now."
  echo "Queue:"
  printf '%s\n' "${ROWS[@]}"
fi
