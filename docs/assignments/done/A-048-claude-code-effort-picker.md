# A-048 — Claude Code: select launch effort / depth

- **Status:** done
- **Area:** area:overlay (+ `scripts/open-agent.py`, `brain/training.py`)
- **parallel-ok:** YES
- **Recommended depth:** low
- **Allowed paths (optional soft hint):** `overlay/agents.js`, `overlay/training.html`, `scripts/open-agent.py`, `brain/training.py`, related tests, ADR/HOST/PROGRESS
- **Forbidden paths (optional soft hint):** auto-paste (A-045); Agent monitor send UX (A-047)
- **Blocked-by:** none
- **Gate:** training-ux
- **Improvement:** none
- **Links:** Alex JARVIS room 2026-09-10 — could not select depth for Claude agents; “implement an assignment to set the effort.” Supersedes A-036’s “Claude cannot control depth” assumption. Landed PR #43.

## Goal
Agent manager lets Alex pick reasoning **effort/depth** for `claude-code` slots the same way Cursor/Codex slots do — persisted on the slot and applied when a **new** window starts via `claude --effort <level>` (`low|medium|high|xhigh|max`). Focusing an existing window does not change that session. Default may come from `~/.claude/settings.json` `effortLevel` when no slot override is set.

## Checklist
- [x] Enable effort UI for `claude-code` (include `max`); keep Cursor low–xhigh
- [x] Persist/validate per-kind efforts in training registry + dashboard effective effort
- [x] `open-agent.py` passes `--effort` for Claude; Codex `-c model_reasoning_effort` unchanged
- [x] Tests + ADR/HOST note; PROGRESS; SESSION
- [x] QUEUE/INDEX → done (this closeout)

## Out of scope
- Changing effort on an already-running Claude session
- Human slots
- Auto-submit prompts

## Notes for the coding agent
Claude CLI: `--effort` with values low, medium, high, xhigh, max.

## Resolution (2026-09-10)
Implemented and merged as focused fix PR #43 (`cursor/claude-code-effort-a825`) before this assignment id existed — desk filed A-048 after the fact so the queue records the ask. UI fills effort options per kind; brain reads Claude `effortLevel` default; launcher uses `--effort`. See ADR follow-up in `docs/DECISIONS.md` / HOST and `docs/PROGRESS.md`.
