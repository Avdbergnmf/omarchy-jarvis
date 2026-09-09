# Astra 6 — build brief: Omarchy Jarvis v0

**Owner:** Alex (Avdbergnmf) on Omarchy.  
**Author of brief:** Firsty (planning agent).  
**Your job:** Implement M0→M3 as completely and tested as practical; leave M4 skill-confirm path stubbed but usable; keep docs current.

Read first: `../AGENTS.md`, `HOST.md`, `DECISIONS.md`, `MILESTONES.md`.

---

## 1. Product (what “done” feels like)

User hits a hotkey → **centered chat overlay** (single textbox) → types e.g.  
“move this window to the scratchpad and open Outlook”  
→ small Ollama model plans tool calls → actions run → **thought bubbles** top-right via Omarchy notifications → clicking one opens a **live console** streaming that run’s log.

Second demo:  
“open my planning on a new workspace”  
→ new workspace + Todoist + Google Calendar + Outlook + WhatsApp.

Voice: **out of scope**. Skill auto-save: **ask first**.

---

## 2. Target architecture

```
overlay/          static or tiny Vite app on 127.0.0.1:<port>
brain/            Python or Node service: prompt + Ollama /api/chat tools loop
actions/          argv CLIs, JSON stdout, exit codes
skills/examples/  metadata.toml/yaml + run.sh
console/          jarvis-console <run-id> → foot/floating terminal tail -F logs/runs/<id>.log
scripts/          doctor, install-hotkey, start, stop
```

**IPC suggestion (keep simple):** overlay POSTs `{prompt}` to `http://127.0.0.1:7421/v1/run`; brain writes `logs/runs/<uuid>.log`, emits notifications, returns `{run_id, reply}`.

**Single-instance overlay:** Hyprland window class `jarvis-overlay`; toggle script focuses or launches; Escape closes.

---

## 3. Stack choices (do not bikeshed unless blocked)

| Piece | Choice | Why on this host |
|-------|--------|------------------|
| LLM runtime | **Ollama** (already installed) | User choice; enable user service |
| Model | Start `qwen2.5:3b` or `llama3.2:3b` (tool-capable). If tools flaky, try `qwen2.5-coder:3b` / document. | ~15 GiB RAM OK for 3B |
| Overlay | Local web UI + Chromium `--app=http://127.0.0.1:…` OR omarchy webapp-style window | Maintainable; matches ADR-002 |
| Actions | Bash or Python CLIs | Easy for agents to extend |
| Notifications | `omarchy-notification-send` + `--exec` | Native Omarchy; clickable |
| Console | `omarchy-launch-floating-terminal-with-presentation` or foot floating + `tail -F` | Live output requirement |
| Repo | This private GitHub repo | Versioning + milestones |

---

## 4. Exact folder tree to implement

```
omarchy-jarvis/
  AGENTS.md
  README.md
  .gitignore
  docs/
    ASTRA_HANDOFF.md   # this file
    HOST.md
    DECISIONS.md
    PROGRESS.md
    MILESTONES.md
  overlay/             # UI
  brain/
    server.py|mjs      # main loop
    tools.json         # OpenAI-compatible tool schemas for Ollama
    system_prompt.md
  actions/
    catalog_bindings   # refresh + query
    run_binding        # execute by description or chord
    workspace_new
    workspace_switch
    scratch_toggle
    scratch_move_here
    open_webapp
    notify_thought
  skills/
    examples/
      open-planning/
        SKILL.md
        run.sh
      scratch-and-mail/
        SKILL.md
        run.sh
    drafts/            # gitignored or empty
  console/
    jarvis-console
  scripts/
    doctor.sh
    start.sh
    stop.sh
    install-hotkey.sh
  logs/                # gitignored
  .github/
    ISSUE_TEMPLATE/
    workflows/ci.yml   # doctor syntax / shellcheck if feasible
```

---

## 5. Tools the model must have (M1–M3)

Implement as real CLIs first; wire JSON schemas second. Each tool: `--help`, dry-run flag where destructive, machine-readable JSON on stdout.

1. **`catalog_bindings`**  
   - Source of truth: `omarchy menu keybindings --print`  
   - Cache to `logs/bindings.cache.txt`; refresh on start and on demand.  
   - Query: substring match on description or chord.

2. **`run_binding`**  
   - Input: binding description **or** chord string (e.g. `SUPER + S`).  
   - Prefer dispatching the **same command Omarchy would run**, not fake key events (more reliable).  
   - Parse strategy: for known patterns call `hyprctl dispatch …` / `omarchy-launch-*`; for opaque commands, run the command column if you can extract it — if not extractable from `--print`, maintain a small map for critical ones and document gaps in DECISIONS.  
   - Minimum must-work: `SUPER + S` (toggle scratchpad), `SUPER + ALT + S` (move to scratch), `SUPER + M` (Outlook), `SUPER + N` (WhatsApp), workspace number switches.

3. **`workspace_new` / `workspace_switch`**  
   - Use `hyprctl workspaces` / `dispatch workspace`. For “new”, switch to the lowest unused numbered workspace or create via Hyprland conventions used by Omarchy (document actual approach).

4. **`scratch_toggle` / `scratch_move_here`**  
   - `hyprctl dispatch togglespecialworkspace scratchpad`  
   - `hyprctl dispatch movetoworkspacesilent special:scratchpad`

5. **`open_webapp`**  
   - Args: name + url → `omarchy-launch-or-focus-webapp` when possible else `omarchy-launch-webapp`.

6. **`notify_thought`**  
   - Wraps `omarchy-notification-send --app-name jarvis … --exec <repo>/console/jarvis-console <run-id>`

7. **`run_skill`**  
   - Executes `skills/**/run.sh` by id; used for open-planning etc.

---

## 6. Example skills (must be tested on this machine)

### `skills/examples/scratch-and-mail/`
- **Utterance:** “move current window to scratchpad and open email”  
- **Steps:** scratch_move_here → open Outlook (SUPER+M / webapp).  
- **Test:** focused window disappears to special:scratchpad; Outlook webapp focuses/opens.

### `skills/examples/open-planning/`
- **Utterance:** “open my planning in a new workspace”  
- **Steps:** workspace_new → open Todoist, Google Calendar (`https://calendar.google.com/`), Outlook, WhatsApp (small delays OK).  
- **Do not** use SUPER+SHIFT+C (HEY).  
- **Test:** `hyprctl clients` shows the four apps on the target workspace.

Ship `SKILL.md` with: name, trigger examples, tools used, safety notes — so future agents copy the pattern.

---

## 7. Overlay UX (M0)

- Centered, ~520×120 or similar, textbox + subtle status (“thinking…”).  
- Submit on Enter; Escape closes.  
- No chat history required in v0 (optional one-line last reply).  
- Hyprland rules: float, center, pin optional, animation minimal.  
- Hotkey install via `~/.config/hypr/bindings.lua` using `o.bind(...)` (match existing file style). Propose **SUPER + SHIFT + J** after verifying free in `omarchy menu keybindings --print`.

---

## 8. Live console (hard requirement)

- Each run: `logs/runs/<uuid>.log` with timestamped lines (thoughts, tool calls, stdout/stderr).  
- `console/jarvis-console <uuid>` opens floating terminal and `tail -F` that file (follow until Ctrl+C).  
- Notification click must launch that helper via `--exec`.  
- Also support `scripts/start.sh` attaching an optional “Jarvis brain” log.

---

## 9. Brain / prompting

System prompt must state:
- You are Jarvis on Omarchy; prefer tools over guessing.
- Keybind chords change; use catalog/run_binding.
- Planning apps = Todoist + Google Calendar + Outlook + WhatsApp.
- Never invent destructive commands; never exfiltrate secrets.
- Short user-facing replies; detailed trace goes to the log/notifications.

Use Ollama tool calling; if the chosen model’s tool support is weak, fall back to a strict JSON action plan parser and document in DECISIONS.md.

---

## 10. Private GitHub hygiene

Repo should already exist as **private** under Avdbergnmf. You will:
1. Create GitHub **Milestones** matching `docs/MILESTONES.md`.  
2. Open issues for M0–M4 workstreams; close with PRs.  
3. Tag releases when exit criteria met.  
4. Keep `docs/PROGRESS.md` updated every working session.  
5. CI: at least `shellcheck` on scripts + `bash -n` / compile check; no secrets.

Suggested first commits after implementation land: `feat(m0): overlay+ollama+console`, `feat(m1): bindings tools`, etc.

---

## 11. doctor.sh checks

- ollama reachable (`ollama list`)  
- model pulled  
- hyprctl OK  
- bindings catalog non-empty  
- overlay port free/listening when started  
- example skills `--dry-run` OK  
- notification send smoke (optional)

---

## 12. Implementation order (do not skip)

1. `scripts/doctor.sh` + start ollama + pull model  
2. actions CLIs + manual tests  
3. example skills run.sh + manual tests  
4. console + notification click  
5. brain loop wiring tools  
6. overlay + hotkey  
7. end-to-end demos for the two example utterances  
8. GitHub milestones/issues/tags + PROGRESS/DECISIONS updates  

---

## 13. Pitfalls specific to this host

- Stock “Calendar” binding ≠ Google Calendar (ADR-006).  
- `ollama` installed but may need `systemctl --user enable --now ollama`.  
- Do not add mako/dunst; Omarchy notifications already work.  
- Prefer launching real Omarchy commands over `ydotool`/fake keys.  
- Virtio/GPU: keep overlay light (no Cesium-level WebGL).  
- User’s Outlook/WhatsApp URLs are already customized in bindings.lua — reuse them.  
- Todoist has a desktop entry but no Super hotkey yet — launching via desktop/webapp is fine; optional follow-up binding is nice-to-have, ask before adding.

---

## 14. Definition of done for your pass

- [ ] Private repo documented and milestones created  
- [ ] M0–M3 exit criteria in MILESTONES.md met on this machine  
- [ ] Two example skills tested; evidence noted in PROGRESS.md  
- [ ] Live console from notification click works  
- [ ] User confirm path for new skills at least stubbed (`skills/drafts/` + README instructions)  
- [ ] `./scripts/doctor.sh` exits 0  
- [ ] Hotkey toggles overlay  

When blocked, write the blocker into PROGRESS.md and DECISIONS.md rather than silently changing architecture.

---

## 15. One-liner for Alex after you’re done

Tell him: hotkey, example prompts that work, how to read the console, and where DECISIONS/PROGRESS live.
