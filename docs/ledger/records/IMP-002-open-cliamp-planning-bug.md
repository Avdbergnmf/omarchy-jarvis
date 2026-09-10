# IMP-002 — "Open cliamp" produced an empty or false-success plan

- **Status:** shipped
- **Owner:** Desk
- **Assignment ids:** A-022
- **Evidence refs:** none — historical, predates A-038 evidence bundles (v0); bounded inline summary below
- **Milestone:** none
- **Links:** issue #15

## Current summary
Shipped. Asking Jarvis to "open cliamp" (CLI Amp) produced an empty plan or a false success
reply instead of a truthful, approvable plan that actually opens or focuses the app. Fixed
entirely within `brain/` — the planner now proposes the correct tool/arguments for this and
similar app names, with unit coverage guarding the regression.

## Events (append-only — never edit or delete a past line; add new lines only)
- 2026-09-10 — hypothesis: issue #15 — "open cliamp" (P2) fails to produce a correct, truthful
  plan. Scope stays in `brain/`; plan → approve → execute stays intact (planning only proposes).
- 2026-09-10 — Alex decision: approved as filed.
- 2026-09-10 — assignment A-022 opened and shipped: the planner now yields a correct plan for
  this app-name phrasing; regression covered in `tests/`. Issue #15 evidence recorded in
  `docs/PROGRESS.md`.
- 2026-09-10 — issue #15 closed.
