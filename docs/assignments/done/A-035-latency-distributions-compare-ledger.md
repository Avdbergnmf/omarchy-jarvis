# A-035 — Latency distributions, filters, version compare, ledger hooks

- **Status:** done
- **Area:** area:overlay (+ light brain/docs)
- **parallel-ok:** YES
- **Recommended depth:** medium
- **Blocked-by:** A-034
- **Gate:** latency
- **Links:** chatgpt-latency-profiler-brief §§12–18 · ADR-054 · graceful if A-026 ledger missing (soft dependency, not blocking)

## Goal
p50/p90/p95/p99 + counts for selectable ranges; jump from slow tail to traces; bounded filters; version/SHA compare with sample counts; config placeholders for future budgets; attach perf evidence to Improvement Ledger / IMP notes; data shaped for later regression flags (no auto-reject required).

## Checklist
- [x] Percentiles + explorability + filters + version compare — nearest-rank p50/p90/p95/p99 on `meaningful_response_latency`; Training stats strip, window 20/50/100, planner/status/version/revision filters; version/SHA compare with sample counts; slow tail (≥ p90) jumps to the waterfall.
- [x] Ledger/PERF evidence hook or docs — Copy PERF note (paste-ready Events line). Training never writes `docs/ledger/` or allocates `IMP-*`. Budget keys are placeholders (`enforced: false`).
- [x] Tests; PROGRESS; SESSION; QUEUE/INDEX → done — `tests/test_latency.py` + `tests/latency-panel.test.cjs`; ADR-054.

## Out of scope
Auto-block merges; Perfetto export (backlog); analytics warehouse.
