# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | depth | path |
|----|-------|--------|------|-------------|-------|------|
| A-027 | Enforced promotion path (protected main + separate Forge actor) | blocked | area:docs | NO | high | [active/A-027-protected-promotion-path.md](active/A-027-protected-promotion-path.md) |
| A-028 | Deterministic candidate-eval foundation | queued | area:docs | NO | high | [active/A-028-eval-harness-v0.md](active/A-028-eval-harness-v0.md) |
| A-030 | Protect safety/eval/control-plane paths | blocked | area:docs | NO | medium | [active/A-030-protect-control-plane-paths.md](active/A-030-protect-control-plane-paths.md) |
| A-031 | Stochastic planner evals v0 (10–20 critical behaviors) | blocked | area:docs | NO | high | [active/A-031-stochastic-evals-v0.md](active/A-031-stochastic-evals-v0.md) |
| A-029 | Preference memory v0 (provenance, precedence, revoke) | queued | area:actions | NO | high | [active/A-029-memory-v0-provenance-prefs.md](active/A-029-memory-v0-provenance-prefs.md) |
| A-033 | Latency profiler foundation (traces/spans/store) | queued | area:brain | NO | high | [active/A-033-latency-trace-foundation.md](active/A-033-latency-trace-foundation.md) |
| A-034 | Training Latency Profiler UI (history + inspector) | queued | area:overlay | NO | medium | [active/A-034-training-latency-profiler-ui.md](active/A-034-training-latency-profiler-ui.md) |
| A-035 | Latency distributions, version compare, ledger hooks | queued | area:overlay | NO | medium | [active/A-035-latency-distributions-compare-ledger.md](active/A-035-latency-distributions-compare-ledger.md) |

Recently completed: A-001 … A-025, A-026, A-032, A-036, A-037, A-038, A-039, A-040 (see [done/](done/)).

**A-032 complete:** the codebase-grounded review reshaped the roadmap and Wave 0 briefs.
The [review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md) is the evidence for the
status and dependency changes below.

**A-039 complete (ADR-038):** claims are only real once pushed to `origin/main`, *before* a
worktree is opened; `assignment-status.sh` reads `origin/main` as canonical and flags any
worktree whose local claim disagrees with it. This is now step 1 in every paste prompt and in
`START.md`'s isolation section.

**A-040 complete (ADR-040):** audited the suite — no bloat found, kept every test. Added
`scripts/test-smoke.sh` (curated critical-path subset) and `scripts/test-full.sh` (mirrors CI);
both are quiet by default (summary + bounded failure tail). Smoke is now the default for
docs-only/small changes; full before landing to main or touching brain/overlay/actions.

**A-036 complete:** Agent monitor now shows launch effort and active work, explains local-only
status, and offers explicit visible-window-now versus local-queue delivery.

**A-037 complete (ADR-041):** `Blocked-by`/`Gate` replace prose dependency notes — structured,
parsed by `assignment-status.sh` and Training (Agent monitor board + Assignments editor), which
now show *why* a row isn't claimable instead of a generic "see brief" hint. No global `stage:`
integers; QUEUE.md keeps its existing columns.

**A-038 complete (ADR-042):** `brain/evidence.py` + `scripts/export-evidence.py` turn one
already-journaled run into a bounded, redacted, content-addressed bundle under
`$XDG_STATE_HOME/jarvis/evidence/` — the fingerprint (model digest, planner mode, schema/prompt
hashes) A-026/A-028 need to compare results across revisions. A-026 and A-028 are unblocked.

**A-026 complete (ADR-044):** `docs/ledger/` — Desk-owned, manual, schema-first Improvement
Ledger; `scripts/ledger-status.py` validates it and allocates the next `IMP-NNN` id the same
fetch-origin/main-first way A-039 fixed assignment claims. Seeded IMP-001…IMP-006 from
A-019–A-025/#15/#16. A-029 is unblocked.

**Next up: A-028** — recommended depth high (deterministic candidate-eval foundation;
`Blocked-by: none`, `Gate: control-plane`). A-029 (also unblocked, area:actions) is an equally
valid parallel-ok:NO alternative.

**Revised Wave 0:** A-027 is externally blocked (private-repo protection unavailable until
Alex chooses a supported plan/visibility/host). A-030 waits for A-027+A-028; A-031 waits for
A-030. See the [roadmap](../SELF_IMPROVE_ROADMAP.md) and
[A-032 review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md).

**Wave 1 (after Wave 0):** A-033 → A-034 → A-035 text latency profiler. Brief: [chatgpt-latency-profiler-brief](../audits/chatgpt-latency-profiler-brief-2026-09-10.md).

**Depth column:** Codex `model_reasoning_effort` recommendation (`low|medium|high|xhigh`). Set it when filing; agents report the **next** row’s depth on closeout.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).