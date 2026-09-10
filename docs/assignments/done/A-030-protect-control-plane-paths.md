# A-030 — Protect safety / eval / control-plane paths

- **Status:** done
- **Area:** area:docs
- **parallel-ok:** NO (control-plane: CODEOWNERS and the authority-surface classification itself — ADR-048)
- **Recommended depth:** medium
- **Soft path hints:** `.github/CODEOWNERS`, `.github/`, `docs/control-plane/`, `docs/evals/`, `START.md`
- **Blocked-by:** none
- **Gate:** control-plane
- **Links:** SELF_IMPROVE_ROADMAP · ChatGPT Q7 · A-032 review · blocks A-031; unattended Forge stays off (ADR-046)

## Goal
Prevent candidates from redefining authorization, trust, evidence or promotion in the same
change they are trying to pass. Use the actual authority surface found by A-032, not only
future eval files. CODEOWNERS is an ownership map. **ADR-049:** public `main` now has a ruleset (PR + `test`, no force-push/deletion) — document that; still do not pretend CODEOWNERS alone is the gate. A-027 cancelled brief stays closed.

## Checklist
- [x] Add a versioned Control Plane boundary/threat map: authority, success definitions, trust, promotion, deployment and ledger integrity
- [x] Inventory and classify at least `brain/server.py`, `brain/training.py`, `brain/validation.py`, `brain/system_prompt.md`, `brain/tools.json`, `actions/core.py`, `scripts/skill-draft.py`, trusted `skills/examples/*`, workflows, eval oracles/baselines, ledger schema/history, promotion policy and CODEOWNERS itself
- [x] Explicitly cover `skills_trusted`: a bundled recipe change alters auto-executable trusted behavior
- [x] Add `.github/CODEOWNERS`; ordinary feature tests may ride with a feature, but existing protected regression/oracle or authorization changes require separate/explicit Alex review
- [x] Document ADR-049 ruleset (PR + `test`) vs CODEOWNERS-as-map; do not claim CODEOWNERS alone enforces review
- [x] Add a deterministic boundary/ownership check that fails when a new authority-bearing path is unclassified
- [x] Reconcile `.github/ISSUE_TEMPLATE/workstream.md` with ADR-034's area + worktree rule
- [x] Document coarse initial ownership caused by mixed Runtime/Control Plane files; file later extraction work rather than claiming physical isolation now
- [x] START/Forge: reject mixed candidate+grader/policy changes unless Alex explicitly scopes the Control Plane change
- [x] On acceptance, unblock A-031 in QUEUE/INDEX
- [x] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Inventing a local substitute for missing repository enforcement; broad autonomous code
rewrites; stochastic runner (A-031); secrets broker; weakening `approval_mode=always`.
