# A-017 — Training Assignments panel (list/edit/generate/handoff)

- **Status:** queued
- **Area:** area:overlay (+ light `area:brain` for assignment CRUD / generate endpoints)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/` (Training Assignments panel), `brain/training.py`, `brain/server.py` (assignment/training endpoints), shared problem↔assignment links, `tests/`, `docs/assignments/` (runtime writes of real assignment files via confirmed save), `docs/SESSION.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/validation/`, `README.md`, `START.md`, `VERSION`, `scripts/` if needed for agent handoff helpers
- **Forbidden paths:** Replacing A-016 Problems chrome; chat overlay plan work (**A-015**); auto-spending cloud credits; sending to agents without explicit user action; rewriting QUEUE semantics without ADR
- **Blocks / blocked-by:** **Blocked by A-016** (needs Training window + nav + Problems selection handoff). Blocks nothing critical; do before A-015 unless Alex reprioritizes.
- **Links:** Alex 2026-09-10 JARVIS — after Problems, Assignments list/detail/save; generate from problem (local model or other on-machine agent); handoff button → Agent monitor

## Goal
In the Training window, an **Assignments** feature page where Alex can:

1. **See the queue** — list current assignments; click one → detail/properties (editable) → **Save** applies changes to the real assignment files / QUEUE/INDEX (confirm-gated if destructive or multi-file).
2. **Create from a problem** — optional linked problem (preselected if he came from Problems “Generate assignment”); **Generate** fills a new assignment form (via **local model** *or* another agent on the computer — user chooses); then **Save/Add** writes it into `docs/assignments/` + queue.
3. **Hand off** — with an assignment selected, a **Hand off to agent** button jumps to the **Agent monitor** page with that assignment preselected for prepare/queue/paste flow.

Done means Assignments is a real triage/create surface, not a dump of titles — same list/detail/save clarity as Problems.

## Checklist
- [ ] Assignments nav panel in Training window (post–A-016 chrome)
- [ ] Queue list (status/area/priority if present); click → detail editor; **Save** persists (preview/confirm for multi-file writes)
- [ ] New assignment form; link optional problem id; inherit context/priority from problem when present
- [ ] **Generate** draft: mode toggle **local Ollama** vs **on-machine coding agent** (Claude/Codex/etc.); never silent cloud spend; show draft in form for edit before Save
- [ ] **Save/Add** creates `active/A-NNN-…`, updates QUEUE + INDEX (+ SESSION touch as today)
- [ ] **Hand off to agent** → navigate to Agent monitor with assignment (+ slot picker) prefilled
- [ ] Deep-link from Problems “Generate assignment” (A-016) into this panel with problem selected
- [ ] ADR; tests; PROGRESS; FEATURES/validation if needed; SESSION; QUEUE/INDEX → done

## Out of scope
- Redesigning Problems list (A-016)
- Fully autonomous multi-agent orchestration / watching live chats
- A-015 plan readability in chat overlay

## Notes for the coding agent
- Reuse confirmed preview patterns from A-008/A-016 for any file writes.
- Generation must be explicit and reviewable; local model default is fine if agent path is stubbed with clear UX.
- Token discipline: read A-016 result + training.js/training.py once; then diffs.
