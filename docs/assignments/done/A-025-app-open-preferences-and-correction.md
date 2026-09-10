# A-025 — App-open preferences + “no, the other X” correction (Bitwarden #16 part 2)

- **Status:** done
- **Area:** area:brain (+ light `area:actions`)
- **parallel-ok:** NO (follows A-024)
- **Soft path hints:** `brain/` (prompt/planner + small preference store), `actions/` (close/focus helpers if needed), `tests/`, docs
- **Blocks / blocked-by:** **Blocked by A-024** (needs top-match open + candidate ranking). Closes the rest of #16.
- **Links:** GitHub #16 · Alex: prefer adjusted by request + preference; say “no, the other bitwarden” → close previous, open other, update weights · ADR-036

## Goal
After A-024 opens a default top match, Alex can correct with natural language like **“no, the other bitwarden”** (or “the other one”). Jarvis should:

1. Close/focus-away the just-opened wrong app when safe  
2. Open the next/alternate match  
3. **Update durable preference weights** so future `open bitwarden` prefers what he meant  

Keep plan → approve → execute for mutating steps. Persist preferences locally (simple JSON under repo or XDG config — document choice in ADR).

## Checklist
- [x] Preference store keyed by query (and optionally desktop ids); read during ranking (integrate with A-024 scorer)
- [x] Detect correction intents after a recent open_app_by_name (“no, the other …”, “not that one”, …)
- [x] Plan: close/dismiss previous match if still focused/owned + open alternate; approve before execute
- [x] Bump weights on successful correction; tests for rank + correction
- [x] ADR + PROGRESS; close GH #16 / move backlog bug to converted when both A-024+A-025 done; SESSION; QUEUE/INDEX → done

## Resolution (2026-09-10)
XDG JSON at `~/.config/jarvis/app-preferences.json` stores per-query stem weights plus a 15-minute `last_open`. `ranked_apps()` applies those weights inside A-024's existing tiers. Phrases like “no, the other bitwarden” are intercepted before the JSON planner and become one reviewed `correct_app_open` action (close owned window if still present, launch next stem, bump weight). See ADR-036.

## Out of scope
- Full multi-turn disambiguation UI picker (optional later)
- Password autofill / Bitwarden vault integration
- Changing Training panels

## Notes
Coordinate ranking API with A-024 so preferences aren’t a second ad-hoc sorter. Token discipline: read open_by_name + planner once; then diffs.
