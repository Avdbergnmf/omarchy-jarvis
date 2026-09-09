#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
case ${1:-} in --help) echo 'Usage: run.sh [--dry-run] — move focused window to scratchpad, open Outlook'; exit 0;; ''|--dry-run) ;; *) echo 'Unknown argument' >&2; exit 2;; esac
args=()
[[ ${1:-} == --dry-run ]] && args+=(--dry-run)
"$root/actions/scratch_move_here" "${args[@]}"
"$root/actions/open_webapp" --name Outlook "${args[@]}"
