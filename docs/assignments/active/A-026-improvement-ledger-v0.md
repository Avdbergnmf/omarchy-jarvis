# A-026 — Improvement Ledger v0 (index, don’t replace QUEUE)

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** YES
- **Soft path hints:** `docs/` (ledger schema + INDEX), `docs/assignments/`
- **Links:** docs/SELF_IMPROVE_ROADMAP.md

## Goal
Durable **Improvement Ledger** (`IMP-####`) = audit/history; **QUEUE** stays operational (`A-###`). Ledger items may spawn assignments. Record hypothesis, evidence, acceptance, links, eval results, Alex decision, outcome. Statuses: observed→proposed→building→evaluated→awaiting_user→approved/rejected→merged→verified. Include evidence pointers and Alex decision.

## Checklist
- [ ] Schema + `docs/ledger/README.md` + INDEX (`improvement_id` ≠ `assignment_id`)
- [ ] Filing bug/feature creates/links IMP row that can enqueue A-### work
- [ ] Seed examples from A-019…A-025 / #15/#16
- [ ] Document desk/Training append rules in START + assignments README
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Replacing QUEUE/Training; forcing journals into git; big Training UI.
