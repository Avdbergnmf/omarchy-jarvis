# Omarchy Jarvis

A local, keyboard-first desktop assistant for Omarchy. Press **SUPER + SHIFT + J**, type a request, and press Enter. Escape closes the overlay. The overlay closes before desktop actions and restores the window you were working in.

Try:
- “open my planning in a new workspace” — Todoist, Google Calendar, Outlook and WhatsApp together.
- “move this window to scratchpad and open email” — hide the original window in scratchpad and open Outlook. SUPER+S reveals scratchpad again.
- “switch to workspace 1” or “open Outlook”.

Click a **Jarvis notification** to open its floating live console. **SUPER+ALT+COMMA** invokes the latest notification’s same native action. The console uses `tail -F`, including after log rotation; Ctrl+C exits. Action summaries and tool results are logged, not private model reasoning.

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

Future generated recipes stay in ignored `skills/drafts/`. Drafts and installed custom recipes are **not exposed to the model** in v0. Only the explicitly requested two examples are executable through `run_skill`.

Prepare a directory containing `SKILL.md` and `run.sh`, then:

```bash
./scripts/skill-draft.py propose my-recipe --source /path/to/candidate
./scripts/skill-draft.py review my-recipe
# Show the complete diff to the user and ask for approval of these exact bytes.
./scripts/skill-draft.py install my-recipe --confirm DIGEST_FROM_REVIEW
```

The installer rejects a missing/mismatched digest, changed draft content, symlinked files and overwriting an existing installation. After explicit approval, run the installed recipe directly at `skills/installed/my-recipe/run.sh`. Custom recipes have shell capabilities and must be reviewed. No automatic promotion or model-generated command execution occurs.

## Internals

`overlay/` contains the small web UI; `brain/` serves it and asks local Ollama for a validated plan; `actions/` exposes reviewed argv tools; `skills/examples/` composes those tools. A run returns HTTP 202 with its id, then status is available at `/v1/runs/<id>`. Token/origin/host guards protect mutations, one desktop run executes at a time, and the HTTP server listens only on loopback.

The binding catalog is live data. Only scratchpad, Outlook/WhatsApp and numbered workspace switches have reviewed execution mappings; unsupported catalog entries are reported explicitly. See ADR-007 for why arbitrary Lua binding callbacks cannot be safely extracted on this host.
