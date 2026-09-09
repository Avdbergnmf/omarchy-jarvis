# Agent guide — Omarchy Jarvis

Read this before changing anything. Optimize for **agent development** and **human understanding**.

## Project goals
1. Local, keyboard-first assistant for **Omarchy** (Hyprland) that turns natural language into safe system actions.
2. Main input: center chat overlay (textbox). No voice in v0.
3. Brain: **Ollama** + small tool-calling model. Actions are scripts/tools, not prompt spaghetti.
4. Keybinds are **data**: parse live catalog; do not hardcode Super combos in the model.
5. Thought bubbles (desktop notifications) with click → **live console** of that run (not just a static file).
6. Heavier workflows become **skills** (scripts + metadata). New skills require **human confirm** before save.
7. Private GitHub repo is the source of truth: milestones, DECISIONS.md, progress log, tested example skills.

## Non-goals (v0)
- Voice, multi-user, LAN exposure of the brain, auto-installing random packages without confirm, replacing Omarchy menus.

## Where things live on this machine
| Path | Role |
|------|------|
| `~/Work/omarchy-jarvis/` | This repo on the implementation host |
| `~/.config/hypr/bindings.lua` | User keybind overrides only |
| Omarchy defaults | `/usr/share/omarchy/default/hypr/bindings/*.lua` |
| Live catalog | `omarchy menu keybindings --print` |
| Notifications | `omarchy-notification-send … [--exec cmd args…]` |
| Webapps | `omarchy-launch-webapp URL` / `omarchy-launch-or-focus-webapp NAME URL` |
| Terminal | `omarchy-launch-terminal` (foot) |
| Browser | Chromium; `omarchy-launch-webapp` for PWAs |

## User-confirmed planning apps (v0 “open planning”)
| App | How to open on this host |
|-----|--------------------------|
| Outlook mail | Binding **SUPER + M** → `https://outlook.live.com/mail/` (also Outlook.desktop) |
| WhatsApp | Binding **SUPER + N** → `https://web.whatsapp.com/` |
| Todoist | Desktop `Todoist.desktop` → `omarchy-launch-webapp https://app.todoist.com/app` (no dedicated hotkey yet) |
| Google Calendar | **Not** the stock SUPER+SHIFT+C (that is HEY calendar). Prefer launch `https://calendar.google.com/` via webapp/focus helper. Document this in DECISIONS.md. |

## Scratchpad (user said “scratchboard”)
- **SUPER + S** → Toggle scratchpad (`special:scratchpad`)
- **SUPER + ALT + S** → Move window to scratchpad (no follow)

## Safety
- Never paste API keys into chat logs.
- Skills that run shell must be reviewable; dry-run / echo mode for risky tools.
- Bind Jarvis overlay to localhost / local IPC only.
- Ask before persisting new skills (user rule).

## How to work in this repo
1. Update `docs/PROGRESS.md` every session (what worked / failed).
2. Record non-obvious choices in `docs/DECISIONS.md` (ADR style: Context → Decision → Consequences).
3. Milestones = GitHub Milestones + tags `v0.1.0`, etc. Close issues against them.
4. Prefer small PRs; keep `actions/` and `skills/` callable from CLI without the UI.
5. After any Hyprland/window change, verify with `hyprctl clients` / `hyprctl workspaces`.
