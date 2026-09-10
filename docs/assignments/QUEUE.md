# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-022 | Fix open cliamp plan/tooling (issue #15) | queued | area:brain | NO | [active/A-022-training.md](active/A-022-training.md) |
| A-025 | App-open preferences + “the other one” correction (#16) | queued | area:brain | NO | [active/A-025-app-open-preferences-and-correction.md](active/A-025-app-open-preferences-and-correction.md) |

Recently completed: A-001 … A-021, A-023, A-019, A-024 (see [done/](done/)).

**A-024 (done):** ambiguous `open_app_by_name` now opens the top-ranked match instead of hard-failing.
**Bitwarden #16:** A-024 done; A-025 (preferences + correction) remains.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
