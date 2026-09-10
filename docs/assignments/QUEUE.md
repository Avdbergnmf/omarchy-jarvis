# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-019 | Proposed-action bubble UX (readable plan in the bubble) | queued | area:overlay | NO | [active/A-019-proposed-action-bubble-ux.md](active/A-019-proposed-action-bubble-ux.md) |
| A-021 | Empty Enter skips report / how-did-that-go Q&A | queued | area:overlay | YES | [active/A-021-empty-enter-skips-report-qa.md](active/A-021-empty-enter-skips-report-qa.md) |
| A-022 | Fix open cliamp plan/tooling (issue #15) | queued | area:brain | NO | [active/A-022-training.md](active/A-022-training.md) |

Recently completed: A-001 … A-020, A-023 (see [done/](done/)).

**A-020:** Done — persistence UX fixed (guide closes + inline report on confirm), run id now visible in chat and auto-captured by auto-run steps, auto-drivable mechanical guided steps (`kind: auto`). See ADR-033.

**A-019:** Plan detail inside proposed-action bubbles (next; same overlay area as A-020 → serial).

**A-021 (simple, parallel-ok):** Empty Enter in report Q&A = Skip. Note: this row is stale in the canonical checkout — it's already implemented and pushed on branch `a021-empty-enter-skips-report-qa`, and a separate session was mid-merge reconciling it into main as of this writing.

**A-023 (done):** Dropped hard Allowed/Forbidden path gates; isolation = worktree + disjoint area. See ADR-034.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
