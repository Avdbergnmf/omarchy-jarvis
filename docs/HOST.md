# Host snapshot — Omarchy VM (try-omarchy) — 2026-09-09

Use this to avoid rediscovery.

## System
- Distro: Omarchy (Arch-based), Hyprland **0.56.2**
- User: `omarchy`
- RAM: ~**15 GiB** (was ~6 GiB earlier — prefer still-lean models first)
- Disk: root spacious; optional `/mnt/extra` for caches
- GitHub CLI: logged in as **`Avdbergnmf`** (repo + workflow scopes)
- Node: v26.8.1 (mise); Python 3.14; Chromium present; terminal = **foot** via `omarchy-launch-terminal`

## Packages already relevant
- `ollama` **0.33.3** installed but server was **not running** at handoff → start/enable it
- `fuzzel` installed; walker/mako/dunst **not** installed — use Omarchy’s `omarchy-notification-send` instead of adding mako
- `libnotify` / `notify-send` available; prefer Omarchy wrapper for click `--exec`

## Key commands
```bash
omarchy menu keybindings --print
hyprctl dispatch workspace <N>
hyprctl dispatch togglespecialworkspace scratchpad
hyprctl dispatch movetoworkspacesilent special:scratchpad
omarchy-launch-webapp 'https://…'
omarchy-launch-or-focus-webapp 'Name' 'https://…'
omarchy-notification-send -g 󰧑 -u normal "Jarvis" "thinking…" --exec jarvis-console <run-id>
omarchy-launch-floating-terminal-with-presentation <cmd>   # useful for console UX
```

## Personal bindings file
`~/.config/hypr/bindings.lua` overrides:
- SUPER+M Outlook
- SUPER+N WhatsApp
- Bitwarden picker, type-email, etc.

## Customization log
`~/Documents/Omarchy-customizations.md`

## Verified implementation update — 2026-09-09
- Checkout: `/home/omarchy/Work/omarchy-jarvis` (not `~/Projects`).
- Default webapp browser is **Brave**; actual classes include `brave-outlook.live.com__mail_-Default`. Chromium is used only for the isolated local overlay.
- Hyprland requires Lua dispatcher expressions (`hl.dsp.*`) on this installed version.
- User services `ollama.service` and `jarvis.service` installed and enabled. qwen2.5:3b downloaded (~1.9 GB).
- SUPER+SHIFT+J was free and is now the Jarvis overlay binding; installed float size 520×150.
- Desktop/session access requires leaving the agent workspace sandbox. Browser/native UI automation connector returned no available surfaces, so native action/Hyprland state tests are the available verification path.
