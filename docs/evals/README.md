# Candidate-eval foundation (A-028, v0)

This defines a **candidate-evaluation** registry and result shape without overloading the two
things it's easy to confuse it with: the human validation catalog (`docs/validation/`) and the
runtime journal's per-run evaluator (`brain/journal.py::evaluate`). **Deterministic CI remains
the first gate** — nothing here replaces or outranks it.

## The four evidence planes

A behavior change is judged by up to four genuinely different mechanisms. Conflating them —
treating one plane's pass as proof for another — is exactly the mistake this doc exists to
prevent (A-032's review found no clean separation before this).

| Plane | What it answers | Where | Runs |
|---|---|---|---|
| **CI / unit** | Does the code do what its test says, right now, deterministically? | `tests/*.py` (204 cases), `tests/*.test.cjs` (5 suites, all reachable — see below) | Every push/PR, `./scripts/test-full.sh` before landing |
| **Runtime anomaly journal** | Did *this one real run* look consistent with what was approved? | `brain/journal.py::evaluate()`, `logs/journal/CURRENT.jsonl` | Every terminal run, live, no model/subprocess call |
| **Human validation** | Did a person actually watch the desktop do the right thing? | `docs/validation/catalog.json` (12 features today), Training's Validate panel | On demand, human-triggered only |
| **Candidate evals** (this doc) | Does a *specific, named* capability or regression hold, on a *pinned* code/model fingerprint, so two revisions are actually comparable? | `docs/evals/cases.json` (deterministic `EVAL-*`) and [`stochastic/`](stochastic/README.md) (`SEVAL-*`, A-031) | On demand. Deterministic cases are "run that unit test". Stochastic planner cases are `scripts/stochastic-evals.py` (planner-only, never executes). |

None of these four "auto-graduates" into another. A journal `flag: null` is not a passing eval.
A Training Verify does not promote a `candidate-capability` case to `protected-regression`
(see Promotion, below). `docs/validation/catalog.json` stays exactly what it already is — a
human-judgment record — and is never relabeled an automated or protected suite by this work.

## Case schema (`docs/evals/schema.json`, cases in `docs/evals/cases.json`)

One case = one **deterministic, side-effect-free, exact-oracle** claim. v0 supports exactly one
`oracle_type`: **`unit-test-reference`** — the oracle *is* an existing `tests/` function, so
"running the case" already means "run that test," with a real pass/fail boolean and none of the
new machinery a live-model or desktop oracle would need. Fields (validated by
`scripts/eval-status.py`, which also confirms every `reference` resolves to a real test
class/method via `ast` parsing — never imported or executed):

- **`id`** / **`version`** — `EVAL-NNN`; version bumps only when the *case definition* changes, distinct from `A-###`/`IMP-###` id spaces.
- **`kind`** — `capability` (can a candidate improve this) or `regression` (does an accepted behavior still hold).
- **`oracle_type`**, **`execution_level`** (`planner-only` | `unit` — never `desktop`/`live` in v0), **`mutation_policy`** (`side-effect-free` — the only value defined; these are mocked-`hyprctl`/mocked-`Ollama` unit tests by construction).
- **`owner`** — always `control-plane`: adding or promoting a case is a Control Plane change (see A-030), not something Runtime/Training does on its own.
- **`protection_class`** — `protected-regression` (an accepted behavior; touching its oracle is itself reviewed) or `candidate-capability` (still exploratory, freer to revise).
- **`reference`** — `tests/test_X.py::ClassName::method_name`.
- **`expected_result`** — `pass` (a case is only filed against an oracle that currently passes; filing one against a known-failing test would misrepresent CI's own signal instead of adding a new one).

Five seed cases (`EVAL-001`…`EVAL-005`) were drawn from known planner/approval history: the
honesty-rewrite guard, the plan→approve→execute invariant, the `skills_trusted` safety
boundary (all `protected-regression`), and A-024/A-025's shipped ambiguous-app-open + "the
other one" correction capabilities (`candidate-capability`, linked from the Improvement Ledger's
[IMP-001](../ledger/records/IMP-001-bitwarden-ambiguous-app-open.md)).

## Result envelope — reuses A-038, adds two fields

A case's *execution result* is not a new format: it's an [A-038](../evidence/README.md) evidence
bundle with `fingerprint.case_id`/`fingerprint.case_version` populated (those fields already
exist in `brain/evidence.py::fingerprint()` — v0 just wires an eval's id/version into them),
plus two additions A-031's runner produces:

- **`counts`** — e.g. `{"total": 1, "passed": 1, "failed": 0}` for a unit-test-reference case (trivially `1/1`); stochastic cases report real N-of-M plus `errored`.
- **`artifact_hash`** — the content-addressed `id` of the evidence bundle. Deterministic cases still use `scripts/export-evidence.py` against a journaled run; stochastic cases write a `kind: eval` bundle via `brain/evidence.py::build_eval_envelope` (same fingerprint, no raw model text).

See [`stochastic/README.md`](stochastic/README.md) for the planner-only N-run runner. Those results do not auto-graduate into `protected-regression` or a promotion gate.

## Promotion is a Control Plane change

A case never silently moves from `candidate-capability` to `protected-regression`. Promotion —
deciding an exploratory capability is now an accepted behavior worth protecting — is a reviewed
edit to `docs/evals/cases.json` under the same `owner: control-plane` discipline as everything
else here. **A human Training Verify does not auto-graduate a case**: clicking Verify on a
`docs/validation/` feature is evidence for the *human validation* plane only, never a case's
`protection_class`.

## Regression-artifact requirement

Closing behavior work (not docs/process-only work) needs a relevant regression artifact — either
a new/updated `tests/` case (and, when it's a named capability/regression worth pinning, a
`docs/evals/cases.json` entry) — or a documented reason only human/VM validation is possible.
See `START.md`'s Safety and session done section.

## Existing coverage inventory (2026-09-10 snapshot)

- **204** Python `unittest` cases across `tests/test_*.py`.
- **5** `.test.cjs` suites (`overlay`, `training`, `validation`, `assignments`, `agents`) — all
  reachable from CI's single entrypoint (`tests/overlay.test.cjs` `require()`s the other four);
  `scripts/check-test-coverage.py` (new, this assignment) fails CI if a future suite ever isn't.
- **12** human-validated features in `docs/validation/catalog.json` (unrelated plane — never
  relabeled or merged into this one).
- These are referenced, not restated, here — this doc is the schema/registry, not a second copy
  of the test suite.

## Out of scope (v0)

Changing human validation semantics; desktop execution from an eval runner; VM end-to-end;
LLM-as-judge; promotional pass-rate thresholds; treating a runtime journal `flag` as a grade.
Stochastic N-runs live in [`stochastic/`](stochastic/README.md) (A-031) and stay diagnostic.
