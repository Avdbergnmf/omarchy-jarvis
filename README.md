# Omarchy Jarvis

Local NL → system actions assistant for **Omarchy** (Hyprland). Keyboard-first. Built to be understood by humans and coding agents.

**Status:** scaffolding / handoff for initial implementation. See [docs/ASTRA_HANDOFF.md](docs/ASTRA_HANDOFF.md).

## Quick mental model

```
[Center overlay textbox]
        ↓
[Ollama tool-calling model]
        ↓
[actions/* + skills/*]  ← keybind catalog is live data
        ↓
[hyprctl / omarchy-launch-* / bindings]
        ↓
[Thought notification] --click→ [live console window]
```

## Repo layout

```
overlay/     # center chat UI (v0: local web UI + Hyprland float rules)
brain/       # Ollama client, tool schemas, prompts
actions/     # atomic CLI tools (run_binding, workspace, open_app, …)
skills/      # composed workflows (YAML/JSON metadata + script)
  examples/  # tested starter skills
console/     # live log viewer launcher
scripts/     # install, bind hotkey, doctor
docs/        # DECISIONS, PROGRESS, milestones, handoff
logs/        # runtime logs (gitignored)
```

## Prerequisites (this machine)
- Omarchy / Hyprland 0.56.x
- `ollama` package installed (start with `systemctl --user enable --now ollama` or `ollama serve`)
- `gh` authenticated as `Avdbergnmf`
- Node 26.x (mise) and/or Python 3.14 for tooling
- ~15 GiB RAM available on current VM

## Human entry points (once implemented)
- Hotkey to toggle overlay (propose **SUPER + SHIFT + J** unless taken — verify with `omarchy menu keybindings --print`)
- `./scripts/doctor.sh`
- Click thought bubble → live console for that session

## License / privacy
Private repository. Do not commit secrets, `.env`, or raw notification payloads with tokens.
