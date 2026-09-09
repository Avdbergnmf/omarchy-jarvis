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

## ADR-007 — Host Lua dispatch and reviewed binding map (2026-09-09)
- **Context:** Live Hyprland 0.56 rejects legacy `hyprctl dispatch workspace ...`; `binds` contains opaque `__lua` callbacks, and catalog output has no command column.
- **Decision:** Use the installed Omarchy Lua expressions (`hl.dsp.focus`, `hl.dsp.window.move`, `hl.dsp.workspace.toggle_special`). Refresh the catalog before resolving an exact chord/description; execute reviewed scratch, Outlook, WhatsApp and numbered-workspace mappings only.
- **Consequences:** Unsupported bindings fail explicitly. Never execute arbitrary Lua callback IDs or model-generated shell. Syntax references: installed `/usr/share/omarchy/default/hypr/bindings/tiling.lua` and https://wiki.hypr.land/Configuring/Basics/Window-Rules/.

## ADR-008 — Workspace placement and launcher safety (2026-09-09)
- **Context:** Focus helpers can jump back to another workspace; the packaged focus wrapper constructs a shell command with eval. The current default browser is Brave despite Chromium being present.
- **Decision:** Reuse a matching app window or launch via the argv-safe `omarchy-launch-webapp`; move each verified window address to the lowest unused positive numbered workspace for planning. Read literal personal Outlook/WhatsApp URLs from bindings.lua.
- **Consequences:** Planning consolidates existing app windows. App identity and final workspace are checked; timeouts return partial progress. No new browser profile is used for the account webapps.

## ADR-009 — Strict JSON plans after failed native tool-call demos (2026-09-09)
- **Context:** qwen2.5:3b native tool calling created only a workspace for the planning request and falsely claimed completion. It also composed scratch_move_here with the full scratch-and-mail recipe, duplicating a mutation.
- **Decision:** Default to Ollama `/api/chat` structured output with a strict action-plan schema and concrete recipe examples. Validate the entire plan before executing any action, reject duplicate calls and recipe/action mixtures, and derive completion messages from successful tool results. Keep the bounded native tools loop opt-in (`JARVIS_PLANNER=tools`) for future model evaluation.
- **Consequences:** No regex prompt router or cloud runtime. Plans are local model output, executed through the same reviewed argv CLIs. End-to-end evidence must prove a new workspace and actual full recipe invocation, not trust model replies. See https://docs.ollama.com/capabilities/tool-calling and https://docs.ollama.com/capabilities/structured-outputs.

## ADR-010 — Local HTTP protection and focus capture (2026-09-09)
- **Context:** A localhost action API must not accept requests from unrelated web pages. The overlay steals focus from the user's intended scratchpad target.
- **Decision:** Bind only 127.0.0.1:7421; require a per-process token, exact Host and same Origin for mutations, no CORS, bounded request sizes, one active desktop run. Record the target address before opening the overlay, close the overlay before actions, and restore that target or fail if it disappeared.
- **Consequences:** The isolated Chromium overlay profile is runtime-only under ignored logs; account webapps keep the user's default browser profile. Escape and toggling close only the Jarvis overlay. Notifications carry action summaries/results, never private model reasoning.

## ADR-011 — One typed action per v0 request (2026-09-09)
- **Context:** An unconstrained JSON actions list still made qwen2.5:3b combine a scratch action with its full recipe. A workspace test also emitted a string instead of an integer.
- **Decision:** Constrain structured generation with per-tool argument schemas and at most one action; compound workflows use a complete approved skill. Invalid plans fail before any desktop mutation.
- **Consequences:** Both recipe variants and planning pass model evaluation. Arbitrary multi-action composition is deferred; extend by adding reviewed recipes. Completion text comes from successful actions rather than model claims.

## ADR-012 — M4 CLI stub and explicit approval (2026-09-09)
- **Context:** M0–M3 includes a usable but limited confirm-before-save path.
- **Decision:** A local CLI copies candidates into drafts, shows complete file diffs, and promotes only an explicitly approved SHA-256 digest. Changes invalidate that digest; existing installations cannot be overwritten. Promoted scripts remain CLI-only.
- **Consequences:** The two requested example skills are preapproved by the implementation request. Future recipes require user approval; no model tool can promote drafts. M4 UI/discovery remains open in issue #5.

## ADR-013 — Chromium app identity on repeat launches (2026-09-09)
- **Context:** `--class=jarvis-overlay` was honored on first launch, but Chromium changed subsequent app windows to a URL-derived class even after restarting its dedicated profile. Tests caught tiled duplicate windows.
- **Decision:** Serve the overlay at the unique `/jarvis-overlay` route. Match both the requested class and Chromium's observed `chrome-127.0.0.1__jarvis-overlay-Default` in window rules, focus tracking and single-instance checks. Keep the dedicated profile and disable extensions; do not kill browser processes as part of normal toggling.
- **Consequences:** Actual browser class differs from the handoff's suggested literal on repeat launches. Matching the stable app identity preserves floating, centering, Escape, focus restoration and single-instance behavior without depending on Chromium honoring a flag.
