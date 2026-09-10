# A-020 — Validate features: record results, run ids, less manual busywork

- **Status:** in_progress
- **Area:** area:overlay (+ `area:brain` validation APIs; light chat/overlay automation helpers)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/validation.js`, `overlay/` Training validation UI, `brain/validation.py`, `brain/server.py` (validation + run-id surfacing), `brain/training.py` if shared, `tests/`, `docs/validation/`, `docs/FEATURES.md`, `docs/assignments/`, `docs/SESSION.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `VERSION`, small scripts only if needed to drive overlay for guided tests
- **Forbidden paths:** Rewriting Problems/Assignments/Agent monitor (A-016–A-018); A-019 bubble work; auto-filing GitHub issues without review; skipping human judgment on “did the desktop do the right thing”
- **Blocks / blocked-by:** Independent of A-019 (same overlay area → **serial**). **Alex priority now** — place above A-019 in QUEUE unless A-019 already in_progress.
- **Links:** Alex 2026-09-10 JARVIS — Validate features broken/frustrating

## Goal
Human validation in Training must actually **persist and reflect** Verify/Fail, show past validations when requested, stop asking for run ids Jarvis never shows, and **automate mechanical setup steps** so Alex mostly judges outcomes after clicking Run.

### 1) Record + list behavior
- After Verify or Fail (+ confirm), the item must **leave the pending list** (or move to validated/failed) and the result must be **really written** to `docs/validation/catalog.json` (and FEATURES sync). Debug/fix if confirm/preview path no-ops.
- With **Include previously validated features** on, show those items and their **validation reports** (date, version, notes, outcome, run id if any) — not only re-run empty forms.

### 2) Run id
- Today the form asks for a run id but Jarvis never surfaces one to Alex. Either **show run id clearly** in chat/overlay after a run (and copy-friendly), and/or **pre-fill / attach last relevant run id** when starting a guided test, and/or make run id optional with an honest “none” path. Do not leave a required-looking field that cannot be filled.

### 3) Trainer-driven steps (effort reduction)
- Guided steps that are pure mechanics (open Jarvis, type the prompt, press Enter / open Training, etc.) should be **performed by the trainer/software** where safe.
- Alex’s job is to **watch the proposed plan and judge the desktop result after Run** (and similar judgment steps). Automate setup; never auto-approve desktop mutations without him.
- Extend catalog step schema if needed (`kind: auto|human` or similar) and migrate existing guides so busywork isn’t on Alex.

## Checklist
- [ ] Reproduce Verify/Fail; confirm whether catalog/FEATURES update; fix persistence + UI list refresh/removal
- [ ] Include-validated: list validated/failed with readable report history; allow re-test without losing history
- [ ] Surfacing/pre-fill/optional run id end-to-end (overlay + API)
- [ ] Auto-drive mechanical guided steps; keep judgment + Run approval human; document which step kinds are auto
- [ ] Tests + ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
- Fully unsupervised validation (no human at all)
- A-019 proposed-action bubble redesign
- Cloud agent dispatch

## Notes for the coding agent
- Start at `overlay/validation.js` preview/confirm + `brain/validation.py`.
- Token discipline: read those once; then diffs.
