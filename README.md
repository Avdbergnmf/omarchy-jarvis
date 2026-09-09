# Omarchy Jarvis

A local, keyboard-first desktop assistant for Omarchy. Press **SUPER + SHIFT + J**, type a request, and press Enter.

Try:
- “open my planning in a new workspace” — Todoist, Google Calendar, Outlook and WhatsApp together.
- “move this window to scratchpad and open email” — hide the original window in scratchpad and open Outlook. SUPER+S reveals scratchpad again.
- “switch to workspace 1” or “open Outlook”.
- “hello” — chitchat with no actions replies immediately; no approval step, no desktop change.
- “you messed up, …” or `/report …` — file a bug. “I wish it could …” or `/feature …` — request a feature. `/backlog` lists open items. `/dispatch <issue> to <agent>` prepares a handoff prompt. See [self-improve loop](#self-improve-loop-reporting-a-miss-or-a-feature) below.

## Human entry points — see it, control it

Jarvis never runs a mutating action before you say so. Every prompt with a proposed action shows a **plan** first:

1. Type a request and press Enter. If it needs no tools (chitchat), you get a reply immediately.
2. Otherwise the overlay shows the proposed action(s) as a checklist and focuses **Run**.
   - **Run** (or press **Enter** while it's focused) executes the plan. The overlay closes, restores the window you were working in, then runs the action(s), showing a live per-tool step list as each one finishes.
   - **Cancel** (or **Esc**) denies the plan — nothing happens to the desktop.
3. **Esc** always denies any plan still awaiting approval and then closes the overlay, so you can never leave one stuck mid-decision. A plan left untouched for 15 minutes auto-denies on its own.
4. The **Open console** button (bottom-left, always visible) opens the live `jarvis-console` for the current run while it's planning/running, or for the **last** run if you reopen the overlay with nothing new typed yet — it remembers the last run id even across closing and reopening the window.
5. The footer on the right shows the model name, whether Ollama answered a health check, and — if someone set `approval_mode = "off"` — a "⚠ approval off" warning, since that mode skips the Run step entirely and is for debugging only.

Click a **Jarvis notification** to open its floating live console. **SUPER+ALT+COMMA** invokes the latest notification’s same native action. The console uses `tail -F`, including after log rotation; Ctrl+C exits. Action summaries and tool results are logged, not private model reasoning.

### Approval modes

Optional config at `~/.config/jarvis/config.toml` (create it yourself; Jarvis falls back to safe defaults if it's missing):

```toml
approval_mode = "always"     # default: every action plan waits for Run
# approval_mode = "skills_trusted"  # reviewed run_skill recipes auto-run; anything else still waits
# approval_mode = "off"      # debugging only: everything auto-runs, overlay shows a warning
show_notifications = true    # desktop "thought bubble" notifications; the overlay is always the source of truth
```

## Self-improve loop: reporting a miss or a feature

Jarvis files rich records instead of silently fixing itself. It never contacts or spends credits on another agent without you pressing Run on that specific action.

- **Report a miss:** say “you messed up …” (or similar) or type `/report …`. Jarvis gathers a context pack (your last run's plan/approval/log tail, plus a live desktop snapshot only if your text sounds window/binding-related) and asks up to **3** short clarifying questions, one at a time — reply normally, or type **`skip`** any time to file with what it already has.
- **Request a feature:** say “I wish it could …” / “add a feature …” or type `/feature …`. Same flow, feature-flavored questions.
- Either way, the **full draft** (title + body) is shown in the same plan/approval panel as any other action before anything happens — **Run** files a real GitHub issue (`gh issue create`) and writes a local mirror under `docs/backlog/{bugs,features}/`; **Cancel**/**Esc** files nothing.
- **`/backlog`** lists open bugs/features (GitHub + the local `docs/backlog/INDEX.md`).
- **`/dispatch <issue> to <agent>`** (agent = `claude-code` | `cursor` | `human`) writes a paste-ready prompt to `docs/backlog/handoffs/issue-<n>-<agent>.md` — you paste it into that agent's chat yourself. No real-send hook exists; nothing is contacted automatically.

See `docs/backlog/README.md` for the difficulty legend and routing guide, and ADR-016 in `docs/DECISIONS.md` for why this is scripted/deterministic rather than left to the local model.

## Status

M0–M3 implementation and two live model-driven recipe demos pass on this host. M4 has a tested CLI draft/review/confirm stub; overlay confirmation UI and dynamic model discovery are follow-up work. See [progress and evidence](docs/PROGRESS.md), [decisions](docs/DECISIONS.md), and [milestones](docs/MILESTONES.md).

This host uses qwen2.5:3b through localhost Ollama. Native tool calling was unreliable in actual demos; the default is a type-constrained JSON plan with at most one reviewed action or complete recipe. Unsupported requests fail explicitly. Experimental native tool looping remains opt-in with `JARVIS_PLANNER=tools` in the service environment.

## Run and check

From `/home/omarchy/Work/omarchy-jarvis`:

```bash
./scripts/start.sh             # user service; serves 127.0.0.1:7421
./scripts/start.sh --console   # also follow the brain service log
./scripts/stop.sh              # stop Jarvis; leaves Ollama running
./scripts/doctor.sh
./actions/catalog_bindings --refresh --query scratch
./actions/run_binding 'SUPER + M' --dry-run
./actions/run_skill open-planning --dry-run
./console/jarvis-console RUN_ID
```

All actions have `--help`, JSON stdout, nonzero failures and a `--dry-run` preview. Planning deliberately moves matching existing webapp windows to the new workspace. It preserves the default browser profile and reuses the personal Outlook/WhatsApp URLs. It opens login pages if those webapps are not signed in; it does not sign in or send messages.

New-host installation (after reviewing the scripts and confirming prerequisites are present):

```bash
./scripts/install-ollama.sh    # localhost user service + 1.9 GB qwen2.5:3b model
./scripts/install-service.sh
./scripts/install-hotkey.sh    # conflict check, backup, Lua rules, reload validation
```

Requires Python 3, Ollama, Hyprland with Omarchy Lua helpers, Omarchy notifications/launchers, foot, Chromium, curl and a running desktop user session. No pip/npm runtime dependencies. Installers do not install OS packages. Existing Hyprland bindings are backed up beside `~/.config/hypr/bindings.lua`. Remove the marked `BEGIN/END OMARCHY JARVIS` block and reload Hyprland to uninstall the binding; `systemctl --user disable --now jarvis` disables startup.

## Testing

```bash
./scripts/doctor.sh --syntax
python3 -m unittest discover -s tests -v
node tests/overlay.test.cjs
./scripts/verify-host.py       # live overlay, notification and log-rotation tests
./scripts/demo-test.py         # live model demos: opens/moves planning apps and a disposable terminal
```

CI also runs ShellCheck. Live scripts require the desktop bus/socket and cannot run in a workspace-only sandbox. Evidence in `logs/` is private runtime data and excluded from Git. Ordinary account windows are never closed by test cleanup.

## Draft → review → confirm (M4 stub)

Future generated recipes stay in ignored `skills/drafts/`. Drafts and installed custom recipes are **not exposed to the model** in v0. Only the four explicitly requested examples (`open-planning`, `scratch-and-mail`, `report-last-failure`, `add-feature-request`) are executable through `run_skill`; the last two aren't in the model-facing `run_skill` enum in `brain/tools.json`, so they're CLI-only reference examples, not something the model can trigger on its own.

Prepare a directory containing `SKILL.md` and `run.sh`, then:

```bash
./scripts/skill-draft.py propose my-recipe --source /path/to/candidate
./scripts/skill-draft.py review my-recipe
# Show the complete diff to the user and ask for approval of these exact bytes.
./scripts/skill-draft.py install my-recipe --confirm DIGEST_FROM_REVIEW
```

The installer rejects a missing/mismatched digest, changed draft content, symlinked files and overwriting an existing installation. After explicit approval, run the installed recipe directly at `skills/installed/my-recipe/run.sh`. Custom recipes have shell capabilities and must be reviewed. No automatic promotion or model-generated command execution occurs.

## Internals

`overlay/` contains the small web UI; `brain/` serves it and asks local Ollama for a validated plan; `actions/` exposes reviewed argv tools; `skills/examples/` composes those tools. A run returns HTTP 202 with its id and `status=planning`; `GET /v1/runs/<id>` reports `status | plan | steps[] | reply`, moving through `planning → awaiting_approval → running → done|error` (or `denied`, or straight to `done` for chitchat with no actions). Bug/feature reports route through one extra state first: `planning → awaiting_answer → awaiting_approval → …`, driven by `POST /v1/runs/<id>/answer` (see [self-improve loop](#self-improve-loop-reporting-a-miss-or-a-feature) above) — deterministically, never by the model (ADR-016). `POST /v1/runs/<id>/approve` executes a plan still `awaiting_approval`; `POST /v1/runs/<id>/deny` cancels a plan in `awaiting_approval` **or** abandons an in-progress `awaiting_answer` Q&A; `POST /v1/runs/<id>/console` opens the live console for that run id (what the overlay's Open console button calls). Token/origin/host guards protect mutations, one desktop run executes at a time (a plan left awaiting approval, or a Q&A left awaiting an answer, for more than 15 minutes auto-denies and frees that slot), and the HTTP server listens only on loopback.

The binding catalog is live data. Only scratchpad, Outlook/WhatsApp and numbered workspace switches have reviewed execution mappings; unsupported catalog entries are reported explicitly. See ADR-007 for why arbitrary Lua binding callbacks cannot be safely extracted on this host.
