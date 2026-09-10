# IMP-003 — Plan details belong inside the proposed-action bubble, not a text dump below it

- **Status:** shipped
- **Owner:** Desk
- **Assignment ids:** A-019
- **Evidence refs:** none — historical, predates A-038 evidence bundles (v0); bounded inline summary below
- **Milestone:** none
- **Links:** follow-up to A-015 · ADR-035

## Current summary
Shipped. A-015 made a plan's `reply` genuinely descriptive, but the proposed-action bubble
itself still showed only a bare tool name plus raw `key=value` argument soup, with the readable
detail stuck in a separate, truncating status line below the bubble. A-019 moved the readable
detail into the bubble itself: each action renders as a card with a friendly title, an optional
description, and small argument chips — the one place a `run_skill` plan's description is
authoritative.

## Events (append-only — never edit or delete a past line; add new lines only)
- 2026-09-10 — hypothesis: Alex — plan info appears as text below the proposed bubble; wants it
  inside the bubble, human-readable, rarely wrapping.
- 2026-09-10 — Alex decision: approved as filed, follow-up to A-015.
- 2026-09-10 — assignment A-019 opened and shipped: `overlay/app.js` renders each action as a
  `.action-card` (friendly title + chips) via a client-side `ACTION_TITLES`/`TITLE_ARGS` map
  covering all 12 known tools; unmapped tools fall back to a prettified tool name with no chips
  lost. The redundant below-bubble `#status` text dump is retired. See ADR-035. In the process,
  a real test-mock bug was found and fixed: the DOM mock's `innerHTML=''` never actually cleared
  `.children`, which combined with a synchronous mocked `setTimeout` turned a latent
  unbounded-growth risk into a real hang once bubbles became multi-node.
