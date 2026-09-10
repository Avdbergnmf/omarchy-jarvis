# A-034 — Training Latency Profiler UI (history + inspector)

- **Status:** queued
- **Area:** area:overlay
- **parallel-ok:** NO
- **Recommended depth:** medium
- **Blocked-by:** A-033
- **Gate:** latency
- **Soft path hints:** `overlay/` Training UI, A-033 store APIs, `tests/`
- **Links:** chatgpt-latency-profiler-brief §§10–11, 31–32

## Goal
Training **Performance / Latency** panel: recent-interaction bars (reaction latency), click → waterfall inspector with parallel/hierarchical spans. Spot spike → understand spike in ~10–20s. Correct timing &gt; polish.

## Checklist
- [ ] Nav entry + history + inspector wired to A-033 store
- [ ] Incomplete/error traces usable
- [ ] UI tests / PROGRESS evidence; SESSION; QUEUE/INDEX → done

## Out of scope
Distributions/version compare (A-035); core span redesign; whole Training rewrite.
