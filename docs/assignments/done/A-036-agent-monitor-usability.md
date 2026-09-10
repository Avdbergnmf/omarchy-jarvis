# A-036 — Agent monitor usability (depth, delivery clarity, live work visibility)

- **Status:** done
- **Area:** area:overlay (+ light `area:brain` / scripts for depth + handoff launch)
- **parallel-ok:** YES (overlay; disjoint from pure docs Wave 0 if careful on shared Training files — prefer after A-032, before relying on Training to dispatch Wave 0)
- **Wave / stage:** **0** (usability gate for dispatching from Training) — ahead of latency Wave 1
- **Soft path hints:** `overlay/agents.js`, `overlay/training.html`, `overlay/training.css`, `brain/training.py`, `scripts/open-agent.py`, slot registry JSON, `tests/`
- **Links:** Alex 2026-09-10 JARVIS — can’t use agent handling intuitively yet

## Goal
Make Training **Agent monitor / handoff** understandable enough that Alex can dispatch standing assignments from the window without guessing.

### 1) Reasoning depth / effort
- Show **current** depth/effort for a slot when known (e.g. from `~/.codex/config.toml` `model_reasoning_effort`, or last-launch setting stored on the slot).
- Allow **selecting** depth when preparing/opening an agent (at least for Codex/Cursor kinds): e.g. medium / high / ultra if the launcher supports `-c model_reasoning_effort=…`.
- Be honest when depth can’t be read or changed mid-flight (session-start only) — UI copy must say so.

### 2) Delivery methods — rewrite UX
Today’s options (`Prepare now if idle — paste yourself` / `Queue locally until free — no automatic send`) are opaque.
- Rename + help text that plain-language explains each option.
- Add or clarify a path that **opens the agent window and surfaces the prompt immediately** (paste-ready / auto-paste if safe) — Alex asked “can’t we just send it the prompt right away?”
- Keep the safety invariant: Jarvis does **not** silently spend cloud credits or pretend a hidden background agent is running; “send” means visible window + prompt delivery Alex can see.

### 3) “Preview marking busy/idle”
- Either **remove** this control or replace with clear actions (“Mark slot busy”, “Mark idle”) plus one-line explanation: it only updates **local slot metadata**, it does not detect live Codex/Claude processes.
- If kept behind preview/confirm, the button label must not be mysterious.

### 4) See who is working on what (e.g. A-032)
- Assignment list filters that hide `in_progress` must not hide the fact work is underway.
- Agent monitor / queue board must show **in_progress assignments**, owning slot if known, and enough status to decide whether to spin the next parallel-ok task.
- Prefer a persistent “Now working” strip: assignment id, title, stage, agent slot, busy/idle.

## Checklist
- [x] Depth display + launch-time selector (Codex/Cursor); honest limits documented in UI
- [x] Delivery options rewritten; immediate prompt-to-visible-window path
- [x] Busy/idle control clarified or removed
- [x] In-progress / active-work visibility even when queue filter excludes them
- [x] Tests + ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Also (light, for dispatch)
- Surface simple blocked/waiting hints from QUEUE when known; full gates = **A-037**.

## Out of scope
Formal gate schema (A-037); auto-detecting arbitrary third-party chats with perfect fidelity; changing Wave 0/1 product scope; latency profiler.

## Notes
Align with ADR-032 (visible windows). Store per-slot `reasoning_effort` in agent registry if needed.

## Resolution
- Cursor/Codex slots now display their saved launch effort or the local Codex config default,
  accept `low`/`medium`/`high`/`xhigh`, and pass a server-owned setting only when a new Codex
  window starts. The UI explains that focusing an existing session cannot change its depth.
- Handoff choices now state whether they open a visible window immediately or save only to the
  local queue. The exact prompt remains reviewable and paste-ready; Jarvis does not submit it.
- Busy/idle controls explicitly update local slot metadata only. A persistent Now working strip
  and queue board expose in-progress assignments, owners where known, and waiting rows.
- Evidence: 158 Python tests and all five JavaScript suites pass; ShellCheck, `doctor.sh --syntax`,
  and `git diff --check` pass. The `feat-agent-monitor` human guide was updated and remains
  unvalidated pending Alex's live Hyprland/Codex window check. No shared service was restarted.
