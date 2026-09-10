# A-031 — Stochastic planner evals v0 (10–20 critical behaviors)

- **Status:** done
- **Area:** area:docs (+ light tests/scripts)
- **parallel-ok:** NO (control-plane: protected evaluator/runner — ADR-048)
- **Recommended depth:** high
- **Soft path hints:** `tests/`, `scripts/`, `docs/evals/`
- **Blocked-by:** none
- **Gate:** control-plane
- **Links:** SELF_IMPROVE_ROADMAP · ChatGPT step 4 · A-032 review · ADR-051

## Goal
For 10–20 critical **planner-only** behaviors, run repeated fresh-context trials under a
pinned A-038 evidence envelope. Note: A-031 transitively also needs A-038 via A-028. Measure first-answer reliability without approving or
executing desktop actions. This is a calibrated diagnostic before it becomes a promotion
threshold.

## Checklist
- [x] Curate 10–20 high-value cases from known failures/safety boundaries; use A-028 capability/regression labels and versioned deterministic oracles — 20 `SEVAL-*` cases in `docs/evals/stochastic/cases.json` (14 `planner-json`, 6 `router`); closed oracle vocabulary, not LLM-as-judge.
- [x] Runner calls a planner-only surface or isolated process and can prove no tool/action execution; each trial gets fresh context and releases all state — `scripts/stochastic-evals.py` spawns a child per trial, tripwires execute/approve/desktop/journal, asserts `LOGS` stayed empty; `tests/test_stochastic_evals.py` covers tripwires + stub isolation.
- [x] Pin/record exact model digest, planner mode, prompt/tools/schema hashes, options, case version, revision and host-relevant facts via A-038 — `brain/evidence.py::build_eval_envelope` writes `kind: eval` bundles; fingerprints include `case_id`/`case_version`, schema/prompt hashes, `planner_source_hash`, host facts.
- [x] Default to a small bounded N (3–5 for development); report successes/trials, failures and all-trials consistency per case plus aggregate—not a vanity scalar — default `--trials 3`, cap 20; report is per-case successes/trials + consistency flags.
- [x] Explain why pass@k is not the product target when the first answer must be correct; do not claim statistical significance from tiny N — `docs/evals/stochastic/README.md` and the runner's `reliability_note`.
- [x] Raw model outputs stay private/ignored; attach a redacted, content-hashed summary to the ledger/PR — `--private-out` is gitignored (`docs/evals/stochastic/private/`); committed summaries under `docs/evals/stochastic/summaries/`.
- [x] Establish a human-approved baseline and tolerance before any result blocks promotion; evaluator changes follow A-030 — `baseline.json` is `unapproved`; `--gate` refuses until Alex fills tolerances. Case/oracle/baseline edits are Control Plane (`owner: control-plane`, required_paths in boundary-v1).
- [x] Confirm deterministic routers separately and reserve desktop/system effects for human or disposable-VM E2E — `--surface router` (6/6 pass, no model); no desktop/live execution_level exists.
- [x] ADR; PROGRESS; SESSION; QUEUE/INDEX → done — ADR-051.

## Out of scope
Approving/executing plans; live desktop mutation; full VM matrix; LLM-as-judge; N-run
everything; auto-tuning prompts against the protected regression set; unattended promotion.
