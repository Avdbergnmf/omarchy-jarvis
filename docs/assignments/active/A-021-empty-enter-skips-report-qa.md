# A-021 — Empty Enter skips report / “how did that go” Q&A

- **Status:** queued
- **Area:** area:overlay
- **parallel-ok:** YES
- **Allowed paths:** `overlay/app.js`, `overlay/index.html` (copy only if needed), `tests/overlay.test.cjs` (or equivalent), `docs/assignments/`, `docs/SESSION.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md` (short note OK)
- **Forbidden paths:** `brain/` behavior changes; Training validation (A-020); plan bubble UX (A-019); changing what Skip files
- **Blocks / blocked-by:** none (disjoint from A-020 validation panel if you only touch chat overlay Q&A/feedback Enter handling — still don’t edit the same files an in-progress A-020 agent is rewriting; use a worktree and avoid `validation.js`)
- **Links:** Alex 2026-09-10 — hit Enter on empty “how did that go” report → do Skip to clear quickly

## Goal
When Jarvis is in the post-run **report / clarifying Q&A** flow (the “how did that go” intake after 👎 Report, or the same Q&A UI), pressing **Enter with an empty answer** should perform the same action as **Skip** (`answer('skip')` / Skip & file now) — so Alex can blast through without typing `skip` or clicking the button.

If Enter on empty during the emoji-only “How did that go?” strip is also a footgun (e.g. submits a blank new prompt), dismiss/skip that strip in the least surprising way (prefer neutral dismiss / hide feedback without starting a new run) — document the choice in PROGRESS.

## Checklist
- [ ] Reproduce: empty Enter in report Q&A today (likely submits `""` instead of skip)
- [ ] Empty Enter → same path as Skip button; non-empty Enter still sends the answer
- [ ] Don’t start a new chat run from Enter while Q&A/feedback is focused and empty
- [ ] Overlay test for empty-Enter → skip
- [ ] PROGRESS one-liner; SESSION; QUEUE/INDEX → done

## Out of scope
- Redesigning RLHF buttons
- Auto-skipping when the field has text
- Brain intake question content

## Notes for the coding agent
- See `overlay/app.js`: `qa-form` submit → `answer(qaAnswer.value.trim())`; `qaSkip` → `answer('skip')`.
- Small, shippable; worktree if A-020 holds overlay files.
