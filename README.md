# Omarchy Jarvis

Local assistant for **Omarchy** (Hyprland). Press **Super+Shift+J**, type what you want, press Enter.

With the default `approval_mode = "always"`, you see a **plan** before anything changes your desktop. **Run** to do it, **Cancel** / **Esc** to abort. The overlay stays open through execution so you can watch it happen — dismiss it with **Esc** or by pressing the hotkey again. There is always exactly **one** Jarvis: pressing the hotkey again either brings the existing overlay to you or dismisses it, never opens a second one. Closing it and reopening it (even later) picks up right where you left off — same reply, same feedback controls — not a blank box. **Open console** (always on the overlay) tails the live log for this or the last run. Once a run finishes, rate it **👍 / 🤔 / 👎** next to the prompt it applies to — good is just logged, 🤔 goes on a local "review later" list (no GitHub issue), and 👎 jumps straight into the bug-report questions with this run's own context already attached.

## Everyday use

| You type… | What happens |
|-----------|----------------|
| `open my planning in a new workspace` | New workspace → Todoist, Google Calendar, Outlook, WhatsApp |
| `move this to scratchpad and open email` | Current window → scratchpad, then Outlook (**Super+S** shows scratchpad) |
| `switch to workspace 1` / `open Outlook` | Single workspace / app actions |
| `open spotify` | Opens (or focuses, if already running) any installed app by name |
| `open youtube` | Opens the YouTube webapp — works even without a local YouTube app installed |
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

`logs/` is never committed. Old run/debug files and journal archives self-trim by file
count; CURRENT and the human feedback list have no byte cap (see [logging](docs/LOGGING.md)). run `./scripts/clean-temp-logs.sh` any time — before
a commit, say — to also clear one-off scratch files (`--profile` additionally clears
the overlay's Chromium cache, skipped automatically if the overlay is currently open).

## Status

Working on this host: overlay + approve flow, planning/scratch recipes, report/feature intake, run journal.  
Still open: **M4** — nicer UI for reviewing/installing new skills (CLI stub exists: `./scripts/skill-draft.py`).

Model: local **qwen2.5:3b** via Ollama. Version: see `VERSION`.

---

**Coding agents:** ignore the rest of this file’s tone — start at [`START.md`](START.md) (invariants also in [`AGENTS.md`](AGENTS.md)).

Type `/` for command suggestions. Use ↑/↓ to select, Tab/Enter to complete, then Enter to submit. Esc dismisses suggestions first. The single UI registry is `overlay/commands.js`; add deterministic commands there when extending the server.

## Training mode

Choose **Training** or type `/train` to review issues, local backlog, neutral feedback and
journal flags. Refresh loads evidence on demand; run polling stays unchanged. Metrics cover
today UTC in the current journal and explicitly identify a bounded sample when needed.
Back to chat / Esc leaves Training without cancelling the chat run.

Select a problem, add comments/acceptance, choose an area and agent slot, then **Preview
assignment & handoff**. Review the full file contents and choose **Confirm — write these
files**. Cancel writes nothing. Work on an existing assignment similarly prepares a
NEW_AGENT or CONTINUE prompt. Copy/paste it into the target chat yourself.

The agent monitor combines QUEUE/SESSION with local slots; it cannot detect live chats.
Mark a slot busy/idle through a confirmation preview. Prepare now rejects busy slots;
Queue until free records intent locally and does not send automatically. Once free,
select the queued assignment and prepare its handoff. New slots are created with their
first confirmed handoff. No connector sends messages or spends credits.

### Validate features
In Training, **Validate features** lists unvalidated and failed guides. Select one, perform
the steps, and check them off. Verify is enabled after all steps; Fail needs a description of
what actually happened. Add the tested run id if useful. Review and confirm to record the
result with date, version and notes. A changed guide requires another human test.

A saved failure offers **Draft bug report in chat** with its expected/actual evidence.
Complete or skip Q&A, review the issue draft, then choose Run to file or Cancel to stop.
Verification never closes issues, and neither automated tests nor agents mark features
human-validated. Include previously validated features to inspect or repeat an earlier test.
