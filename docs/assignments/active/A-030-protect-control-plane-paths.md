# A-030 — Protect safety / eval / control-plane paths

- **Status:** blocked
- **Area:** area:docs
- **parallel-ok:** NO (promotion/evaluator ownership is serial Control Plane work)
- **Recommended depth:** medium
- **Soft path hints:** `.github/CODEOWNERS`, `.github/`, `docs/control-plane/`, `docs/evals/`, `START.md`
- **Blocks / blocked-by:** After **A-027 + A-028**. Blocks A-031 and unattended Forge.
- **Links:** SELF_IMPROVE_ROADMAP · ChatGPT Q7 · A-032 review

## Goal
Prevent candidates from redefining authorization, trust, evidence or promotion in the same
change they are trying to pass. Use the actual authority surface found by A-032, not only
future eval files. CODEOWNERS is an ownership map; A-027's enforced review rule is what makes
it a gate.

## Checklist
- [ ] Add a versioned Control Plane boundary/threat map: authority, success definitions, trust, promotion, deployment and ledger integrity
- [ ] Inventory and classify at least `brain/server.py`, `brain/training.py`, `brain/validation.py`, `brain/system_prompt.md`, `brain/tools.json`, `actions/core.py`, `scripts/skill-draft.py`, trusted `skills/examples/*`, workflows, eval oracles/baselines, ledger schema/history, promotion policy and CODEOWNERS itself
- [ ] Explicitly cover `skills_trusted`: a bundled recipe change alters auto-executable trusted behavior
- [ ] Add `.github/CODEOWNERS`; ordinary feature tests may ride with a feature, but existing protected regression/oracle or authorization changes require separate/explicit Alex review
- [ ] Verify A-027 actually requires code-owner review and protects the ownership/workflow files; API evidence required
- [ ] Add a deterministic boundary/ownership check that fails when a new authority-bearing path is unclassified
- [ ] Reconcile `.github/ISSUE_TEMPLATE/workstream.md` with ADR-034's area + worktree rule
- [ ] Document coarse initial ownership caused by mixed Runtime/Control Plane files; file later extraction work rather than claiming physical isolation now
- [ ] START/Forge: reject mixed candidate+grader/policy changes unless Alex explicitly scopes the Control Plane change
- [ ] On acceptance, unblock A-031 in QUEUE/INDEX
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Inventing a local substitute for missing repository enforcement; broad autonomous code
rewrites; stochastic runner (A-031); secrets broker; weakening `approval_mode=always`.
