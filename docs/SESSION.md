# Session (in-flight agent work)

> Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- **A-029** in_progress — Claude @ `a029-memory-v0-provenance-prefs` / `~/Work/omarchy-jarvis-a029-memory-v0-provenance-prefs` (claim committed to main first, per ADR-038)
- **A-028** done — see [done/A-028-eval-harness-v0.md](assignments/done/A-028-eval-harness-v0.md) / ADR-045
- **A-041** filed — Agent Monitor tiles + per-agent auto-queue redesign (queued, area:overlay, depth high, gate training-dispatch)

## Checklist
- [x] A-039 Cross-worktree claims — done, merged to main, worktree/branch removed
- [x] A-036 Agent monitor usability — done
- [x] A-040 Test suite token optimization — done, merged to main, worktree/branch removed
- [x] A-037 Release gates + claimability visibility — done, merged to main
- [x] A-038 Evidence identity + durable operational bundles v0 — done, merged to main, worktree/branch removed
- [x] A-026 Improvement Ledger v0 — done, merged to main, worktree/branch removed
- [x] A-028 Deterministic candidate-eval foundation — done, merged to main, worktree/branch removed
- [ ] A-041 Agent Monitor redesign — queued (filed; not started)
- [ ] A-029 Preference memory v0 — in_progress, worktree opened

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

## Next action (one concrete step)
- In the `a029-memory-v0-provenance-prefs` worktree: versioned v2 preference-record schema (provenance/authority/expiry/status), v1 migration preserving exact ranking, cross-process locking, inspect/revoke/restore, bounded growth, tests, ADR.

## Parallel agent
- none

## Blockers
- none
