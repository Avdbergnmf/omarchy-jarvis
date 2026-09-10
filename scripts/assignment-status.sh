#!/usr/bin/env bash
# Show queue, in-progress work, and a naive claimability hint for new agents.
# Canonical claim truth is origin/main (A-039): a claim only counts once it is
# pushed there, so this script reads QUEUE from origin/main, not the local
# checkout's branch, and cross-checks every worktree for unpushed/stale claims.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

QUEUE_REL="docs/assignments/QUEUE.md"
INDEX_REL="docs/assignments/INDEX.md"
SESSION_REL="docs/SESSION.md"

extract_rows() {
  grep -E '^\| A-[0-9]+ \|' 2>/dev/null || true
}

row_id() { echo "$1" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/,"",$2); print $2}'; }
row_status() { echo "$1" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/,"",$4); print $4}'; }
row_area() { echo "$1" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/,"",$5); print $5}'; }
# A-037: the brief's own path link (last markdown link in the row), independent of any
# columns added between area and path (e.g. the depth column) — never index by position here.
row_path() { echo "$1" | grep -oE '\]\([^)]+\)' | tail -1 | sed -E 's/^\]\(|\)$//g' || true; }

echo "=== Worktree isolation (read-only hints) ==="
CURRENT_BRANCH=$(git symbolic-ref --quiet --short HEAD || printf 'detached HEAD')
printf 'Current: %s [%s]\n' "$ROOT" "$CURRENT_BRANCH"
declare -a WT_PATHS=()
declare -a WT_BRANCHES=()
TREE=""
BRANCH=""
while IFS= read -r -d '' FIELD; do
  case "$FIELD" in
    worktree\ *) TREE=${FIELD#worktree } ;;
    branch\ *) BRANCH=${FIELD#branch refs/heads/} ;;
    detached) BRANCH="detached HEAD" ;;
    "")
      if [[ -n "$TREE" ]]; then
        WT_PATHS+=("$TREE")
        WT_BRANCHES+=("${BRANCH:-unknown}")
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
echo

echo "=== Claim source ==="
FETCH_OK=1
if ! git fetch origin --quiet 2>/dev/null; then
  FETCH_OK=0
  echo "OFFLINE: could not fetch origin. Falling back to local $QUEUE_REL ($CURRENT_BRANCH) — may be stale."
fi
CANON_SOURCE="origin/main"
CANON_TEXT=""
if ((FETCH_OK)) && CANON_TEXT=$(git show origin/main:"$QUEUE_REL" 2>/dev/null); then
  echo "Reading canonical claims from origin/main:$QUEUE_REL (the only place a claim counts, per A-039)."
else
  CANON_SOURCE="local ($ROOT, branch $CURRENT_BRANCH)"
  CANON_TEXT=$(cat "$QUEUE_REL" 2>/dev/null || true)
  echo "Reading claims from $CANON_SOURCE — NOT guaranteed canonical. Fetch/merge before trusting this for a claim decision."
fi
echo

echo "=== Who is working (SESSION, every worktree) ==="
for i in "${!WT_PATHS[@]}"; do
  TREE="${WT_PATHS[$i]}"
  BR="${WT_BRANCHES[$i]}"
  SESSION_FILE="$TREE/$SESSION_REL"
  if [[ -f "$SESSION_FILE" ]]; then
    printf -- '--- %s [%s] ---\n' "$TREE" "$BR"
    sed -n '/^## Active goal/,/^## Checklist/p' "$SESSION_FILE" | sed '$d'
  fi
done
echo

echo "=== QUEUE (canonical: $CANON_SOURCE) ==="
mapfile -t ROWS < <(printf '%s\n' "$CANON_TEXT" | extract_rows)
if ((${#ROWS[@]} == 0)); then
  echo "(queue empty of open A-### rows)"
else
  printf '%s\n' "${ROWS[@]}"
fi

echo
echo "=== Blocked-by / gate (from active briefs, canonical: $CANON_SOURCE) ==="
brief_text() {
  local relpath="docs/assignments/$1" text
  if ((FETCH_OK)) && text=$(git show "origin/main:$relpath" 2>/dev/null); then
    printf '%s' "$text"
  else
    cat "$relpath" 2>/dev/null || true
  fi
}
brief_meta() {
  # $1 body, $2 label — matches "- **Label:** value" (A-037 structured metadata).
  # `|| true`: under pipefail, grep's no-match (1) would otherwise kill the script via set -e
  # when this is called as `VAR=$(brief_meta ...)` — no match just means "field absent".
  printf '%s\n' "$1" | grep -E "^- \*\*$2:\*\*" | head -1 | sed -E "s/^- \*\*$2:\*\* ?//" || true
}
# INDEX.md (not QUEUE.md) is the status source for Blocked-by lookups: done assignments are
# removed from QUEUE's open rows entirely, but INDEX keeps every id ever filed with its real
# status — an id genuinely absent from INDEX (typo, not yet filed) must stay conservatively
# "unmet", which a QUEUE-only lookup could not distinguish from "done and delisted".
INDEX_TEXT=""
if ((FETCH_OK)) && INDEX_TEXT=$(git show "origin/main:$INDEX_REL" 2>/dev/null); then :; else
  INDEX_TEXT=$(cat "$INDEX_REL" 2>/dev/null || true)
fi
mapfile -t INDEX_ROWS < <(printf '%s\n' "$INDEX_TEXT" | extract_rows)
declare -A STATUS_BY_ID=()
for row in "${INDEX_ROWS[@]+"${INDEX_ROWS[@]}"}"; do
  STATUS_BY_ID["$(row_id "$row")"]="$(row_status "$row")"
done
declare -A UNMET_BY_ID=()
ANY_BLOCKED=0
for row in "${ROWS[@]+"${ROWS[@]}"}"; do
  RID=$(row_id "$row")
  RPATH=$(row_path "$row")
  [[ "$RPATH" == active/* ]] || continue
  BODY=$(brief_text "$RPATH")
  [[ -n "$BODY" ]] || continue
  BLOCKED_BY_RAW=$(brief_meta "$BODY" 'Blocked-by')
  GATE_RAW=$(brief_meta "$BODY" 'Gate')
  # A-037 hardening: strip parentheticals and em-dash prose before extracting ids; dedupe.
  BLOCKED_BY_CLEAN=$(sed -E 's/\([^)]*\)//g; s/ —.*//; s/ –.*//' <<<"$BLOCKED_BY_RAW")
  mapfile -t IDS < <(grep -oE 'A-[0-9]+' <<<"$BLOCKED_BY_CLEAN" | awk '!seen[$0]++' || true)
  UNMET=()
  for bid in "${IDS[@]+"${IDS[@]}"}"; do
    st="${STATUS_BY_ID[$bid]:-}"
    [[ "$st" == "done" || "$st" == "cancelled" ]] || UNMET+=("$bid")
  done
  GATE_NOTE=""
  [[ -n "$GATE_RAW" && "$GATE_RAW" != "none" ]] && GATE_NOTE=" gate:$GATE_RAW"
  if ((${#UNMET[@]} > 0)); then
    UNMET_JOINED=$(IFS=,; echo "${UNMET[*]}")
    UNMET_BY_ID["$RID"]="$UNMET_JOINED"
    printf 'BLOCKED: %s waiting on %s%s\n' "$RID" "$UNMET_JOINED" "$GATE_NOTE"
    ANY_BLOCKED=1
  elif [[ -n "$GATE_NOTE" ]]; then
    printf 'ready:%s -> %s\n' "$GATE_NOTE" "$RID"
  fi
done
if ((ANY_BLOCKED == 0)); then
  echo "(no structured Blocked-by dependencies are currently unmet)"
fi
# A-037 hardening: show rows with status=blocked but no id dependencies (human-blocked).
for row in "${ROWS[@]+"${ROWS[@]}"}"; do
  RID=$(row_id "$row")
  RSTATUS=$(row_status "$row")
  RPATH=$(row_path "$row")
  [[ "$RSTATUS" == "blocked" && "$RPATH" == active/* ]] || continue
  BODY=$(brief_text "$RPATH")
  [[ -n "$BODY" ]] || continue
  BLOCKED_BY_RAW=$(brief_meta "$BODY" 'Blocked-by')
  BLOCKED_BY_CLEAN=$(sed -E 's/\([^)]*\)//g; s/ —.*//; s/ –.*//' <<<"$BLOCKED_BY_RAW")
  mapfile -t IDS < <(grep -oE 'A-[0-9]+' <<<"$BLOCKED_BY_CLEAN" || true)
  if ((${#IDS[@]} == 0)); then
    echo "HUMAN-BLOCKED: $RID (status=blocked; not an id dependency)"
  fi
done

echo
echo "=== in_progress (canonical) ==="
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
echo "=== Cross-worktree claim mismatches (unpushed/stale claims) ==="
MISMATCH=0
for i in "${!WT_PATHS[@]}"; do
  TREE="${WT_PATHS[$i]}"
  BR="${WT_BRANCHES[$i]}"
  LOCAL_QUEUE="$TREE/$QUEUE_REL"
  [[ -f "$LOCAL_QUEUE" ]] || continue
  mapfile -t LOCAL_ROWS < <(extract_rows <"$LOCAL_QUEUE")
  for lrow in "${LOCAL_ROWS[@]+"${LOCAL_ROWS[@]}"}"; do
    lid=$(row_id "$lrow")
    lstatus=$(row_status "$lrow")
    for crow in "${ROWS[@]+"${ROWS[@]}"}"; do
      cid=$(row_id "$crow")
      [[ "$lid" == "$cid" ]] || continue
      cstatus=$(row_status "$crow")
      if [[ "$lstatus" != "$cstatus" ]]; then
        printf 'MISMATCH: %s local=%s on %s [%s] vs canonical=%s — push the claim commit to origin/main or treat as stale.\n' \
          "$lid" "$lstatus" "$TREE" "$BR" "$cstatus"
        MISMATCH=1
      fi
    done
  done
done
if ((MISMATCH == 0)); then
  echo "(none found — every checked worktree agrees with canonical)"
fi

echo
echo "=== Claim hint (new / parallel agent) ==="
echo "Reminder (A-039): push your QUEUE/INDEX/SESSION status change to origin/main FIRST,"
echo "then open your worktree from the updated origin/main — do not claim only on a branch."
if ((${#ROWS[@]} == 0)); then
  echo "No assignment in queue is possible right now. The queue is empty."
  exit 0
fi

if ((${#IN_PROG[@]} == 0)); then
  # top queued, skipping anything with an unmet structured Blocked-by (A-037)
  for row in "${ROWS[@]}"; do
    if echo "$row" | grep -qi '| queued |'; then
      RID=$(row_id "$row")
      if [[ -n "${UNMET_BY_ID[$RID]:-}" ]]; then
        echo "Skipping $RID (queued but Blocked-by ${UNMET_BY_ID[$RID]} not done yet) — see Blocked-by section above."
        continue
      fi
      echo "Nothing in progress — claim first queued row:"
      echo "$row"
      exit 0
    fi
  done
  echo "No assignment in queue is possible right now. (No queued rows are actually unblocked.)"
  printf '%s\n' "${ROWS[@]}"
  exit 0
fi

echo "Something is already in_progress. You may only claim queued + parallel-ok: YES with an area:"
echo "different from every in_progress row below (A-023/ADR-034: area + worktree is the isolation;"
echo "any Allowed/Forbidden paths in active/*.md are optional context, never a gate — same area never"
echo "counts as parallel-safe just because paths look disjoint)."
IN_PROG_AREAS=()
for row in "${IN_PROG[@]}"; do
  IN_PROG_AREAS+=("$(row_area "$row")")
done
FOUND=0
for row in "${ROWS[@]}"; do
  if echo "$row" | grep -qi '| queued |' && echo "$row" | grep -qi '| YES |'; then
    RID=$(row_id "$row")
    if [[ -n "${UNMET_BY_ID[$RID]:-}" ]]; then
      echo "Skipping $RID (queued but Blocked-by ${UNMET_BY_ID[$RID]} not done yet) — see Blocked-by section above."
      continue
    fi
    ROW_AREA=$(row_area "$row")
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
