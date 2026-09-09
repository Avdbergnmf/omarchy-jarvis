# Omarchy Jarvis

Local assistant for **Omarchy** (Hyprland). Press **Super+Shift+J**, type what you want, press Enter.

You always see a **plan** before anything changes your desktop. **Run** to do it, **Cancel** / **Esc** to abort. **Open console** (always on the overlay) tails the live log for this or the last run.

## Everyday use

| You type… | What happens |
|-----------|----------------|
| `open my planning in a new workspace` | New workspace → Todoist, Google Calendar, Outlook, WhatsApp |
| `move this to scratchpad and open email` | Current window → scratchpad, then Outlook (**Super+S** shows scratchpad) |
| `switch to workspace 1` / `open Outlook` | Single workspace / app actions |
| `hello` | Chat only — no plan, no desktop change |
| `you messed up…` or `/report …` | Bug report flow (questions optional; **skip** allowed) |
| `I wish it could…` or `/feature …` | Feature request flow |
| `/backlog` | List open bugs/features |
| `/dispatch 12 to claude-code` | Writes a paste-ready handoff file (does **not** message anyone) |

After report/feature intake, you still hit **Run** to file the GitHub issue (or Cancel to file nothing).

## Start / stop

```bash
cd ~/Work/omarchy-jarvis
./scripts/start.sh          # Ollama + Jarvis (http://127.0.0.1:7421)
./scripts/start.sh --console
./scripts/stop.sh           # stops Jarvis; leaves Ollama up
./scripts/doctor.sh         # health check
```

Hotkey install (once per machine): `./scripts/install-hotkey.sh`  
First-time Ollama/model/service: `./scripts/install-ollama.sh` then `./scripts/install-service.sh`

Optional config: `~/.config/jarvis/config.toml`

```toml
approval_mode = "always"   # or "skills_trusted" / "off" (debug only)
log_level = "info"         # "debug" for module noise
show_notifications = true
```

## Where things live (for you)

| Thing | Path |
|-------|------|
| This guide | `README.md` |
| Your “next task” queue | [`docs/assignments/QUEUE.md`](docs/assignments/QUEUE.md) |
| Paste prompts for coding agents | [`docs/assignments/prompts/`](docs/assignments/prompts/README.md) |
| Current agent checklist | [`docs/SESSION.md`](docs/SESSION.md) |
| Decisions / progress | [`docs/DECISIONS.md`](docs/DECISIONS.md) · [`docs/PROGRESS.md`](docs/PROGRESS.md) |
| How runs are logged | [`docs/LOGGING.md`](docs/LOGGING.md) |

## Status

Working on this host: overlay + approve flow, planning/scratch recipes, report/feature intake, run journal.  
Still open: **M4** — nicer UI for reviewing/installing new skills (CLI stub exists: `./scripts/skill-draft.py`).

Model: local **qwen2.5:3b** via Ollama. Version: see `VERSION`.

---

**Coding agents:** ignore the rest of this file’s tone — start at [`START.md`](START.md) (invariants also in [`AGENTS.md`](AGENTS.md)).
