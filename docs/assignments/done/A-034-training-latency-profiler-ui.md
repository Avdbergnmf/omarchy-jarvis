# A-034 — Training Latency Profiler UI (history + inspector)

- **Status:** done
- **Area:** area:overlay
- **parallel-ok:** YES (Alex force-parallel with A-041 overlay; this assignment did not edit `overlay/agents.js`)
- **Recommended depth:** medium
- **Blocked-by:** A-033
- **Gate:** latency
- **Soft path hints:** `overlay/` Training UI, A-033 store APIs, `tests/`
- **Links:** chatgpt-latency-profiler-brief §§10–11, 31–32 · ADR-053

## Goal
Training **Performance / Latency** panel: recent-interaction bars (reaction latency), click → waterfall inspector with parallel/hierarchical spans. Spot spike → understand spike in ~10–20s. Correct timing &gt; polish.

## Checklist
- [x] Nav entry + history + inspector wired to A-033 store — Training → Latency; GET `/v1/latency/traces` + `/v1/latency/traces/<id>`; bars = MRL.
- [x] Incomplete/error traces usable — listed with `no MRL` / error styling; unfinished spans remain in the waterfall.
- [x] UI tests / PROGRESS evidence; SESSION; QUEUE/INDEX → done — `tests/latency-panel.test.cjs`; ADR-053.

## Out of scope
Distributions/version compare (A-035); core span redesign; whole Training rewrite.
