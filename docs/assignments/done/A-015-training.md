# A-015 — I wanna see what the plan is its going to execute with some more details...

- **Status:** done
- **Area:** area:skills (scope expanded to brain/server.py + brain/system_prompt.md with Alex's explicit sign-off — see ADR-029)
- **parallel-ok:** NO
- **Allowed paths:** skills/, tests/, docs/assignments/, docs/SESSION.md, docs/PROGRESS.md, docs/DECISIONS.md, brain/server.py, brain/system_prompt.md (expanded), docs/validation/catalog.json + docs/FEATURES.md (per the checklist's own "add/update human validation entry" step)
- **Forbidden paths:** overlay/, actions/; approval bypass; real agent dispatch
- **Links:** Manual training observation; ADR-029

## Goal
I wanna see what the plan is its going to execute with some more details...

## Human comments / evidence
Record human test as validated for Overlay chat and approval on Jarvis 0.5.2.

docs/validation/catalog.json
docs/FEATURES.md

i think theres something weird going on with this validation request. The hello thing works, if it asks me do execute a plan, it works as expect it to kinda, butttt, I get very little information about that plan. It kinda tells me what feature/skill its gonna do, but not really with what parameters etc, and its very poorly readable for a human. I think we can improve here...

## Checklist
- [x] Read START, SESSION and QUEUE; check ownership before claiming
- [x] Reproduce and document expected vs actual behavior from the linked problem
- [x] Implement the scoped change; clarify acceptance with Alex if evidence is insufficient
- [x] Verify relevant tests and Doctor; add/update human validation entry
- [x] Update SESSION, PROGRESS, QUEUE and INDEX; move to done/ on acceptance

## Out of scope
Unrelated queue work, unreviewed skills, silent cloud spending.

## Resolution (2026-09-10)
Traced the terse plan/step text to `action_label()`/`json_plan()`'s reply in
`brain/server.py` (`skills/`-only could not have fixed it — nothing read `SKILL.md` at
runtime). Alex explicitly expanded scope to `brain/server.py` + `brain/system_prompt.md`
(AskUserQuestion; "Expand scope to brain/ (Recommended)"). See ADR-029 for the full
decision, `docs/PROGRESS.md` (2026-09-10 — A-015) for evidence, and
`tests/test_jarvis.py` for new/updated coverage. VERSION 0.5.2 → 0.5.3;
feat-overlay-chat re-flipped to unvalidated for Alex to re-test.
