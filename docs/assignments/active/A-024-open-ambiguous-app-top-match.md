# A-024 — Ambiguous open_app_by_name → open top match (Bitwarden #16 part 1)

- **Status:** queued
- **Area:** area:actions
- **parallel-ok:** YES
- **Soft path hints:** `actions/` (esp. resolve/open_by_name), `tests/`, docs bookkeeping
- **Blocks / blocked-by:** Blocks **A-025** preference/correction polish (A-025 can start stubs after this lands). Independent of A-022 (cliamp/brain).
- **Links:** GitHub #16 · backlog `bug-open-bitwarden` · run `d60fc0c2-f806-4e74-af11-6c853d3dfe1b`

## Goal
Today `open bitwarden` plans correctly but **execution fails** with “Multiple installed apps match 'bitwarden'… be more specific.” Alex wants: on multiple matches, **open the top match** instead of erroring (Bitwarden is the fixture; behavior is general).

Preserve plan → approve → execute. Reply should name which app was chosen when useful.

## Checklist
- [ ] Reproduce multiple-match failure for `bitwarden` (and a synthetic multi-match unit fixture)
- [ ] Change resolver: ranked candidates → launch/focus **best** match; stop hard-failing on ties/multiples (define stable ranking: exact > prefix > substring > fuzzy; break ties deterministically)
- [ ] Surface chosen desktop name/id in action result/summary for honesty
- [ ] Regression tests; PROGRESS; SESSION; QUEUE/INDEX → done
- [ ] Leave preference weights / “the other one” to **A-025** (optional hook: return alternate candidates in result metadata for later)

## Out of scope
- Learning/preference store and correction utterances (A-025)
- Closing the wrong window after correction (A-025)
- Overlay Training UI; cliamp (#15 / A-022)

## Notes
Error text only listed one name (“Bitwarden”) but still failed as multiple — inspect duplicate `.desktop` entries / id vs name collisions on the host.
