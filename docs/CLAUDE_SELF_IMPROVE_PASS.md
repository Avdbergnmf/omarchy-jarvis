# Claude Code — Jarvis self-improve / issue & backlog pass

Work in **`~/Work/omarchy-jarvis`** (canonical; private repo `Avdbergnmf/omarchy-jarvis`). Read `AGENTS.md`, `docs/HOST.md`, `docs/DECISIONS.md` (esp. ADR-014/015 transparency), and the current overlay + `brain/server.py` before coding.

## Product goal
Jarvis should **self-improve through a human-in-the-loop loop**, not silently “fix” everything itself:

1. User can say Jarvis **messed up** (or request a **new feature**).
2. Jarvis files a **rich GitHub issue** (or backlog item) packed with context another smarter agent can act on cold.
3. Jarvis may **ask clarifying questions** (optional — user can skip).
4. Solving is **not always immediate**. Issues/features enter a tracked backlog.
5. User (or Jarvis on command) can later ask **another agent** (Claude Code, Cursor/Astra, Firsty, etc.) to pick up issues — routed by **difficulty** and **where credits exist**.
6. Keep optimizing for **agent handoff quality** and **human readability** (same project ethos as AGENTS.md).

This builds on the existing **plan → approve → execute** control plane. Do not remove transparency.

## Non-goals
- Fully autonomous self-modification of Jarvis without approval
- Auto-spending cloud credits without an explicit user command
- Voice
- Replacing Ollama for the local brain
- Filing issues that contain secrets (tokens, `.env`, email contents, notification payloads with credentials)

## Concepts to implement

### A. Two record types
| Type | When | GitHub | Local |
|------|------|--------|-------|
| **Bug / miss** | “that was wrong”, “you messed up”, failed run report | Issue labeled `bug`, `jarvis-reported` | `docs/backlog/bugs/…` mirror optional |
| **Feature** | “I wish it could…”, “add …” | Issue labeled `enhancement`, `backlog` | `docs/backlog/features/<slug>.md` **required** |

Every record must be written so a **cold agent** can start without the chat history.

### B. Mandatory context pack (every issue/feature body)
Auto-attach as much as possible (redact secrets):

- User’s complaint / request (verbatim)
- Jarvis’s last plan (tools + args) and approval choice (ran / denied / n/a)
- `run_id` + path to `logs/runs/<id>.log` (summarize last N tool steps; do not dump megabytes into GitHub — link/path + excerpt)
- Host facts: Omarchy/Hyprland, relevant `hyprctl clients/workspaces` snapshot if window-related
- Binding catalog hits if relevant (`catalog_bindings` query)
- Expected vs actual behavior
- Suspected layer: overlay | brain/planner | action CLI | skill | Hyprland/Omarchy | docs
- Acceptance criteria for a fix (“done when…”)
- Suggested milestone (M4/M5/new) and rough difficulty: `S` (docs/UI copy), `M` (action/skill), `L` (architecture / multi-agent)
- Recommended solver: `local-jarvis` | `claude-code` | `cursor-agent` | `human` + one-line why (credits/difficulty)

Use a fixed markdown template checked into `docs/templates/ISSUE_BUG.md` and `docs/templates/ISSUE_FEATURE.md`.

### C. Conversational flow in the overlay
New intents (natural language + optional slash commands):

- `/report …` or “that was wrong / you messed up …” → start **bug intake**
- `/feature …` or “add a feature / I want …” → start **feature intake**
- `/backlog` → summarize open bugs/features (from `gh issue list` + local backlog index)
- `/dispatch <issue> to <agent>` → **prepare** a handoff prompt (and optionally open/copy it); do **not** spend other agents’ credits unless user explicitly confirms in the approve UI

Intake states:
1. Capture seed text + auto context pack from last run (if any).
2. Ask **up to 3** clarifying questions (one at a time or as a short list). User can reply **`skip`** to file with what we have.
3. Show the **draft issue/feature** in the plan/approval UI (transparency): title, labels, body preview.
4. User hits **Run** (= file it via `gh`) or **Cancel**.
5. On success: show issue URL + local backlog path; offer “copy handoff prompt for Claude Code”.

### D. Local backlog (human + agent readable)
```
docs/backlog/
  README.md          # how to triage; difficulty legend; agent routing guide
  INDEX.md           # auto or script-maintained table: id | type | title | difficulty | status | gh issue
  bugs/
  features/
  handoffs/          # generated prompts for other agents, one file per dispatch
docs/templates/
  ISSUE_BUG.md
  ISSUE_FEATURE.md
  HANDOFF_AGENT.md
```

`docs/backlog/README.md` must explain: not every issue is insta-solved; credits are scarce; prefer filing well → batch-fix on the agent that has budget.

### E. Contacting other agents (careful)
Jarvis **does not** silently wake paid agents. Implement:

1. **`prepare_handoff`** action: given issue number, write `docs/backlog/handoffs/issue-<n>-<agent>.md` using `HANDOFF_AGENT.md` (includes clone path, branch suggestion, acceptance criteria, files to read, forbidden actions).
2. Overlay / reply shows the path and a one-liner the user can paste into Claude Code / Cursor.
3. Optional later hook: if a Grok Bot / Cursor agent API exists on this machine, gate it behind explicit approve + config `dispatch.enabled = false` by default in `~/.config/jarvis/config.toml`.
4. Routing heuristic (document in backlog README; encode as suggestions only):
   - `S` → local docs fix or user
   - `M` → Claude Code Sonnet on this repo
   - `L` / cross-cutting → Opus or Cursor cloud agent when credits allow
   - Never imply Firsty/other chat agents were messaged unless the user commanded a real send and a connector exists

### F. Tools / actions to add
CLI + tool schemas (same pattern as existing `actions/`):

- `report_bug` (draft only vs `--submit` after approval)
- `report_feature`
- `list_backlog`
- `prepare_handoff --issue N --agent claude-code|cursor|…`
- Prefer wrapping `gh issue create/list/view` with the logged-in `Avdbergnmf` account; repo `Avdbergnmf/omarchy-jarvis`

Wire into `brain/tools.json` + system prompt: for complaints/features, prefer these tools / a dedicated skill over random shell.

### G. Skill examples
Add reviewed example skills (and test them):

- `skills/examples/report-last-failure/` — uses last `run_id` context → draft bug
- `skills/examples/add-feature-request/` — feature intake → draft

Still subject to plan/approve before `gh issue create`.

## Implementation constraints
- Keep **approve-before-mutate**: filing a GitHub issue counts as mutate → must go through plan/Run.
- Reuse overlay plan checklist + Open console.
- Extend overlay slightly if needed for Q&A turns (short question + answer field) without abandoning the control plane.
- Redact obvious secrets (regex for `sk-`, `ghp_`, `gho_`, bearer tokens).
- Update `docs/DECISIONS.md` (new ADR), `docs/PROGRESS.md`, `README.md`, `AGENTS.md` (self-improve loop).
- Push to GitHub; keep CI/doctor green; add unit tests for template fill + redaction + intake state machine.
- Canonical path remains `~/Work/omarchy-jarvis`.

## Acceptance criteria
1. User can report a miss from the overlay; after optional questions (or skip), **Run** creates a GitHub issue with the full context template; **Cancel** creates nothing.
2. User can file a feature the same way; a `docs/backlog/features/*.md` file exists and INDEX updates.
3. `/backlog` (or equivalent prompt) lists open items usefully.
4. `prepare_handoff` writes a paste-ready prompt another agent can use without this chat.
5. No other agent is contacted/charged unless user explicitly approved a dispatch path that actually sends (default is prepare-only).
6. `./scripts/doctor.sh` passes; tests updated; PROGRESS records a live demo (issue URL of a test issue is OK — close/label `jarvis-smoke` if needed).

## Suggested build order
1. Templates + `docs/backlog/` skeleton + ADR
2. Actions wrapping `gh` + redaction
3. Brain intents / skill + system prompt
4. Overlay Q&A + draft preview in approve UI
5. Handoff generator
6. Tests, doctor, demo, commit/PR

## One-liner when done
Tell Alex how to say “you messed up”, how skip/questions work, where backlog lives, and how to paste a handoff into Claude Code.
