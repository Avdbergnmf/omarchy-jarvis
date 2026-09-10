#!/usr/bin/env bash
# Restart the Jarvis brain (systemd user unit). Needed after brain/overlay code
# changes so Python reloads and the Chromium overlay picks up fresh JS/HTML.
# Docs-only / assignment queue edits do NOT require this.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

systemctl --user import-environment WAYLAND_DISPLAY HYPRLAND_INSTANCE_SIGNATURE DISPLAY XDG_CURRENT_DESKTOP 2>/dev/null || true
systemctl --user start ollama.service 2>/dev/null || true
systemctl --user restart jarvis.service

for ((i=0;i<40;i++)); do
  if curl -fsS http://127.0.0.1:7421/health >/dev/null 2>&1; then
    ver=$(curl -fsS http://127.0.0.1:7421/health 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("version") or d.get("jarvis_version") or "")' 2>/dev/null || true)
    echo "Jarvis restarted and healthy${ver:+ (version $ver)}."
    echo "Re-open the overlay (Super+Shift+J) or Training window so the UI reloads."
    [[ ${1:-} != --console ]] || "$root/console/jarvis-console" brain
    exit 0
  fi
  sleep .25
done

echo "Jarvis did not come back; check: journalctl --user -u jarvis -n 50 --no-pager" >&2
echo "Also: $root/logs/brain.log" >&2
exit 1
