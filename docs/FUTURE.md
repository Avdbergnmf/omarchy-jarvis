# Future ideas (parked)

Ideas worth remembering that are **not** current work. Do not file assignments or spend
credits on these unless Alex explicitly pulls one forward.

## Unattended Forge (parked 2026-09-10)

**Idea:** a separate Forge bot/account that opens candidate PRs and pushes branches without
Alex babysitting every step — “agents improve Jarvis in the background,” with merges still
gated (eventually by real branch protection + budgets + kill switch).

**Why parked**
- Branch protection on public `main` now exists (ADR-049), but spend/credits for an unattended loop still do not.
- Alex does not have the credits/budget for an unattended coding loop right now.
- Cool architecture to keep on paper; wrong time to build.

**Still true while parked**
- Visible Claude/Codex windows + paste-ready handoffs are the Forge we actually use.
- Unattended Forge / auto-merge / auto-deploy stay **off**.
- If this comes back: new assignment after protection + spend limits exist — do not reopen A-027.

See also: [SELF_IMPROVE_ROADMAP](SELF_IMPROVE_ROADMAP.md) Wave 2 (prerequisites only), ADR-046.
