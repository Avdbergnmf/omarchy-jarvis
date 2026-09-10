# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-024 | Ambiguous open_app_by_name → top match (Bitwarden #16) | queued | area:actions | YES | [active/A-024-open-ambiguous-app-top-match.md](active/A-024-open-ambiguous-app-top-match.md) |
| A-022 | Fix open cliamp plan/tooling (issue #15) | queued | area:brain | NO | [active/A-022-training.md](active/A-022-training.md) |
| A-025 | App-open preferences + “the other one” correction (#16) | queued | area:brain | NO | [active/A-025-app-open-preferences-and-correction.md](active/A-025-app-open-preferences-and-correction.md) |

Recently completed: A-001 … A-021, A-023, A-019 (see [done/](done/)).

**Bitwarden #16 split:** A-024 (actions, open top match) then A-025 (preferences + correction). A-022 cliamp can run in parallel with A-024 (disjoint areas).

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
