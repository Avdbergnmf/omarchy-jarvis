# Claude Code — Jarvis transparency & control pass

You are working on **Omarchy Jarvis** at `~/Work/omarchy-jarvis` (private GitHub: `Avdbergnmf/omarchy-jarvis`). Read `AGENTS.md`, `docs/HOST.md`, `docs/DECISIONS.md`, and skim `brain/server.py` + `overlay/*` before changing anything.

## Problem (user feedback)
The current v0 **works as a start** but feels **non-transparent**. The user types a prompt, sees “Thinking…”, then a short reply — while tools already ran. They want to **see and control** what Jarvis is doing. This pass is **UX + control-plane**, not a rewrite of actions/skills.

## Goals
1. **See**: live visibility into plan, each tool call, args, results, and errors — in the overlay itself (not only a detached log).
2. **Control**: no mutating desktop action runs until the user approves (v0 default). Support deny / cancel. Optional later: “auto-run trusted skills only”.
3. **Inspect**: one-click (or hotkey) to open the existing live console for the current/last run.
4. Keep Omarchy-native pieces: `omarchy-notification-send --exec`, `hyprctl`, webapp launchers, example skills.

## Non-goals
- Voice
- New skills without user confirm to *save*
- Replacing Ollama
- Fake-key / ydotool approaches
- Expanding beyond workspace/window + existing skills unless needed for the control UI

## Current architecture (do not throw away)
- Overlay: Chromium `--app` → `http://127.0.0.1:7421/jarvis-overlay` (class `jarvis-overlay`)
- Brain: `brain/server.py` (stdlib HTTP + Ollama tool/JSON plan loop)
- Actions: `actions/*` CLIs
- Skills: `skills/examples/open-planning`, `scratch-and-mail`
- Console: `console/jarvis-console <run_id>` tails `logs/runs/<id>.log`
- Gap: overlay only polls final `reply`; server executes tools immediately after planning

## Required design

### A. Two-phase runs
Every user prompt becomes:
1. **PLAN** — model proposes actions (tool name + arguments + short rationale). Persist to the run log. **Do not execute yet.**
2. **WAIT** — overlay shows the plan clearly.
3. **EXECUTE** — only after `POST /v1/runs/<id>/approve` (or per-step approve).  
   **DENY** — `POST /v1/runs/<id>/deny` cancels with no side effects.

Hello/chitchat with zero actions can skip the approve step and just show the reply.

### B. Overlay UI (transparency)
Expand the overlay enough to be readable (still centered float; adjust window size in toggle script / chromium `--window-size`).

Must show:
- Status: `planning | awaiting approval | running | done | error | denied`
- Proposed actions as a checklist (tool, key args, human label)
- Live step list while executing (tool → result summary)
- Primary buttons: **Run** / **Cancel** (keyboard: Enter confirms when awaiting approval if focus on Run; Esc still closes/cancels safely — document behavior)
- Link/button: **Open console** → launch `jarvis-console` for this `run_id`
- Small footer: model name, ollama ok/fail, last run id

Avoid dumping raw chain-of-thought. Show **structured** plan + tool IO only.

### C. Modes (config file, not rebuild)
`~/.config/jarvis/config.toml` or repo `logs/config.toml` (document choice in DECISIONS):
- `approval_mode = "always"` (default) | `"skills_trusted"` | `"off"` (off only for debugging; warn in UI)
- `show_notifications = true` (thought bubbles remain, but overlay is source of truth)

### D. API additions (suggest; keep auth token)
- `POST /v1/run` → returns `run_id`, `status=awaiting_approval`, `plan={actions,reply}`
- `GET /v1/runs/<id>` → include `status`, `plan`, `steps[]`, `reply`
- `POST /v1/runs/<id>/approve`
- `POST /v1/runs/<id>/deny`
- Optional: `POST /v1/runs/<id>/approve_step`

### E. Docs / agent hygiene
- Add ADR to `docs/DECISIONS.md`: default approve-before-execute for transparency.
- Update `docs/PROGRESS.md` with before/after and how to demo.
- Update `README.md` “Human entry points” for Run/Cancel/Console.
- Do **not** leave `~/Projects/omarchy-jarvis` stale if that’s an old checkout — treat **`~/Work/omarchy-jarvis` as canonical** and push to GitHub.

## Acceptance tests (must pass on this Omarchy host)
1. Prompt “hello” → reply, no approve needed, no hypr/webapp side effects.
2. Prompt “toggle scratchpad” (or equivalent) → plan visible with `scratch_toggle` / binding → **nothing happens until Run** → after Run, scratchpad toggles.
3. Cancel on planning skill → no apps opened / no workspace change.
4. During execute, overlay step list updates; **Open console** shows the same events live.
5. `./scripts/doctor.sh` still green; existing example skills still work under approve flow.
6. Record evidence in `docs/PROGRESS.md`.

## Implementation order
1. Server: plan/approve/deny states + richer `GET /v1/runs/<id>`
2. Overlay: plan panel + Run/Cancel + step stream + Open console
3. Config approval_mode
4. Docs + manual host verification
5. Commit/PR with a clear summary for Alex

## Style constraints
- Prefer small diffs; reuse `actions/` and skills.
- Keep localhost-only auth as now.
- Match Omarchy dark aesthetic; stay keyboard-first.
- If something is ambiguous, choose the more transparent default and note it in DECISIONS.md.

## One-liner when done
Tell Alex: how to open Jarvis, that actions wait for **Run**, how to **Cancel**, how to open the **live console**, and where the ADR lives.
