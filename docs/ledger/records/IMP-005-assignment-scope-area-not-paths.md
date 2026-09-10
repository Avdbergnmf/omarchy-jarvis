# IMP-005 — Assignment scope should be area + worktree, not a hard path allowlist

- **Status:** shipped
- **Owner:** Desk
- **Assignment ids:** A-023
- **Evidence refs:** none — historical, predates A-038 evidence bundles (v0); bounded inline summary below
- **Milestone:** none
- **Links:** ADR-034

## Current summary
Shipped. `Allowed paths:`/`Forbidden paths:` were being read as hard gates, forcing a
scope-expansion ask for every one-line fix next door — even though git worktree + branch
isolation (ADR-024) already makes each concurrent agent's checkout independent regardless of
which files it touches. A-023 made isolation officially **worktree + a disjoint `area:`**, with
path lists downgraded to optional soft hints for a reviewer, never a claim gate.

## Events (append-only — never edit or delete a past line; add new lines only)
- 2026-09-10 — hypothesis: Alex — hard path fences cause constant scope-expansion asks;
  worktrees already isolate checkouts, so the path-list gate is redundant and annoying.
- 2026-09-10 — Alex decision: approved as filed.
- 2026-09-10 — assignment A-023 opened and shipped: `TEMPLATE.md`, `docs/assignments/README.md`,
  `START.md`'s Parallel work section, and all paste prompts reworded so "claimable in parallel"
  reduces to one check — does this row's `area:` differ from every `in_progress` row's `area:`.
  `scripts/assignment-status.sh`'s claim hint now actually computes area disjointness. See
  ADR-034; this was itself written up *because* a same-area double-claim (A-020/A-021) produced
  a real merge conflict this session that a second session had to untangle — direct evidence
  that path-list disjointness was never sufficient once shared bookkeeping files are in play.
