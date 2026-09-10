# A-008 — Training mode (improvement control plane)

- **Status:** done
- **Area:** area:overlay (+ `area:brain` for APIs; `area:docs` for feature/metrics surfaces)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/`, `brain/`, `docs/assignments/`, `docs/backlog/`, `docs/FEATURES.md` (create), `docs/LOGGING.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `README.md`, `START.md` (pointer only), `scripts/`, `tests/`, `VERSION`
- **Forbidden paths:** Implementing A-009 validation runner in full (stub hooks OK); silent auto-spend on cloud agents without explicit user confirm
- **Blocks / blocked-by:** Prefer after **A-007** (slash + command registry). **Blocks A-009** (validation UI lives here).
- **Reserved for:** Astra 6 (see `docs/backlog/handoffs/active/astra6-A008-A009.md`)
- **Links:** Alex 2026-09-09 — training mode for controlling Jarvis improvement

## Goal
A **Training mode** Alex can open via overlay button and/or slash command (e.g. `/train`). It is the human control surface for improving Jarvis:

### Must show
1. **Open issues / problems** — GitHub open issues + local backlog + neutrals/RLHF “review later” if present  
2. **Improvement context** — pointers that help agents (SESSION, QUEUE, recent journal eval flags, known ADRs)  
3. **Version** — `VERSION` / git describe  
4. **Performance metrics (simple viz)** — e.g. counts: runs today, % thumbs up/neutral/down, eval flags, approve vs deny — charts can be minimal CSS/SVG; no heavy analytics stack  

### Must do (human-in-the-loop)
5. **Select a problem** → optional edit/add comments → **Send to agent to draft an assignment** (pick target: `claude-code` | `cursor` | `human` | future bots). Default = prepare handoff / write `docs/assignments/active/A-NNN-….md` + QUEUE row (reuse desk authoring rules in `docs/assignments/README.md`). **No silent credit spend** — user confirms.  
6. **Work on assignment** button → choose cloud/local coding agent → prepare CONTINUE/NEW_AGENT paste **or** (if a real connector exists later) dispatch with explicit confirm.  
7. **Agent monitor** — overview of agents/work: what’s in_progress (QUEUE + SESSION), optional “queued for agent X when free”. Click through: at minimum open the handoff file / copy prompt / deep-link instructions; if Cursor/Claude chat URLs aren’t available, show clear “paste this in …” UX.  
8. **Assign to existing vs new agent** — when creating work: pick an existing “agent slot” (queue until free **or** send now if idle) **or** create a new slot/handoff. Persist slots in a small local registry (e.g. `docs/assignments/agents.json` or `~/.config/jarvis/agents.toml`) — document format.

### Safety
- Plan/approve style confirms for any mutate (file issue, write assignment, “dispatch”).  
- Never imply an agent was messaged if only a file was written.

## Checklist
- [x] `/train` (and button) enters Training mode UI; Esc/back exits to normal chat
- [x] Register command in A-007 registry
- [x] Panels: issues/backlog, version, basic metrics viz
- [x] Problem → comments → generate assignment (agent picker) with confirm
- [x] Work-on-assignment (agent picker) + monitor list + queue-on-busy / send-if-idle / new agent
- [x] Docs: README human section + ADR; extend assignments README for “training-authored” rows
- [x] Tests for API/UI smoke; PROGRESS; QUEUE → done

## Out of scope
Full autonomous multi-agent orchestration; billing APIs; A-009 human test runner (link placeholders OK).

## Phased delivery OK
Ship read-only dashboard first, then assignment generation, then agent monitor — but don’t mark done until all “Must do” items work at least via prepare-handoff UX.
