#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$HOME/.config/systemd/user" "$root/logs/runs"
chmod 700 "$root/logs" "$root/logs/runs"
unit="$HOME/.config/systemd/user/jarvis.service"
[[ ! -f $unit ]] || cp -a "$unit" "$unit.bak.$(date +%s)"
cat > "$unit" <<UNIT
[Unit]
Description=Omarchy Jarvis localhost brain and overlay
After=graphical-session.target ollama.service
PartOf=graphical-session.target
[Service]
Type=simple
WorkingDirectory=$root
ExecStart=/usr/bin/python3 "$root/brain/server.py"
Environment=JARVIS_MODEL=qwen2.5:3b
UMask=0077
Restart=on-failure
RestartSec=3
StandardOutput=append:$root/logs/brain.log
StandardError=append:$root/logs/brain.log
[Install]
WantedBy=graphical-session.target
UNIT
systemctl --user daemon-reload
systemctl --user enable jarvis.service
"$root/scripts/start.sh"
