# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-013 | Parallel agents: default git worktrees | in_progress | area:docs | YES | [active/A-013-parallel-worktrees-default.md](active/A-013-parallel-worktrees-default.md) |
| A-007 | Slash-command autocomplete | queued | area:overlay | NO | [active/A-007-slash-command-autocomplete.md](active/A-007-slash-command-autocomplete.md) |
| A-008 | Training mode (improvement control plane) | queued | area:overlay | NO | [active/A-008-training-mode.md](active/A-008-training-mode.md) |
| A-009 | Human validation tests in Training mode | queued | area:overlay | NO | [active/A-009-human-validation-tests.md](active/A-009-human-validation-tests.md) |

Recently completed: A-001 … A-006, A-010, A-011, A-012 (see [done/](done/)).

**Astra / overlay track:** A-007→A-008→A-009 may be in progress on `codex/training-track` — re-check `assignment-status` before claiming those.

**A-013** is in progress on its own worktree (`~/Work/omarchy-jarvis-a013`, branch `a013-parallel-worktrees`).

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
