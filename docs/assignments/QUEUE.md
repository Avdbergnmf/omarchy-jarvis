# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | depth | path |
|----|-------|--------|------|-------------|-------|------|
| A-040 | Test suite optimization (token cost + redundancy) | in_progress | area:docs | NO | medium | [active/A-040-test-suite-token-optimization.md](active/A-040-test-suite-token-optimization.md) |
| A-037 | Release gates + claimability visibility | queued | area:docs | NO | medium | [active/A-037-assignment-stages.md](active/A-037-assignment-stages.md) |
| A-027 | Enforced promotion path (protected main + separate Forge actor) | blocked | area:docs | NO | high | [active/A-027-protected-promotion-path.md](active/A-027-protected-promotion-path.md) |
| A-038 | Evidence identity + durable operational bundles v0 | queued | area:brain | NO | high | [active/A-038-evidence-identity-durable-bundles-v0.md](active/A-038-evidence-identity-durable-bundles-v0.md) |
| A-026 | Improvement Ledger v0 (Desk-owned audit wrapping QUEUE) | blocked | area:docs | NO | high | [active/A-026-improvement-ledger-v0.md](active/A-026-improvement-ledger-v0.md) |
| A-028 | Deterministic candidate-eval foundation | blocked | area:docs | NO | high | [active/A-028-eval-harness-v0.md](active/A-028-eval-harness-v0.md) |
| A-030 | Protect safety/eval/control-plane paths | blocked | area:docs | NO | medium | [active/A-030-protect-control-plane-paths.md](active/A-030-protect-control-plane-paths.md) |
| A-031 | Stochastic planner evals v0 (10–20 critical behaviors) | blocked | area:docs | NO | high | [active/A-031-stochastic-evals-v0.md](active/A-031-stochastic-evals-v0.md) |
| A-029 | Preference memory v0 (provenance, precedence, revoke) | blocked | area:actions | NO | high | [active/A-029-memory-v0-provenance-prefs.md](active/A-029-memory-v0-provenance-prefs.md) |
| A-033 | Latency profiler foundation (traces/spans/store) | queued | area:brain | NO | high | [active/A-033-latency-trace-foundation.md](active/A-033-latency-trace-foundation.md) |
| A-034 | Training Latency Profiler UI (history + inspector) | queued | area:overlay | NO | medium | [active/A-034-training-latency-profiler-ui.md](active/A-034-training-latency-profiler-ui.md) |
| A-035 | Latency distributions, version compare, ledger hooks | queued | area:overlay | NO | medium | [active/A-035-latency-distributions-compare-ledger.md](active/A-035-latency-distributions-compare-ledger.md) |

Recently completed: A-001 … A-025, A-032, A-036, A-039 (see [done/](done/)).

**A-032 complete:** the codebase-grounded review reshaped the roadmap and Wave 0 briefs.
The [review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md) is the evidence for the
status and dependency changes below.

**A-039 complete (ADR-038):** claims are only real once pushed to `origin/main`, *before* a
worktree is opened; `assignment-status.sh` reads `origin/main` as canonical and flags any
worktree whose local claim disagrees with it. This is now step 1 in every paste prompt and in
`START.md`'s isolation section.

**High (Alex):** **A-040** — lean the test suite / smoke vs full so agents waste fewer tokens (now claimable, A-039 docs track is done).

**A-036 complete:** Agent monitor now shows launch effort and active work, explains local-only
status, and offers explicit visible-window-now versus local-queue delivery.

**After A-032 — Training dispatch usability (do before grinding Wave 0 from the window):** A-037 remains after completed A-036 (gates + blocked-by, not stage integers).

**Revised Wave 0:** A-027 is externally blocked (private-repo protection unavailable until
Alex chooses a supported plan/visibility/host). A-038 is the first self-improve foundation;
its acceptance unblocks A-026 and A-028. A-030 waits for A-027+A-028; A-031 waits for A-030;
A-029 waits for A-026 and stays last. See the [roadmap](../SELF_IMPROVE_ROADMAP.md) and
[A-032 review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md).

**Wave 1 (after Wave 0):** A-033 → A-034 → A-035 text latency profiler. Brief: [chatgpt-latency-profiler-brief](../audits/chatgpt-latency-profiler-brief-2026-09-10.md).

**Depth column:** Codex `model_reasoning_effort` recommendation (`low|medium|high|xhigh`). Set it when filing; agents report the **next** row’s depth on closeout.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).