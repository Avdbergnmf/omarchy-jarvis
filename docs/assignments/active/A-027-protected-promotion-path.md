# A-027 — Protected promotion path (main ruleset + human merge gate)

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** YES
- **Soft path hints:** `docs/`, `START.md`, `scripts/`, `.github/`
- **Links:** docs/SELF_IMPROVE_ROADMAP.md

## Goal
Experiments free in worktrees/branches; **promotion to main/live** requires Alex/ruleset. Protect `main` (PR required, restrict direct pushes, required checks when CI exists). Document promotion checklist + kill/disable commands.

## Checklist
- [ ] Apply or document GitHub ruleset on `main`
- [ ] Add `docs/PROMOTION.md`; link from START
- [ ] Update agent prompts: branch/PR default; no silent main
- [ ] Optional minimal CI as required check
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Auto-merge; snapshot automation; staged deploy.
