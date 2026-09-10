# A-007 — Slash-command autocomplete

- **Status:** done
- **Area:** area:overlay
- **parallel-ok:** NO (serialize before training-mode UI that adds more `/` commands)
- **Allowed paths:** `overlay/`, `brain/server.py` (command registry endpoint only if needed), `docs/PROGRESS.md`, `docs/DECISIONS.md`, `README.md`, `tests/overlay.test.cjs`
- **Forbidden paths:** Full training-mode UI (A-008); agent dispatch; rewriting skills
- **Blocks / blocked-by:** none; **blocks A-008** prefer this first
- **Links:** Alex 2026-09-09 — typing `/` should suggest commands like a good CLI

## Goal
When the overlay input starts with `/` (or the user types `/` mid-empty field), show an **autocomplete list** of known Jarvis slash commands (filter-as-you-type), keyboard navigable (↑/↓, Tab/Enter to complete, Esc to dismiss), similar to Claude Code / Discord / good CLIs.

## Checklist
- [x] Inventory current slash commands (`/report`, `/feature`, `/backlog`, `/dispatch`, …) into a single registry the UI can read (JSON endpoint or static list kept in sync — document)
- [x] Overlay: dropdown/palette under the textbox; filter by prefix; insert completion
- [x] Keep existing command behavior unchanged when submitted
- [x] Tests for filter + keyboard; README one-liner
- [x] PROGRESS + short ADR if non-obvious; QUEUE → done; move to `docs/assignments/done/`

## Out of scope
Training mode panel (A-008). Fuzzy search across natural language (only `/` commands).

## Notes
Ship a registry A-008 can extend when adding `/train` (or similar).
