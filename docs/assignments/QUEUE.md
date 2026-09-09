# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-007 | Slash-command autocomplete | queued | area:overlay | NO | [active/A-007-slash-command-autocomplete.md](active/A-007-slash-command-autocomplete.md) |
| A-008 | Training mode (improvement control plane) | queued | area:overlay | NO | [active/A-008-training-mode.md](active/A-008-training-mode.md) |
| A-009 | Human validation tests in Training mode | queued | area:overlay | NO | [active/A-009-human-validation-tests.md](active/A-009-human-validation-tests.md) |

Recently completed: A-001 … A-006, A-010, A-011 (see [done/](done/)).

**Order (serial):** A-010 done → **A-007** → **A-008** → **A-009**.

**Astra 6:** owns **A-008 + A-009** after A-010/A-007 clear — paste [`docs/backlog/handoffs/active/astra6-A008-A009.md`](../backlog/handoffs/active/astra6-A008-A009.md).

**A-011** done (open apps by name).

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
