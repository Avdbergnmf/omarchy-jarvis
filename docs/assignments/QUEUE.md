# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-022 | Fix open cliamp plan/tooling (issue #15) | queued | area:brain | NO | [active/A-022-training.md](active/A-022-training.md) |

Recently completed: A-001 … A-021, A-023 (see [done/](done/)).

**A-020 (done):** Persistence UX fixed (guide closes + inline report on confirm), run id now visible in chat and auto-captured by auto-run steps, auto-drivable mechanical guided steps (`kind: auto`). See ADR-033.

**A-021 (done):** Empty Enter in report Q&A = Skip.

**A-019 (done):** Proposed-action bubble UX — each action is a card (friendly title, description for skills, truncating chips) instead of a bare tool name plus key=value soup below a redundant status line. See ADR-035.

**A-023 (done, parallel-ok docs):** Dropped hard Allowed/Forbidden path gates; isolation = worktree + disjoint area. See ADR-034.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
