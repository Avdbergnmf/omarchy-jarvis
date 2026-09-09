# Claude Code — bake agent efficiency + resumable progress into the repo

Work in `~/Work/omarchy-jarvis`. **Small docs (+ tiny script) pass.** Do not rewrite overlay/brain.

## Goal
1. Standing **token/context discipline** so agents don’t melt quotas.
2. A **resumable checklist** for in-flight work so when tokens die mid-pass, the next agent picks up cold without session logs.

## Add / update

### A. Docs
1. **`START.md`** (create or edit) — sections near the top:
   - **Token & context discipline**
   - **Resumable work (SESSION / checklist)** — how to start, update, and continue
2. **`AGENTS.md`** — condensed pointers to both.
3. **`docs/passes/README.md`** — pass etiquette + “update SESSION before you stop.”

### B. Resumable progress artifact (required)
Add **`docs/SESSION.md`** (or `docs/passes/SESSION.md` — pick one, link from START; prefer **`docs/SESSION.md`** at a stable path).

Purpose: single “where are we” file the next agent reads first after START.

Must include a template like:

```markdown
# Session (in-flight agent work)
> Agents: update this **before** stopping or when finishing a checklist item.
> Humans: safe to edit. Not a substitute for GitHub issues / PROGRESS history.

## Active goal
- Pass / issue: (link or path)
- Area label: (overlay|brain|…)
- Branch:

## Checklist
- [ ] …
- [x] …

## Done this session (evidence)
- commits / files / commands that passed

## Next action (one concrete step)
- …

## Blockers
- none | …
```

Rules to encode in START:
- At the **start** of a pass or “fix issues” stint: create/refresh checklist from the pass acceptance criteria or issue tasks (checkboxes).
- **Check off** items as you complete them; don’t delete the plan mid-flight.
- Before context gets fat or when stopping: flush **Next action** + checklist to `docs/SESSION.md` and a one-liner in `docs/PROGRESS.md`.
- Next agent: START → **SESSION.md** → `git status`/`diff` → continue **Next action** — **never** require pasted chat/Codex logs.
- When the goal is fully done: mark checklist complete, clear or archive session body to a short “last completed” stub, move pass to archive per lifecycle, leave lasting notes in PROGRESS/issues.

Optional but nice: `scripts/agent-status.sh` (or `agent-handoff-continue.sh`) prints SESSION checklist summary + git status -sb + last commits + active passes.

### C. Token & context discipline (must appear in START)
- Continue from **repo** (SESSION, git, PROGRESS, `docs/passes/active/`) — never paste agent session transcripts.
- Read once, then prefer diffs; no re-reading huge unchanged files every turn.
- One chunk per session; stop at that chunk’s acceptance; commit; update SESSION/PROGRESS.
- No drive-by refactors; keep `logs/` out of context unless a specific run_id; don’t echo huge tool outputs back into context.
- Sonnet-class model for impl unless stuck.

## Acceptance
- Cold agent can resume from SESSION.md alone after a kill.
- Efficiency + resume rules visible in START without another essay from Alex.
- Template exists; example filled or clearly empty stub.
- Docs/script only; doctor green if scripts touched.
- Mark this efficiency pass done in SESSION when you finish; archive this brief if passes/ layout exists.

## Out of scope
Runtime Jarvis journal/logging features; re-doing the mega entrypoint implementation in this pass.
