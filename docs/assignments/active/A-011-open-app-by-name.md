# A-011 — Open apps by name (Spotify + fuzzy match)

- **Status:** queued
- **Area:** area:actions (+ light `area:brain` for planner/tool wiring)
- **parallel-ok:** YES
- **Allowed paths:** `actions/` (esp. open helpers, catalog), `brain/tools.json`, `brain/system_prompt.md`, `brain/server.py` (tool allowlist / plan examples only if required), `skills/examples/` (optional thin skill), `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/validation/`, `tests/`, `README.md`
- **Forbidden paths:** `overlay/` (owned by A-010/A-007 track); training mode A-008/A-009
- **Blocks / blocked-by:** none — may run parallel with overlay work. Related: **A-012** (YouTube + no false “opening…” plans).
- **Converted from:** GitHub #11 / `docs/backlog/bugs/converted/bug-spotify.md`
- **Links:** run_id `4fdd44c0-0202-45ce-affb-d0bca61aa230`; Alex: “spotify” → expected open Spotify; wants general exact/close app-name matching

## Goal
Saying **`spotify`** (and similarly named installed apps) should produce a real open/focus plan, not “not a supported action.”

Prefer a **general** mechanism: resolve user text to an installed app / `.desktop` / Omarchy webapp / binding description via **exact or close-enough name match**, then launch/focus helpers — not a one-off Spotify hardcode (Spotify is the acceptance fixture).

## Checklist
- [ ] Reproduce: prompt `spotify` currently plans empty + unsupported reply
- [ ] Design resolver: desktop apps + Omarchy webapps + optional binding catalog titles; fuzzy/close match with clear no-match behavior
- [ ] Wire tool(s) into planner + system prompt examples
- [ ] Spotify opens/focuses on this host; add 1–2 other name tests if cheap
- [ ] Regression test(s); update FEATURES + validation stub if required
- [ ] PROGRESS + ADR if non-obvious; QUEUE → done; move to `docs/assignments/done/`

## Out of scope
Overlay lifecycle; training mode; installing Spotify if missing (document prerequisite).

## Notes
Check `omarchy menu keybindings --print` and `~/.local/share/applications/` for Spotify. Keep approve-before-execute.
