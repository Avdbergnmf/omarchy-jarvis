# A-028 — Deterministic candidate-eval foundation (separate evidence planes)

- **Status:** blocked
- **Area:** area:docs
- **parallel-ok:** NO (candidate evaluation is Control Plane work)
- **Recommended depth:** high
- **Soft path hints:** `docs/evals/`, `.github/workflows/ci.yml`, `tests/`, `scripts/`, `START.md`
- **Blocked-by:** A-038
- **Gate:** control-plane
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · A-032 review · ADR-028 (human validation remains separate) · blocks A-030 and A-031

## Goal
Define a candidate-evaluation registry and result envelope without overloading the human
validation catalog or the runtime journal evaluator. Capability asks whether a candidate can
improve; regression protects an accepted behavior. Deterministic CI remains the first gate.

## Checklist
- [ ] Document four distinct evidence planes: CI/unit, runtime anomaly journal, human validation, candidate evals
- [ ] Add `docs/evals/` schema/README with case id/version, capability|regression, oracle type, execution level, mutation policy, owner/protection class and expected result
- [ ] Define A-038 result envelope fields (revision/dirty identity, Jarvis version, model digest when applicable, planner, prompt/tool/schema/options hashes, case version, counts and artifact hash)
- [ ] Inventory existing tests and human guides; reference them where useful but do not relabel `docs/validation/catalog.json` as an automated/protected eval suite
- [ ] Make `.github/workflows/ci.yml` run every Python test and every current `tests/*.test.cjs` suite under one stable, unique `checks / test` job; add a contract preventing quiet suite omission
- [ ] Seed a small deterministic capability/regression set from known planner/approval failures with side-effect-free exact oracles
- [ ] Define reviewed capability→regression promotion as a Control Plane change; a human Training Verify does not auto-graduate a case
- [ ] START/assignments: closing behavior work needs a relevant regression artifact, or a documented reason only human/VM validation is possible
- [ ] On acceptance, unblock A-030 only if A-027 is also done; A-031 still waits for A-030
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Changing existing human validation semantics; stochastic N-runs; desktop execution from an
eval runner; VM E2E; LLM-as-judge; promotional thresholds; treating journal flags as grades.
