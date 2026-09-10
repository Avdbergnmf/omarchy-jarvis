# Assignment queue

Oldest queued at the top among `queued`. At most one non-parallel `in_progress` unless `parallel-ok: YES` and disjoint areas.

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|

Recently completed: A-001 … A-021, A-023, A-019, A-024, A-022, A-025 (see [done/](done/)).

**A-025 (done):** “no, the other bitwarden” closes the last owned open, launches the next match, and remembers the preference.
**A-024 (done):** ambiguous `open_app_by_name` now opens the top-ranked match instead of hard-failing.
**A-022 (done):** system prompt now tells the model to still call `open_app_by_name` for an unrecognized name instead of declining.
**Bitwarden #16:** A-024 + A-025 done.

**How to run:** paste a prompt from [`prompts/`](prompts/README.md).
