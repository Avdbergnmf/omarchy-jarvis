# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | depth | path |
|----|-------|--------|------|-------------|-------|------|
| A-035 | Latency distributions, version compare, ledger hooks | in_progress | area:overlay | YES | medium | [active/A-035-latency-distributions-compare-ledger.md](active/A-035-latency-distributions-compare-ledger.md) |
| A-042 | Parallel claimability tooling migration (default YES + status hints) | queued | area:docs | NO | medium | [active/A-042-parallel-claimability-tooling.md](active/A-042-parallel-claimability-tooling.md) |

Recently completed: A-001 … A-025, A-026, A-027-cancelled, A-028, A-029, A-030, A-031, A-032, A-033, A-034, A-036, A-037, A-038, A-039, A-040, A-041 (see [done/](done/)).

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

**A-029 complete (ADR-047):** `~/.config/jarvis/app-preferences.json` moves to a versioned v2
schema — each app-open ranking influence is now a durable, provenance-carrying record
(`id`/`authority`/`source`/`created_at`/`confidence`/`expiry`/`status`) instead of a bare int
weight, with explicit authority-tiered precedence (`explicit_correction`/`migrated_v1` always
outrank any amount of `inferred` repetition), inspect/revoke/restore, byte-identical in-memory v1
migration with one-time backup, quarantine for unreadable/unknown-version files, `fcntl.flock`
cross-process locking, and bounded growth (oldest revoked pruned first). IMP-001 updated.

**In progress:** **A-035** (latency distributions/compare, depth **medium**). A-042 remains queued (`parallel-ok: NO`, control-plane tooling).

**A-027 / branch protection (ADR-049):** repo is **public**; `main` ruleset requires PR + `test` check, blocks force-push/deletion. ADR-046's "no protection" stance is superseded. Unattended Forge stays parked ([FUTURE.md](../FUTURE.md)). Parallel claimability: **ADR-048** (`parallel-ok` defaults YES).

**Revised Wave 0:** A-030 and A-031 are done. See the [roadmap](../SELF_IMPROVE_ROADMAP.md)
and [A-032 review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md).

**Wave 1 (after Wave 0):** A-033 → A-034 → A-035 text latency profiler. Brief: [chatgpt-latency-profiler-brief](../audits/chatgpt-latency-profiler-brief-2026-09-10.md).

**Depth column:** Codex `model_reasoning_effort` recommendation (`low|medium|high|xhigh`). Set it when filing; agents report the **next** row’s depth on closeout.

**A-034 complete (ADR-053):** Training → Latency panel — MRL history bars + waterfall inspector on the A-033 store; incomplete/error traces stay listed. Covered by `tests/latency-panel.test.cjs`. A-035 owns distributions/compare/ledger.

**A-041 complete (ADR-043):** Agent Manager now has status-colored tiles, per-agent FIFO queues, canonical available-work filtering, and visible-window auto-advance that never pastes/submits prompts.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
