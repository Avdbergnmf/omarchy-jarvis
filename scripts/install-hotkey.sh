#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/install-hotkey.py
hyprctl reload
errors=$(hyprctl configerrors)
if [[ -n $errors && $errors != 'ok' ]]; then printf '%s\n' "$errors" >&2; exit 1; fi
