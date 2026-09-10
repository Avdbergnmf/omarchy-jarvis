# IMP-004 — Validate features didn't visibly persist and asked for unavailable run ids

- **Status:** shipped
- **Owner:** Desk
- **Assignment ids:** A-020
- **Evidence refs:** none — historical, predates A-038 evidence bundles (v0); bounded inline summary below
- **Milestone:** none
- **Links:** ADR-033

## Current summary
Shipped. Training's Verify/Fail didn't clearly leave the pending list after a confirmed
result, the guided-step run-id field asked for something Jarvis never showed anywhere, and every
mechanical "open Jarvis, type X, press Enter" step was manual busywork before a human even
reached the part needing judgment. A-020 fixed persistence visibility, surfaced the run id in
the overlay footer, and added an `auto`-kind guided step that runs itself via the same
`/v1/run` path a chat send uses — three independent, separately addressable fixes landed
together.

## Events (append-only — never edit or delete a past line; add new lines only)
- 2026-09-10 — hypothesis: Alex — Validate features feels broken/frustrating: unclear
  persistence, a run-id field nothing populates, and mechanical setup steps done by hand.
- 2026-09-10 — Alex decision: approved as filed; independent of A-019 (same overlay area, so
  serial, not parallel) and prioritized above it.
- 2026-09-10 — assignment A-020 opened and shipped: `validationSaved()` closes the guide back to
  the list on a confirmed result; the validation list shows each item's last report inline; the
  overlay footer surfaces and lets you copy the current run id; a catalog step can now be
  `{"text","kind":"auto","prompt"}` with a **Run this step** button that posts the prompt, polls
  the run, and auto-fills the evidence field. `feat-overlay-chat`'s three "Type: ..." steps
  migrated to `auto` as the reference case. See ADR-033.
