# A-024 — Ambiguous open_app_by_name → open top match (Bitwarden #16 part 1)

- **Status:** done
- **Area:** area:actions
- **parallel-ok:** YES
- **Soft path hints:** `actions/` (esp. resolve/open_by_name), `tests/`, docs bookkeeping
- **Blocks / blocked-by:** Blocks **A-025** preference/correction polish (A-025 can start stubs after this lands). Independent of A-022 (cliamp/brain).
- **Links:** GitHub #16 · backlog `bug-open-bitwarden` · run `d60fc0c2-f806-4e74-af11-6c853d3dfe1b`

## Goal
Today `open bitwarden` plans correctly but **execution fails** with “Multiple installed apps match 'bitwarden'… be more specific.” Alex wants: on multiple matches, **open the top match** instead of erroring (Bitwarden is the fixture; behavior is general).

Preserve plan → approve → execute. Reply should name which app was chosen when useful.

## Checklist
- [x] Reproduce multiple-match failure for `bitwarden` (and a synthetic multi-match unit fixture)
- [x] Change resolver: ranked candidates → launch/focus **best** match; stop hard-failing on ties/multiples (define stable ranking: exact > prefix > substring > fuzzy; break ties deterministically)
- [x] Surface chosen desktop name/id in action result/summary for honesty (already free via existing `entry['name']` in `open_by_name()`'s result)
- [x] Regression tests; PROGRESS; SESSION; QUEUE/INDEX → done
- [x] Leave preference weights / “the other one” to **A-025** (optional metadata hook skipped — not required, A-025 can resolve again itself)

## Resolution (2026-09-10)
`resolve_app()` in `actions/core.py` no longer raises when a tier has multiple candidates —
it returns the first (top) one, deterministic via `desktop_entries()`'s own most-local-dir-
first ordering. Covered by `tests/test_jarvis.py::test_resolve_app_exact_prefix_fuzzy_and_ambiguous`
(updated) and new `test_resolve_app_picks_top_match_for_duplicate_desktop_entries`.

## Out of scope
- Learning/preference store and correction utterances (A-025)
- Closing the wrong window after correction (A-025)
- Overlay Training UI; cliamp (#15 / A-022)

## Notes
Error text only listed one name (“Bitwarden”) but still failed as multiple — inspect duplicate `.desktop` entries / id vs name collisions on the host.
