# A-016 — Training window overhaul (Hyprland window + Problems-first UX)

- **Status:** done
- **Area:** area:overlay (+ light `area:brain` for training problem APIs)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/` (esp. training UI; may add dedicated training HTML/JS/CSS), `brain/training.py`, `brain/server.py` (training endpoints only), `brain/validation.py` if shared problem model, `actions/` only if needed for a `jarvis-training` / Hyprland float launch helper, `scripts/` launch/hotkey, `tests/`, `docs/assignments/`, `docs/SESSION.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/validation/`, `README.md`, `START.md`, `VERSION`
- **Forbidden paths:** Rewriting chat overlay core (plan/approve/execute) beyond a slim “Open Training” entry; claiming A-015’s plan-detail work; silent cloud spend; auto-dispatching coding agents without Alex confirm
- **Blocks / blocked-by:** Blocks **A-017**. Independent of A-015 (can ship in parallel conceptually, but same overlay area → **serial**; do A-016 after or instead of A-015 only if Alex prioritizes — **Alex priority: this assignment**). Prefer completing A-016 Problems phase before polishing A-015 if both claimed by same agent.
- **Links:** Alex 2026-09-10 JARVIS room — Training is a main self-improve surface; current Training view is chaotic; wants separate Hyprland window

## Goal
Training becomes a **dedicated Hyprland window** (not a cramped view stuffed inside the chat overlay). Layout: **top status/stats bar** (keep existing metrics/info, restyle), then **nav buttons** for Training features (Problems, Validate, Assignments/Agents, …).

**First vertical to make excellent: Problems to review.**  
List is **color-coded by source/kind/area**, supports **easy dismiss / check-off / delete**, click opens a **detail pane** (editable fields + **Save**), includes a **priority** field agents respect, and a clear button to **Generate agent assignment** (reuse existing confirmed preview/handoff flow). Patterns that work here should be applied to the other Training sections so the whole window stops feeling like one undifferentiated dump.

Done for Alex means: he can open Training as its own window, triage problems calmly, edit/prioritize, and kick assignment generation without hunting through a wall of UI.

## Checklist
### Shell / chrome
- [x] Launch Training as its own Hyprland float/window (separate from Super+Shift+J chat overlay); document hotkey or entry from chat (“Open Training”)
- [x] Top bar: version/revision, metrics/stats, refresh, period/sample note — stylized, scannable, not colliding with content
- [x] Feature nav buttons (Problems | Validate features | Assignments / Agents | …); only one panel active at a time
- [x] ADR for “Training = separate window + panel navigation”

### Problems to review (primary)
- [x] Problem list: color/badge by source (bad feedback, eval flag, validation fail, backlog, …) and/or area
- [x] Row actions: check-off / dismiss / delete (persist; confirm destructive deletes)
- [x] Click row → detail panel: full context (run id, version, path/url, notes), editable fields, **priority** (e.g. P0–P3 or high/med/low), **Save**
- [x] Detail action: **Generate agent assignment** (or equivalent) → existing confirm-gated prepare/handoff; pass priority + edited fields into the assignment
- [x] Empty / loading / error states that are readable
- [x] Brain/API: persist problem edits, status (open/done/dismissed), priority; don’t lose evidence on refresh

### Carry patterns to other panels
- [x] Apply the same distinguishability (nav + list/detail or clear sections) to Validate and Assignments/Agents enough that they stop feeling like one scroll dump — full redesign of those can be follow-ups if huge, but minimum: same chrome + clear separation
- [x] Tests (overlay/training JS + Python training API); PROGRESS + FEATURES/validation touch if user-visible
- [x] Update SESSION Next action as you go; QUEUE/INDEX → done; move this file to `docs/assignments/done/`

## Out of scope
- Perfecting chat plan parameter readability (that’s **A-015**)
- Auto-sending work to Claude/Codex without paste/confirm
- Full visual redesign of the chat overlay itself
- Building every future Training feature in one pass — Problems-first is the acceptance bar; other panels need structure, not feature-complete parity
- Full **Assignments** create/edit/generate/handoff UX — that is **A-017** (after this). Problems “Generate assignment” may deep-link / preselect into that panel once A-017 exists; until then a minimal confirm-gated prepare is OK

## Notes for the coding agent
- Current Training is `#training-view` inside the chat Chromium `--app` (`overlay/index.html` + `training.js` + `/v1/training`). Target: own window/process or second app URL with Hyprland rules — prefer one brain server, two UIs.
- Keep plan→approve→execute and confirmed file writes for handoffs.
- Token discipline: read training.js/training.py/index once; then diffs.
- Ask Alex only if hotkey binding conflicts; otherwise pick a sensible default (e.g. Super+Shift+T) and document in HOST/customizations note / README.

## Completion evidence — 2026-09-10
- Separate /jarvis-training app, dedicated Chromium profile/class, authenticated Open Training entry and direct launcher; no new binding or service restart during isolated work.
- Three navigation panels, problem badges/list/detail, saved priority/notes/status and original evidence, confirmed local delete tombstones, saved-problem assignment previews.
- 112 Python tests, all UI smoke scenarios, JS syntax, ShellCheck, Doctor syntax and isolated HTTP save/preview/confirm/delete passed.
- Host Hyprland clients/workspaces read successfully. Browser connector unavailable: actual floating-window launch and visual QA remain human validation steps, not claimed as verified.
- Live Doctor retains the documented report-last-failure dry-run failure with missing logs/runs; unrelated skill code unchanged.
- ADR-030; version 0.5.4; feat-train guide updated and unvalidated. A-017/A-018 remain queued.
