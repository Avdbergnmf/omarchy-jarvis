# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-039 | Cross-worktree claim visibility (stop double-claiming) | in_progress | area:docs | YES | [active/A-039-cross-worktree-claim-visibility.md](active/A-039-cross-worktree-claim-visibility.md) |
| A-036 | Agent monitor usability (depth, delivery, live work) | in_progress | area:overlay | YES | [active/A-036-agent-monitor-usability.md](active/A-036-agent-monitor-usability.md) |
| A-040 | Test suite optimization (token cost + redundancy) | queued | area:docs | NO | [active/A-040-test-suite-token-optimization.md](active/A-040-test-suite-token-optimization.md) |
| A-037 | Release gates + claimability visibility | queued | area:docs | NO | [active/A-037-assignment-stages.md](active/A-037-assignment-stages.md) |
| A-027 | Enforced promotion path (protected main + separate Forge actor) | blocked | area:docs | NO | [active/A-027-protected-promotion-path.md](active/A-027-protected-promotion-path.md) |
| A-038 | Evidence identity + durable operational bundles v0 | queued | area:brain | NO | [active/A-038-evidence-identity-durable-bundles-v0.md](active/A-038-evidence-identity-durable-bundles-v0.md) |
| A-026 | Improvement Ledger v0 (Desk-owned audit wrapping QUEUE) | blocked | area:docs | NO | [active/A-026-improvement-ledger-v0.md](active/A-026-improvement-ledger-v0.md) |
| A-028 | Deterministic candidate-eval foundation | blocked | area:docs | NO | [active/A-028-eval-harness-v0.md](active/A-028-eval-harness-v0.md) |
| A-030 | Protect safety/eval/control-plane paths | blocked | area:docs | NO | [active/A-030-protect-control-plane-paths.md](active/A-030-protect-control-plane-paths.md) |
| A-031 | Stochastic planner evals v0 (10–20 critical behaviors) | blocked | area:docs | NO | [active/A-031-stochastic-evals-v0.md](active/A-031-stochastic-evals-v0.md) |
| A-029 | Preference memory v0 (provenance, precedence, revoke) | blocked | area:actions | NO | [active/A-029-memory-v0-provenance-prefs.md](active/A-029-memory-v0-provenance-prefs.md) |
| A-033 | Latency profiler foundation (traces/spans/store) | queued | area:brain | NO | [active/A-033-latency-trace-foundation.md](active/A-033-latency-trace-foundation.md) |
| A-034 | Training Latency Profiler UI (history + inspector) | queued | area:overlay | NO | [active/A-034-training-latency-profiler-ui.md](active/A-034-training-latency-profiler-ui.md) |
| A-035 | Latency distributions, version compare, ledger hooks | queued | area:overlay | NO | [active/A-035-latency-distributions-compare-ledger.md](active/A-035-latency-distributions-compare-ledger.md) |

Recently completed: A-001 … A-025, A-032 (see [done/](done/)).

**A-032 complete:** the codebase-grounded review reshaped the roadmap and Wave 0 briefs.
The [review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md) is the evidence for the
status and dependency changes below.

**High (Alex):** **A-040** — lean the test suite / smoke vs full so agents waste fewer tokens (after A-039 docs track).

**HIGHEST (Alex):** **A-039** — claims must be visible on shared main/all worktrees so CONTINUE cannot double-claim (parallel-ok with A-036).

**A-036** is **in_progress** on worktree `~/Work/omarchy-jarvis-a036-agent-monitor-usability` (desk synced status onto main).

**After A-032 — Training dispatch usability (do before grinding Wave 0 from the window):** A-036 then A-037 (gates + blocked-by, not stage integers).

**Revised Wave 0:** A-027 is externally blocked (private-repo protection unavailable until
Alex chooses a supported plan/visibility/host). A-038 is the first self-improve foundation;
its acceptance unblocks A-026 and A-028. A-030 waits for A-027+A-028; A-031 waits for A-030;
A-029 waits for A-026 and stays last. See the [roadmap](../SELF_IMPROVE_ROADMAP.md) and
[A-032 review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md).

**Wave 1 (after Wave 0):** A-033 → A-034 → A-035 text latency profiler. Brief: [chatgpt-latency-profiler-brief](../audits/chatgpt-latency-profiler-brief-2026-09-10.md).

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
