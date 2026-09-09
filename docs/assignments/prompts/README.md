# Paste prompts for Alex (easy find)

**Always start coding agents from the repo, not chat history.**

| When you say… | Copy this file into Claude/Codex/Cursor |
|---------------|----------------------------------------|
| **Next step** / continue same line of work | [`CONTINUE.txt`](CONTINUE.txt) |
| **Another agent is working — parallel next** | [`PARALLEL.txt`](PARALLEL.txt) |
| **Brand-new agent** (cold start) | [`NEW_AGENT.txt`](NEW_AGENT.txt) |

Queue of work: [`../QUEUE.md`](../QUEUE.md)  
How Firsty (or any desk agent) adds work: [`../README.md`](../README.md)

Canonical path: `~/Work/omarchy-jarvis/docs/assignments/prompts/`

## Who is working?
- `docs/SESSION.md` + the `in_progress` column in [`../QUEUE.md`](../QUEUE.md)
- `./scripts/assignment-status.sh` — run this first; it hints what a new agent may claim

If nothing is claimable, agents must stop and say **“No assignment in queue is possible right now.”** plus the queue list (or that the queue is empty). They must **not** grab a `parallel-ok: NO` task while another assignment is in progress — they should take a `parallel-ok: YES` candidate or report nothing possible.
