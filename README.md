# Omarchy Jarvis

Local assistant for **Omarchy** (Hyprland). Press **Super+Shift+J**, type what you want, press Enter.

With the default `approval_mode = "always"`, you see a **plan** before anything changes your desktop: each proposed action is a scannable card — a friendly title (what/where), extra parameters as small chips (hover for the full value if truncated), and for a skill recipe, a description of what it actually does. **Run** to do it, **Cancel** / **Esc** to abort. The overlay stays open through execution so you can watch it happen — dismiss it with **Esc** or by pressing the hotkey again. There is always exactly **one** Jarvis: pressing the hotkey again either brings the existing overlay to you or dismisses it, never opens a second one. Closing it and reopening it (even later) picks up right where you left off — same reply, same feedback controls — not a blank box. **Open console** (always on the overlay) tails the live log for this or the last run. Once a run finishes, rate it **👍 / 🤔 / 👎** next to the prompt it applies to — good is just logged, 🤔 goes on a local "review later" list (no GitHub issue), and 👎 jumps straight into the bug-report questions with this run's own context already attached.

## Everyday use

| You type… | What happens |
|-----------|----------------|
| `open my planning in a new workspace` | New workspace → Todoist, Google Calendar, Outlook, WhatsApp |
| `move this to scratchpad and open email` | Current window → scratchpad, then Outlook (**Super+S** shows scratchpad) |
| `switch to workspace 1` / `open Outlook` | Single workspace / app actions |
| `open spotify` | Opens (or focuses, if already running) any installed app by name |
| `no, the other bitwarden` | After a recent open: closes that window if still owned, opens the next match, and remembers the preference |
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
./scripts/restart.sh        # reload brain after code changes (then re-open overlay)
./scripts/stop.sh           # stops Jarvis; leaves Ollama up
./scripts/doctor.sh         # health check
```


## Reload after pulling code

Assignment / docs-only changes on disk need **no** restart.

After **brain** or **overlay** code changes (or a VERSION bump), run:

```bash
cd ~/Work/omarchy-jarvis && ./scripts/restart.sh
```

Then open the overlay again (`Super+Shift+J`) or Training so the window loads fresh JS/HTML. Equivalent: `systemctl --user restart jarvis.service`.


Hotkey install (once per machine): `./scripts/install-hotkey.sh`  
First-time Ollama/model/service: `./scripts/install-ollama.sh` then `./scripts/install-service.sh`

Optional config: `~/.config/jarvis/config.toml`

```toml
approval_mode = "always"   # or "skills_trusted" / "off" (debug only)
log_level = "info"         # "debug" for module noise
show_notifications = true
latency_profiler = true    # false/off/0 disables A-033 traces; see docs/LATENCY.md
latency_budget_p50_ms = 0  # 0/absent = unset; placeholders only, never a merge gate
latency_budget_p90_ms = 0
```

App-open preference weights (which Bitwarden to prefer after “the other one”) live in `~/.config/jarvis/app-preferences.json`, created on first correction. Not repo-tracked.

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

Choose **Open Training** in chat or type `/train` to open a separate, resizable Hyprland
floating window. Reopening focuses that window; chat and its pending plan remain intact.
With Jarvis already running, `./scripts/open-training.py` opens the same window directly.
No new global hotkey is installed. Problems, Validate features, Assignments, and Agent manager
have separate navigation panels beneath the version and metric cards.

Refresh imports issues, backlog, bad/neutral feedback, journal flags and failed human tests
on demand. Metrics cover today UTC in the current journal and label bounded samples;
retained problems can be older. Original evidence is bounded/redacted and retained locally
in ignored `logs/training/problems.json`, together with edits, priority and status.
Select a problem to edit its title, notes, area and P0–P3 priority, then **Save**. **Done** and
**Dismiss** persist locally; filter those statuses to reopen an item. **Delete…** previews
a local deletion for confirmation and keeps a tombstone to prevent re-import. It does not
close GitHub issues or delete source evidence. Refresh keeps unsaved detail edits; use
**Discard edits / reload** to abandon them or recover from a stale-edit conflict.

**Save & generate agent assignment** saves the problem and opens a linked new draft in
**Assignments**. The form inherits its title, notes, area and priority; the original evidence
is included when saved. You can edit the draft independently of the original problem.
**New assignment** starts a manual draft with an optional linked problem.

The Assignments queue shows status, area, priority and parallel policy. Select a row to
inspect the full brief and edit title, goal, checklist, comments, scope and priority.
Queued/blocked briefs are editable; owned or closed work is read-only. Status and parallel
policy stay with the owning workflow. **Preview Save / Add** shows exact changes to the
brief, QUEUE, INDEX and a preparation note in SESSION. Only **Confirm** writes them, and it
rejects intervening source or ownership changes. Unknown sections and ownership notes are
preserved. Refresh keeps unsaved edits; **Discard edits / reload** fetches current disk state.

**Generate draft** uses the configured downloaded local Ollama model with the selected scope
and problem context. It writes nothing, and rejects remote/cloud model metadata. Review the
result in the form before saving. Alternatively choose **On-machine coding agent** to get a
prompt to copy yourself. Your selected agent may use paid services; Jarvis does not launch
or contact it. Paste its JSON response into the import box to fill the draft, then review it.

After a confirmed save, **Hand off to agent** opens **Agent manager** with that assignment
selected. Choose an existing tile or **+ New agent**; cold-start versus continue is automatic,
with a manual override under Advanced. Confirm to save the reviewable handoff. Cancelling creates no files;
it does not undo an earlier problem or assignment Save.

The agent manager combines the canonical assignment state with local slots; it cannot detect live chats.
Each slot is a color-coded tile (idle, working, waiting, blocked or error) with its ordered
personal assignment queue directly underneath. Click one for its overview (status, current/queued assignments,
last handoff) and, for a Claude Code or Cursor/Codex slot, **Open agent window**: a real,
individually focusable terminal window running that agent's own CLI, never a hidden
background job. A second click focuses the same window instead of opening another one.
Human slots have no automated window — those are worked in your own terminal. Mark a slot
busy/idle through a confirmation preview. **Available work** reuses Blocked-by, area and
parallel claimability; it does not invent a second scheduler. Start visibly now rejects busy
slots and opens the agent window after confirmation. Personal queues retain multiple reviewed
handoffs in FIFO order. While Agent manager is open, completion on `origin/main` advances the
next claimable personal item, opens/focuses the visible window and displays its prompt. Jarvis
never pastes or submits that prompt, and no connector silently spends credits.

### Validate features
In Training, **Validate features** lists unvalidated and failed guides, each showing its last
report (date, version, outcome, notes) right in the list — not only after you click in. Select
one, perform the steps, and check them off. A step marked **Run this step** is mechanical
(type a prompt, press Enter); clicking it submits that exact prompt through the same chat send
a human uses, shows the reply/status right there, and fills in the run id for you — Jarvis
never auto-approves or auto-denies anything, so a step that reaches an approval prompt still
waits for you in chat. The chat overlay's footer now shows the current run's id (click to
copy) so you're never asked to attach evidence you were never shown. Verify is enabled after
all steps; Fail needs a description of what actually happened. Review and confirm to record
the result with date, version and notes — the guide closes back to the list, where the update
is immediately visible. A changed guide requires another human test.

A saved failure offers **Draft bug report in chat** with its expected/actual evidence.
Complete or skip Q&A, review the issue draft, then choose Run to file or Cancel to stop.
Verification never closes issues, and neither automated tests nor agents mark features
human-validated. Include previously validated features to inspect or repeat an earlier test.
