# Assignments — queue for coding agents

This is how Alex (via Firsty or any other **desk agent**) turns “I want X” into work a coding agent can run without the chat history.

## Mental model
```
Alex → desk agent (Firsty / …) → writes assignment file + QUEUE row
     → Alex pastes CONTINUE / PARALLEL / NEW_AGENT into Claude|Codex|Cursor
     → coding agent updates checklist / SESSION → done/ → next
```

Durable product truth stays in **issues, backlog, ADRs, PROGRESS**.  
Assignments are **scoped work orders** with a **checkbox plan** so token death is recoverable.

## Layout
```
docs/assignments/
  README.md          ← you are here (authoring rules)
  QUEUE.md           ← ordered work; what’s in_progress
  INDEX.md           ← all ids + status
  TEMPLATE.md        ← copy for new assignments
  active/            ← open work orders
  done/              ← finished work orders
  prompts/           ← PASTE THESE (Alex’s easy find)
```

Related: `docs/passes/` for large historical briefs; prefer **assignments** for the ongoing “next thing Alex asked for” stream. Big epics may still use a pass file linked from an assignment.

## Statuses
`queued` → `in_progress` → `done` (or `blocked` / `cancelled`)

Rules:
- **Claimability is computed, not declared** (ADR-047): `queued` + every `Blocked-by` id `done` +
  `area:` disjoint from every `in_progress` row. See "Parallel claimability" below.
- Coding agents check off boxes in the assignment file and mirror “Next action” in `docs/SESSION.md`.
- On done: move `active/A-###-*.md` → `done/`, update QUEUE + INDEX + PROGRESS.

## Parallel claimability: `parallel-ok` defaults to YES
A row is claimable when the queue says it is ready, its dependencies are met, and nobody is
working its area — nothing else. The absence of a positive flag never refuses a claim.

```
for row in QUEUE order:
    skip unless row.status == "queued"
    skip if any Blocked-by id is not "done" in INDEX.md      # ADR-041
    take it if nothing is in_progress                        # first ready row wins
    skip if row.parallel-ok is NO                            # reasoned kill-switch only
    skip if row.area matches any in_progress row's area      # ADR-034
    -> claimable in parallel
```

All inputs come from `origin/main` (ADR-038), never a branch-local copy. `parallel-ok: NO` is
*self*-restricting: it says when **this** row may be claimed, never that an in-progress row locks
the repository.

**Default `YES`.** Write `NO` only when one of three reasons applies, and name it in the brief:

| reason | means |
|--------|-------|
| `control-plane` | redefines authorization, promotion, evaluation, trust, or the claim rules themselves |
| `single-writer` | redesigns a shared runtime seam no concurrent writer can tolerate even from another area (`brain/server.py` approve/execute or planner routing, the journal writer) |
| `human-serial` | Alex asked for this one to run alone |

`area:brain` on its own is **not** a reason — additive instrumentation is fine, a planner-routing
redesign is not. Ordering is **not** a reason either: "do this after A-0NN" belongs in
`Blocked-by:`, which is recomputed as blockers complete, while a stale `NO` lasts forever. A bare
`NO` with no reason is a filing bug — the desk treats it as `YES` pending review.

## Shared bookkeeping while parallel
The merge pain ADR-034 cited was never in product code; it was in the files every assignment
touches. Independent of areas or flags:

1. **Reserve your ADR number in the claim commit** — the same push to `origin/main` that flips
   your row to `in_progress` appends a one-line reserved stub to `docs/DECISIONS.md`. A-026 had to
   renumber 043 → 044 at merge time for want of this.
2. **QUEUE/INDEX: your own row only.** Never reorder rows or rewrite the prose block under the
   table mid-flight; add your narrative at merge time. Row-per-assignment merges cleanly by itself.
3. **SESSION: your own lines only** — your Active-goal bullet, your checklist line, your
   `## Parallel agent` entry. Never rewrite another agent's.
4. **PROGRESS: append at the end**, a new dated `## YYYY-MM-DD — A-NNN …` section. Never edit an
   existing one, even to correct it.
5. **Rebase on `origin/main` immediately before merging.** PR #18 conflicted on these same files
   with no parallel agent at all, purely from a stale base.

## Release gates: `Blocked-by` + `Gate` (not a stage counter)
An assignment blocked on other work sets **`Blocked-by:`** to a comma-separated list of
`A-###` ids (or `none`) — this is the only field `./scripts/assignment-status.sh` and Training's
Agent monitor parse to compute real claimability and print *why* a row isn't claimable yet. A
human-only blocker (a decision only Alex can make, not an id) stays `Blocked-by: none` with the
reason in prose. **`Gate:`** is an optional, purely informational grouping label (e.g.
`control-plane`, `latency`) — never auto-enforced, never a second numbering scheme; it exists so
Training can group/filter related blocked work without inventing global `stage: 0/1/2` integers
(see [ADR-041](../DECISIONS.md#adr-041--structured-blocked-by--gate-replace-stage-integers-2026-09-10)).
Changing `Blocked-by`/`Gate` never auto-flips `Status`: a human (or the desk) still sets
`Status: blocked → queued` once the real-world dependency is actually resolved.

## The Improvement Ledger: durable "why," not disposable "what"
`docs/assignments/` (this directory) is disposable execution work — an assignment is claimed,
done, and archived to `done/`. [`docs/ledger/`](../ledger/README.md) (A-026) is the durable
record of *why* behavior changed: one `IMP-NNN` may span several assignments. Only **Desk**
writes ledger records — Runtime/Training/Forge never allocate an `IMP-*` id. An assignment may
optionally set `- **Improvement:** IMP-NNN` to link back to its ledger record; this is unrelated
to `Gate` (queue sequencing) — see the ledger README for the full model, id-allocation
discipline (same claim-on-`origin/main`-first pattern as A-039), and evidence requirements.

## How a desk agent creates an assignment (standard)
When Alex asks for a change/add (in any chat):

1. **Name it** — short title; id `A-NNN` monotonic (see INDEX).
2. **Copy** `TEMPLATE.md` → `active/A-NNN-slug.md`.
3. Fill: goal, area, parallel-ok, checklist (acceptance as boxes), out of scope, links (issue/pass); allowed/forbidden paths are optional soft hints, not required. Set `Blocked-by`/`Gate` if this depends on other work (see below) — leave both `none` otherwise.
4. Append row to `QUEUE.md` as `queued` (or `in_progress` if Alex will run it immediately).
5. Add INDEX line.
6. Tell Alex which paste prompt to use:
   - same agent continuing → `prompts/CONTINUE.txt`
   - new cold agent → `prompts/NEW_AGENT.txt`
   - second agent while first busy → `prompts/PARALLEL.txt`
7. Do **not** implement Jarvis product code in the desk role unless Alex asked that agent to build — desk default is **queue + prompts only**.

### Parallel dispatch uses isolated worktrees

Concurrent coding agents **must** each have a dedicated branch and worktree;
single-agent serial work may use the canonical checkout. Follow the exact
[creation, push and cleanup commands in START](../../START.md#required-isolation-for-concurrent-agents),
which now require **pushing the claim commit to `origin/main` first**
(A-039) — a worktree is only opened after the claim lands on `origin/main`, so
`git fetch origin` + `./scripts/assignment-status.sh` is always enough to see
every live claim, not just this branch's copy.
Dispatch the absolute working directory with the prompt; an already assigned
isolated tree must be reused. Never send parallel agents a blanket `cd` to the
canonical tree. Record owner + branch + worktree in the desk claim (pushed to
`origin/main`) and the worker's SESSION before implementation. Worktrees do not
relax area disjointness (the actual parallel-safety rule — see
[ADR-034](../DECISIONS.md#adr-034--assignment-scope-is-area--worktree-not-hard-path-fences-2026-09-10))
or isolate live services. Merge shared bookkeeping carefully, preserving other
workers' claims and evidence. A claim that outlives its agent (crash, abandoned
worktree) is released via [START's stale-claim
recovery](../../START.md#recovering-a-stale-claim), not silently reclaimed.

### Constraints for good assignments
- Every assignment gets a **Recommended depth** (`low|medium|high|xhigh`) in the brief **and** the QUEUE `depth` column.
- On batch closeout, agents must name the **next** queued row’s recommended depth for Alex.
- **One area** when possible; if multi-area, split into two assignments.
- Checklist items must be **verifiable**.
- Explicit **out of scope** to stop mega-passes.
- Link existing ADRs/passes instead of pasting novels.
- Leave `parallel-ok: YES` (the default) unless one of the three named reasons above applies;
  a `NO` must say which. Do not encode ordering here — use `Blocked-by:`.
- Closing behavior work needs a relevant regression artifact (a `tests/` case, and a
  [`docs/evals/`](../evals/README.md) entry when it names a capability/regression worth
  pinning) or a documented reason only human/VM validation is possible (A-028).

## Alex commands (coding agent interpretation)
| Alex says | Coding agent does |
|-----------|-------------------|
| next step / continue | CONTINUE.txt behavior |
| another agent is working, parallel next | PARALLEL.txt behavior |
| (new chat, no context) | NEW_AGENT.txt behavior |

## Token discipline
Never tell Alex to paste agent session logs into the next agent. Point at QUEUE + SESSION + git.

## Visibility for humans
- **Who is working right now?** `docs/SESSION.md` (Active goal) and any QUEUE row with `in_progress`.
- **What can a second agent take?** `./scripts/assignment-status.sh` (claim hint). New agents follow `prompts/NEW_AGENT.txt` and compute the claim set above; if it is genuinely empty, reply **No assignment in queue is possible right now** with the queue list. Until A-042 lands, the script still ANDs on a literal `YES` and silently honors an unreasoned `NO` — if it offers nothing while a dependency-free row sits in an untouched area, that row's flag is the bug, not the queue.

## One assignment then report (default)
Coding agents complete **a single** assignment per invocation unless Alex explicitly enables a batch (`keep going`, `batch N`, `until queue empty`). After each assignment they update QUEUE/SESSION/PROGRESS; after the batch (or the single default) they **stop and summarize** for Alex instead of silently draining the queue.

## Training-authored assignments and local slots
Training previews generate a monotonic A-NNN brief, queued QUEUE/INDEX rows and an active
handoff using NEW_AGENT/CONTINUE. The user sees exact bytes and confirms before writing.
Rows carry area scope, an optional soft path hint, a verification checklist and source evidence.
Training still stamps `parallel-ok: NO` on every draft it writes and its editor cannot change the
flag (ADR-031) — a desk agent must correct it by hand until **A-042** flips that default to `YES`. Human comments should state the expected outcome; an agent must clarify
insufficient acceptance before broadening work. Preparation does not claim the assignment.

Local slots are stored in ignored `logs/training/agents.json` (version 1, `agents` list),
following `agents.example.json`: id, label, kind, status idle/busy, current_assignment,
queued_assignment_ids, optional Cursor/Codex `reasoning_effort` (`low|medium|high|xhigh`),
plus last_handoff. QUEUE in_progress makes a matching slot busy even
if its manual status says idle. This is coordination metadata, not live agent telemetry.
Queued handoffs never auto-send. Confirm previews expire after 15 minutes, are single-use,
and reject intervening changes to SESSION, QUEUE, INDEX, slots or target files. Writes are
serialized in-process, replaced per-file and rolled back on ordinary I/O failure; a process
crash during a multi-file write can require git/status review. External editors must follow
ownership rules; they do not share the process lock.

## Feature completion requires a human test entry
For each user-visible feature, add/update `docs/validation/catalog.json` and regenerate
`docs/FEATURES.md` per [the schema](../validation/catalog.schema.md). Include concrete steps,
expected behavior and shipped version; leave it unvalidated for Alex. Unit/CI checks remain
mandatory and do not substitute for human validation. Training's Verify/Fail confirmations
record the human's date/version/notes. Failing can draft a reviewed bug; verifying closes no issue.
