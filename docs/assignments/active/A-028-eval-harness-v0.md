# A-028 — Eval harness v0 (capability vs regression + bug→case rule)

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** YES
- **Soft path hints:** `docs/validation/`, `docs/FEATURES.md`, `START.md`
- **Links:** docs/SELF_IMPROVE_ROADMAP.md

## Goal
Label evals **capability** vs **regression**. Bug/assignment close requires automated test and/or validation catalog entry. Eval/safety changes should not silently ride in unrelated behavior PRs.

## Checklist
- [ ] Schema/docs for suite split; label existing entries; graduation on Verify
- [ ] START/assignments: regression artifact in acceptance
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Stochastic N-runs; VM e2e; LLM-as-judge.
