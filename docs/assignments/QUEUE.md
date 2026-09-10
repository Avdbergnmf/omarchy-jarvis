# Assignment queue

Oldest queued at the top among `queued`. At most one `in_progress` unless extras are area-disjoint and not a reasoned `parallel-ok: NO` (ADR-048; default is YES).

| id | title | status | area | parallel-ok | depth | path |
|----|-------|--------|------|-------------|-------|------|
| A-043 | Training Problems: whole row bubble clickable | queued | area:overlay | YES | low | [active/A-043-problem-row-full-bubble-click.md](active/A-043-problem-row-full-bubble-click.md) |
| A-045 | Agent manager: opt-in auto-send prompt | queued | area:overlay | YES | medium | [active/A-045-agent-auto-send-prompt-option.md](active/A-045-agent-auto-send-prompt-option.md) |
| A-046 | Validate features overhaul (simple cards) | queued | area:overlay | YES | high | [active/A-046-validate-features-overhaul.md](active/A-046-validate-features-overhaul.md) |
| A-047 | Agent monitor: dynamic status + simpler send | queued | area:overlay | YES | high | [active/A-047-agent-monitor-dynamic-status-send.md](active/A-047-agent-monitor-dynamic-status-send.md) |

Recently completed: A-001 … A-025, A-026, A-027-cancelled, A-028, A-029, A-030, A-031, A-032, A-033, A-034, A-035, A-036, A-037, A-038, A-039, A-040, A-041, A-042, A-044, A-048 (see [done/](done/)).

**A-044 complete:** `overlay/training.js` gained `setHandoffText()` as the single place that
syncs the handoff textarea value with the Copy button's `hidden`/`disabled` state, and
`copyText()` — a guarded Clipboard API call that falls back to focus+select+
`document.execCommand('copy')` and never reports success on a path that didn't actually copy.
The real "feels dead" bug was `overlay/agents.js` `pollAgentAdvance` filling the textarea on
auto-advance without re-showing a previously-hidden Copy button; it now routes through the same
helper. **A-045 is unblocked** (`gate:training-ux` satisfied). Did not add a Copy control to the
agent-detail panel (checklist's optional item) — `last_handoff` is a handoff-file path, not the
prepared text, and no endpoint serves that file's content to the client.

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

**Next up:** A-043 (low) and A-045 (medium, now unblocked) are both claimable; A-046 and A-047 (both high) remain queued behind them.

**A-042 complete (ADR-048 tooling):** Training defaults new briefs to `parallel-ok: YES`; `assignment-status.sh` prints NO reasons, warns on a bare NO (treat as YES pending desk review), and emits a non-blocking `HEADS-UP` on soft path-hint overlap. Paste prompts compute the same claim set. `area:docs` vs `area:control-plane` split is a written proposal only.

**A-027 / branch protection (ADR-049):** repo is **public**; `main` ruleset requires PR + `test` check, blocks force-push/deletion. ADR-046's "no protection" stance is superseded. Unattended Forge stays parked ([FUTURE.md](../FUTURE.md)). Parallel claimability: **ADR-048** (`parallel-ok` defaults YES).

**Revised Wave 0:** A-030 and A-031 are done. See the [roadmap](../SELF_IMPROVE_ROADMAP.md)
and [A-032 review](../audits/chatgpt-plan-vs-codebase-review-2026-09-10.md).

**Wave 1 (after Wave 0):** A-033 → A-034 → A-035 text latency profiler. Brief: [chatgpt-latency-profiler-brief](../audits/chatgpt-latency-profiler-brief-2026-09-10.md).

**Depth column:** Codex `model_reasoning_effort` recommendation (`low|medium|high|xhigh`). Set it when filing; agents report the **next** row’s depth on closeout.

**A-035 complete (ADR-054):** Training Latency distributions — p50/p90/p95/p99, bounded filters, version/SHA compare, slow-tail jump, paste-ready PERF note. Budget keys are placeholders and never block merges. Did not write `docs/ledger/` or allocate an IMP id.

**A-034 complete (ADR-053):** Training → Latency panel — MRL history bars + waterfall inspector on the A-033 store; incomplete/error traces stay listed. Covered by `tests/latency-panel.test.cjs`. A-035 owns distributions/compare/ledger.

**A-041 complete (ADR-043):** Agent Manager now has status-colored tiles, per-agent FIFO queues, canonical available-work filtering, and visible-window auto-advance that never pastes/submits prompts.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
