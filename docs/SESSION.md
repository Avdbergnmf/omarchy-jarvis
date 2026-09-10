# Session (in-flight agent work)

> Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- **A-028** in_progress — Claude @ `a028-eval-harness-v0` / `~/Work/omarchy-jarvis-a028-eval-harness-v0` (claim committed to main first, per ADR-038)
- **A-026** done — see [done/A-026-improvement-ledger-v0.md](assignments/done/A-026-improvement-ledger-v0.md) / ADR-044
- **A-041** filed — Agent Monitor tiles + per-agent auto-queue redesign (queued, area:overlay, depth high, gate training-dispatch)

## Checklist
- [x] A-039 Cross-worktree claims — done, merged to main, worktree/branch removed
- [x] A-036 Agent monitor usability — done
- [x] A-040 Test suite token optimization — done, merged to main, worktree/branch removed
- [x] A-037 Release gates + claimability visibility — done, merged to main
- [x] A-038 Evidence identity + durable operational bundles v0 — done, merged to main, worktree/branch removed
- [x] A-026 Improvement Ledger v0 — done, merged to main, worktree/branch removed
- [ ] A-041 Agent Monitor redesign — queued (filed; not started)
- [ ] A-028 Deterministic candidate-eval foundation — in_progress, worktree opened

## Done this session (evidence)
- Desk: reproduced A-036 claim only on feature branch; main still said queued. Filed A-039; synced A-036 → in_progress on main.
- Claude: implemented A-039 (ADR-038) — claim-on-origin/main-first protocol, `assignment-status.sh` canonical read + mismatch detector, stale-claim recovery. Merged, worktree/branch removed.
- Codex: implemented A-036 launch-depth, delivery, local-status and active-work behavior; all tests pass.
- Claude: implemented A-040 (ADR-040) — audited the test suite (kept everything), added `scripts/test-smoke.sh`/`test-full.sh`, quiet-by-default output policy in START/prompts. Merged, worktree/branch removed.
- Claude: implemented A-037 (ADR-041) — `Blocked-by`/`Gate` structured metadata replace free-text dependency prose; `assignment-status.sh` computes real unmet blockers via `INDEX.md`. Merged, worktree/branch removed.
- Claude: claimed A-038 by pushing QUEUE/INDEX/SESSION status → in_progress directly to `origin/main` before opening the feature worktree.
- Claude: implemented A-038 (ADR-042) — `brain/evidence.py` (fingerprint + tiered envelope + content-addressed atomic bundle writer) and `scripts/export-evidence.py`, the bounded callable exporter. `brain/server.py` now records `mode`/`model` per run so the fingerprint is derivable from the journal. A-026/A-028 unblocked. 20 new tests; 180/180 tests pass. Merged, worktree/branch removed.
- Desk/Firsty: filed **A-041** (Agent Monitor tiles + per-agent auto-queue redesign) from Alex's 2026-09-10 UX notes; ADR-043 stub reserved for the auto-submit-vs-paste policy decision at implement time.
- Claude: claimed A-026 by pushing QUEUE/INDEX/SESSION status → in_progress directly to `origin/main` before opening the feature worktree.
- Claude: implemented A-026 (ADR-044) — `docs/ledger/` Desk-owned Improvement Ledger (README/TEMPLATE/INDEX + `records/`), `scripts/ledger-status.py` (validates INDEX vs records vs assignment ids; computes next `IMP-NNN` the same fetch-origin/main-first way as A-039). Seeded IMP-001…IMP-006 from A-019–A-025/#15/#16. Optional `Improvement:` assignment metadata added to `brain/training.py` (same pattern as A-037's Blocked-by/Gate). A-029 unblocked. 10 new tests (9 in `tests/test_ledger.py` + 1 in `tests/test_assignments.py`); 190/190 pass. Renumbered its ADR from a colliding 043 (already claimed by A-041's stub) to ADR-044 during merge.

## Next action (one concrete step)
- In the `a028-eval-harness-v0` worktree: four evidence planes doc, `docs/evals/` case schema + seed cases, CI suite-omission contract, START/assignments regression-artifact requirement, ADR. On acceptance, do NOT unblock A-030 (still waits on external A-027).

## Parallel agent
- none

## Blockers
- none
