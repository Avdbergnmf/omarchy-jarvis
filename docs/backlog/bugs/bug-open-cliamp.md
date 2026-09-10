# Bug: open cliamp

GitHub issue: https://github.com/Avdbergnmf/omarchy-jarvis/issues/15

## Complaint (verbatim)
open cliamp

## Clarifying Q&A
- Q: What did you expect to happen?
  A: open cliamp, its in my app list so should be available somewhere...
- Q: What actually happened instead?
  A: told me its not installed or i mistyped...
- Q: Any steps to reproduce, or was this a one-off?
  A: seems to happen everytime

## Context pack
- Last plan (tools + args): {"actions": [], "reply": "I couldn't find 'cliamp' as an available app. Please ensure you have spelled it correctly and try again."}
- Approval choice: ran
- Jarvis version: 0.5.6
- Run id: 2e633ed1-d03d-4e4e-8c67-bc1154285402
- Run log: logs/journal/CURRENT.jsonl (or version archive); console: logs/runs/2e633ed1-d03d-4e4e-8c67-bc1154285402.log
- Log excerpt (last steps): [{"ts": "2026-09-10T08:48:00.304630+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "2e633ed1-d03d-4e4e-8c67-bc1154285402", "phase": "prompt", "prompt": "open cliamp"}, {"ts": "2026-09-10T08:48:13.286473+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "2e633ed1-d03d-4e4e-8c67-bc1154285402", "phase": "process", "process": {"actions": [], "reply": "I couldn't find 'cliamp' as an available app. Please ensure you have spelled it correctly and try again."}}, {"ts": "2026-09-10T08:48:13.303050+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "2e633ed1-d03d-4e4e-8c67-bc1154285402", "phase": "done", "happened": {"status": "done", "reply": "I couldn't find 'cliamp' as an available app. Please ensure you have spelled it correctly and try again.", "steps": []}, "ok": true}, {"ts": "2026-09-10T08:48:13.303539+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "2e633ed1-d03d-4e4e-8c67-bc1154285402", "phase": "eval", "eval": {"ok": false, "flag": "suspicious", "note": "Action-like request produced no tools; review the reply."}, "ok": true}, {"ts": "2026-09-10T08:48:18.247608+00:00", "jarvis_version": "0.5.6", "git_describe": "v0.0.1-62-g0be3627-dirty", "run_id": "2e633ed1-d03d-4e4e-8c67-bc1154285402", "phase": "feedback", "feedback": {"rating": "bad"}}]
- Host facts: (not window-related; skipped)
- Binding catalog hits: (not binding-related; skipped)

## Expected vs actual
- Expected: open cliamp, its in my app list so should be available somewhere...
- Actual: told me its not installed or i mistyped...

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

