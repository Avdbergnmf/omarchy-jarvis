# A-035 — Latency distributions, filters, version compare, ledger hooks

- **Status:** queued
- **Area:** area:overlay (+ light brain/docs)
- **parallel-ok:** NO
- **Recommended depth:** medium
- **Wave:** **1**
- **Blocks / blocked-by:** **Blocked by A-034** (graceful if A-026 ledger missing)
- **Links:** chatgpt-latency-profiler-brief §§12–18

## Goal
p50/p90/p95/p99 + counts for selectable ranges; jump from slow tail to traces; bounded filters; version/SHA compare with sample counts; config placeholders for future budgets; attach perf evidence to Improvement Ledger / IMP notes; data shaped for later regression flags (no auto-reject required).

## Checklist
- [ ] Percentiles + explorability + filters + version compare
- [ ] Ledger/PERF evidence hook or docs
- [ ] Tests; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Auto-block merges; Perfetto export (backlog); analytics warehouse.
