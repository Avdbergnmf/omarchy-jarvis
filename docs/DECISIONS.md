# Decisions log

Format: **ADR-NNN — Title** (date). Context → Decision → Consequences.

## ADR-001 — Ollama over LM Studio (2026-09-09)
- **Context:** Need a local lightweight tool-calling brain; LM Studio felt like extra GUI fluff.
- **Decision:** Use **Ollama** CLI/API as the only local runtime for v0.
- **Consequences:** Simpler headless ops; pull a small instruct+tools model (≤3B preferred on this VM historically; RAM is now ~15 GiB so 3B–7B is plausible — start 3B, document).

## ADR-002 — Overlay = local web UI in Hyprland float (2026-09-09)
- **Context:** Need something easy to ship and maintain as the *main* input surface.
- **Decision:** Small localhost web UI (HTML/JS or minimal Vite) shown as a centered floating Hyprland window with windowrules; not GTK-first for v0.
- **Consequences:** Fast UI iteration; must add solid `windowrulev2` and a single-instance toggle. Can later swap shell without rewriting tools.

## ADR-003 — Keybinds as data + composed skills (2026-09-09)
- **Context:** Fear of rewriting rules when expanding beyond workspaces.
- **Decision:** Ship `run_binding` fed by `omarchy menu keybindings --print` from day one, plus a few composed tools/skills (`scratch_toggle`, `open_planning`).
- **Consequences:** Model never owns chord strings; catalog stays in sync with Omarchy updates.

## ADR-004 — Confirm before saving skills (2026-09-09)
- **Context:** Cloud/agents may draft automation; user wants control.
- **Decision:** Skill drafts land in `skills/drafts/`; promote to `skills/` only after explicit user OK.
- **Consequences:** UI/CLI must support propose → show diff → confirm.

## ADR-005 — Thought bubbles → live console (2026-09-09)
- **Context:** Debugging agent thoughts; file-only logs are weak.
- **Decision:** Use `omarchy-notification-send` with `--exec` launching a **live** console (tail -F / streaming) for that run id.
- **Consequences:** Each run gets `logs/runs/<id>.log`; console attaches to the stream.

## ADR-006 — Google Calendar vs stock “Calendar” binding (2026-09-09)
- **Context:** User’s planning stack includes Google Calendar. Stock **SUPER + SHIFT + C** opens HEY calendar; **SUPER + CTRL + ALT + D** toggles Omarchy clock shell, not Google Calendar.
- **Decision:** Planning skill opens Google Calendar via `omarchy-launch-or-focus-webapp` / `omarchy-launch-webapp https://calendar.google.com/` — do not call the HEY binding for “planning”.
- **Consequences:** Document clearly so agents don’t “fix” Calendar by simulating SUPER+SHIFT+C.
