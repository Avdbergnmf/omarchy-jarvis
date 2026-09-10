# A-031 — Stochastic planner evals v0 (10–20 critical behaviors)

- **Status:** blocked
- **Area:** area:docs (+ light tests/scripts)
- **parallel-ok:** NO (protected evaluator/runner work is serial)
- **Recommended depth:** high
- **Soft path hints:** `tests/`, `scripts/`, `docs/evals/`
- **Blocked-by:** A-028, A-030
- **Gate:** control-plane
- **Links:** SELF_IMPROVE_ROADMAP · ChatGPT step 4 · A-032 review

## Goal
For 10–20 critical **planner-only** behaviors, run repeated fresh-context trials under a
pinned A-038 evidence envelope. Note: A-031 transitively also needs A-038 via A-028. Measure first-answer reliability without approving or
executing desktop actions. This is a calibrated diagnostic before it becomes a promotion
threshold.

## Checklist
- [ ] Curate 10–20 high-value cases from known failures/safety boundaries; use A-028 capability/regression labels and versioned deterministic oracles
- [ ] Runner calls a planner-only surface or isolated process and can prove no tool/action execution; each trial gets fresh context and releases all state
- [ ] Pin/record exact model digest, planner mode, prompt/tools/schema hashes, options, case version, revision and host-relevant facts via A-038
- [ ] Default to a small bounded N (3–5 for development); report successes/trials, failures and all-trials consistency per case plus aggregate—not a vanity scalar
- [ ] Explain why pass@k is not the product target when the first answer must be correct; do not claim statistical significance from tiny N
- [ ] Raw model outputs stay private/ignored; attach a redacted, content-hashed summary to the ledger/PR
- [ ] Establish a human-approved baseline and tolerance before any result blocks promotion; evaluator changes follow A-030
- [ ] Confirm deterministic routers separately and reserve desktop/system effects for human or disposable-VM E2E
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Approving/executing plans; live desktop mutation; full VM matrix; LLM-as-judge; N-run
everything; auto-tuning prompts against the protected regression set; unattended promotion.
