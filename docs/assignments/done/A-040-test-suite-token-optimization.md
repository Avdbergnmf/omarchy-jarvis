# A-040 — Test suite optimization (token cost + redundancy)

- **Status:** queued
- **Area:** area:docs (+ `tests/` maintenance; no product behavior changes unless a test is wrong)
- **parallel-ok:** NO while A-039 (docs) is in_progress; claim after A-039 (or PARALLEL only if A-039 done)
- **Priority:** high — agents burn context running/reading a bloated suite
- **Soft path hints:** `tests/`, `START.md` / prompts (what agents must run), optional `scripts/` smoke target, `docs/DECISIONS.md`
- **Links:** Alex 2026-09-10 — ridiculous number of tests; worry they waste tokens

## Context (desk snapshot)
- ~**153** Python unittest cases (~1s runtime locally) plus several `*.cjs` overlay/training suites
- Largest file: `tests/test_jarvis.py` (~674 lines); total test sources ~2k lines
- Token cost is less wall-clock than **agents pasting full outputs / re-reading entire suites** and **mandatory full runs on tiny docs edits**

## Goal
Make the suite **lean where safe** and teach agents a **cheap default vs full** policy:

1. **Audit** for redundancy (duplicate py vs cjs coverage, overlapping cases, low-value assertions, copy-paste variants).
2. **Cull or merge** only when coverage of real regressions (honesty, open-app, journal, training, validation) stays intact — prefer parametrize/table-driven over deleting critical cases.
3. **Split** into:
   - **smoke** (fast, always) — critical path subset agents run by default on small changes
   - **full** — CI / before merge to main / when touching brain/overlay/actions
4. Update START + CONTINUE/NEW_AGENT so agents **don’t dump full test logs into context**; run smoke by default; full when needed; summarize fail lists only.
5. Short ADR: what we kept, what we cut, how smoke is selected.

Do **not** weaken protected eval ideas (A-028/A-030) — this is engineering unit/overlay tests, not deleting the future capability/regression harness.

## Checklist
- [x] Inventory: count per file, overlap map, token/log pain points for agents — 158 Python cases (93 in `test_jarvis.py`), 5 `.cjs` suites; no duplicate py/cjs coverage found (different layers — server logic vs overlay UI); `subTest` already used in 5 places (already table-driven). The real pain point is `-v`/full-suite pasting, not test count.
- [x] Propose keep/merge/drop list with risk notes; implement approved culls/merges — **kept everything**; audit found no safe cull (every test name maps to a distinct named regression, out-of-scope risk to guess otherwise). See ADR-040.
- [x] Add `scripts/test-smoke.sh` (or make target) + document `test-full` — both added, quiet-by-default (summary + bounded failure tail, full output to `logs/tests/*.log`).
- [x] Update START/prompts: default smoke; full before land-on-main; no pasting megabyte test output — `START.md` Token & context discipline + all three paste prompts' Land-on-main steps.
- [x] Confirm critical regressions still covered; time both smoke and full — smoke: 71 py cases + 5 cjs suites in ~0.4s; full: doctor+158 py+shellcheck+node-check+5 cjs in ~1.5s. Verified failure detection by injecting a false assertion into `test_journal.py`, confirming `test-smoke.sh` reports it correctly, then reverting.
- [x] ADR + PROGRESS; SESSION; QUEUE/INDEX → done — ADR-040.

## Out of scope
Deleting human validation catalog; stochastic eval harness (A-031); rewriting product code to make tests pass; inventing flaky desktop e2e.

## Notes
Wall-clock is already ~1s for Python — optimize for **agent token/behavior**, not microseconds. Prefer fewer, sharper tests over many near-duplicates.
