# A-027 — Enforced promotion path (protected main + separate Forge actor)

- **Status:** blocked
- **Area:** area:docs
- **parallel-ok:** NO (control-plane: repository protection rules and the promotion actor — ADR-046)
- **Recommended depth:** high
- **Soft path hints:** `docs/`, `START.md`, `scripts/`, `.github/`
- **Blocked-by:** none
- **Gate:** none
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · A-032 review · blocks A-030 and unattended Forge

## Goal

**Human decision blocker:** This assignment is blocked on a human decision, not an assignment id.
Alex must choose GitHub Pro, deliberate public visibility, or another authoritative host with
private-repo protection before this work can proceed.

Create a **verified hard promotion gate**, not a policy-only approximation. Candidate branches
and PRs may be automated later; merge/promotion requires Alex and repository enforcement.
The Forge identity may push candidate branches and open/update PRs but must not bypass the
rules or supply Alex's approval.

Live A-032 evidence (2026-09-10): this repository is private, and both GitHub ruleset and
classic branch-protection API reads return HTTP 403: “Upgrade to GitHub Pro or make this
repository public to enable this feature.” Do not change visibility or hosting without Alex.
Keep unattended Forge disabled while this row is blocked.

## Checklist
- [ ] Record Alex's explicit hosting/plan choice and unblock this brief; never infer public visibility
- [ ] Define separate Alex (approver) and Forge (candidate-only, non-bypass) actors/credentials
- [ ] Apply protection to `main`: PR required, stable `checks / test` required, no force-push/deletion, stale/last-push review handled, and no actor/app/admin bypass that defeats the gate
- [ ] Verify effective rules through the API and record bounded evidence; CODEOWNERS or prose alone does not pass
- [ ] Add `docs/PROMOTION.md`: candidate → CI/evals → Alex review → optional VM → merge → version/tag → optional system snapshot → canonical deploy → health → ledger
- [ ] Define “system-affecting,” canonical deploy checkout/revision, `scripts/stop.sh`, git revert/restart and health evidence; reconcile the policy with VERSION 0.5.9 while tags stop at v0.3.0
- [ ] Update START and assignment prompts to require branch + PR by default and prohibit candidate-tree/shared-service deploys
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope

Making the repository public; buying/changing a plan without Alex; local hooks presented as
security; auto-merge; autonomous deploy; snapshot automation; staged deploy; implementing
Forge itself; weakening checks merely to make protection green.
