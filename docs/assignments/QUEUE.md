# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-032 | ChatGPT deep review: plan vs codebase (plan perfection) | queued | area:docs | NO | [active/A-032-chatgpt-plan-codebase-review.md](active/A-032-chatgpt-plan-codebase-review.md) |
| A-036 | Agent monitor usability (depth, delivery, live work) | queued | area:overlay | YES | [active/A-036-agent-monitor-usability.md](active/A-036-agent-monitor-usability.md) |
| A-037 | Formal assignment stages + blocked visibility | queued | area:docs | NO | [active/A-037-assignment-stages.md](active/A-037-assignment-stages.md) |
| A-027 | Protected promotion path (main ruleset) | queued | area:docs | YES | [active/A-027-protected-promotion-path.md](active/A-027-protected-promotion-path.md) |
| A-026 | Improvement Ledger v0 (IMP-* wraps QUEUE) | queued | area:docs | YES | [active/A-026-improvement-ledger-v0.md](active/A-026-improvement-ledger-v0.md) |
| A-028 | Eval harness v0 (capability vs regression) | queued | area:docs | YES | [active/A-028-eval-harness-v0.md](active/A-028-eval-harness-v0.md) |
| A-030 | Protect safety/eval/control-plane paths | queued | area:docs | YES | [active/A-030-protect-control-plane-paths.md](active/A-030-protect-control-plane-paths.md) |
| A-031 | Stochastic evals v0 (~10–20 critical behaviors) | queued | area:docs | YES | [active/A-031-stochastic-evals-v0.md](active/A-031-stochastic-evals-v0.md) |
| A-029 | Memory v0 (typed prefs + provenance) | queued | area:brain | NO | [active/A-029-memory-v0-provenance-prefs.md](active/A-029-memory-v0-provenance-prefs.md) |
| A-033 | Latency profiler foundation (traces/spans/store) | queued | area:brain | NO | [active/A-033-latency-trace-foundation.md](active/A-033-latency-trace-foundation.md) |
| A-034 | Training Latency Profiler UI (history + inspector) | queued | area:overlay | NO | [active/A-034-training-latency-profiler-ui.md](active/A-034-training-latency-profiler-ui.md) |
| A-035 | Latency distributions, version compare, ledger hooks | queued | area:overlay | NO | [active/A-035-latency-distributions-compare-ledger.md](active/A-035-latency-distributions-compare-ledger.md) |

Recently completed: A-001 … A-025 (see [done/](done/)).

**A-032 first (Alex):** Sol 5.6 ultra-high-depth review of roadmap vs tree — **before** implementing Wave 0.

**How Alex should prompt Sol**
- Same ongoing Sol chat → paste [`CONTINUE.txt`](prompts/CONTINUE.txt) and add: `Do A-032 only. Batch 1. Stop when A-032 is done.` (Saying only “next” is OK **if** SESSION already points at A-032; safer to name **A-032**.)
- Cold/new Sol chat → paste [`NEW_AGENT.txt`](prompts/NEW_AGENT.txt); it should claim the first queued row (**A-032**).
- Briefing without chat history: `docs/audits/chatgpt-self-improve-discussion-brief-2026-09-10.md`

**After A-032 — Training dispatch usability (do before grinding Wave 0 from the window):** A-036 then A-037 (stages).

**Wave 0 / stage 1 (after A-032; ideally after A-036/A-037 if dispatching from Training):** A-027 → A-026 → A-028 → A-030 → A-031 → A-029. Roadmap: [docs/SELF_IMPROVE_ROADMAP.md](../SELF_IMPROVE_ROADMAP.md).

**Wave 1 (after Wave 0):** A-033 → A-034 → A-035 text latency profiler. Brief: [chatgpt-latency-profiler-brief](../audits/chatgpt-latency-profiler-brief-2026-09-10.md).

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
