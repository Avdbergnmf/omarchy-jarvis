# A-046 — Validate features overhaul (simple cards, optional how-to)

- **Status:** queued
- **Area:** area:overlay (+ `brain/validation.py`, `docs/validation/`, light FEATURES sync)
- **parallel-ok:** YES
- **Recommended depth:** high
- **Allowed paths (optional soft hint):** `overlay/validation.js`, `overlay/training.html`, `overlay/training.css`, `brain/validation.py`, `docs/validation/**`, `docs/FEATURES.md`, related tests, ADR/PROGRESS/SESSION
- **Forbidden paths (optional soft hint):** Agent manager / Problems / Assignments redesigns (A-043–A-045); auto-approving desktop Run/Cancel
- **Blocked-by:** none
- **Gate:** training-ux
- **Improvement:** none
- **Links:** Alex JARVIS room 2026-09-10 — Validate needs a big overhaul; “Run this step” broken; drop mandatory step checkboxes; clean card + copy prompt + Validate/Fail + report; optional expandable how-to; heavier QA only when an agent requests it after the last push

## Goal
Replace the guided checkbox / “Run this step” Validate UX with a **simple judgment card**.

### Default card (always enough to finish)
For each feature under review, show a clean card with:
- What to try (the prompt / command Alex should use)
- **Copy** for that prompt/command
- **Validate** and **Failed** (record outcome + notes → catalog/FEATURES as today)
- Produce / open a **report** on fail (existing draft-report path is fine if it still works)

No step checkboxes. Verify must **not** require ticking a list. “Run this step” automation is out of the primary path (it currently does not work reliably for Alex).

### Optional detail (click to expand)
Extra how-to / judgment hints may live behind expanding the card (or an explicit “How to test” disclosure). They help Alex figure out the check — they are **never** hard gates for Validate/Fail.

### When Validate appears in the workflow
Alex does **not** want full feature-QA on every assignment update. Catalog / pending human checks should be the lightweight prompt-judgment flow above.

Heavier QA (broader test suites, multi-step desktop scripts, “double-check the agent’s last push”) should run **only when an agent explicitly requests it after landing the latest version** — optional, on-demand, not the default for every task. Document that policy (ADR + Training copy); wire a minimal hook if one already exists (e.g. agent-requested validation flag / handoff note), otherwise specify the desk convention and a follow-up stub rather than boiling the ocean.

### Broken today (fix or delete)
- “Run this step” path in `overlay/validation.js` (`post('/v1/run', {prompt})` + poll) — either remove from primary UX or repair only if it becomes a non-blocking convenience behind the optional disclosure. Prefer remove/simplify over another half-working auto-runner.

Done for Alex: Validate feels like “copy this prompt, try it, say yes/no + short notes,” with optional help on click — not a mandatory checklist.

## Checklist
- [ ] Reproduce current guide: mandatory checkboxes block Verify; “Run this step” failure mode
- [ ] Redesign list + detail: card with prompt, Copy, Validate, Failed, notes, report; no required step ticks
- [ ] Optional expandable how-to (migrate old `steps` into optional help, not gates)
- [ ] Catalog schema / migration: support `prompt` (or equivalent) as the primary try-this field; keep history (`last_run`) intact
- [ ] Policy + copy: human Validate = lightweight; deep QA only when agent requests post-push — ADR amending/superseding the A-020 “auto-drive every mechanical step” emphasis where it conflicts
- [ ] Tests; PROGRESS; SESSION; QUEUE/INDEX → done; move brief to `done/`

## Out of scope
- Unsupervised validation with no human judgment
- Auto-clicking Run/Cancel in the chat overlay
- Reworking Agent manager handoff (A-044/A-045) or Problems row click (A-043)

## Notes for the coding agent
Start at `overlay/validation.js` + `docs/validation/catalog.json` / `catalog.schema.md` + ADR-033 (A-020). Prefer deleting complexity over repairing the auto-step runner. Token discipline: one read of validation.js + schema, then implement.
