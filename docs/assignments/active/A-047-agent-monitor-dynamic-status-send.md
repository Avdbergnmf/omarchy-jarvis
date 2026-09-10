# A-047 — Agent monitor: dynamic status colors + simpler send

- **Status:** queued
- **Area:** area:overlay (+ light `brain/training.py` if status/advance needs richer signals)
- **parallel-ok:** YES
- **Recommended depth:** high
- **Allowed paths (optional soft hint):** `overlay/agents.js`, `overlay/training.html`, `overlay/training.css`, `overlay/training.js`, agent-advance / dashboard bits in `brain/training.py` + `brain/server.py`, tests, ADR/PROGRESS/SESSION
- **Forbidden paths (optional soft hint):** Validate overhaul (A-046); Problems row click (A-043); inventing hidden background agents
- **Blocked-by:** none
- **Gate:** training-ux
- **Improvement:** none
- **Links:** Alex JARVIS room 2026-09-10 — status-colored cards; dynamic lifecycle (starting → working → idle/next); 10s poll while panel open + force-check; Available work as selector; drop primary assignment dropdown + Preview; Send / Queue buttons; preview + assignment override → Advanced. Builds on A-041 tiles (left-border colors exist but lifecycle/UX still weak).

## Goal
Make Agent manager feel **live and one-click**, not a form with a preview gate.

### 1) Dynamic, visible status on cards
Tiles already have `status-idle|working|waiting|blocked|error` border colors — make status **actually track the lifecycle** Alex describes:

| Phase | Meaning (approx.) |
|-------|-------------------|
| starting / starting-up | Just sent / window opening / handoff prepared, claim not on `origin/main` yet |
| working | Assignment claimed (`in_progress`) for this slot |
| waiting | Personal queue item not yet claimable (blocked-by / area / busy) |
| idle | Nothing current and nothing ready-next |
| error | Launch/advance failure (existing) |

Refine names to fit the existing vocabulary if needed, but **cards must read differently by state** (color + label). When a handoff finishes and there is no ready-next personal item → idle; if there is ready-next → advance into it (existing auto-advance policy), not stuck “working.”

### 2) Poll while the panel is open
While Agent manager is visible: refresh queue + slot status about **every 10 seconds** (dashboard and/or advance — reuse `pollAgentAdvance` / refresh patterns). Add an explicit **Check now** (force refresh) button. Stop or idle-down when the panel is hidden. Do not burn cloud spend; this is local status + prepare/focus only unless A-045 opt-in auto-send is on.

### 3) Simplify dispatch UX
- **Available work** is the primary assignment selector (click a ready row → that work is selected for the chosen agent).
- Remove the primary **Work on assignment** `<select>` from the main form (keep a way to override under **Advanced** if Alex must force a non-listed id).
- Move **Preview assignment** into Advanced (power users still can dry-run file writes).
- Primary actions become direct buttons, e.g. **Send now** (visible start) and **Add to queue** — one confirm step max if the existing preview/confirm safety for disk writes still requires it; prefer the shortest path that still respects “no silent main writes.” Goal: stop making Preview the default verb.

### 4) ADR / copy
Document the status state machine and polling rule; update the muted “never pastes” line if A-045 lands first (compose carefully). Align with ADR-043 (visible window; no auto-submit unless opt-in).

Done for Alex: open Agent manager → pick available work + agent → Send/Queue → watch cards flip starting → working → idle/next on a 10s pulse (or Check now), without fighting a dropdown + Preview flow.

## Checklist
- [ ] Audit current `computed_status` / tile CSS / `pollAgentAdvance`; list gaps vs the table above
- [ ] Implement richer status + stronger card coloring/labels
- [ ] 10s poll while panel open + Check now; no poll when hidden
- [ ] Available work = selector; assignment dropdown + Preview demoted to Advanced; Send now / Add to queue primary
- [ ] Idle vs auto-advance-to-next when current work leaves the live queue
- [ ] Tests; ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope
- Implementing A-045 auto-paste (compose with it if already merged; do not block on it)
- Reworking Assignments editor / Validate / Problems
- Cloud Agent Manager (Cursor.com) — this is local Training Agent manager only

## Notes for the coding agent
Start at `overlay/training.html` agent section + `overlay/agents.js` + A-041/ADR-043. Prefer evolving `computed_status` over a second parallel status field. Token discipline: one pass on agents.js/html/css, then implement.
