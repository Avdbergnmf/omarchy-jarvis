# A-019 — Proposed-action bubble UX (readable plan in the bubble)

- **Status:** done
- **Area:** area:overlay (+ light `area:brain` only if structured plan fields are missing)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/` (`app.js`, `index.html`, `style.css`, related tests), `brain/server.py` / plan payload **only if** overlay cannot render without structured fields, `tests/`, `docs/assignments/`, `docs/SESSION.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/validation/`, `VERSION`
- **Forbidden paths:** Training window redesign (A-016–A-018); approval bypass; dumping raw JSON as the primary UI
- **Blocks / blocked-by:** Follow-up to **A-015** (brain labels improved; overlay still hard to read — Alex 2026-09-10)
- **Links:** Alex JARVIS room — plan info appears as text below the proposed bubble; wants it **inside** the proposed-action bubble, human-readable/intuitive; wrap if needed but prefer layout that rarely wraps

## Goal
When Jarvis shows a plan to approve, the **proposed action bubble(s)** carry the important what/where/params in a scannable human layout — not a separate hard-to-read text dump underneath.

- Put the planning detail **into** the proposed-action bubble UI.
- Prefer short structured lines/chips (tool, target, key args) over walls of prose or `key=value` soup.
- CSS: allow wrap when unavoidable (`overflow-wrap` / sensible max-width), but design content so a normal overlay width **rarely needs** wrapping.
- Keep Run/Cancel flow unchanged.

Done for Alex: he can glance at the bubble and understand the plan without decoding the below-bubble text.

## Checklist
- [x] Reproduce current approve UI (bubble + below-bubble text); note what A-015 already ships vs what is still overlay-only
- [x] Redesign `#plan` / `#plan-actions` (and retire or demote redundant below-bubble dump) so each action is a readable bubble/card
- [x] Show human labels + important args (workspace, app name, skill, URL host, etc.) — truncate long values with title/tooltip for full text
- [x] Wrapping: CSS allows wrap; content prefers single-line / compact chips; no horizontal scroll of the overlay
- [x] Live step list stays consistent with the new labels where applicable
- [x] Overlay tests updated; optional small brain field only if structured data is missing
- [x] ADR + PROGRESS; FEATURES/validation touch if user-visible; SESSION; QUEUE/INDEX → done

## Out of scope
- Training Problems/Assignments/Agent monitor
- Changing which tools exist
- Auto-approve

## Notes for the coding agent
- Start at `overlay/app.js` `renderPlan` / `formatAction` and `#draft-preview` vs `#plan-actions`.
- A-015 forbade overlay and fixed `action_label()` in brain — this assignment is the **presentation** pass.
- Token discipline: read overlay plan render once; then diffs.

## Resolution (2026-09-10)
`renderPlan()` builds each action as a `.action-card` (title + description for run_skill +
truncating chips) instead of a bare `<li>` text dump; `#status` no longer repeats the reply
below it. No brain/plan-payload change was needed — `plan.actions`/`plan.reply` already carry
everything the bubble needs. Found and fixed a pre-existing test-mock hazard along the way
(orphaned background poll chain + `innerHTML` not clearing `.children`) that turned a thrown
assertion into a silent hang instead of a clean failure. See ADR-035 and `docs/PROGRESS.md`.
