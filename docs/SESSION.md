# Session (in-flight agent work)

> Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- Assignment: _(none — A-025 done; queue empty)_
- Branch: main
- Worktree: `/home/omarchy/Work/omarchy-jarvis`
- Batch: 1 (default; stopped)

## Checklist
- [x] A-024 Bitwarden/ambiguous top match — done
- [x] A-022 cliamp — done
- [x] A-025 preferences + correction — done (`correct_app_open` + XDG weights)

## Done this session (evidence)
- A-025: XDG `app-preferences.json` weights fold into A-024 ranking; “no, the other …” is
  deterministic (not model-planned) and one reviewed action that closes the owned window
  if still present, opens the next stem, and bumps its weight. 153 Python tests pass
  (9 new); overlay tests + doctor.sh --syntax pass. ADR-036. VERSION 0.5.9.

## Next action (one concrete step)
- Human: restart Jarvis (`./scripts/restart.sh`) and validate feat-open-by-name correction steps; queue is empty

## Parallel agent
- none in_progress

## Blockers
- none
