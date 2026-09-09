#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
failed=0
check() { if "$@"; then printf 'OK: %s\n' "$*"; else printf 'FAIL: %s\n' "$*"; failed=1; fi; }
if [[ ${1:-} == --syntax ]]; then
  while IFS= read -r file; do check bash -n "$file"; done < <(find scripts skills -name '*.sh')
  check python3 -m compileall -q brain actions console scripts tests
  exit "$failed"
fi
check ollama list
model_ready() { ollama list | awk '{print $1}' | grep -Fx "${JARVIS_MODEL:-qwen2.5:3b}"; }
if model_ready; then
  printf 'OK: selected model is available\n'
else
  printf 'FAIL: selected model is unavailable\n'
  failed=1
fi
check hyprctl -j workspaces
check ./actions/catalog_bindings --refresh --query scratch
check ./skills/examples/open-planning/run.sh --dry-run
check ./skills/examples/scratch-and-mail/run.sh --dry-run
check gh auth status
check ./actions/report_bug --title 'Doctor check' --body 'Doctor dry-run body' --difficulty S --dry-run
check ./actions/report_feature --title 'Doctor check' --body 'Doctor dry-run body' --difficulty S --dry-run
check ./actions/list_backlog --dry-run
check ./actions/prepare_handoff --issue 1 --agent human --dry-run
check ./skills/examples/report-last-failure/run.sh --dry-run
check ./skills/examples/add-feature-request/run.sh --dry-run 'doctor check feature'
check python3 -c 'import socket,urllib.request,json; s=socket.socket();
try: s.bind(("127.0.0.1",7421)); print("Port 7421 free (brain stopped)")
except OSError: assert json.load(urllib.request.urlopen("http://127.0.0.1:7421/health"))["service"] == "omarchy-jarvis"; print("Jarvis listening")
finally: s.close()'
if [[ ${1:-} == --notify ]]; then check ./actions/notify_thought --run-id doctor --message 'Doctor notification: click for live log'; fi
exit "$failed"
