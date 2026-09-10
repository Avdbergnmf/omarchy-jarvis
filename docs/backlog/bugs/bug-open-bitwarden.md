# Bug: open bitwarden

GitHub issue: https://github.com/Avdbergnmf/omarchy-jarvis/issues/16

## Complaint (verbatim)
open bitwarden

## Clarifying Q&A
- Q: What did you expect to happen?
  A: open bitwarden
- Q: What actually happened instead?
  A: told me there are multiple apps with that name. I would like if there are multiple apps, just open the top match. This top match should be adjusted based on what was requested, and what I prefer. I should be able to tell Jarvis afterward something like, no, the other bitwarden, and then it should close the previous one, and open the new one, and adjust the weights with which it picks or something like that.

## Context pack
- Last plan (tools + args): {"actions": [{"tool": "open_app_by_name", "arguments": {"name": "bitwarden"}}], "reply": "Opening Bitwarden."}
- Approval choice: ran (failed)
- Jarvis version: 0.5.6
- Run id: d60fc0c2-f806-4e74-af11-6c853d3dfe1b
- Run log: logs/journal/CURRENT.jsonl (or version archive); console: logs/runs/d60fc0c2-f806-4e74-af11-6c853d3dfe1b.log
- Log excerpt (last steps): [{"ts": "2026-09-10T09:25:55.243500+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "d60fc0c2-f806-4e74-af11-6c853d3dfe1b", "phase": "prompt", "prompt": "open bitwarden"}, {"ts": "2026-09-10T09:26:11.183612+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "d60fc0c2-f806-4e74-af11-6c853d3dfe1b", "phase": "process", "process": {"actions": [{"tool": "open_app_by_name", "arguments": {"name": "bitwarden"}}], "reply": "Opening Bitwarden."}}, {"ts": "2026-09-10T09:26:14.267981+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "d60fc0c2-f806-4e74-af11-6c853d3dfe1b", "phase": "done", "happened": {"status": "error", "reply": "Action failed: {\"ok\": false, \"error\": \"Multiple installed apps match 'bitwarden': Bitwarden \\u2014 be more specific\"}", "steps": [{"tool": "open_app_by_name", "arguments": {"name": "bitwarden"}, "label": "bitwarden", "status": "error", "summary": "{\"ok\": false, \"error\": \"Multiple installed apps match 'bitwarden': Bitwarden — be more specific\"}"}]}, "ok": false}, {"ts": "2026-09-10T09:26:14.268411+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "d60fc0c2-f806-4e74-af11-6c853d3dfe1b", "phase": "eval", "eval": {"ok": false, "flag": "suspicious", "note": "Execution failed; inspect happened."}, "ok": false}, {"ts": "2026-09-10T09:26:27.430204+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "d60fc0c2-f806-4e74-af11-6c853d3dfe1b", "phase": "feedback", "feedback": {"rating": "bad"}}]
- Host facts: (not window-related; skipped)
- Binding catalog hits: (not binding-related; skipped)

## Expected vs actual
- Expected: open bitwarden
- Actual: told me there are multiple apps with that name. I would like if there are multiple apps, just open the top match. This top match should be adjusted based on what was requested, and what I prefer. I should be able to tell Jarvis afterward something like, no, the other bitwarden, and then it should close the previous one, and open the new one, and adjust the weights with which it picks or something like that.

## Suspected layer
brain/planner

## Acceptance criteria (done when…)
Bug is fixed and covered by a regression test.

## Area ownership
Choose area:overlay | area:brain | area:actions | area:skills | area:docs during triage.
Default single-writer for brain/control plane; parallel-ok requires explicit scope.
Allowed paths: (fill during triage)
Forbidden paths: (fill during triage)

## Suggested milestone / difficulty
- Milestone: M5
- Difficulty: M

## Recommended solver
claude-code — contained action/skill change, cheap on Claude Code Sonnet

---
Filed by Jarvis (`report_bug`) so a cold agent can act without chat history. Secrets are redacted before filing.

