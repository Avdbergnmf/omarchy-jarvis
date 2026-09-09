# Bug: spotify

GitHub issue: https://github.com/Avdbergnmf/omarchy-jarvis/issues/11

## Complaint (verbatim)
spotify

## Clarifying Q&A
- Q: What did you expect to happen?
  A: Opens spotify
- Q: What actually happened instead?
  A: it told me it cant open spotify because its not yet supported. I wonder if its possible I can just get it to look for exact/close enough matches in app names and make this more general or something?
- Q: Any steps to reproduce, or was this a one-off?
  A: it happens every time

## Context pack
- Last plan (tools + args): {"actions": [], "reply": "Spotify is not a supported action. How else may I assist you?"}
- Approval choice: ran
- Jarvis version: 0.4.1
- Run id: 4fdd44c0-0202-45ce-affb-d0bca61aa230
- Run log: logs/journal/CURRENT.jsonl (or version archive); console: logs/runs/4fdd44c0-0202-45ce-affb-d0bca61aa230.log
- Log excerpt (last steps): [{"ts": "2026-09-09T19:41:53.703073+00:00", "jarvis_version": "0.4.1", "git_describe": "v0.0.1-17-g3b75a0d-dirty", "run_id": "4fdd44c0-0202-45ce-affb-d0bca61aa230", "phase": "prompt", "prompt": "spotify"}, {"ts": "2026-09-09T19:41:56.446916+00:00", "jarvis_version": "0.4.1", "git_describe": "v0.0.1-17-g3b75a0d-dirty", "run_id": "4fdd44c0-0202-45ce-affb-d0bca61aa230", "phase": "process", "process": {"actions": [], "reply": "Spotify is not a supported action. How else may I assist you?"}}, {"ts": "2026-09-09T19:41:56.458727+00:00", "jarvis_version": "0.4.1", "git_describe": "v0.0.1-17-g3b75a0d-dirty", "run_id": "4fdd44c0-0202-45ce-affb-d0bca61aa230", "phase": "done", "happened": {"status": "done", "reply": "Spotify is not a supported action. How else may I assist you?", "steps": []}, "ok": true}, {"ts": "2026-09-09T19:41:56.459093+00:00", "jarvis_version": "0.4.1", "git_describe": "v0.0.1-17-g3b75a0d-dirty", "run_id": "4fdd44c0-0202-45ce-affb-d0bca61aa230", "phase": "eval", "eval": {"ok": true, "flag": null, "note": "No inconsistency in recorded results; desktop effects are not independently verified."}, "ok": true}, {"ts": "2026-09-09T19:42:02.782279+00:00", "jarvis_version": "0.4.1", "git_describe": "v0.0.1-17-g3b75a0d-dirty", "run_id": "4fdd44c0-0202-45ce-affb-d0bca61aa230", "phase": "feedback", "feedback": {"rating": "bad"}}]
- Host facts: (not window-related; skipped)
- Binding catalog hits: (not binding-related; skipped)

## Expected vs actual
- Expected: Opens spotify
- Actual: it told me it cant open spotify because its not yet supported. I wonder if its possible I can just get it to look for exact/close enough matches in app names and make this more general or something?

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



---
**Converted to assignment [A-011](../../../assignments/active/A-011-open-app-by-name.md)** on 2026-09-09. Removed from open bug backlog; GitHub #11 closed.
