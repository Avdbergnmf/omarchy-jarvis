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

## Agent monitor window rules — A-018 (2026-09-10)
- Only `foot` is installed as a terminal binary (`alacritty`/`kitty`/`ghostty` have config
  dirs but no binary); `claude` and `codex` CLIs are both installed and on `PATH`.
- `scripts/open-agent.py` opens/focuses one **real** terminal window per local agent slot —
  never a hidden background job — via `omarchy-launch-or-focus-tui --app-id=jarvis-agent-<slot
  id> <claude|codex>` (the same launch-or-focus primitive ADR-023's `open_app_by_name` uses
  for webapps, here wrapping a TUI instead). The `--app-id` becomes the window's class, so
  each slot gets its own addressable, re-focusable window even with several agents running
  at once; a second click focuses the existing window instead of relaunching.
- `claude-code` kind → `claude`; `cursor` kind → `codex` (the installed CLI matching that
  slot's existing "Cursor / Codex" label). `human` kind has no process for Jarvis to
  launch — those slots are worked by Alex himself in his own terminal.
- New Claude windows may add `--effort <low|medium|high|xhigh|max>` from the slot's saved
  `reasoning_effort`. New Codex windows may add `-c model_reasoning_effort="…"` with
  `low|medium|high|xhigh` only (`max` is Claude-only). Focusing an existing window does
  not change that session's depth. Claude's non-secret default, when no slot override is
  set, is `effortLevel` in `~/.claude/settings.json` (missing/invalid = unknown).
- Per-slot launch state lives under `logs/agent-windows/<slot-id>.{log,lock}` (gitignored,
  same pattern as `logs/training-window.log`); the lock only prevents a double-launch race
  from a rapid second click before the window appears.
