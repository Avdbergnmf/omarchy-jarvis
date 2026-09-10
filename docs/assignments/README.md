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
- **One primary `in_progress`** unless extras are `parallel-ok: YES` with disjoint `area:`.
- Coding agents check off boxes in the assignment file and mirror “Next action” in `docs/SESSION.md`.
- On done: move `active/A-###-*.md` → `done/`, update QUEUE + INDEX + PROGRESS.

## How a desk agent creates an assignment (standard)
When Alex asks for a change/add (in any chat):

1. **Name it** — short title; id `A-NNN` monotonic (see INDEX).
2. **Copy** `TEMPLATE.md` → `active/A-NNN-slug.md`.
3. Fill: goal, area, parallel-ok, checklist (acceptance as boxes), out of scope, links (issue/pass); allowed/forbidden paths are optional soft hints, not required.
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
[creation, push and cleanup commands in START](../../START.md#required-isolation-for-concurrent-agents).
Dispatch the absolute working directory with the prompt; an already assigned
isolated tree must be reused. Never send parallel agents a blanket `cd` to the
canonical tree. Record owner + branch + worktree in the desk claim and the
worker's SESSION before implementation. Reconcile claims read-only across
`git worktree list` and the desk queue: branch-local QUEUE/SESSION can be stale.
Worktrees do not relax area disjointness (the actual parallel-safety rule — see
[ADR-034](../DECISIONS.md#adr-034--assignment-scope-is-area--worktree-not-hard-path-fences-2026-09-10))
or isolate live services. Merge shared bookkeeping carefully, preserving other workers' claims and evidence.

### Constraints for good assignments
- **One area** when possible; if multi-area, split into two assignments.
- Checklist items must be **verifiable**.
- Explicit **out of scope** to stop mega-passes.
- Link existing ADRs/passes instead of pasting novels.
- Mark `parallel-ok: NO` for `area:brain` / control-plane by default.

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
- **What can a second agent take?** `./scripts/assignment-status.sh` (claim hint). New agents follow `prompts/NEW_AGENT.txt`: prefer `parallel-ok: YES` when something is already in progress; otherwise reply **No assignment in queue is possible right now** with the queue list.

## One assignment then report (default)
Coding agents complete **a single** assignment per invocation unless Alex explicitly enables a batch (`keep going`, `batch N`, `until queue empty`). After each assignment they update QUEUE/SESSION/PROGRESS; after the batch (or the single default) they **stop and summarize** for Alex instead of silently draining the queue.

## Training-authored assignments and local slots
Training previews generate a monotonic A-NNN brief, queued QUEUE/INDEX rows and an active
handoff using NEW_AGENT/CONTINUE. The user sees exact bytes and confirms before writing.
Rows are serial by default with area scope, an optional soft path hint, a verification
checklist and source evidence. Human comments should state the expected outcome; an agent must clarify
insufficient acceptance before broadening work. Preparation does not claim the assignment.

Local slots are stored in ignored `logs/training/agents.json` (version 1, `agents` list),
following `agents.example.json`: id, label, kind, status idle/busy, current_assignment,
queued_assignment_ids, plus last_handoff. QUEUE in_progress makes a matching slot busy even
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
