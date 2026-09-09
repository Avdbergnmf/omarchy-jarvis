# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-013 | Parallel agents: default git worktrees | queued | area:docs | YES | [active/A-013-parallel-worktrees-default.md](active/A-013-parallel-worktrees-default.md) |
| A-012 | Open YouTube + honest open plans | queued | area:actions | YES | [active/A-012-open-youtube-honest-plans.md](active/A-012-open-youtube-honest-plans.md) |
| A-007 | Slash-command autocomplete | done | area:overlay | NO | [done/A-007-slash-command-autocomplete.md](done/A-007-slash-command-autocomplete.md) |
| A-008 | Training mode (improvement control plane) | done | area:overlay | NO | [done/A-008-training-mode.md](done/A-008-training-mode.md) |
| A-009 | Human validation tests in Training mode | done | area:overlay | NO | [done/A-009-human-validation-tests.md](done/A-009-human-validation-tests.md) |

Recently completed: A-001 … A-006, A-010, A-011 (see [done/](done/)).

**A-012** (from bug #12) is `parallel-ok: YES` — YouTube webapp/browser + no false “Opening…” empty plans. Pairs with completed A-011.

**Training track:** A-007 → A-008 → A-009 done on `codex/training-track`; see the [archived handoff](../backlog/handoffs/archive/astra6-A008-A009.md).

**A-013** (from Claude’s A-011 note) — document/default isolated worktrees for parallel agents.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
