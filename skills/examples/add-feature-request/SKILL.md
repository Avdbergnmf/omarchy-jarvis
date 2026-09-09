---
name: add-feature-request
description: Draft and file a feature request from CLI-supplied text, without interactive Q&A.
---

# add-feature-request

Takes optional feature text as its first non-flag argument and calls `report_feature` with a minimal title/body built from it, skipping the clarifying questions. It's a scripted shortcut demonstrating how a skill composes the reviewed `report_feature` action for a cold agent to read; the primary, recommended path for a human is `/feature …` or "I wish it could …" in the overlay, which gathers the full context pack and asks up to 3 questions first.

Execute `./run.sh "add a dark mode toggle"` from this directory, or `actions/run_skill add-feature-request` from the repository root (the `run_skill` tool takes no free-text argument, so a model-triggered call files a placeholder draft that still needs editing — CLI use with real text is the intended way to exercise this one). Preview with `./run.sh --dry-run`.

Triggers: not listed in the run_skill enum in brain/tools.json, so the model cannot select it — reference example only.

Safety: only calls `report_feature`, which is still subject to plan/approve before `gh issue create` runs and to the same redaction. These examples were explicitly requested; future generated skills stay in drafts until the user approves promotion.
