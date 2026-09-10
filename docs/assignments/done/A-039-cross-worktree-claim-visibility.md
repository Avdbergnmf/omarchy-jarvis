# A-039 — Cross-worktree claim visibility (stop double-claiming)

- **Status:** queued → mark **in_progress** when claimed
- **Area:** area:docs (+ `scripts/`, prompts; light Training read of claims OK)
- **parallel-ok:** YES (disjoint from A-036 `area:overlay`)
- **Priority:** **HIGHEST** — blocks safe parallel CONTINUE/NEW_AGENT
- **Soft path hints:** `docs/assignments/prompts/`, `START.md`, `scripts/assignment-status.sh`, optional `docs/assignments/CLAIMS.md` or push-claim helper, Training board if trivial
- **Links:** Alex 2026-09-10 — agent claims + worktree but main QUEUE/SESSION unchanged; next agent re-claims same task; overlapping code risk. Live evidence: A-036 `in_progress` only on `omarchy-jarvis-a036-agent-monitor-usability`, still `queued` on `main`.

## Goal
When an agent **claims** an assignment and opens a worktree, **every other agent** (and Training / `assignment-status`) must see that claim **immediately** from the shared truth (`origin/main` or an equivalent shared claims surface) — not only inside the claimer’s unpushed branch.

Acceptance:
1. Claim protocol: mark `QUEUE`/`INDEX` (+ SESSION owner/branch/worktree) **on main (or push a claim commit to `origin/main` first)** *before* doing product work in the feature worktree — or maintain a desk-owned `CLAIMS`/`locks` file on main that claimers update via a small documented push.
2. `assignment-status.sh` aggregates **all worktrees** + `origin/main` so double-claim is impossible to miss.
3. `NEW_AGENT.txt` / `CONTINUE.txt` / START: refuse to claim if another tree or origin already has `in_progress` for that id / conflicting area.
4. Training Agent monitor (if easy) shows live claims from the same source of truth.
5. Document recovery: stale claim, crashed agent, how to release.

Keep plan→approve→execute untouched. Do not require merging the whole feature branch to advertise a claim.

## Checklist
- [x] Reproduce: claim on worktree-only leaves `main` saying `queued` (A-036 case) — confirmed live before this assignment started (SESSION/PROGRESS 2026-09-10), then re-created synthetically by editing a worktree's local `QUEUE.md` without pushing and confirming `assignment-status.sh` flags it, then reverted.
- [x] Implement shared claim visibility: claim commit pushed straight to `origin/main` *before* opening the feature worktree (no separate CLAIMS file needed — QUEUE/INDEX/SESSION on `origin/main` already carry owner/branch/worktree).
- [x] Update prompts + START so claim-to-shared-truth is step 1 of claiming (`START.md`, `NEW_AGENT.txt`, `CONTINUE.txt`, `PARALLEL.txt`, `prompts/README.md`, `docs/assignments/README.md`).
- [x] Harden `assignment-status.sh` to scan worktrees + origin (canonical `origin/main` QUEUE read, per-worktree SESSION listing, cross-worktree `MISMATCH` detector).
- [x] Tests or scripted smoke; ADR; PROGRESS; SESSION; QUEUE/INDEX → done — see ADR-038, PROGRESS 2026-09-10 entry.
- [x] Verify a second CONTINUE cannot claim an id already in_progress elsewhere — `assignment-status.sh` claim hint now reads `origin/main`, where both A-039 and A-036 show `in_progress`, so neither is offered as claimable.
- [~] Training Agent monitor shows live claims from the same source of truth — **deferred to A-036** (`area:overlay`, already `in_progress`, whose own checklist item "In-progress / active-work visibility even when queue filter excludes them" covers this surface exactly; touching `overlay/training.*` now would duplicate/conflict with that in-flight work).

Also ensure prompts require **merge to main at batch end** (CONTINUE/NEW_AGENT/START) — already landed by Alex directly on `main` (commit `73e44f7`) while this assignment was being claimed; picked up via merge and left intact.

## Out of scope
Rewriting A-036 product UI (coordinate only); full lock server; changing parallel-ok area rules.

## Notes
START already warns QUEUE/SESSION are branch-local — that warning is the bug. Fix the protocol, don’t just warn louder.
