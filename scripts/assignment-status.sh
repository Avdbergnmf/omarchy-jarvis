#!/usr/bin/env bash
# Show queue, in-progress work, and a naive claimability hint for new agents.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Worktree isolation (read-only hints) ==="
CURRENT_BRANCH=$(git symbolic-ref --quiet --short HEAD || printf 'detached HEAD')
printf 'Current: %s [%s]\n' "$ROOT" "$CURRENT_BRANCH"
TREE=""
BRANCH=""
while IFS= read -r -d '' FIELD; do
  case "$FIELD" in
    worktree\ *) TREE=${FIELD#worktree } ;;
    branch\ *) BRANCH=${FIELD#branch refs/heads/} ;;
    detached) BRANCH="detached HEAD" ;;
    "")
      if [[ -n "$TREE" ]]; then
        if [[ -d "$TREE" ]] && STATE=$(git --no-optional-locks -C "$TREE" status --porcelain --untracked-files=normal 2>/dev/null); then
          if [[ -n "$STATE" ]]; then
            printf 'DIRTY: %s [%s]\n' "$TREE" "${BRANCH:-unknown}"
            if [[ "$TREE" != "$ROOT" ]]; then
              if [[ "$BRANCH" != "$CURRENT_BRANCH" ]]; then
                echo "Hint: another checkout is dirty on a different branch; use your isolated worktree."
              fi
              echo "Do not checkout/stash/reset/clean or edit that tree."
            fi
          else
            printf 'Clean: %s [%s]\n' "$TREE" "${BRANCH:-unknown}"
          fi
        else
          printf 'Unavailable: %s (verify ownership manually)\n' "$TREE"
        fi
      fi
      TREE=""
      BRANCH=""
      ;;
  esac
done < <(git worktree list --porcelain -z)
echo "Concurrent agents require separate worktrees/branches (START.md); no automatic claim."
echo "QUEUE/SESSION below are branch-local. Check other trees' claims read-only and coordinate with the desk."
echo

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

echo "Something is already in_progress. You may only claim queued + parallel-ok: YES with an area:"
echo "different from every in_progress row below (A-023/ADR-034: area + worktree is the isolation;"
echo "any Allowed/Forbidden paths in active/*.md are optional context, never a gate — same area never"
echo "counts as parallel-safe just because paths look disjoint)."
IN_PROG_AREAS=()
for row in "${IN_PROG[@]}"; do
  IN_PROG_AREAS+=("$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/,"",$5); print $5}')")
done
FOUND=0
for row in "${ROWS[@]}"; do
  if echo "$row" | grep -qi '| queued |' && echo "$row" | grep -qi '| YES |'; then
    ROW_AREA=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/,"",$5); print $5}')
    CONFLICT=0
    for A in "${IN_PROG_AREAS[@]}"; do
      [[ "$ROW_AREA" == "$A" ]] && CONFLICT=1 && break
    done
    if ((CONFLICT == 0)); then
      echo "Candidate ($ROW_AREA differs from every in_progress area):"
      echo "$row"
      FOUND=1
    fi
  fi
done
if ((FOUND == 0)); then
  echo "No assignment in queue is possible right now."
  echo "Queue:"
  printf '%s\n' "${ROWS[@]}"
fi
