# A-029 — Memory v0 (typed records + provenance on preference store)

- **Status:** queued
- **Area:** area:brain
- **parallel-ok:** NO
- **Soft path hints:** `brain/`, `~/.config/jarvis/` schema, `tests/`, `docs/`
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · extends A-025

## Goal
Memory v0 from app-preferences: kinds (`explicit_instruction`, `preference`, `observation`), provenance, write gate, inspect/revert. XDG/gitignored.

## Checklist
- [ ] Schema + migrate existing prefs
- [ ] Provenance writes; ranking read helper
- [ ] Docs + tests; ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Full episodic memory; embeddings; secrets in memory.
