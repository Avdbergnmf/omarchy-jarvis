#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
systemctl --user start ollama.service
systemctl --user import-environment WAYLAND_DISPLAY HYPRLAND_INSTANCE_SIGNATURE DISPLAY XDG_CURRENT_DESKTOP
systemctl --user start jarvis.service
for ((i=0;i<40;i++)); do
  if curl -fsS http://127.0.0.1:7421/health >/dev/null 2>&1; then
    [[ ${1:-} != --console ]] || "$root/console/jarvis-console" brain
    exit 0
  fi
  sleep .25
done
echo 'Jarvis did not start; check logs/brain.log and journalctl --user -u jarvis' >&2
exit 1
