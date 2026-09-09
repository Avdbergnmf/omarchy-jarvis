# A-010 — Overlay lifecycle, single-instance, feedback prompt context

- **Status:** queued
- **Area:** area:overlay (+ `area:brain` only if close/restore/single-instance hooks require it)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/`, `scripts/toggle-overlay.py`, `scripts/install-hotkey.py`, `brain/server.py` (close/focus/single-instance / feedback state only), `README.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `tests/`
- **Forbidden paths:** Training mode (A-008/A-009); slash registry redesign beyond what’s needed for focus; unrelated skills
- **Blocks / blocked-by:** **Do this before A-007–A-009** (Alex priority). Unblocks sane UX for RLHF/report.
- **Links:** Alex 2026-09-09 JARVIS room — dismiss after task but restore state; one Jarvis via shortcut; prompt shown with feedback; report text wiped

## Goal
Fix overlay / feedback UX so Jarvis feels like **one** always-reachable assistant:

1. **After a task finishes**, the Jarvis window should **go away** (dismiss), but **reopening** (Super+Shift+J) must restore the **same UI state** (last run, feedback controls, console target, etc. — not a blank amnesiac overlay).
2. **Single instance only.** The “already open somewhere” behavior is wrong/confusing. There is one Jarvis; the hotkey must **focus or re-summon that instance from anywhere**, never imply a second mysterious copy the user can’t find.
3. **Feedback context:** When a prompt has been handled, clear it from the **input box**. Show that prompt text **with the feedback controls** (+ / neutral / −) so Alex knows what the thumbs apply to.
4. **Bug:** In report / feedback typing, whatever Alex types is **removed instantly** and nothing useful happens — find and fix (likely competing key handlers, re-render wiping controlled input, or form reset on poll).

## Checklist
- [ ] Reproduce: finish a run → note overlay visibility; hotkey when “open somewhere”; feedback row vs input; type in report/Q&A and watch wipe
- [ ] Dismiss-on-complete + persist/restore state on reopen (document what is restored)
- [ ] Hotkey = sole entry: focus existing or recreate single instance; kill “already open” dead-ends
- [ ] Last prompt displayed beside/above feedback; input cleared after submit/complete
- [ ] Fix report/feedback input wipe; add regression test
- [ ] README human note; PROGRESS + ADR if needed; QUEUE → done; move to `docs/assignments/done/`

## Out of scope
Training mode features; new slash commands beyond fixing focus.

## Notes for the coding agent
Read A-004 follow-along / A-005 RLHF code paths first — this likely interacts with “overlay stays open during execute” and post-run feedback UI. Prefer one Chromium `--app` profile/class `jarvis-overlay`. Token discipline: START → this file → git diff.
