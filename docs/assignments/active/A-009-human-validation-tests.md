# A-009 — Human validation tests in Training mode

- **Status:** queued
- **Area:** area:overlay (+ `area:docs` feature catalog; light `area:brain`)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/` (training mode), `docs/FEATURES.md`, `docs/validation/` (create), `docs/assignments/`, `brain/` (endpoints to list pending validations / record results), `actions/report_bug` wiring, `README.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `tests/`
- **Forbidden paths:** Replacing unit/CI tests; auto-closing issues without human mark
- **Blocks / blocked-by:** After **A-008** (lives inside Training mode)
- **Reserved for:** Astra 6 (see `docs/backlog/handoffs/active/astra6-A008-A009.md`)
- **Links:** Alex 2026-09-09 — agent-listed tests needing human feedback to verify features

## Goal
Every user-facing **feature** is listed in docs in an agent-friendly catalog (`docs/FEATURES.md` or `docs/validation/catalog.yaml`). Features not yet **human-validated** appear in Training mode as a **validation queue**.

For each pending item, Alex can **run the guided test** (steps the coding agent wrote), then:
- **Verify** — mark feature validated (date, version, notes)
- **Fail / bug** — attach outcome and file/add to issue list (reuse report intake / `report_bug` with context)

Coding agents, when finishing a feature assignment, must **add or update** a validation entry (steps + expected) so it shows up here until Alex verifies.

## Checklist
- [ ] Define catalog schema (id, title, area, steps[], expected, status: unvalidated|validated|failed, last_run, jarvis_version)
- [ ] Seed catalog from existing features (planning, scratch-and-mail, report/feature, RLHF, follow-along, …)
- [ ] Training mode: “Validate features” list + run UI + verify / file-bug actions
- [ ] Document in START/assignments README: agents must add validation entries when shipping features
- [ ] Tests; PROGRESS + ADR; QUEUE → done

## Out of scope
Automating GUI judgment without Alex; flaky full Hyprland CI in GitHub Actions.

## Notes
Keep steps copy-pasteable for humans (“Press Super+Shift+J, type …, expect …”).
