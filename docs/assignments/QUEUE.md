# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-019 | Proposed-action bubble UX (readable plan in the bubble) | queued | area:overlay | NO | [active/A-019-proposed-action-bubble-ux.md](active/A-019-proposed-action-bubble-ux.md) |
| A-022 | Fix open cliamp plan/tooling (issue #15) | queued | area:brain | NO | [active/A-022-training.md](active/A-022-training.md) |
| A-023 | Simplify assignment scope (area + worktree, soft paths) | queued | area:docs | YES | [active/A-023-simplify-assignment-path-scope.md](active/A-023-simplify-assignment-path-scope.md) |

Recently completed: A-001 … A-021 (see [done/](done/)).

**A-020 (done):** Persistence UX fixed (guide closes + inline report on confirm), run id now visible in chat and auto-captured by auto-run steps, auto-drivable mechanical guided steps (`kind: auto`). See ADR-033.

**A-021 (done):** Empty Enter in report Q&A = Skip.

**A-019:** Plan detail inside proposed-action bubbles — next; no other overlay work in_progress.

**A-023 (parallel-ok docs):** Drop hard Allowed/Forbidden path gates; isolation = worktree + area.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
