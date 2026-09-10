# A-018 — Training Agent monitor (tiles, visible agent windows, queue board)

- **Status:** done
- **Area:** area:overlay (+ light `area:brain` / `scripts` for launch + window focus)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/` (Agent monitor panel), `brain/training.py`, `brain/server.py` (agent slot / launch endpoints), `scripts/` (launch Claude/Codex/etc. into real Hyprland windows), Hyprland helpers as needed, `tests/`, `docs/assignments/`, `docs/SESSION.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/HOST.md`, `README.md`, `START.md`, `VERSION`
- **Forbidden paths:** Hidden/headless-only agent runs as the primary path; silent cloud spend; stealing A-016/A-017 UX; rewriting chat overlay (A-015)
- **Blocks / blocked-by:** **Blocked by A-017** (Hand off + assignment preselect). Prefer after A-016 chrome exists. Before A-015.
- **Links:** Alex 2026-09-10 JARVIS — Agent monitor tiles; click agent → overview + **open visible Hyprland window** showing live progress (like opening Claude Code yourself); left assignment list to spin up/assign; interactive parallel-aware queue board

## Goal
Agent monitor is where Alex **sees and steers local coding agents without them living in the background**.

- **Agent tiles** — one tile per known/running agent (slot). Click → overview (status, current assignment, last handoff, busy/idle).
- **Open agent window (critical)** — from that overview, open/focus a real **Hyprland window** for that agent’s session (Claude Code / Codex / terminal UI), so progress is visible as if he launched and pasted the prompt himself — not a hidden background job.
- **Left: assignment list** — select an assignment (preselected if navigated from Assignments “Hand off”); configure settings; **spin up a new agent** or **assign an existing** idle slot, then launch into a visible window with the handoff prompt.
- **Queue board** — clearer interactive view of which assignments are queued / in progress / done, and which are **parallel-ok** vs serial — a nicer live version of `QUEUE.md` / `assignment-status`.

Done means Alex can monitor and drive agents from Training without digging for hidden terminals.

## Checklist
- [x] Agent monitor panel in Training nav (post A-016/A-017)
- [x] Tile grid for agent slots; click → detail overview
- [x] **Open / focus Hyprland window** for that agent’s live session (launch if needed); document window rules/classes
- [x] Left assignment list; preselect from A-017 handoff deep-link
- [x] Actions: assign existing idle agent **or** create/launch new slot with settings (kind, label, prompt template CONTINUE/NEW_AGENT/PARALLEL)
- [x] Launch path always yields a **visible** window + paste-ready or auto-pasted prompt (confirm before spend if cloud)
- [x] Interactive queue board: status, area, parallel-ok, current worker; reflects disk QUEUE/SESSION without lying
- [x] ADR (visible agents over hidden); tests where feasible; PROGRESS; HOST note for hotkeys/window rules; SESSION; QUEUE/INDEX → done

## Out of scope
- Fully detecting arbitrary third-party chats with perfect fidelity if the tool exposes no handle — be honest; prefer launch-under-Training so the window is known
- Cloud auto-dispatch without confirm
- Problems/Assignments CRUD (A-016/A-017)
- Chat plan detail (A-015)

## Notes for the coding agent
- Prefer `hyprctl` clients + known app_id/class for Claude/Codex/foot; reuse Omarchy launch patterns.
- Slot metadata alone is not enough — Alex explicitly rejected background/hidden as the main UX.
- Token discipline: read A-016/A-017 results + current training agent UI once; then diffs.

## Resolution (2026-09-10)
`scripts/open-agent.py` + `POST /v1/training/agent-window` open/focus a real per-slot
terminal via `omarchy-launch-or-focus-tui`; tile grid + detail overview + queue board added
to `overlay/agents.js`/`training.html`. No auto-typed prompt (out of scope decision, see
ADR-032) — Copy handoff remains the paste step, but the window is now always visible.
138 Python tests + all 5 JS suites pass. See ADR-032 and `docs/PROGRESS.md` for full detail.
