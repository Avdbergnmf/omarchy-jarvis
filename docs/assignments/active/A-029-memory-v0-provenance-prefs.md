# A-029 — Memory v0 (typed records + provenance on preference store)

- **Status:** queued
- **Area:** area:brain
- **parallel-ok:** NO
- **Soft path hints:** `brain/`, `~/.config/jarvis/` schema, `tests/`, `docs/`
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · extends A-025

## Goal
Memory v0 records: id, type, content, source, created_at, scope, confidence, authority, supersedes, expires_at, status. **explicit_instruction ≠ inferred preference ≠ agent_observation**. Extend app-preferences; write gate; inspect/revert. XDG + backup; schema docs in git.

## Checklist
- [ ] Schema + migrate existing prefs
- [ ] Provenance writes; ranking read helper
- [ ] Docs + tests; ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Full episodic memory; embeddings; secrets in memory.
