# A-029 — Preference memory v0 (provenance, precedence and revoke)

- **Status:** queued
- **Area:** area:actions
- **parallel-ok:** NO
- **Recommended depth:** high
- **Soft path hints:** `actions/core.py`, `brain/server.py` only if run provenance is required, `~/.config/jarvis/` schema, `tests/`, `docs/`
- **Blocked-by:** none
- **Gate:** control-plane
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · extends A-025 · A-032 review · unblocked by A-026 (done) · last assignment in this gate

## Goal
Harden only the proven app-choice preference seam from A-025. Preserve query/stem ranking,
but make every durable influence inspectable and revocable with provenance and explicit
authority. Do not introduce general memories or allow observations to alter behavior.

## Checklist
- [ ] Versioned schema in git; separate ephemeral `last_open` interaction state from durable preference records
- [ ] Record id, constrained type, normalized query/chosen desktop stem, source run/event, created_at, authority, confidence where meaningful, supersedes/revokes, expiry and status—no free-form secret-bearing memory body
- [ ] Define precedence: explicit instruction/correction wins; inference cannot outweigh it by repetition; agent observation never changes ranking in v0
- [ ] Migrate v1 integer weights without changing current choices; create and test a recoverable pre-migration backup and quarantine malformed/unknown versions instead of silently overwriting
- [ ] Add cross-process-safe atomic writes/locking and bounded growth; test concurrent/lost-update behavior
- [ ] Provide callable inspect and revoke/restore paths; any UI-triggered mutation keeps plan → approve → execute
- [ ] Tests cover precedence, migration, corruption, expiry, revoke and A-025 correction compatibility
- [ ] Link the change to its IMP record; docs/human validation if user-visible behavior changes; ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Genericable “memory platform” APIs; episodic memory; embeddings/vector search; consolidation;
free-form agent observations; secrets; remote sync; model-written authority/confidence.
