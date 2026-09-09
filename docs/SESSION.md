# Session (in-flight agent work)

> Agents: update before stopping. Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- Assignment: A-004 — follow-along visibility
- Area: area:overlay
- Branch: main

## Checklist
- [x] Reproduce: `restore_target()` closed every overlay-class window at the *start* of
      `execute_plan`/`execute_tools_plan`, before any step ran or the poller could show
      progress; it then re-focused the pre-overlay window, which each action's own
      dispatch (open_app/workspace/etc.) immediately re-focused past — net effect: overlay
      vanishes instantly on Run, screen flashes to the old window, real result appears
      later (up to ~30s for a newly-launched webapp) with nothing visible in between.
- [x] Fix: `restore_target()` no longer closes the overlay (still focuses the pre-overlay
      target first, required for scratch_move_here-style "current window" correctness).
      Overlay now stays open through execution; only Escape (`/v1/close`, unchanged) or
      re-pressing the hotkey (toggle-overlay.py's existing single-instance logic,
      unchanged) dismisses it.
- [x] Tests: `test_restore_target_focuses_without_closing_overlay` (server), regression
      guard that no `closewindow` dispatch happens for `restore_target` anymore.
- [x] README one-liner.
- [x] PROGRESS + ADR-019.
- [ ] Live host verification (script closed session before running `scripts/verify-host.py`
      / a real approve-and-watch demo) — do this first if resuming.
- [ ] QUEUE/INDEX → done; move file to `docs/assignments/done/`

## Done this session (evidence)
- Desk: filed A-004 + A-005 into QUEUE (Firsty)
- Root-caused and fixed the overlay auto-close-on-Run in `brain/server.py::restore_target`;
  added a regression test; documented in ADR-019 and PROGRESS.md.

## Next action (one concrete step)
- Run `./scripts/doctor.sh` (live) and, if possible, `./scripts/verify-host.py` to confirm
  the overlay still opens/closes/single-instances correctly with the closewindow call
  removed from the execute path (verify-host.py itself doesn't exercise that path, but
  doctor's live checks + a manual approve should be re-confirmed after any host restart).
  Then mark A-004 done (QUEUE + INDEX + move to done/) and start A-005.

## Parallel agent
- Desk (Firsty): filed **A-006** log hygiene (`parallel-ok: YES`, docs/scripts). Another agent may take A-006 without touching overlay/server A-004 files.
- A-004/A-005 remain serial for the overlay agent.

## Blockers
- none
