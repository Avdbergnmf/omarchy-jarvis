# A-042 — Parallel claimability: migrate tooling and prompts to ADR-048

- **Status:** queued
- **Area:** area:docs (+ `scripts/`, two lines of `brain/training.py`, `tests/`)
- **parallel-ok:** NO (control-plane: claim-rule / Training default tooling — ADR-048)
- **Recommended depth:** medium
- **Allowed paths (optional soft hint):** `scripts/assignment-status.sh`, `scripts/agent-status.py`, `brain/training.py` (new-brief default only), `docs/assignments/prompts/*`, `docs/assignments/{README,TEMPLATE}.md`, `START.md`, `.github/ISSUE_TEMPLATE/workstream.md`, `tests/test_assignments.py`, `tests/test_journal.py`
- **Forbidden paths (optional soft hint):** `overlay/` (A-041 owns the Agent Monitor UI); `brain/training.py` beyond the default flag and any `parallel-ok` plumbing
- **Blocked-by:** none
- **Gate:** control-plane
- **Improvement:** none
- **Links:** [ADR-048](../../DECISIONS.md#adr-048--claimability-is-computed-parallel-ok-yes-is-the-default-2026-09-10) · [audit](../../audits/parallel-claimability-2026-09-10.md) · supersedes the authoring half of ADR-034 · does not implement A-041

## Goal
ADR-048 flipped the policy and the flags by hand. Until the tooling agrees, the policy is enforced
only by review: `brain/training.py` still stamps `parallel-ok: NO` on every Training-authored
brief, `assignment-status.sh` still silently honors a bare `NO` with no reason, and
`scripts/agent-status.py` still rejects `parallel-ok` issues on rules ADR-034 retired a week ago.
Done means the default is `YES` everywhere a row can be created, a `NO` without a reason is
visibly flagged rather than quietly obeyed, and an agent reading any paste prompt computes the
same claim set the script does.

Do **not** implement the Agent Monitor redesign (A-041) or split `area:` values without Alex's
explicit go-ahead — the area proposal below is a written recommendation, not a change to make.

## Checklist

### Stop the ratchet
- [ ] `brain/training.py::prepare_assignment_save`: new briefs and their QUEUE/INDEX rows default to `parallel-ok: YES`, not `NO` (two literals)
- [ ] Decide and record whether `parallel-ok` becomes an editable field (`META_FIELDS`) or stays workflow-owned per ADR-031; if it stays workflow-owned, say so in `docs/assignments/README.md` so the next filer knows why the editor cannot change it
- [ ] `tests/test_assignments.py`: a new Training-authored draft is `YES`; an existing row's flag still survives an unrelated field edit

### Make a bare `NO` visible
- [ ] `scripts/assignment-status.sh`: print each `NO` row's reason next to it, parsed from the brief's `parallel-ok:` line
- [ ] Same script: print `WARNING: A-NNN is parallel-ok: NO with no reason — treat as YES pending desk review` for any `NO` lacking one of `control-plane` / `single-writer` / `human-serial`
- [ ] Same script: print a non-blocking `HEADS-UP` when a candidate's soft path hints intersect an `in_progress` row's (see ADR-048's named residual risk — a human noticing, never a machine deciding; must not remove any candidate from the hint)
- [ ] Verify the hint against a synthetic QUEUE reproducing the original bug (A-028 `in_progress` `area:docs`; A-029/A-033/A-041 queued and disjoint — all three must be offered) and against the current shape (A-029 `in_progress` `area:actions` → A-033 and A-041 offered, A-030/A-042 withheld as reasoned `NO`)

### Prompts and policy prose agree with the script
- [ ] `prompts/NEW_AGENT.txt`, `prompts/PARALLEL.txt`, `prompts/CONTINUE.txt`, `prompts/README.md`: replace "only `parallel-ok: YES`" with ADR-048's computed rule; keep claim-on-`origin/main`-first (A-039) and the minimal-token stop unchanged
- [ ] `START.md` Parallel work section and `docs/assignments/{README,TEMPLATE}.md` re-read end to end for leftover "NO by default" phrasing
- [ ] Document the Alex escape hatch explicitly: an override phrase may authorize claiming an area-disjoint `NO` row, recorded in SESSION when used

### Retire the contradictions on the issue side
- [ ] `scripts/agent-status.py`: drop `parallel-ok requires Allowed paths: and Forbidden paths:` (ADR-034 made path lists soft hints) and narrow `control-plane/single-writer scope cannot be parallel-ok` so plain `area:brain` no longer trips it
- [ ] `tests/test_journal.py`'s `agent-status` overview assertions updated to match
- [ ] `.github/ISSUE_TEMPLATE/workstream.md` reconciled with area + worktree (also listed in A-030's checklist — whoever lands first wins; delete the duplicate item from the other brief)

### Write down, do not execute, the area proposal
- [ ] Add a short section to the audit (or a follow-up ADR stub) evaluating `area:docs` → `area:docs` + `area:control-plane`: which open rows move, the `AREAS` tuple in `brain/training.py` and `scripts/agent-status.py`, the five GitHub labels, and how in-flight rows would migrate safely
- [ ] Leave the decision to Alex; do not change `AREAS` in this assignment

### Close out
- [ ] `./scripts/test-full.sh` green (touches `brain/` and `scripts/`); note the pre-existing `test_write_prunes_journal_archive_on_rotation` flake if it reappears
- [ ] Update docs/SESSION.md Next action as you go
- [ ] docs/PROGRESS.md note (append a new dated section; never edit an existing one)
- [ ] QUEUE/INDEX → done; move this file to docs/assignments/done/

## Out of scope
- Agent Monitor tiles / per-agent auto-queue (A-041) — reference it, do not build it
- Changing `AREAS`, the five GitHub area labels, or any row's `area:` value
- Worktree mechanics (ADR-024), claim-on-`origin/main` (ADR-038), `Blocked-by`/`Gate` (ADR-041)
- Re-hardening `Allowed paths:`/`Forbidden paths:` into a claim gate — ADR-034 settled this; the
  new `HEADS-UP` line must never remove a candidate
- Fixing the flaky journal-archive prune test (own row, `area:brain`)

## Notes for the coding agent
`brain/training.py` is also in A-041's soft path hints. If A-041 is `in_progress` when you claim
this, your change there is two literals — land it first and tell that agent, or rebase onto it.
That overlap is a heads-up, not a gate (ADR-034/ADR-048).

This row is `parallel-ok: NO (control-plane)` on purpose: it rewrites the claim rules, so it must
not run beside another agent reading them. It is also `area:docs`, so it additionally cannot be
claimed while another docs row (A-030) holds that area — that is the policy working, not a bug.
`control-plane` here means single-writer-by-review: A-027 is cancelled and `main` will never be
API-enforced (ADR-048), so nothing mechanical backstops a bad merge of this file set.

Token discipline: read `docs/audits/parallel-claimability-2026-09-10.md` once; it already contains
the evidence, the option tradeoffs and the exact algorithm. Do not re-derive them.
