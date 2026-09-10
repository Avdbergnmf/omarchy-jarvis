# A-015 — Richer readable plan details on approve

- **Status:** queued
- **Area:** area:overlay (+ light brain for plan payload)
- **parallel-ok:** NO
- **Allowed paths:** overlay/, brain/server.py (plan JSON richness only), tests/, docs/assignments/, docs/SESSION.md, docs/PROGRESS.md, docs/DECISIONS.md, docs/FEATURES.md, docs/validation/
- **Forbidden paths:** actions/ (except labels if needed); approval bypass; Training window redesign (that is A-016); real agent dispatch
- **Links:** Manual training observation
- **Prepared for:** My coding agent (claude-code); human must paste the handoff

## Goal
I wanna see what the plan is its going to execute with some more details...

## Human comments / evidence
Record human test as validated for Overlay chat and approval on Jarvis 0.5.2.

docs/validation/catalog.json
docs/FEATURES.md

i think theres something weird going on with this validation request. The hello thing works, if it asks me do execute a plan, it works as expect it to kinda, butttt, I get very little information about that plan. It kinda tells me what feature/skill its gonna do, but not really with what parameters etc, and its very poorly readable for a human. I think we can improve here...

## Checklist
- [ ] Read START, SESSION and QUEUE; check ownership before claiming
- [ ] Reproduce and document expected vs actual behavior from the linked problem
- [ ] Implement the scoped change; clarify acceptance with Alex if evidence is insufficient
- [ ] Verify relevant tests and Doctor; add/update human validation entry
- [ ] Update SESSION, PROGRESS, QUEUE and INDEX; move to done/ on acceptance

## Out of scope
Unrelated queue work, unreviewed skills, silent cloud spending.
