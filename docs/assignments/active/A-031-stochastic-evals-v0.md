# A-031 — Stochastic evals v0 (~10–20 critical behaviors)

- **Status:** queued
- **Area:** area:docs (+ light tests/scripts)
- **parallel-ok:** YES
- **Soft path hints:** `tests/`, `scripts/`, `docs/validation/`, `docs/evals/`
- **Blocks / blocked-by:** **After A-028**. Prefer after A-027.
- **Links:** SELF_IMPROVE_ROADMAP · ChatGPT step 4

## Goal
For ~10–20 critical behaviors, run N trials (start 3–5) and report **consistency**, not only pass@1. Document set, local runner, how summaries attach to ledger/PRs later.

## Checklist
- [ ] Curate 10–20 behaviors; capability vs regression labels
- [ ] Minimal runner; gitignored traces + summary artifact
- [ ] Docs: pass@k vs consistency; promotion expectations
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Full VM matrix; LLM-as-judge; N-run everything.
