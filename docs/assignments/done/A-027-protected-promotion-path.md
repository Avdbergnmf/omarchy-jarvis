# A-027 — Enforced promotion path (protected main + separate Forge actor) — CANCELLED

- **Status:** cancelled
- **Area:** area:docs
- **parallel-ok:** NO
- **Recommended depth:** high
- **Blocked-by:** none
- **Gate:** none
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · A-032 review · ADR-046

## Outcome (2026-09-10)

**Cancelled / deferred indefinitely.** Alex decided not to make `omarchy-jarvis` public and
not to buy GitHub Pro right now. Private Free GitHub cannot enable branch protection /
rulesets (API 403). There is **nothing agents or Jarvis can do** to create a verified hard
promotion gate on this remote under those constraints.

### Standing rules for humans and agents
- Do **not** wait on A-027, GitHub Pro, or “make the repo public.”
- Do **not** change repository visibility or billing without an explicit new Alex decision.
- Do **not** pretend CODEOWNERS, local hooks, or prose are branch protection.
- Unattended Forge / auto-merge / auto-deploy stay **off**. Merges remain human-reviewed
  under the normal branch + PR (or direct push) workflow Alex already uses.
- If Alex later enables Pro or another host with real protection, **file a new assignment**
  rather than reopening this cancelled brief.

## Original goal (archived)
Create a verified hard promotion gate (protected `main`, non-bypass Forge actor, API-proven
rules). Blocked on hosting/plan choice; that choice is now “neither Pro nor public for now.”

## Checklist
- [x] Record Alex's explicit decision (no Pro, no public) — ADR-046
- [x] Remove A-027 from the live queue; stop blocking dependents on it
- [x] Document that hard protection is unavailable on this remote for now
- [ ] *(Not doing)* Apply GitHub branch protection / rulesets
- [ ] *(Not doing)* Verify protection via API

## Out of scope
Making the repository public; buying GitHub Pro; inventing fake local “protection.”
