# Session (in-flight agent work)

> Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- **A-030** in_progress — Codex @ `main` / `~/Work/omarchy-jarvis` (serial assignment; claim committed to main before implementation)
- **A-029** done — see [done/A-029-memory-v0-provenance-prefs.md](assignments/done/A-029-memory-v0-provenance-prefs.md) / ADR-047
- **A-027 cancelled** — no GitHub Pro / no public; ADR-046; do not wait on branch protection
- **A-041** filed — Agent Monitor tiles + per-agent auto-queue redesign (queued, area:overlay, depth high, gate training-dispatch)
- **Next:** A-030 (area:docs, now unblocked), A-033 (area:brain), or A-041 (area:overlay, gate training-dispatch) — queued, disjoint areas

## Checklist
- [x] A-039 Cross-worktree claims — done, merged to main, worktree/branch removed
- [x] A-036 Agent monitor usability — done
- [x] A-040 Test suite token optimization — done, merged to main, worktree/branch removed
- [x] A-037 Release gates + claimability visibility — done, merged to main
- [x] A-038 Evidence identity + durable operational bundles v0 — done, merged to main, worktree/branch removed
- [x] A-026 Improvement Ledger v0 — done, merged to main, worktree/branch removed
- [x] A-028 Deterministic candidate-eval foundation — done, merged to main, worktree/branch removed
- [x] A-029 Preference memory v0 — done, merged to main, worktree/branch removed
- [x] A-027 Protected promotion — cancelled (ADR-046)
- [ ] A-030 Protect control-plane paths — in_progress (unblocked; no enforceable GitHub gate)
- [ ] A-041 Agent Monitor redesign — queued (filed; not started)

## Done this session (evidence)
- Desk: reproduced A-036 claim only on feature branch; main still said queued. Filed A-039; synced A-036 → in_progress on main.
- Claude: implemented A-039 (ADR-038) — claim-on-origin/main-first protocol, `assignment-status.sh` canonical read + mismatch detector, stale-claim recovery. Merged, worktree/branch removed.
- Codex: implemented A-036 launch-depth, delivery, local-status and active-work behavior; all tests pass.
- Claude: implemented A-040 (ADR-040) — audited the test suite (kept everything), added `scripts/test-smoke.sh`/`test-full.sh`, quiet-by-default output policy in START/prompts. Merged, worktree/branch removed.
- Claude: implemented A-037 (ADR-041) — `Blocked-by`/`Gate` structured metadata replace free-text dependency prose. Merged, worktree/branch removed.
- Claude: implemented A-038 (ADR-042) — `brain/evidence.py` + `scripts/export-evidence.py`, content-addressed evidence bundles. A-026/A-028 unblocked. Merged, worktree/branch removed.
- Desk/Firsty: filed **A-041** (Agent Monitor tiles + per-agent auto-queue redesign); ADR-043 stub reserved for the auto-submit-vs-paste policy decision at implement time.
- Claude: implemented A-026 (ADR-044) — `docs/ledger/` Desk-owned Improvement Ledger, `scripts/ledger-status.py`. Seeded IMP-001…IMP-006. A-029 unblocked. Merged, worktree/branch removed.
- Claude: claimed A-028 by pushing QUEUE/INDEX/SESSION status → in_progress directly to `origin/main` before opening the feature worktree.
- Claude: implemented A-028 (ADR-045) — `docs/evals/` documents the four evidence planes (CI/unit, runtime journal, human validation, candidate evals) and none auto-graduates into another; `docs/evals/schema.json`/`cases.json` define one `unit-test-reference` case shape (deterministic, side-effect-free by construction); `scripts/eval-status.py` validates cases and confirms every `reference` resolves to a real test via `ast.parse`; `scripts/check-test-coverage.py` (new CI step) fails on any `tests/*.test.cjs` unreachable from a CI entrypoint or `tests/*.py` not matching `unittest discover`'s pattern — the "no quiet suite omission" contract. Seeded EVAL-001…EVAL-005 from known planner/approval history. Result envelope reuses A-038's `fingerprint()` verbatim plus `counts`/`artifact_hash`, documented for A-031's future runner (no runner built). `START.md`/assignments README now require a regression artifact to close behavior work. A-030 intentionally left blocked (still needs external A-027). Found and fixed a real bug in `check-test-coverage.py`'s first draft (closed over the wrong variable, silently reading the real repo instead of its test fixture). 14 new tests (5 + 9); 204/204 pass.
- Claude: implemented A-029 (ADR-047) — `~/.config/jarvis/app-preferences.json` moves to a versioned v2 schema: each app-open ranking influence is now a durable, provenance-carrying record (`id`/`authority`/`source`/`created_at`/`confidence`/`expiry`/`status`) instead of a bare int weight. Authority-tiered precedence via a large integer multiplier (`explicit_correction`/`migrated_v1` always outrank any amount of `inferred` repetition) without touching `ranked_apps()`'s existing sort key. v1 files migrate in memory on every load (pure, no mutation-on-read), byte-identical ranking, backed up once (`.v1.bak`) on first write; unreadable/unknown-version files are quarantined, never silently overwritten. `fcntl.flock`-based cross-process locking closes the old bare-counter's read-modify-write race. Bounded growth (`PREF_RECORD_KEEP`, oldest revoked pruned first). `inspect_preferences`/`revoke_preference`/`restore_preference` for transparency and reversibility. `correct_open()` now calls `add_preference_record(..., authority='explicit_correction')` instead of the old `bump_app_weight`. Found and fixed a real bug in `_prune_records`'s first draft (default arg bound at def-time, so test patching of `PREF_RECORD_KEEP` had no effect — fixed by always passing it explicitly from `save_app_prefs`). IMP-001 updated with the hardening event. 19 new tests; 223/223 pass. Merged, worktree/branch removed.

## Next action (one concrete step)
- Implement A-030's versioned Control Plane boundary map, CODEOWNERS policy map, and deterministic classification check; then run the smoke/full checks and close the assignment.

## Parallel agent
- none

## Blockers
- none
