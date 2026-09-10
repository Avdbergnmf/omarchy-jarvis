# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
| A-016 | Training window overhaul (Problems-first) | queued | area:overlay | NO | [active/A-016-training-window-overhaul.md](active/A-016-training-window-overhaul.md) |
| A-017 | Training Assignments panel (list/edit/generate/handoff) | queued | area:overlay | NO | [active/A-017-training-assignments-panel.md](active/A-017-training-assignments-panel.md) |
| A-015 | Richer readable plan details on approve | queued | area:overlay | NO | [active/A-015-training.md](active/A-015-training.md) |

Recently completed: A-001 … A-014 (see [done/](done/)).

**A-016 (Alex priority):** Training as its own Hyprland window — top stats bar, feature nav, Problems list/detail/priority/assignment button first.

**A-017 (after A-016):** Assignments panel — queue list + detail/save, generate from problem (local model or on-machine agent), handoff → Agent monitor.

**A-015:** Chat overlay plan readability — same area, after Training track unless Alex says otherwise.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
