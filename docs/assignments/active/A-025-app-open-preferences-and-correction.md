# A-025 — App-open preferences + “no, the other X” correction (Bitwarden #16 part 2)

- **Status:** queued
- **Area:** area:brain (+ light `area:actions`)
- **parallel-ok:** NO (follows A-024)
- **Soft path hints:** `brain/` (prompt/planner + small preference store), `actions/` (close/focus helpers if needed), `tests/`, docs
- **Blocks / blocked-by:** **Blocked by A-024** (needs top-match open + candidate ranking). Closes the rest of #16.
- **Links:** GitHub #16 · Alex: prefer adjusted by request + preference; say “no, the other bitwarden” → close previous, open other, update weights

## Goal
After A-024 opens a default top match, Alex can correct with natural language like **“no, the other bitwarden”** (or “the other one”). Jarvis should:

1. Close/focus-away the just-opened wrong app when safe  
2. Open the next/alternate match  
3. **Update durable preference weights** so future `open bitwarden` prefers what he meant  

Keep plan → approve → execute for mutating steps. Persist preferences locally (simple JSON under repo or XDG config — document choice in ADR).

## Checklist
- [ ] Preference store keyed by query (and optionally desktop ids); read during ranking (integrate with A-024 scorer)
- [ ] Detect correction intents after a recent open_app_by_name (“no, the other …”, “not that one”, …)
- [ ] Plan: close/dismiss previous match if still focused/owned + open alternate; approve before execute
- [ ] Bump weights on successful correction; tests for rank + correction
- [ ] ADR + PROGRESS; close GH #16 / move backlog bug to converted when both A-024+A-025 done; SESSION; QUEUE/INDEX → done

## Out of scope
- Full multi-turn disambiguation UI picker (optional later)
- Password autofill / Bitwarden vault integration
- Changing Training panels

## Notes
Coordinate ranking API with A-024 so preferences aren’t a second ad-hoc sorter. Token discipline: read open_by_name + planner once; then diffs.
