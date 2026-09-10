# A-028 — Deterministic candidate-eval foundation (separate evidence planes)

- **Status:** done
- **Area:** area:docs
- **parallel-ok:** NO (candidate evaluation is Control Plane work)
- **Recommended depth:** high
- **Soft path hints:** `docs/evals/`, `.github/workflows/ci.yml`, `tests/`, `scripts/`, `START.md`
- **Blocked-by:** none
- **Gate:** control-plane
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · A-032 review · ADR-028 (human validation remains separate) · unblocked by A-038 (done) · blocks A-030 and A-031

## Goal
Define a candidate-evaluation registry and result envelope without overloading the human
validation catalog or the runtime journal evaluator. Capability asks whether a candidate can
improve; regression protects an accepted behavior. Deterministic CI remains the first gate.

## Checklist
- [x] Document four distinct evidence planes: CI/unit, runtime anomaly journal, human validation, candidate evals — `docs/evals/README.md`.
- [x] Add `docs/evals/` schema/README with case id/version, capability|regression, oracle type, execution level, mutation policy, owner/protection class and expected result — `docs/evals/schema.json` + `cases.json`.
- [x] Define A-038 result envelope fields (revision/dirty identity, Jarvis version, model digest when applicable, planner, prompt/tool/schema/options hashes, case version, counts and artifact hash) — reuses `brain/evidence.py::fingerprint()` verbatim (`case_id`/`case_version` already existed); `counts`/`artifact_hash` documented in `docs/evals/README.md` for A-031's runner.
- [x] Inventory existing tests and human guides; reference them where useful but do not relabel `docs/validation/catalog.json` as an automated/protected eval suite — inventory table in `docs/evals/README.md` (204 py cases, 5 cjs suites, 12 validation features), validation catalog explicitly untouched.
- [x] Make `.github/workflows/ci.yml` run every Python test and every current `tests/*.test.cjs` suite under one stable, unique `checks / test` job; add a contract preventing quiet suite omission — job already was `checks / test`; added `scripts/check-test-coverage.py` as a new CI step.
- [x] Seed a small deterministic capability/regression set from known planner/approval failures with side-effect-free exact oracles — EVAL-001…EVAL-005 in `docs/evals/cases.json`.
- [x] Define reviewed capability→regression promotion as a Control Plane change; a human Training Verify does not auto-graduate a case — `docs/evals/README.md` "Promotion is a Control Plane change".
- [x] START/assignments: closing behavior work needs a relevant regression artifact, or a documented reason only human/VM validation is possible — added to `START.md` and `docs/assignments/README.md`.
- [x] On acceptance, unblock A-030 only if A-027 is also done; A-031 still waits for A-030 — A-030's `Blocked-by: A-027, A-028` left unchanged; A-027 is still externally blocked, so `assignment-status.sh` correctly still reports A-030 as blocked (on A-027 only, now that A-028 is done).
- [x] ADR; PROGRESS; SESSION; QUEUE/INDEX → done — ADR-045.

## Out of scope
Changing existing human validation semantics; stochastic N-runs; desktop execution from an
eval runner; VM E2E; LLM-as-judge; promotional thresholds; treating journal flags as grades.
