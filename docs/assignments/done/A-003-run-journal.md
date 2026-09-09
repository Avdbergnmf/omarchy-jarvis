# A-003 — Run journal (prompt → process → done → eval)

- **Status:** done
- **Area:** area:brain
- **parallel-ok:** NO
- **Allowed paths:** `brain/`, `actions/core.py` (shared log helper only), `console/`, `docs/LOGGING.md`, `VERSION`, `docs/DECISIONS.md`, `docs/PROGRESS.md`, `tests/`
- **Forbidden paths:** Unrelated overlay redesign
- **Links:** Part C of [CLAUDE_AGENT_ENTRYPOINT_PASS.md](../../passes/archive/CLAUDE_AGENT_ENTRYPOINT_PASS.md)

## Goal
Run journal JSONL: prompt → process → done → light eval with jarvis_version + ts; module logs debug-only; version bump resets CURRENT journal.

## Checklist
- [x] VERSION + LOGGING.md
- [x] Journal writer + eval heuristics
- [x] Debug level gated
- [x] Version reset/archive behavior
- [x] Tests + doctor; PROGRESS; assignment done

## Out of scope
Cloud LLM eval; OpenTelemetry.
