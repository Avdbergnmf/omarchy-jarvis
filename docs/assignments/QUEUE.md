# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-007 | Slash-command autocomplete | queued | area:overlay | NO | [active/A-007-slash-command-autocomplete.md](active/A-007-slash-command-autocomplete.md) |
| A-008 | Training mode (improvement control plane) | queued | area:overlay | NO | [active/A-008-training-mode.md](active/A-008-training-mode.md) |
| A-009 | Human validation tests in Training mode | queued | area:overlay | NO | [active/A-009-human-validation-tests.md](active/A-009-human-validation-tests.md) |

Recently completed: A-001 … A-006, A-010 … A-014 (see [done/](done/)).

**A-014** — [Completed all seven hygiene chunks](done/A-014-hygiene-bug-hunt-cleanup.md) on `a014-hygiene`; pending merge/deployment. See SESSION for validation and the scoped-out skill follow-up.

**Astra / overlay track:** A-007→A-008→A-009 may be in progress on `codex/training-track` — re-check `assignment-status` before claiming those.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
