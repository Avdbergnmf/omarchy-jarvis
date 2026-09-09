# A-001 — Agent efficiency + SESSION resume

- **Status:** done
- **Area:** area:docs
- **parallel-ok:** YES
- **Allowed paths:** `START.md`, `AGENTS.md`, `docs/SESSION.md`, `docs/passes/README.md`, `docs/assignments/**`, `scripts/agent-status.sh`, `scripts/assignment-status.sh`, `scripts/agent-handoff-continue.sh`, `docs/PROGRESS.md`, `docs/DECISIONS.md`
- **Forbidden paths:** `brain/`, `overlay/`, `actions/`, `skills/` (product code)
- **Links:** [CLAUDE_AGENT_EFFICIENCY.md](../../passes/archive/CLAUDE_AGENT_EFFICIENCY.md)

## Goal
Bake token/context discipline and resumable SESSION checklist into START/AGENTS; keep assignment queue usable. Docs/scripts only.

## Checklist
- [x] Implement efficiency pass ideas still missing from START
- [x] Ensure START links to assignments/prompts and QUEUE
- [x] SESSION.md live and referenced
- [x] assignment-status.sh works
- [x] PROGRESS note; mark done in QUEUE/INDEX; move to done/

## Out of scope
Overlay/brain/actions feature work.
