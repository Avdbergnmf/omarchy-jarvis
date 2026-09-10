# A-030 — Protect safety / eval / control-plane paths

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** NO (promotion/evaluator ownership is serial Control Plane work)
- **Recommended depth:** medium
- **Soft path hints:** `.github/CODEOWNERS`, `.github/`, `docs/control-plane/`, `docs/evals/`, `START.md`
- **Blocked-by:** none
- **Gate:** control-plane
- **Links:** SELF_IMPROVE_ROADMAP · ChatGPT Q7 · A-032 review · blocks A-031; unattended Forge stays off (ADR-046)

## Goal
Prevent candidates from redefining authorization, trust, evidence or promotion in the same
change they are trying to pass. Use the actual authority surface found by A-032, not only
future eval files. CODEOWNERS is an ownership map only — **A-027 is cancelled** (no GitHub Pro / no public repo), so there is no API-enforced review gate on this remote. Document that limit; do not invent a local substitute that claims to be branch protection.

## Checklist
- [ ] Add a versioned Control Plane boundary/threat map: authority, success definitions, trust, promotion, deployment and ledger integrity
- [ ] Inventory and classify at least `brain/server.py`, `brain/training.py`, `brain/validation.py`, `brain/system_prompt.md`, `brain/tools.json`, `actions/core.py`, `scripts/skill-draft.py`, trusted `skills/examples/*`, workflows, eval oracles/baselines, ledger schema/history, promotion policy and CODEOWNERS itself
- [ ] Explicitly cover `skills_trusted`: a bundled recipe change alters auto-executable trusted behavior
- [ ] Add `.github/CODEOWNERS`; ordinary feature tests may ride with a feature, but existing protected regression/oracle or authorization changes require separate/explicit Alex review
- [ ] Document explicitly that A-027/branch protection is unavailable (ADR-046); CODEOWNERS + human review are policy, not an enforceable gate — do not claim otherwise
- [ ] Add a deterministic boundary/ownership check that fails when a new authority-bearing path is unclassified
- [ ] Reconcile `.github/ISSUE_TEMPLATE/workstream.md` with ADR-034's area + worktree rule
- [ ] Document coarse initial ownership caused by mixed Runtime/Control Plane files; file later extraction work rather than claiming physical isolation now
- [ ] START/Forge: reject mixed candidate+grader/policy changes unless Alex explicitly scopes the Control Plane change
- [ ] On acceptance, unblock A-031 in QUEUE/INDEX
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Inventing a local substitute for missing repository enforcement; broad autonomous code
rewrites; stochastic runner (A-031); secrets broker; weakening `approval_mode=always`.
