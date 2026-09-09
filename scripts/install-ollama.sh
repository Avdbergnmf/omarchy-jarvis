#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$HOME/.config/systemd/user"
unit="$HOME/.config/systemd/user/ollama.service"
if ! systemctl --user cat ollama.service >/dev/null 2>&1; then
  cat > "$unit" <<'UNIT'
[Unit]
Description=Ollama local model runtime
After=network.target
[Service]
ExecStart=/usr/bin/ollama serve
Environment=OLLAMA_HOST=127.0.0.1:11434
Restart=on-failure
RestartSec=3
[Install]
WantedBy=default.target
UNIT
fi
systemctl --user daemon-reload
systemctl --user enable --now ollama
for ((i=0;i<30;i++)); do if ollama list >/dev/null 2>&1; then break; fi; sleep 1; done
ollama pull "${JARVIS_MODEL:-qwen2.5:3b}"
