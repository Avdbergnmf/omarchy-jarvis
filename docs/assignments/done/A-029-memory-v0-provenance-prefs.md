# A-029 — Preference memory v0 (provenance, precedence and revoke)

- **Status:** done
- **Area:** area:actions
- **parallel-ok:** NO
- **Recommended depth:** high
- **Soft path hints:** `actions/core.py`, `brain/server.py` only if run provenance is required, `~/.config/jarvis/` schema, `tests/`, `docs/`
- **Blocked-by:** none
- **Gate:** control-plane
- **Improvement:** IMP-001
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · extends A-025 · A-032 review · unblocked by A-026 (done) · last assignment in this gate

## Goal
Harden only the proven app-choice preference seam from A-025. Preserve query/stem ranking,
but make every durable influence inspectable and revocable with provenance and explicit
authority. Do not introduce general memories or allow observations to alter behavior.

## Checklist
- [x] Versioned schema in git; separate ephemeral `last_open` interaction state from durable preference records — v2 `{"version":2,"records":{...},"last_open":...}`; `last_open` untouched from A-025.
- [x] Record id, constrained type, normalized query/chosen desktop stem, source run/event, created_at, authority, confidence where meaningful, supersedes/revokes, expiry and status—no free-form secret-bearing memory body — all fields present; `supersedes`/`revokes` reserved/nullable (no v0 write path populates them).
- [x] Define precedence: explicit instruction/correction wins; inference cannot outweigh it by repetition; agent observation never changes ranking in v0 — `EXPLICIT_TIER_MULTIPLIER` encodes this as plain int comparison; no `inferred` write path exists.
- [x] Migrate v1 integer weights without changing current choices; create and test a recoverable pre-migration backup and quarantine malformed/unknown versions instead of silently overwriting — in-memory migration on every load (identical ranking), `.v1.bak`/quarantine on first write.
- [x] Add cross-process-safe atomic writes/locking and bounded growth; test concurrent/lost-update behavior — `fcntl.flock`-based `_app_prefs_lock`; 16-thread/40-write concurrency test proves zero lost updates; `PREF_RECORD_KEEP` bounded pruning.
- [x] Provide callable inspect and revoke/restore paths; any UI-triggered mutation keeps plan → approve → execute — `inspect_preferences`/`revoke_preference`/`restore_preference`; no new UI/tool added, so plan→approve→execute is untouched.
- [x] Tests cover precedence, migration, corruption, expiry, revoke and A-025 correction compatibility — `tests/test_app_preferences.py` (19 cases) + updated `tests/test_jarvis.py::OpenByNameTest`.
- [x] Link the change to its IMP record; docs/human validation if user-visible behavior changes; ADR; PROGRESS; SESSION; QUEUE/INDEX → done — linked to [IMP-001](../../ledger/records/IMP-001-bitwarden-ambiguous-app-open.md) (new event + `Improvement:` field above); no validation entry needed (ranking/correction UX provably unchanged; inspect/revoke/restore are backend-only in v0). ADR-047.

## Out of scope
Genericable “memory platform” APIs; episodic memory; embeddings/vector search; consolidation;
free-form agent observations; secrets; remote sync; model-written authority/confidence.
