# A-037 — Release gates + claimability visibility (not a second wave counter)

- **Status:** queued
- **Area:** area:docs (+ light `area:overlay` / `brain/training.py` for surfacing)
- **parallel-ok:** NO (after **A-036**; coordinate with **A-026**)
- **Recommended depth:** medium
- **Soft path hints:** `docs/assignments/`, `START.md`, `scripts/assignment-status.sh`, Training panels, `docs/MILESTONES.md`, ledger docs when present
- **Blocked-by:** none (A-036 done)
- **Gate:** training-dispatch
- **Links:** Alex stages/waves idea; desk review vs roadmap/ledger; do not invent a parallel ID space vs A-026

## Decision (why not “stage: 0/1/2” algebra)

Informal **Wave 0 / Wave 1** prose already exists. A global integer **stage** system with “shift everything +1” would **duplicate**:

- **QUEUE order** + `parallel-ok` / area rules
- **`Blocks / blocked-by`** (already on the assignment template)
- **Improvement Ledger** `IMP-*` lifecycle (A-026) — improvement state, not queue release gating
- **`docs/MILESTONES.md`**

**Better model:** one queue (`A-###`); sequencing via **`blocked-by`** + optional **`gate:`** labels; Training/`assignment-status` **explains why something isn’t claimable**. “New wave” = add a **gate** (stub assignment or record) that later work `blocked-by` — not renumber everything.

## Goal
In Training Agent monitor / Assignments, Alex sees:

1. In-progress work (with A-036)
2. Blocked + **why** (dependency, parallel/area, waiting on gate)
3. Optional **gate** slug on each assignment (`plan-review`, `control-plane`, `latency`, …)
4. Editor/generate/repo can set `blocked-by` + `gate`

Optional cheap: confirmable “add gate” that offers to attach `blocked-by` — **not** global stage shift.

## Checklist
- [ ] ADR: gates + blocked-by + QUEUE order; relate to A-026 / MILESTONES; reject stage integers unless A-032 demands them
- [ ] Frontmatter: `blocked-by`, optional `gate:`; migrate Wave prose into gate labels
- [ ] `assignment-status.sh`: claimability + blocked reasons
- [ ] Training: show gate + blocked reasons (on A-036 board)
- [ ] Editor/generate + README/START; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
Global stage shift-up; auto-start next gate; replace QUEUE with ledger; latency profiler.

## Notes — initial gates (labels; order from blocked-by/QUEUE)
- `plan-review` — A-032
- `training-dispatch` — A-036 / A-037
- `control-plane` — A-026…A-031, A-029
- `latency` — A-033…A-035
