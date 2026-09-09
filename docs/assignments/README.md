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
3. Fill: goal, area, parallel-ok, allowed/forbidden paths, checklist (acceptance as boxes), out of scope, links (issue/pass).
4. Append row to `QUEUE.md` as `queued` (or `in_progress` if Alex will run it immediately).
5. Add INDEX line.
6. Tell Alex which paste prompt to use:
   - same agent continuing → `prompts/CONTINUE.txt`
   - new cold agent → `prompts/NEW_AGENT.txt`
   - second agent while first busy → `prompts/PARALLEL.txt`
7. Do **not** implement Jarvis product code in the desk role unless Alex asked that agent to build — desk default is **queue + prompts only**.

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
