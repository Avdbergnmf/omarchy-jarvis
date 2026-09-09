# A-003 — Run journal (prompt → process → done → eval)

- **Status:** queued
- **Area:** area:brain
- **parallel-ok:** NO
- **Allowed paths:** `brain/`, `actions/core.py` (shared log helper only), `console/`, `docs/LOGGING.md`, `VERSION`, `docs/DECISIONS.md`, `docs/PROGRESS.md`, `tests/`
- **Forbidden paths:** Unrelated overlay redesign
- **Links:** Part C of [CLAUDE_AGENT_ENTRYPOINT_PASS.md](../../passes/active/CLAUDE_AGENT_ENTRYPOINT_PASS.md)

## Goal
Run journal JSONL: prompt → process → done → light eval with jarvis_version + ts; module logs debug-only; version bump resets CURRENT journal.

## Checklist
- [ ] VERSION + LOGGING.md
- [ ] Journal writer + eval heuristics
- [ ] Debug level gated
- [ ] Version reset/archive behavior
- [ ] Tests + doctor; PROGRESS; assignment done

## Out of scope
Cloud LLM eval; OpenTelemetry.
