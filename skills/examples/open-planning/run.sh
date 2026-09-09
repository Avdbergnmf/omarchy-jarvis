#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
case ${1:-} in --help) echo 'Usage: run.sh [--dry-run] — new workspace with four planning apps'; exit 0;; ''|--dry-run) ;; *) echo 'Unknown argument' >&2; exit 2;; esac
args=()
[[ ${1:-} == --dry-run ]] && args+=(--dry-run)
result=$("$root/actions/workspace_new" "${args[@]}")
printf '%s\n' "$result"
workspace=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["workspace"])' <<< "$result")
for app in Todoist 'Google Calendar' Outlook WhatsApp; do
  "$root/actions/open_webapp" --name "$app" --workspace "$workspace" "${args[@]}"
done
