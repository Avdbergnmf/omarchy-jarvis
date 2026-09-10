# IMP-001 — Ambiguous app-open should pick a match, then let Alex correct it

- **Status:** shipped
- **Owner:** Desk
- **Assignment ids:** A-024, A-025
- **Evidence refs:** none — historical, predates A-038 evidence bundles (v0); bounded inline summary below
- **Milestone:** none
- **Links:** issue #16 · backlog `bug-open-bitwarden` · run `d60fc0c2-f806-4e74-af11-6c853d3dfe1b` · ADR-036

## Current summary
Shipped. `open bitwarden` used to plan correctly but fail at execution with "Multiple installed
apps match 'bitwarden'… be more specific," because two `.desktop` entries matched. A-024 made an
ambiguous match open the top-ranked candidate instead of erroring. A-025 closed the rest of #16:
a natural-language correction ("no, the other bitwarden" / "the other one") closes the
just-opened window, opens the next-ranked match, and durably bumps that stem's preference weight
in `~/.config/jarvis/app-preferences.json` so future opens rank it higher.

## Events (append-only — never edit or delete a past line; add new lines only)
- 2026-09-10 — hypothesis: issue #16 — ambiguous `open_app_by_name` hard-fails instead of doing
  something useful; Alex wants a top-match default plus a way to say "no, the other one."
- 2026-09-10 — Alex decision: approved, split into two assignments (top-match open, then
  preference/correction) since the second depends on the first's ranked-candidate output.
- 2026-09-10 — assignment A-024 opened and shipped: ambiguous `open_app_by_name` now launches the
  top-ranked `.desktop` match (exact > prefix > substring > fuzzy tiers) instead of hard-failing.
- 2026-09-10 — assignment A-025 opened and shipped: `APP_CORRECTION_RE`-matched phrases route to a
  new reviewed `correct_app_open` tool (closes the just-opened window only if it still exists and
  still matches, opens the next-ranked stem, bumps its weight); `last_open` state has a 15-minute
  TTL so a stale "the other one" doesn't close an unrelated window. See ADR-036 and
  `tests/test_jarvis.py::OpenByNameTest` for the regression coverage. Not independently verified:
  a live two-Bitwarden Hyprland round trip outside this sandbox — flagged for Alex in A-025's
  PROGRESS note.
- 2026-09-10 — issue #16 closed.
