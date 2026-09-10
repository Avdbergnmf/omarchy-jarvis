# Bug: Play my Rubba Dub playlist on Spotify

GitHub issue: https://github.com/Avdbergnmf/omarchy-jarvis/issues/14

## Complaint (verbatim)
Play my Rubba Dub playlist on Spotify

## Clarifying Q&A
- Q: What did you expect to happen?
  A: it to navigate to my spotify, and start playing the Rubba Dub playlist.
- Q: What actually happened instead?
  A: just navigated to spotify
- Q: Any steps to reproduce, or was this a one-off?
  A: another point, please allow me to skip questions by pressing enter again with an empty textbox.

## Context pack
- Last plan (tools + args): {"actions": [{"tool": "open_app_by_name", "arguments": {"name": "Spotify"}}], "reply": "Opening Spotify."}
- Approval choice: ran
- Jarvis version: 0.5.2
- Run id: 99f47f00-d5df-4cfd-8132-26cf944b8a10
- Run log: logs/journal/CURRENT.jsonl (or version archive); console: logs/runs/99f47f00-d5df-4cfd-8132-26cf944b8a10.log
- Log excerpt (last steps): [{"ts": "2026-09-10T06:44:00.871414+00:00", "jarvis_version": "0.5.2", "git_describe": "v0.0.1-46-g15a2836", "run_id": "99f47f00-d5df-4cfd-8132-26cf944b8a10", "phase": "prompt", "prompt": "Play my Rubba Dub playlist on Spotify"}, {"ts": "2026-09-10T06:44:03.221263+00:00", "jarvis_version": "0.5.2", "git_describe": "v0.0.1-46-g15a2836", "run_id": "99f47f00-d5df-4cfd-8132-26cf944b8a10", "phase": "process", "process": {"actions": [{"tool": "open_app_by_name", "arguments": {"name": "Spotify"}}], "reply": "Opening Spotify."}}, {"ts": "2026-09-10T06:44:05.486012+00:00", "jarvis_version": "0.5.2", "git_describe": "v0.0.1-46-g15a2836", "run_id": "99f47f00-d5df-4cfd-8132-26cf944b8a10", "phase": "done", "happened": {"status": "done", "reply": "Completed: Spotify.", "steps": [{"tool": "open_app_by_name", "arguments": {"name": "Spotify"}, "label": "Spotify", "status": "done", "summary": "{\"ok\": true, \"name\": \"Spotify\", \"address\": \"0x55b8afbebf10\", \"workspace\": 1, \"class\": \"Spotify\"}"}]}, "ok": true}, {"ts": "2026-09-10T06:44:05.486370+00:00", "jarvis_version": "0.5.2", "git_describe": "v0.0.1-46-g15a2836", "run_id": "99f47f00-d5df-4cfd-8132-26cf944b8a10", "phase": "eval", "eval": {"ok": false, "flag": "suspicious", "note": "Tools reported completion; desktop side effects have not been independently verified."}, "ok": true}, {"ts": "2026-09-10T06:44:13.648209+00:00", "jarvis_version": "0.5.2", "git_describe": "v0.0.1-46-g15a2836", "run_id": "99f47f00-d5df-4cfd-8132-26cf944b8a10", "phase": "feedback", "feedback": {"rating": "bad"}}]
- Host facts: (not window-related; skipped)
- Binding catalog hits: (not binding-related; skipped)

## Expected vs actual
- Expected: it to navigate to my spotify, and start playing the Rubba Dub playlist.
- Actual: just navigated to spotify

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

