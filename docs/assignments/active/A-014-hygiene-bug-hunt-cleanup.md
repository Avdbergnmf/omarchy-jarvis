# A-014 — Hygiene: bug hunt, tests, lean cleanup

- **Status:** in_progress
- **Area:** area:docs (also light `area:brain`, `area:actions`, `tests/` as needed)
- **parallel-ok:** YES
- **Allowed paths:** `docs/` (except stealing overlay assignment bodies for A-007–A-009), `scripts/`, `tests/`, `brain/` (dead code, honesty, journal/logging hygiene), `actions/` (dead/duplicate helpers), `README.md`, `START.md`, `AGENTS.md`, `VERSION` (patch only if behavior changes), root config that is clearly unused
- **Forbidden paths:** `overlay/` UI redesign; claiming/rewriting **A-007 / A-008 / A-009**; training-track branch; drive-by feature work; breaking plan→approve→execute
- **Blocks / blocked-by:** none (parallel with overlay track)
- **Links:** Alex 2026-09-09 — burn Codex session on small planned chunks: bug hunt / fix / cleanup / leaner obvious wins

## Goal
Improve Jarvis reliability and lean-ness in **small commits** until Codex session tokens run out. Prefer correctness and deleting/simplifying obvious BS over new features.

## Chunk plan (do in order; one chunk ≈ one commit; keep going)
1. **Bookkeeping sanity** — QUEUE/INDEX/SESSION match disk; leftover backlog smoke bug triage (convert, fix, or close with note); doctor/scripts still run.
2. **Test gaps** — run full test suite; fix flakes/failures; add focused tests for A-011/A-012 honesty + open_app_by_name / open youtube if thin.
3. **Dead / duplicate code** — grep unused tools, prompts, scripts; remove or slim with evidence; no behavior regressions.
4. **Planner honesty / empty-plan lies** — harden remaining success-without-actions paths; keep replies truthful.
5. **Log / journal noise** — ensure debug stays debug; CURRENT journal rotation still correct; trim chatty paths.
6. **Docs drift** — FEATURES/validation items match shipped code; START.md stays short; no contradictory parallel rules.
7. **Opportunistic micro-fixes** — only if clearly better and still in allowed paths.

After each chunk: update checklist, PROGRESS one line, SESSION Next action, commit+push branch. On token pressure: stop, leave tree clean, summarize chunks shipped.

## Checklist
- [x] Chunk 1 bookkeeping
- [x] Chunk 2 tests
- [x] Chunk 3 dead code
- [x] Chunk 4 honesty
- [ ] Chunk 5 logging
- [ ] Chunk 6 docs drift
- [ ] Chunk 7 micro-fixes (optional)
- [ ] QUEUE → done when chunks exhausted or tokens die mid-flight (leave partial checklist honest)

## Out of scope
Overlay Training mode / slash autocomplete (Astra). New big features. Refactors “while we’re here” that touch half the tree.

## Notes
Alex enabled **batch until session token limit**. Default one-assignment stop does **not** apply — keep going through chunks until tokens or checklist done.
