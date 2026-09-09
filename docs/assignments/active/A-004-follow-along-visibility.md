# A-004 — Follow-along visibility (see what Jarvis is doing)

- **Status:** queued
- **Area:** area:overlay (+ light `area:brain` / `area:actions` only if required to restore focus)
- **parallel-ok:** NO (touches overlay + post-run focus behavior; serialize with A-005 if both in flight — A-004 first)
- **Allowed paths:** `overlay/`, `scripts/toggle-overlay.py`, `scripts/install-hotkey.py`, `brain/server.py` (only focus/restore/post-run UX hooks), `actions/` (only if adding a small `focus_workspace`/`reveal` helper), `docs/PROGRESS.md`, `docs/DECISIONS.md`, `README.md`, `tests/`
- **Forbidden paths:** Rewriting intake/report tools; RLHF UI (that’s A-005); unrelated skills
- **Blocks / blocked-by:** none (A-005 should land after this so feedback UI sits on the steadier overlay)
- **Links:** user ask 2026-09-09 JARVIS room — “move along… chance to see what it’s doing… feel more permanent”

## Goal
When Jarvis opens apps or switches workspaces, **Alex can actually see it happen**. Today the overlay / focus restore often steals the moment. After a run, the experience should feel **stable and inspectable**, not a flash then back to nowhere.

## Checklist
- [ ] Reproduce current behavior: approve planning or workspace switch; note what focus/overlay does (document in SESSION / ADR)
- [ ] Design: after execute (or per step), **follow** the target workspace/window so the user watches the result; don’t yank focus back to a buried window before they can look
- [ ] Overlay UX: feel more **permanent** — e.g. stay available or re-summon cleanly after a run without losing last run / Open console; avoid “blink and it’s gone” if that’s the bug
- [ ] Keep plan→approve→execute; Esc/Cancel semantics intact
- [ ] Tests (overlay and/or host verify) + README one-liner for humans
- [ ] PROGRESS + ADR; QUEUE → done; move this file to `docs/assignments/done/`

## Out of scope
Thumbs up/down feedback (A-005). New skills. Changing which apps planning opens.

## Notes for the coding agent
Prefer Hyprland-native focus (`hyprctl`) over fake keys. Read existing `restore_target` / overlay close behavior in `brain/server.py` before rewriting. Token discipline: START → this file → git diff.
