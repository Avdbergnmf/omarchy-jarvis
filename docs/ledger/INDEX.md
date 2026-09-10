# Improvement Ledger index

Validated by `scripts/ledger-status.py` — run it before allocating the next id (see
[README](README.md#id-allocation-desk-only-collision-resistant)).

| id | title | status | assignment ids | path |
|----|-------|--------|-----------------|------|
| IMP-001 | Ambiguous app-open should pick a match, then let Alex correct it | shipped | A-024, A-025 | [records/IMP-001-bitwarden-ambiguous-app-open.md](records/IMP-001-bitwarden-ambiguous-app-open.md) |
| IMP-002 | "Open cliamp" produced an empty or false-success plan | shipped | A-022 | [records/IMP-002-open-cliamp-planning-bug.md](records/IMP-002-open-cliamp-planning-bug.md) |
| IMP-003 | Plan details belong inside the proposed-action bubble | shipped | A-019 | [records/IMP-003-proposed-action-bubble-ux.md](records/IMP-003-proposed-action-bubble-ux.md) |
| IMP-004 | Validate features didn't visibly persist and asked for unavailable run ids | shipped | A-020 | [records/IMP-004-validate-features-persistence.md](records/IMP-004-validate-features-persistence.md) |
| IMP-005 | Assignment scope should be area + worktree, not a hard path allowlist | shipped | A-023 | [records/IMP-005-assignment-scope-area-not-paths.md](records/IMP-005-assignment-scope-area-not-paths.md) |
| IMP-006 | Empty Enter should Skip in the report / "how did that go" Q&A | shipped | A-021 | [records/IMP-006-empty-enter-skips-report-qa.md](records/IMP-006-empty-enter-skips-report-qa.md) |

Next id: **IMP-007**. Seeded from A-019…A-025 / issues #15, #16 (A-026's own acceptance
criterion) — the six most recent Wave-adjacent improvements at the time this ledger was created;
earlier history (A-001…A-018) is not backfilled in v0.
