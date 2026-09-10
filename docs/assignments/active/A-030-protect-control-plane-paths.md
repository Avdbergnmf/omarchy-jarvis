# A-030 — Protect safety / eval / control-plane paths

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** YES
- **Soft path hints:** `CODEOWNERS`, `.github/`, `docs/`, `START.md`
- **Blocks / blocked-by:** With/after **A-027**. Complements A-028.
- **Links:** SELF_IMPROVE_ROADMAP · ChatGPT Q7

## Goal
Prevent candidates from improving scores by editing the grader. Ordinary `tests/` may ship with features; **protected** paths (regression/capability eval defs, safety/auth/promotion policy, ledger integrity) need CODEOWNERS + separate PR or explicit Alex override.

## Checklist
- [ ] Protected path list + CODEOWNERS
- [ ] Ruleset/CODEOWNER review (or document blocker)
- [ ] START/Forge: split PRs; reject mixed control-plane+feature dumps
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Stochastic runner (A-031); secrets broker.
