# A-011 — Open apps by name (Spotify + fuzzy match)

- **Status:** done
- **Area:** area:actions (+ light `area:brain` for planner/tool wiring)
- **parallel-ok:** YES
- **Allowed paths:** `actions/` (esp. open helpers, catalog), `brain/tools.json`, `brain/system_prompt.md`, `brain/server.py` (tool allowlist / plan examples only if required), `skills/examples/` (optional thin skill), `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/validation/`, `tests/`, `README.md`
- **Forbidden paths:** `overlay/` (owned by A-010/A-007 track); training mode A-008/A-009
- **Blocks / blocked-by:** none — may run parallel with overlay work
- **Converted from:** GitHub #11 / `docs/backlog/bugs/converted/bug-spotify.md`
- **Links:** run_id `4fdd44c0-0202-45ce-affb-d0bca61aa230`; Alex: “spotify” → expected open Spotify; wants general exact/close app-name matching

## Goal
Saying **`spotify`** (and similarly named installed apps) should produce a real open/focus plan, not “not a supported action.”

Prefer a **general** mechanism: resolve user text to an installed app / `.desktop` / Omarchy webapp / binding description via **exact or close-enough name match**, then launch/focus helpers — not a one-off Spotify hardcode (Spotify is the acceptance fixture).

## Checklist
- [x] Reproduce: prompt `spotify` currently plans empty + unsupported reply — confirmed: `open_webapp`'s enum only covers Todoist/Google Calendar/Outlook/WhatsApp; nothing else resolved a bare app name to a tool at all.
- [x] Design resolver: desktop apps + Omarchy webapps + optional binding catalog titles; fuzzy/close match with clear no-match behavior — `.desktop`-only by design (see ADR-023 for why webapps/bindings stay on their existing tools rather than being folded in); exact → unambiguous prefix/substring → single closest fuzzy match; a tie raises listing candidates instead of guessing.
- [x] Wire tool(s) into planner + system prompt examples — `open_app_by_name` in `brain/tools.json`, `tool_argv`/`action_label` in `server.py`, a JSON-plan example, and system-prompt guidance disambiguating it from `open_webapp`.
- [x] Spotify opens/focuses on this host; add 1–2 other name tests if cheap — real live launch + refocus verified (see PROGRESS.md); dry-run also checked against Discord and Google Photos.
- [x] Regression test(s); update FEATURES + validation stub if required — `OpenByNameTest` (9 cases); `docs/FEATURES.md` row + `docs/validation/items/feat-open-by-name.md`.
- [x] PROGRESS + ADR if non-obvious; QUEUE → done; move to `docs/assignments/done/` — ADR-023.

Note: implemented via an isolated `git worktree` on `main` rather than the shared checkout, since another agent had uncommitted A-007 work sitting there on a different branch at the time — see the provenance note in `docs/PROGRESS.md`.

## Out of scope
Overlay lifecycle; training mode; installing Spotify if missing (document prerequisite).

## Notes
Check `omarchy menu keybindings --print` and `~/.local/share/applications/` for Spotify. Keep approve-before-execute.
