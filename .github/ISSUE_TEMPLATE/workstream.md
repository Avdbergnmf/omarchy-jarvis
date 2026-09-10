---
name: Milestone workstream
about: Track a Jarvis milestone with host evidence
---
## Exit criteria

## Implementation

## Verification on host

## Remaining limitations

## Area and ownership
Choose one label: area:overlay | area:brain | area:actions | area:skills | area:docs.
Isolation is a **different area** plus a **separate worktree/branch** (ADR-034). Paths are
optional soft hints, never a claim gate.

`parallel-ok` defaults to YES (ADR-048). A `NO` kill-switch needs a reason (`control-plane` /
`single-writer` / `human-serial`). Do not treat `area:brain` alone as "cannot be parallel-ok".
`single-writer` still applies to approve/execute and `brain/server.py` redesign.

Soft path hints (optional):

## Run evidence
Run id:
Journal path / archive:
Jarvis version:
Expected vs actual:
