#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
case ${1:-} in --help) echo 'Usage: run.sh [--dry-run] ["feature text"] — draft+file a feature request without interactive Q&A'; exit 0;; esac
args=()
text=''
for a in "$@"; do
  if [[ "$a" == --dry-run ]]; then args+=(--dry-run); else text=$a; fi
done
text=${text:-'(no description given on the command line — edit the filed draft with the real request before anyone picks it up)'}
title="Feature: ${text:0:80}"
body=$(printf 'Request (verbatim)\n%s\n\nFiled without interactive Q&A by the add-feature-request example skill. For the full context-pack + clarifying-question flow, use /feature in the overlay instead.\n' "$text")
"$root/actions/report_feature" --title "$title" --body "$body" --difficulty M "${args[@]}"
