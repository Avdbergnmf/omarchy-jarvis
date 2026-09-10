# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-032 | ChatGPT deep review: plan vs codebase (plan perfection) | queued | area:docs | NO | [active/A-032-chatgpt-plan-codebase-review.md](active/A-032-chatgpt-plan-codebase-review.md) |
| A-027 | Protected promotion path (main ruleset) | queued | area:docs | YES | [active/A-027-protected-promotion-path.md](active/A-027-protected-promotion-path.md) |
| A-026 | Improvement Ledger v0 (IMP-* wraps QUEUE) | queued | area:docs | YES | [active/A-026-improvement-ledger-v0.md](active/A-026-improvement-ledger-v0.md) |
| A-028 | Eval harness v0 (capability vs regression) | queued | area:docs | YES | [active/A-028-eval-harness-v0.md](active/A-028-eval-harness-v0.md) |
| A-030 | Protect safety/eval/control-plane paths | queued | area:docs | YES | [active/A-030-protect-control-plane-paths.md](active/A-030-protect-control-plane-paths.md) |
| A-031 | Stochastic evals v0 (~10–20 critical behaviors) | queued | area:docs | YES | [active/A-031-stochastic-evals-v0.md](active/A-031-stochastic-evals-v0.md) |
| A-029 | Memory v0 (typed prefs + provenance) | queued | area:brain | NO | [active/A-029-memory-v0-provenance-prefs.md](active/A-029-memory-v0-provenance-prefs.md) |

Recently completed: A-001 … A-025 (see [done/](done/)).

**A-032 first (Alex):** Sol 5.6 ultra-high-depth review of roadmap vs tree — **before** implementing Wave 0.

**Wave 0 (after A-032):** A-027 → A-026 → A-028 → A-030 → A-031 → A-029. Roadmap: [docs/SELF_IMPROVE_ROADMAP.md](../SELF_IMPROVE_ROADMAP.md).

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
