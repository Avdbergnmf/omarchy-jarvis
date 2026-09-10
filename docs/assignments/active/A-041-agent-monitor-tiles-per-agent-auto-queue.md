# A-041 — Agent Monitor tiles + per-agent auto-queue redesign

- **Status:** queued
- **Area:** area:overlay
- **parallel-ok:** YES
- **Recommended depth:** high
- **Allowed paths (optional soft hint):** `overlay/agents.js`, `overlay/training.html`, `overlay/training.css`, `brain/training.py`, `brain/server.py` (slot registry / queue advancement), `logs/training/agents.json`, `tests/`
- **Forbidden paths (optional soft hint):** none
- **Blocked-by:** none
- **Gate:** training-dispatch
- **Links:** Alex 2026-09-10 product intent — Agent Manager redesign · unblocks Training-driven dispatch workflow · builds on A-018/A-036

## Goal
Make the Agent Manager (Training → Agents) actually useful for dispatching and monitoring work. Alex finds the current implementation (A-018/A-036: slot tiles, delivery modes, depth, local queue that only stores handoffs) still not useful because the tiles don't show what agents are doing at a glance, available work isn't surfaced clearly, and the "queue" doesn't auto-run anything.

Done means Alex can:
- See at a glance which agents are idle / working / waiting / blocked / error (color-coded tiles)
- See each agent's personal assignment queue (ordered A-### list with status) directly under its tile
- Pick claimable assignments from a clear "available work" panel
- Assign multiple future assignments to one agent that auto-start when that agent finishes and the next item becomes claimable
- Have the system automatically choose NEW_AGENT vs CONTINUE based on slot state (no manual template choice except in dev/advanced cases)

## Checklist

### Layout & glanceability
- [ ] Agent tiles are the **main feature**: horizontal stack at the **top** of the panel, interactive
- [ ] Each tile is **color-coded** by agent status: idle / working / waiting / blocked / error (document the status labels/colors clearly)
- [ ] Under each tile: that agent's **personal assignment queue** (ordered list of A-### with status), neatly visualized
- [ ] Tile click → detail view with tile-specific actions (as today, but adapted to new layout)

### Available work panel
- [ ] Clear panel/section showing **currently claimable assignments**
- [ ] Use existing claimability rules from `assignment-status.sh` / Training's `unmet_blocked_by` (Blocked-by / parallel-ok / area disjointness — do NOT invent a second claimability model)
- [ ] From available work: pick assignment → pick existing bot tile (optionally tweak properties) OR hit **+** to create new agent tile with properties
- [ ] Selected assignment can be enqueued to agent's personal queue or started immediately

### Auto cold-start vs Continue
- [ ] System chooses NEW_AGENT vs CONTINUE automatically from slot state (no window / new slot → cold start; existing busy/idle session with prior handoff → continue)
- [ ] Hide template choice behind **dev/advanced foldout** for rare manual overrides only
- [ ] Template selection UI must not be prominent in normal workflow

### Per-agent queue with auto-advance
- [ ] Each agent tile can have **multiple** future assignments queued to it (not just one handoff saved locally)
- [ ] When agent finishes current work (detect via QUEUE/INDEX/claim change on `origin/main` — align with A-039's claim protocol), Jarvis:
  - Refreshes claimability (re-check `Blocked-by`/area/parallel rules)
  - Picks the next item in **that agent's** queue that is now free/claimable
  - **Auto-starts** it: open/focus visible window + prepare handoff (see safety note)
- [ ] Queue UI lives directly under the agent tile (not in a separate panel)
- [ ] Queue shows assignment id, title, status (queued-to-this-agent / blocked-waiting / ready-next)

### Safety / policy (must be explicit — see ADR-032/036/039)
- [ ] **Visible window path:** auto-advance must keep a visible window (no hidden background agents)
- [ ] **No silent spend:** Jarvis must not silently spend cloud credits or pretend a hidden agent is running
- [ ] **"Send" meaning:** visible window + reviewable handoff the user can see
- [ ] **Open design choice (document in brief + add ADR stub checklist item):** whether auto-advance:
  - Requires one human paste into the visible window (safe default: auto-open/focus + auto-prepare, but human pastes), OR
  - May auto-submit into an already-open agent window (system-driven continue — Alex prefers this, but do NOT weaken no-hidden-agent / no-silent-spend without clear ADR + Alex confirmation at implement time)
- [ ] **Prefer:** auto-open/focus + auto-prepare next handoff; paste/submit automation only if already supported safely for that backend
- [ ] Document this policy choice clearly in the assignment and the implementing ADR

### Kill/repurpose confusing UI
- [ ] Retire or relabel the confusing "Save in local queue for later" delivery dropdown (per-agent queue **is** the queue now)
- [ ] "Open visible window now" path becomes the normal start action (or is implicit in tile-based assignment)
- [ ] Existing delivery dropdown terminology should not persist in the redesigned UI

### Standard closeout
- [ ] Update docs/SESSION.md Next action as you go
- [ ] docs/PROGRESS.md note
- [ ] ADR (new ADR-### documenting the per-agent queue semantics, auto-advance policy, and safety invariants)
- [ ] Tests (overlay JS, Python backend if queue advancement logic lives in `brain/`)
- [ ] QUEUE/INDEX → done; move this file to docs/assignments/done/

## Out of scope
- Full multi-agent orchestration / dependency graph beyond per-agent FIFO queue
- Changing the underlying `Blocked-by`/`Gate`/area claimability semantics (A-037 already shipped that; reuse it, don't replace it)
- Auto-running assignments without any visible window or human oversight
- Removing human validation or approval paths for new assignments
- Rewriting the Assignments panel (A-017) — this is Agent monitor only

## Notes for the coding agent
**Token discipline:**
- Read A-018/A-036 done briefs + ADR-032/039 once for context
- Read current `overlay/agents.js`, `overlay/training.html`, `brain/training.py` once
- Afterward, prefer `git diff` to re-reading full files

**Coordination:**
- A-034 (latency profiler UI) is also `area:overlay` and queued — if it goes `in_progress` before you claim this, coordination may be needed on shared overlay chrome
- `logs/training/agents.json` is the ignored slot registry (A-036 structure, version 1)
- Auto-advance semantics should check `origin/main`'s QUEUE/INDEX for claim/status changes (A-039 protocol)

**Implementation hints:**
- Claimability: reuse `brain/training.py`'s existing `unmet_blocked_by` logic (A-037), don't duplicate
- Status detection for tiles: derive from slot's `current_assignment` + QUEUE status + (optionally) last-handoff recency
- Auto-advance trigger: could be polling `origin/main` (simple but latency) or a filesystem watch on local `.git/refs/remotes/origin/main` after agent finishes (more responsive)
- Prefer explicit state ("agent finished A-038 at 14:32, next claimable is A-026") over silent background checks

**Acceptance:**
- Must visibly show tiles + under-tile queues + available-work panel in Training
- Must demonstrate assigning 2+ future assignments to one agent tile
- Must demonstrate (or document how to test) auto-advance when the agent finishes and the next queued item becomes claimable
- Must document the chosen auto-submit policy in the ADR and this brief before closeout
