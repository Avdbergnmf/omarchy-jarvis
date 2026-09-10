# Paste prompts for Alex (easy find)

**Always start coding agents from the repo, not chat history.**

| When you say… | Copy this file into Claude/Codex/Cursor |
|---------------|----------------------------------------|
| **Next step** / continue same line of work | [`CONTINUE.txt`](CONTINUE.txt) |
| **Another agent is working — parallel next** | [`PARALLEL.txt`](PARALLEL.txt) |
| **Brand-new agent** (cold start) | [`NEW_AGENT.txt`](NEW_AGENT.txt) |

Queue of work: [`../QUEUE.md`](../QUEUE.md)  
How Firsty (or any desk agent) adds work: [`../README.md`](../README.md)

Concurrent agents must use separate worktrees/branches; paste the assigned absolute
working directory with the prompt. Reuse an already assigned isolated tree.
See [START commands](../../../START.md#required-isolation-for-concurrent-agents).
`origin/main`'s QUEUE/SESSION is the canonical claim truth (A-039): an agent
must push its claim there **before** opening a worktree, not just record it
branch-locally. `./scripts/assignment-status.sh` fetches and reads `origin/main`.

Canonical prompt source path: `~/Work/omarchy-jarvis/docs/assignments/prompts/`

## Who is working?
- `docs/SESSION.md` + the `in_progress` column in [`../QUEUE.md`](../QUEUE.md)
- `./scripts/assignment-status.sh` — run this first; it hints what a new agent may claim

If nothing is claimable, agents must stop **immediately with minimal tokens** and say **“No assignment in queue is possible right now.”** plus a one-line queue status. No exploring, no invented chores, no full-suite runs. Override only if Alex explicitly says so; if unclear, ask one question and stop. Claimability is **computed** (ADR-048), the same set `./scripts/assignment-status.sh` prints: queued + Blocked-by met + disjoint `area:`. A reasoned `parallel-ok: NO` (`control-plane` / `single-writer` / `human-serial`) is a self-restricting kill-switch; a bare `NO` is a filing bug (script WARNING, treat as YES pending desk review). Path hints never gate a claim. Alex may authorize an area-disjoint reasoned-`NO` row with `force parallel A-NNN` (record in SESSION).

## One vs many assignments
- **Default:** agent finishes **one** assignment, then reports back to you.
- **Keep going:** tell it explicitly, e.g. `keep going for 3` / `batch 2` / `until queue empty` (it still stops if nothing is claimable or tokens are tight).
- Recorded in `docs/SESSION.md` as `Batch: N` or `Batch: until-empty` while running.

## After a batch: merge to main
Agents must **merge their finished work into `origin/main` before stopping** (PR+merge or direct merge when allowed). Do not leave the only copy on a feature branch — that causes forgotten merges and wasted follow-up tokens. If merge is blocked, they must say **BLOCKED ON MERGE** explicitly.

After a successful merge they must **remove their worktree**, delete the merged branch, and `cd` back to `~/Work/omarchy-jarvis` on updated `main` **before** stopping or claiming the next assignment.

## Recommended depth
QUEUE has a **depth** column (`low|medium|high|xhigh`). Assignment briefs carry **Recommended depth**. On batch closeout, agents must tell Alex the **next** row’s depth.
