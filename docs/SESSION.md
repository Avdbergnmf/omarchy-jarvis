# Session (in-flight agent work)

> Agents: update before stopping. Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- Assignment: _(none — A-004 done; next queued is A-005)_
- Area: area:overlay
- Branch: main

## Checklist
- [x] A-004 follow-along visibility — done, see `docs/assignments/done/A-004-follow-along-visibility.md`
- [ ] A-005 RLHF feedback (next)

## Done this session (evidence)
- A-004: `restore_target()` in `brain/server.py` no longer closes the overlay window at the
  start of execution (only focuses the pre-overlay target, still required for
  scratch_move_here-style actions). Overlay now stays open through planning → approval →
  live steps → terminal reply; dismissed only via Esc or re-pressing the hotkey.
- Tests: `test_restore_target_focuses_without_closing_overlay`,
  `test_restore_target_noop_without_a_target` (58 tests total, all green).
- Live-verified on this host: opened a real overlay via `toggle-overlay.py`, submitted and
  approved a real `scratch_toggle` run through the HTTP API, and confirmed via `hyprctl
  clients` that the overlay window (`0x5626b3fd5ed0`) was present at every stage —
  post-open, post-plan, post-approve, and post-`done` — then confirmed `POST /v1/close`
  still dismisses it correctly. `./scripts/doctor.sh` (live) and `--syntax`, `node
  tests/overlay.test.cjs`, and `shellcheck` all pass.
- ADR-019 + PROGRESS.md entry added. README one-liner added.
- QUEUE/INDEX updated; assignment file moved to `docs/assignments/done/`.
- Committed to `main` (see git log).

## Next action (one concrete step)
- Take **A-005** (post-run RLHF feedback: +/neutral/−) next — read
  `docs/assignments/active/A-005-rlhf-feedback.md`. Not started this session (one
  assignment chunk per session per START.md's token discipline).

## Parallel agent
- **A-006** (log hygiene, `parallel-ok: YES`, area:docs) is queued and disjoint from
  overlay/brain — safe for another agent to pick up concurrently.

## Blockers
- none
