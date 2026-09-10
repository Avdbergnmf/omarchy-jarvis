# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-019 | Proposed-action bubble UX (readable plan in the bubble) | queued | area:overlay | NO | [active/A-019-proposed-action-bubble-ux.md](active/A-019-proposed-action-bubble-ux.md) |
| A-021 | Empty Enter skips report / how-did-that-go Q&A | queued | area:overlay | YES | [active/A-021-empty-enter-skips-report-qa.md](active/A-021-empty-enter-skips-report-qa.md) |

Recently completed: A-001 … A-020 (see [done/](done/)).

**A-020:** Done — persistence UX fixed (guide closes + inline report on confirm), run id now visible in chat and auto-captured by auto-run steps, auto-drivable mechanical guided steps (`kind: auto`). See ADR-033.

**A-019:** Plan detail inside proposed-action bubbles (next; same overlay area as A-020 → serial).

**A-021 (simple, parallel-ok):** Empty Enter in report Q&A = Skip.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
