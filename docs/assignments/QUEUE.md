# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-005 | Post-run RLHF feedback (+/neutral/−) | queued | area:overlay | NO | [active/A-005-rlhf-feedback.md](active/A-005-rlhf-feedback.md) |
| A-006 | Log hygiene (gitignore, retention, temps) | queued | area:docs | YES | [active/A-006-log-hygiene.md](active/A-006-log-hygiene.md) |

Recently completed: A-001 · A-002 · A-003 · A-004 (see [done/](done/)).

**Order:** **A-005** next (overlay is steadier now that A-004 landed). **A-006** may run in parallel (docs/scripts only; do not touch overlay/A-005 files).

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
