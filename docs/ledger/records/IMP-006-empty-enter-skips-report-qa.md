# IMP-006 — Empty Enter should Skip in the report / "how did that go" Q&A

- **Status:** shipped
- **Owner:** Desk
- **Assignment ids:** A-021
- **Evidence refs:** none — historical, predates A-038 evidence bundles (v0); bounded inline summary below
- **Milestone:** none
- **Links:** none

## Current summary
Shipped. In the post-run report/clarifying-Q&A flow (the "how did that go" intake after a 👎
Report, or the same Q&A UI elsewhere), pressing Enter on an empty answer did nothing useful —
Alex had to type `skip` or click the Skip button to move on. A-021 made empty Enter behave
exactly like Skip in that flow.

## Events (append-only — never edit or delete a past line; add new lines only)
- 2026-09-10 — hypothesis: Alex — hitting Enter on an empty report/Q&A answer should Skip, so he
  can blast through without typing `skip` or reaching for the mouse.
- 2026-09-10 — Alex decision: approved as filed; scoped to the overlay chat Q&A/feedback Enter
  handling only, disjoint from A-020's Training validation panel (same overlay area, so still
  serial per QUEUE, not parallel).
- 2026-09-10 — assignment A-021 opened and shipped: empty-Enter in the report/Q&A flow now
  triggers the same `answer('skip')` path as the Skip button; covered in
  `tests/overlay.test.cjs`.
