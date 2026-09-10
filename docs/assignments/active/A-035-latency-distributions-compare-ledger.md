# A-035 — Latency distributions, filters, version compare, ledger hooks

- **Status:** in_progress
- **Area:** area:overlay (+ light brain/docs)
- **parallel-ok:** YES
- **Recommended depth:** medium
- **Blocked-by:** A-034
- **Gate:** latency
- **Links:** chatgpt-latency-profiler-brief §§12–18 · graceful if A-026 ledger missing (soft dependency, not blocking)

## Goal
p50/p90/p95/p99 + counts for selectable ranges; jump from slow tail to traces; bounded filters; version/SHA compare with sample counts; config placeholders for future budgets; attach perf evidence to Improvement Ledger / IMP notes; data shaped for later regression flags (no auto-reject required).

## Checklist
- [ ] Percentiles + explorability + filters + version compare
- [ ] Ledger/PERF evidence hook or docs
- [ ] Tests; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Auto-block merges; Perfetto export (backlog); analytics warehouse.
