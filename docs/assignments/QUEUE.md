# Assignment queue

Oldest queued at the top among `queued`. **Claimability is computed, not declared** (ADR-047):
`queued` + every `Blocked-by` id `done` + `area:` disjoint from every `in_progress` row. `parallel-ok`
defaults to **YES**; a `NO` must name a reason (`control-plane` / `single-writer` / `human-serial`)
and only restricts *that* row — an in-progress `NO` never blocks anyone else.

| id | title | status | area | parallel-ok | depth | path |
|----|-------|--------|------|-------------|-------|------|
| A-030 | Protect safety/eval/control-plane paths | queued | area:docs | NO | medium | [active/A-030-protect-control-plane-paths.md](active/A-030-protect-control-plane-paths.md) |
| A-031 | Stochastic planner evals v0 (10–20 critical behaviors) | blocked | area:docs | NO | high | [active/A-031-stochastic-evals-v0.md](active/A-031-stochastic-evals-v0.md) |
| A-029 | Preference memory v0 (provenance, precedence, revoke) | in_progress | area:actions | YES | high | [active/A-029-memory-v0-provenance-prefs.md](active/A-029-memory-v0-provenance-prefs.md) |
| A-033 | Latency profiler foundation (traces/spans/store) | queued | area:brain | YES | high | [active/A-033-latency-trace-foundation.md](active/A-033-latency-trace-foundation.md) |
| A-034 | Training Latency Profiler UI (history + inspector) | queued | area:overlay | YES | medium | [active/A-034-training-latency-profiler-ui.md](active/A-034-training-latency-profiler-ui.md) |
| A-035 | Latency distributions, version compare, ledger hooks | queued | area:overlay | YES | medium | [active/A-035-latency-distributions-compare-ledger.md](active/A-035-latency-distributions-compare-ledger.md) |
| A-041 | Agent Monitor tiles + per-agent auto-queue redesign | queued | area:overlay | YES | high | [active/A-041-agent-monitor-tiles-per-agent-auto-queue.md](active/A-041-agent-monitor-tiles-per-agent-auto-queue.md) |
| A-042 | Parallel claimability: migrate tooling and prompts to ADR-047 | queued | area:docs | NO | medium | [active/A-042-parallel-claimability-tooling.md](active/A-042-parallel-claimability-tooling.md) |

Recently completed: A-001 … A-025, A-026, A-027-cancelled, A-028, A-032, A-036, A-037, A-038, A-039, A-040 (see [done/](done/)).

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

**A-028 complete (ADR-045):** `docs/evals/` — four evidence planes documented, one
`unit-test-reference` case schema, `scripts/eval-status.py` + `scripts/check-test-coverage.py`
(new CI step, "no quiet suite omission"). Seeded EVAL-001…EVAL-005. **A-030 is now claimable**
(A-027 cancelled — ADR-046; A-028 done).

**Next up: A-029** — recommended depth high (preference memory v0, area:actions;
`Blocked-by: none`). A-033 (area:brain) and A-041 (area:overlay, `Gate: training-dispatch`) are
equally valid, disjoint-area alternatives.

**A-027 cancelled (ADR-046):** Alex will not buy GitHub Pro or make the repo public for now.
Private Free cannot do branch protection — agents must **not** wait on it or invent a fake gate.
Unattended Forge/auto-merge stay off; human-reviewed merges continue.

**Revised Wave 0:** A-030 is claimable (docs/control-plane ownership map without enforceable
GitHub protection). A-031 still waits on A-030. See the [roadmap](../SELF_IMPROVE_ROADMAP.md)
and [A-032 review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md).

**Wave 1 (after Wave 0):** A-033 → A-034 → A-035 text latency profiler. Brief: [chatgpt-latency-profiler-brief](../audits/chatgpt-latency-profiler-brief-2026-09-10.md).

**Depth column:** Codex `model_reasoning_effort` recommendation (`low|medium|high|xhigh`). Set it when filing; agents report the **next** row’s depth on closeout.

**A-041 filed:** Agent Monitor tiles + per-agent auto-queue redesign (queued, `area:overlay`, depth high, `Gate: training-dispatch`) — Alex UX 2026-09-10; does not block Wave 0/1 claimability.

**ADR-047 — parallel claimability unstuck (2026-09-10):** every open row was `parallel-ok: NO`, so a
second agent had nothing to take even with dependency-free rows in untouched areas. Claimability is
now **computed, not declared**: `queued` + `Blocked-by` met + area disjoint. `parallel-ok` defaults
to **YES**; a `NO` must name `control-plane` / `single-writer` / `human-serial` and restricts only
its own row. A-029, A-033, A-034, A-035 and A-041 flipped to YES; A-030/A-031 keep `NO` with their
control-plane reason written in. With A-029 (`area:actions`) in progress, a second agent can claim
**A-033** or **A-041**. Analysis:
[parallel-claimability-2026-09-10](../audits/parallel-claimability-2026-09-10.md). Tooling and
prompt migration is **A-042**.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).