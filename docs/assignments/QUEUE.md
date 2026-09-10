# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-020 | Validate features: record results, run ids, less busywork | in_progress | area:overlay | NO | [active/A-020-validate-features-ux.md](active/A-020-validate-features-ux.md) |
| A-019 | Proposed-action bubble UX (readable plan in the bubble) | queued | area:overlay | NO | [active/A-019-proposed-action-bubble-ux.md](active/A-019-proposed-action-bubble-ux.md) |
| A-021 | Empty Enter skips report / how-did-that-go Q&A | queued | area:overlay | YES | [active/A-021-empty-enter-skips-report-qa.md](active/A-021-empty-enter-skips-report-qa.md) |
| A-022 | Fix open cliamp plan/tooling (issue #15) | queued | area:brain | NO | [active/A-022-training.md](active/A-022-training.md) |
| A-023 | Simplify assignment scope (area + worktree, soft paths) | queued | area:docs | YES | [active/A-023-simplify-assignment-path-scope.md](active/A-023-simplify-assignment-path-scope.md) |

Recently completed: A-001 … A-018 (see [done/](done/)).

**A-020 (Alex priority):** Validate features must persist Verify/Fail, show prior validation reports, fix run-id UX, automate mechanical guided steps (Alex judges after Run).

**A-019:** Plan detail inside proposed-action bubbles (after A-020 unless already claimed).

**A-021 (simple, parallel-ok):** Empty Enter in report Q&A = Skip.

**A-023 (parallel-ok docs):** Drop hard Allowed/Forbidden path gates; isolation = worktree + area.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
