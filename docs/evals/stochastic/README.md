# Stochastic planner evals (A-031, v0)

Repeated **fresh-context**, **planner-only** trials of 20 critical behaviors. This is a
calibrated diagnostic of first-answer reliability. It is **not** a promotion threshold, not a
desktop E2E suite, and not a replacement for A-028's deterministic `EVAL-*` cases.

Deterministic CI remains the first gate. A human Training Verify never auto-graduates a case.
Evaluator/oracle/baseline edits are Control Plane changes (A-030 / ADR-050).

## Two surfaces, never averaged together

| Surface | What it calls | Model? | Trials |
|---|---|---|---|
| `planner-json` | `brain/server.py::json_plan` | yes (or `--backend stub`) | N (default 3, development band 3–5) |
| `router` | `brain/server.py::route_prompt` | no | always 1 |

Router cases confirm the scripted intake / correction / slash-command routers separately, as
A-031's brief requires. Mixing them into a planner pass-rate would launder a deterministic
100% into a stochastic number.

## Why pass@k is not the product target

The overlay shows the user **one** plan. If the first answer is wrong, the user has to notice,
cancel, and ask again. `pass@k` (k>1) asks "did any of k independent samples succeed?" — that
is a research-sampling statistic, not the thing a person experiences. v0 therefore reports
**successes/trials per case** (the first-answer hit rate at this N), plus whether the planned
*action* and the canonical *output digest* were identical across trials.

At N=3–5 this is a smoke signal, not a confidence interval. Do not quote an aggregate
percentage as a product claim. The useful questions are: which cases are unanimous, which
flip between revisions, and did the honesty guard have to rewrite a false action claim.

## Planner-only, proven

`scripts/stochastic-evals.py` launches each trial in a fresh child process. Before calling the
planner the child replaces every approve / execute / desktop / journal path with a tripwire,
points `LOGS` at an empty temp directory it then checks stayed empty, and allows outbound HTTP
only to `http://127.0.0.1:11434/`. A tripwire voids the run (exit 1). Nothing is approved,
nothing is executed, no live Hyprland mutation.

## Cases (`cases.json`, schema `schema.json`)

20 cases (`SEVAL-001`…`SEVAL-020`) drawn from known failures and safety boundaries:

- Honesty / no-false-claim: chitchat, YouTube (fad6f832 / A-012), destructive request
- Tool choice: Spotify, WhatsApp-as-webapp, unrecognized `cliamp` (#15 / A-022)
- One-action recipes: scratch-and-mail, open-planning
- Argument types: workspace 3 as an integer
- Scratchpad pair: toggle vs move-here
- Catalog over guessed chords (ADR-003)
- Planner-excluded issue filing (ADR-009)
- Deterministic routers: "the other one" / Bitwarden (A-025), not stealing "open the other
  workspace", `/report` intake, `/backlog`, `/dispatch` (never contacts an agent)

Ids are `SEVAL-*`, distinct from A-028's `EVAL-*` (those oracles *are* existing unit tests).
Oracles are a closed vocabulary evaluated in code — never `eval()`, never LLM-as-judge.
Tool names in `expect` are checked against the schemas that actually ship.

## Evidence envelope (A-038)

Each case writes a `kind: eval` bundle via `brain/evidence.py::build_eval_envelope`: the same
fingerprint A-038 defined (`model_digest`, planner mode, prompt/schema hashes, `case_id` /
`case_version`, options) plus `counts` and per-trial `{index, outcome, output_digest}`. Raw
model text is **never** in the bundle. Default dest is `$XDG_STATE_HOME/jarvis/evidence/`
(private, gitignored). Pass `--evidence-out` to override; `--no-evidence` for debug runs.

A redacted summary (hashes, counts, reasons — no replies) can be committed. Raw outputs go
only to `--private-out` (mode 0600, gitignored under `docs/evals/stochastic/private/`).

## Baseline (human-approved before anything gates)

`baseline.json` ships `status: unapproved`. `--gate` **refuses to run** until Alex has:

1. Read a specific summary of a specific fingerprint
2. Set `status: approved`, `approved_by`, `approved_at`, `approved_summary`, `trials`
3. Written a `min_successes` / `of_trials` tolerance for **every** `planner-json` case

Until then the runner's exit code is runner health (validation, tripwires, model errors), not
how many trials passed. Auto-tuning prompts against this set is out of scope.

## How to run

```bash
./scripts/stochastic-evals.py --validate                 # registry only; CI runs this
./scripts/stochastic-evals.py --surface router           # no model
./scripts/stochastic-evals.py --trials 3                 # needs local Ollama
./scripts/stochastic-evals.py --backend stub \
    --stub docs/evals/stochastic/fixtures/stub-replies.json
```

`--backend stub` proves the runner, oracles, isolation and evidence shape without a model.
It is **not** a measurement of qwen. Live planner trials need Ollama; this cloud agent did
not spend extra model credits on them.

## Out of scope

Approving or executing plans; live desktop mutation; VM matrix; LLM-as-judge; N-run
everything; promotional pass-rate; unattended promotion; treating a journal `flag` as a grade.
