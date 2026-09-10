# Control Plane boundary v1

The Control Plane is everything that can redefine authorization, success, trust, evidence,
promotion, deployment, or ledger history. Its machine-readable inventory is
[`boundary-v1.json`](boundary-v1.json); `scripts/check-control-plane.py` verifies that every
tracked file under a boundary root is classified, every required authority path exists, every
protected-regression oracle source is classified, and CODEOWNERS mirrors the inventory.

## Threat and ownership map

| Authority | Current surface | Failure if a candidate controls both sides |
|---|---|---|
| Authorization and execution | `brain/server.py`, `brain/system_prompt.md`, `brain/tools.json`, `actions/` | A plan can approve itself, bypass review, or expand executable tools. |
| Success definitions | `docs/evals/`, protected oracle sources, `brain/validation.py`, `docs/validation/` | A candidate can weaken the grader or relabel its own result as accepted. |
| Trust | `skills/examples/`, `scripts/skill-draft.py`, `approval_mode=skills_trusted` in Runtime | A bundled recipe edit changes behavior that may auto-execute in trusted-skills mode. |
| Evidence | workflows, `brain/evidence.py`, `brain/journal.py`, eval/coverage checkers | A candidate can omit a suite or manufacture the evidence used to judge it. |
| Work allocation and promotion | `START.md`, `AGENTS.md`, issue templates, assignments policy, roadmap, CODEOWNERS | A candidate can redefine who may claim, review, merge, or deploy it. |
| Deployment identity | `VERSION`, install/start/stop/restart scripts | Reviewed bytes and running bytes can diverge. |
| Ledger integrity | `docs/ledger/`, `scripts/ledger-status.py` | Rejected or abandoned history can be erased or rewritten as success. |

Ownership is deliberately coarse. Runtime and Control Plane logic are mixed in `brain/`,
`actions/`, and `scripts/`; CODEOWNERS therefore maps whole directories even though many lines
are ordinary Runtime code. This is a review boundary, not physical isolation. A later assignment
should extract authorization, grader, trusted-skill manifest/digest, and deployment-policy
modules before narrowing these patterns.

## Review rule

Ordinary feature implementation and its new tests may remain in one feature PR. A change to an
existing protected-regression oracle, authorization path, trusted bundled skill, workflow,
ledger schema/history, this boundary, or promotion policy must be explicitly scoped as a Control
Plane change and reviewed by Alex. A candidate must not change both product behavior and the
grader/policy used to accept that behavior unless Alex explicitly scopes the mixed change.

`.github/CODEOWNERS` is the ownership map. Live API evidence on 2026-09-10 showed an active
default-branch ruleset requiring pull requests plus the `test` status check and preventing
bypass, deletion, and force-push, but requiring **zero approvals** and **no code-owner review**.
Thus CI and PR flow are enforced, while CODEOWNERS and the explicit-human-review policy are not.
Unattended Forge, auto-merge, and auto-deploy remain off. ADR-049 supersedes ADR-046's old
no-ruleset observation; A-030 records the ownership boundary without reopening A-027.
