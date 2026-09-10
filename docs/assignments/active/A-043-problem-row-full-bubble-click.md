# A-043 — Training Problems: whole row bubble clickable

- **Status:** queued
- **Area:** area:overlay
- **parallel-ok:** YES
- **Recommended depth:** low
- **Allowed paths (optional soft hint):** `overlay/training.js`, `overlay/training.css`, related overlay tests, `docs/assignments/`, `docs/SESSION.md`, `docs/PROGRESS.md`
- **Forbidden paths (optional soft hint):** chat overlay plan bubbles (A-019); Agent Monitor tiles (A-041); changing Done/Dismiss/Delete semantics
- **Blocked-by:** none
- **Gate:** training-ux
- **Improvement:** none
- **Links:** Alex JARVIS room 2026-09-10 — “whole bubble thing in the list clickable, not just the title/text”

## Goal
In Training → Problems, each `.problem-row` card should select that problem when Alex clicks **anywhere on the bubble** (badges, padding, title area) — not only the title button text.

Done for Alex: missing the narrow title hit-target no longer fails to open the detail pane; action buttons (Done / Dismiss / Reopen / Delete…) still do their own jobs without also selecting (or instead of selecting in a confusing way).

## Checklist
- [ ] Reproduce: click badges / card padding vs title — only title selects today (`renderProblems` in `overlay/training.js`)
- [ ] Make the row the primary select target (button role / keyboard: Enter/Space if the row becomes the control; keep accessible name from the problem title)
- [ ] Action buttons: `stopPropagation` (or equivalent) so they do not double-fire select; Delete preview / status posts unchanged
- [ ] Selected styling (`.problem-row.selected`) still clear; pointer cursor on the clickable card
- [ ] Overlay/training tests cover row click vs action click if practical
- [ ] Update docs/SESSION.md Next action as you go
- [ ] docs/PROGRESS.md note
- [ ] QUEUE/INDEX → done; move this file to docs/assignments/done/

## Out of scope
- Assignments list / Agent Monitor / Latency rows (unless an identical one-liner bug is trivially the same pattern — call out, do not expand scope)
- Redesigning badges, actions layout, or problem detail form
- Chat `#plan` / proposed-action bubbles

## Notes for the coding agent
Token discipline: start at `renderProblems()` (~title `addEventListener('click', … selectProblem)`). Prefer one row-level listener + stopPropagation on `.problem-actions` buttons over duplicating handlers on every child.
