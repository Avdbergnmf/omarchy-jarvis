# A-026 — Improvement Ledger v0 (Desk-owned audit wrapping QUEUE)

- **Status:** done
- **Area:** area:docs
- **parallel-ok:** NO (single writer for ledger schema/index/history)
- **Recommended depth:** high
- **Soft path hints:** `docs/` (ledger schema + INDEX), `docs/assignments/`
- **Blocked-by:** none
- **Gate:** control-plane
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · A-032 review · unblocked by A-038 (done) · unblocks A-029 on completion

## Goal
Create a versioned, Desk-owned Improvement Ledger. The ledger explains why behavior changed;
QUEUE remains disposable execution work. One `improvement_id` may link many `assignment_id`s.
V0 is manual and schema-first: Runtime/Training/Forge do not allocate or mutate ledger records.
Use a single Desk allocator against reconciled canonical state or a collision-resistant id;
do not copy Training's branch-local “max + 1” allocation without cross-worktree protection.

## Checklist
- [x] Versioned schema + `docs/ledger/README.md` + validated/generated INDEX (`improvement_id` ≠ `assignment_id`) — `IMP-NNN` vs `A-NNN` prefixes are always distinct; `docs/ledger/{README,TEMPLATE,INDEX}.md`.
- [x] Per-item current summary plus append-only events: hypothesis, bounded evidence refs, acceptance, assignments/PRs/commits, eval summaries, Alex decision+rationale, outcome and verification — see `TEMPLATE.md` and the six seed records.
- [x] Define id allocation and duplicate detection across worktrees; only Desk writes v0 records — same fetch-origin/main-first discipline as A-039 (ADR-038), documented in the ledger README; `scripts/ledger-status.py` detects duplicates/mismatches.
- [x] Define state vocabulary without pretending to enforce the future full state machine; preserve rejection/abandonment history — `hypothesis → in_progress → shipped | rejected | abandoned`, informal, Desk sets `Status:` by hand; events are append-only by convention.
- [x] Require A-038 durable evidence refs/content hashes or in-record bounded summaries; an ignored `logs/...` path alone is not durable evidence — enforced in the README's Evidence section; all six seed records use the bounded-inline-summary path (they predate A-038).
- [x] Seed representative records from A-019…A-025 / #15/#16 and validate links — IMP-001…IMP-006; `scripts/ledger-status.py` validates every `Assignment ids:` reference against `docs/assignments/INDEX.md`.
- [x] Add optional `Improvement: IMP-*` assignment metadata; confirm Training preserves unknown metadata/sections — added to `META_FIELDS`/`FIELD_LIMITS` (`brain/training.py`), form field in `overlay/training.html`; `tests/test_assignments.py::test_improvement_link_is_a_structured_optional_hint` confirms it survives an unrelated edit.
- [x] Allow an optional milestone note; do not invent assignment `stage:` integers (A-037 owns gates) — `Milestone:` field in `TEMPLATE.md`, purely informational.
- [x] Document Desk append/update rules in START + assignments README; Runtime/Training integration gets a later assignment — cross-references added to both; Runtime/Training/Forge writing the ledger stays explicitly out of scope.
- [x] On acceptance, deliberately unblock A-029 in QUEUE/INDEX — `Blocked-by: none`, `Status: queued`.
- [x] ADR; PROGRESS; SESSION; QUEUE/INDEX → done — ADR-044.

## Out of scope
Replacing QUEUE/Training; runtime issue/Training auto-linking; auto-allocating ids from
worktrees; forcing raw/private journals into git; a big Training UI; enforcing the full
formal state machine; release-gate UX (A-037).
