# A-013 — Default isolated git worktrees for parallel agents

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** YES
- **Allowed paths:** `START.md`, `AGENTS.md`, `docs/assignments/**`, `docs/assignments/prompts/**`, `scripts/assignment-status.sh`, `scripts/` (optional `worktree-add` helper), `docs/HOST.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `README.md` (short pointer)
- **Forbidden paths:** Product overlay/brain/actions feature work
- **Blocks / blocked-by:** none
- **Links:** Claude’s A-011 write-up — shared checkout collided with uncommitted `codex/training-track` WIP; solved via `git worktree add … main`

## Goal
When two assignments run **in parallel** on this host, agents must **not** share one dirty working tree (checkout/stash fights). **Default:** each parallel coding agent works in its own **`git worktree`** on `main` (or a dedicated branch), then commits/pushes; primary checkout stays free for the other track.

Document this as required agent policy (START + assignment prompts + desk README), and optionally ship a tiny helper script that creates `~/Work/omarchy-jarvis-<slug>` worktrees the same way A-011 did.

## Checklist
- [ ] ADR: why worktrees are the default for `parallel-ok` / concurrent agents on this host
- [ ] Update `START.md`, `docs/assignments/README.md`, `NEW_AGENT.txt` / `PARALLEL.txt` / `CONTINUE.txt` with the rule + exact commands
- [ ] Optional: `scripts/worktree-add.sh` (or document-only if script is overkill) — create, path convention, remove after merge
- [ ] `assignment-status.sh` hints if the shared tree looks dirty on another branch
- [ ] PROGRESS note citing A-011 lesson; QUEUE → done

## Out of scope
Changing product code; forcing worktrees for single-agent serial work.

## Notes
Canonical product path remains `~/Work/omarchy-jarvis`. Example used successfully: `git worktree add ~/Work/omarchy-jarvis-<task> main`. Training track already uses `/home/omarchy/Work/omarchy-jarvis-training`.
