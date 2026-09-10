# A-027 — Protected promotion path (main ruleset + human merge gate)

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** YES
- **Soft path hints:** `docs/`, `START.md`, `scripts/`, `.github/`
- **Links:** docs/SELF_IMPROVE_ROADMAP.md

## Goal
Forge may **unattended** branch/commit/PR/update checks. **Merge to main** requires Alex + ruleset (required PR/checks, no force-push, no credential bypass). Document ladder: candidate → CI → evals → review → (VM if system-affecting) → merge/tag → (snapshot if system-affecting) → deploy → health → ledger. Protect `main` (PR required, restrict direct pushes, required checks when CI exists). Document promotion checklist + kill/disable commands.

## Checklist
- [ ] Apply or document GitHub ruleset on `main`
- [ ] Add `docs/PROMOTION.md`; link from START
- [ ] Update agent prompts: branch/PR default; no silent main
- [ ] Optional minimal CI as required check
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Auto-merge; snapshot automation; staged deploy.
