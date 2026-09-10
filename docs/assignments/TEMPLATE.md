# A-NNN — Title

- **Status:** queued | in_progress | blocked | done | cancelled
- **Area:** area:overlay | area:brain | area:actions | area:skills | area:docs
- **parallel-ok:** YES  (default; write `NO (<control-plane|single-writer|human-serial>: <surface>)` only when one genuinely applies — see ADR-047. Ordering goes in `Blocked-by:`, never here)
- **Recommended depth:** low | medium | high | xhigh  (Codex `model_reasoning_effort`; show in QUEUE; tell Alex on closeout)
- **Allowed paths (optional soft hint):** likely-touched paths, if useful context — never a hard gate; isolation is worktree + a disjoint `area:`, not a path allowlist
- **Forbidden paths (optional soft hint):** anything worth flagging explicitly — never a hard gate
- **Blocked-by:** none | A-NNN[, A-NNN...]  (structured — `assignment-status.sh` computes claimability from this, not prose; see ADR-041)
- **Gate:** none | <lowercase-hyphen-slug>  (optional grouping label, e.g. `control-plane`; informational, never auto-enforced)
- **Improvement:** none | IMP-NNN  (optional back-link into `docs/ledger/`, A-026 — the durable "why," not queue sequencing)
- **Links:** issue #N · pass path · ADR · what this blocks (prose, e.g. "unblocks A-029")

## Goal
One paragraph. What “done” means for Alex.

## Checklist
- [ ] …
- [ ] Update docs/SESSION.md Next action as you go
- [ ] docs/PROGRESS.md note
- [ ] QUEUE/INDEX → done; move this file to docs/assignments/done/

## Out of scope
- …

## Notes for the coding agent
Token discipline: read once, prefer git diff, no session-log pastes.
