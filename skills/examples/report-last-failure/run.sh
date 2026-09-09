#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
case ${1:-} in --help) echo 'Usage: run.sh [--dry-run] — draft a bug report from the most recently modified run log'; exit 0;; ''|--dry-run) ;; *) echo 'Unknown argument' >&2; exit 2;; esac
args=()
[[ ${1:-} == --dry-run ]] && args+=(--dry-run)
latest=$(find "$root/logs/runs" -maxdepth 1 -type f -name '*.log' -printf '%T@\t%p\n' 2>/dev/null | sort -rn | head -n1 | cut -f2)
if [[ -z "$latest" && ${1:-} != --dry-run ]]; then
  printf '{"ok":false,"error":"No run logs found under logs/runs/"}\n'
  exit 1
fi
if [[ -z "$latest" ]]; then
  run_id='(none yet)'; excerpt='(no run logs on this host yet)'
else
  run_id=$(basename "$latest" .log)
  excerpt=$(tail -n 20 "$latest")
fi
title="Bug: run ${run_id} needs review"
body=$(printf 'Auto-drafted from the most recent run log (no interactive Q&A — for the full context-pack + clarifying-question flow, use /report in the overlay instead).\n\nRun id: %s\nRun log: logs/runs/%s.log\n\nLog excerpt (last 20 lines):\n%s\n' "$run_id" "$run_id" "$excerpt")
"$root/actions/report_bug" --title "$title" --body "$body" --difficulty M "${args[@]}"
