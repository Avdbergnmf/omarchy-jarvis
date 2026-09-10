# A-033 — Latency profiler foundation (InteractionTrace + spans + storage + core instrumentation)

- **Status:** queued
- **Area:** area:brain (+ light `docs/`)
- **parallel-ok:** YES
- **Recommended depth:** high
- **Blocked-by:** none
- **Gate:** latency
- **Soft path hints:** `brain/`, `docs/LOGGING.md`, new `docs/LATENCY.md`, `tests/`, optional SQLite under XDG/`logs/` (gitignored)
- **Links:** `docs/audits/chatgpt-latency-profiler-brief-2026-09-10.md` · queued after the control-plane gate in practice (QUEUE order), not a hard id dependency; Alex may reorder

## Goal
Architecture for text-first latency profiling **without** Training UI yet.

1. **InteractionTrace** per submitted message (`trace_id`; link `run_id`)
2. Hierarchical **spans** (parent/child, parallel OK, monotonic high-res durations)
3. Primary **`meaningful_response_latency`** = submit → first visible meaningful content (not “Thinking…”, not TTFT alone); also `ack_latency` if applicable
4. Canonical span vocabulary (document it)
5. Instrument from **Enter/submit** through model/tools/render/persistence — diagnostic spans only
6. Local store; privacy: timings/metadata default; no auto-store of prompts/payloads
7. Core emits events; no Training UI coupling
8. Tests: reaction/TTFT/nested/parallel/incomplete/error/privacy/off

## Checklist
- [ ] ADR + `docs/LATENCY.md`
- [ ] Trace/span API + persistence; VERSION/git/model metadata
- [ ] Critical-path instrumentation (minimal overlay hooks only if needed for visible/render marks)
- [ ] Overhead note; tests; PROGRESS; SESSION; QUEUE/INDEX → done
- [ ] Blind spots for A-034/A-035; ledger proposals for architecture smells — no unbounded redesign

## Out of scope
Training UI (A-034); distributions/compare/ledger (A-035); voice; Prometheus stack; hard latency SLOs before baselines.
