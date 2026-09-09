---
name: report-last-failure
description: Draft and file a bug report from the most recently modified run log, without interactive Q&A.
---

# report-last-failure

Finds the most recently modified file under `logs/runs/`, tails its last 20 lines, and calls `report_bug` with a title/body built from that excerpt. No clarifying questions — it's a scripted shortcut for "just file something from what just happened," demonstrating how a skill composes the reviewed context-gathering + filing actions. For the full context pack (last plan, host facts, binding hits) and up to 3 clarifying questions, use `/report …` or say "you messed up …" in the overlay instead — that's the primary path.

Execute `./run.sh` from this directory, or `actions/run_skill report-last-failure` from the repository root. Preview with `./run.sh --dry-run`. Output is JSON lines; a nonzero exit stops the recipe (e.g. no run logs exist yet).

Triggers: not listed in the run_skill enum in brain/tools.json, so the model cannot select it — this is a reference example for cold agents on how to compose `report_bug`, not the recommended everyday path.

Safety: only reads local log files and files a GitHub issue via `report_bug`, which itself is still subject to plan/approve before `gh issue create` runs. Secrets are redacted by `report_bug`. These examples were explicitly requested; future generated skills stay in drafts until the user approves promotion.
