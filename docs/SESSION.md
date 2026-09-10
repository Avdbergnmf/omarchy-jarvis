# Session (in-flight agent work)

> Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- **A-041** in_progress — Codex @ `a041-agent-monitor-auto-queue` / `~/Work/omarchy-jarvis-a041-agent-monitor-auto-queue` (parallel area:overlay; ADR-043 reserved)
- **A-033** in_progress — latency profiler foundation (claim via PR; ruleset)
- **A-031** done — merged PR #25 / ADR-051

## Checklist
- [x] A-039 Cross-worktree claims — done, merged to main, worktree/branch removed
- [x] A-036 Agent monitor usability — done
- [x] A-040 Test suite token optimization — done, merged to main, worktree/branch removed
- [x] A-037 Release gates + claimability visibility — done, merged to main
- [x] A-038 Evidence identity + durable operational bundles v0 — done, merged to main, worktree/branch removed
- [x] A-026 Improvement Ledger v0 — done, merged to main, worktree/branch removed
- [x] A-028 Deterministic candidate-eval foundation — done, merged to main, worktree/branch removed
- [x] A-029 Preference memory v0 — done, merged to main, worktree/branch removed
- [x] A-027 Protected promotion — cancelled (ADR-046)
- [x] A-030 Protect control-plane paths — done (PR + `test` enforced; CODEOWNERS review remains policy)
- [x] A-031 Stochastic planner evals v0 — done (ADR-051); baseline remains human-unapproved
- [ ] A-041 Agent Monitor redesign — in_progress (isolated worktree; area:overlay)

## Done this session (evidence)
- Desk: reproduced A-036 claim only on feature branch; main still said queued. Filed A-039; synced A-036 → in_progress on main.
- Claude: implemented A-039 (ADR-038) — claim-on-origin/main-first protocol, `assignment-status.sh` canonical read + mismatch detector, stale-claim recovery. Merged, worktree/branch removed.
- Codex: implemented A-036 launch-depth, delivery, local-status and active-work behavior; all tests pass.
- Claude: implemented A-040 (ADR-040) — audited the test suite (kept everything), added `scripts/test-smoke.sh`/`test-full.sh`, quiet-by-default output policy in START/prompts. Merged, worktree/branch removed.
- Claude: implemented A-037 (ADR-041) — `Blocked-by`/`Gate` structured metadata replace free-text dependency prose. Merged, worktree/branch removed.
- Claude: implemented A-038 (ADR-042) — `brain/evidence.py` + `scripts/export-evidence.py`, content-addressed evidence bundles. A-026/A-028 unblocked. Merged, worktree/branch removed.
- Desk/Firsty: filed **A-041** (Agent Monitor tiles + per-agent auto-queue redesign); ADR-043 stub reserved for the auto-submit-vs-paste policy decision at implement time.
- Claude: implemented A-026 (ADR-044) — `docs/ledger/` Desk-owned Improvement Ledger, `scripts/ledger-status.py`. Seeded IMP-001…IMP-006. A-029 unblocked. Merged, worktree/branch removed.
- Claude: claimed A-028 by pushing QUEUE/INDEX/SESSION status → in_progress directly to `origin/main` before opening the feature worktree.
- Claude: implemented A-028 (ADR-045) — `docs/evals/` four evidence planes; `EVAL-001`…`EVAL-005`; `eval-status.py` + `check-test-coverage.py`. A-030 left blocked at the time.
- Claude: implemented A-029 (ADR-047) — provenance-carrying app-open preference records. Merged, worktree/branch removed.
- Codex: implemented A-030 (ADR-050) — Control Plane boundary v1, CODEOWNERS, `check-control-plane.py`. A-031 unblocked.
- Cursor/Grok: implemented A-031 (ADR-051) — planner-only stochastic eval runner. 20 `SEVAL-*` cases (14 `json_plan`, 6 `route_prompt`). Fresh child process per trial with execution tripwires; A-038 `kind: eval` bundles; pass@k not reported; baseline unapproved. Router 6/6 and stub-planner 14/14 in `docs/evals/stochastic/summaries/`. Live Ollama N-runs not spent.

## Next action (one concrete step)
- A-041: redesign Agent Manager tiles/available-work/per-agent queues in the isolated worktree; preserve visible-window and no-silent-spend policy.

## Parallel agent
- none

## Blockers
- none
