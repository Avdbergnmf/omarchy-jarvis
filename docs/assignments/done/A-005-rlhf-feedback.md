# A-005 — Post-run RLHF feedback (+ / neutral / −)

- **Status:** done
- **Area:** area:overlay (+ `area:brain` for recording feedback + wiring − into report intake)
- **parallel-ok:** NO
- **Allowed paths:** `overlay/`, `brain/`, `docs/LOGGING.md`, `docs/backlog/` (if storing neutral marks), `docs/PROGRESS.md`, `docs/DECISIONS.md`, `README.md`, `tests/`, `actions/report_bug` only if extending context pack
- **Forbidden paths:** Silent auto-filing issues without Run; contacting other agents; A-004 scope (land A-004 first if focus/overlay still flaky)
- **Blocks / blocked-by:** Prefer after **A-004**
- **Links:** user ask 2026-09-09 — RLHF after prompt: good / neutral / bad→report

## Goal
After a prompt finishes (`done` / `error`), show quick feedback:
- **+ / good / thumbs up** — mark run as good (journal + local store)
- **neutral** — “didn’t fully work, don’t want to dig in now” → mark for **later review** (no bug filed yet)
- **− / bad / thumbs down** — enter existing **report / bug intake** flow with this `run_id` pre-attached

All of this must stay transparent (visible in overlay); filing a GitHub issue still requires approve/**Run** as today.

## Checklist
- [x] Overlay controls after terminal run (accessible, keyboard-friendly if reasonable) — native `<button>`s, keyboard-reachable, shown only when terminal + unrated.
- [x] Persist feedback: journal event and/or `logs/` or backlog “review later” list for neutrals (document choice in ADR) — `feedback` journal phase for all ratings; neutral also appends to local-only `logs/feedback/needs-review.jsonl`. ADR-020.
- [x] Thumbs down → start report intake with context pack from this run (reuse self-improve path) — reuses `start_intake`, now parameterized with `source_run_id` so context always describes the *rated* run, not whichever ran most recently.
- [x] Neutral does **not** spam GitHub; list somehow (`/backlog` or a small “needs review” section) — document — `needs-review.jsonl`, documented in `docs/LOGGING.md` and ADR-020; never touches `gh`.
- [x] Thumbs up is cheap (no questions) — journal-only, no intake.
- [x] Tests + README human blurb — `FeedbackTest` (7 cases) + extended `overlay.test.cjs`; README one-liner added.
- [x] PROGRESS + ADR; QUEUE → done; move to `docs/assignments/done/` — ADR-020, PROGRESS.md entry, this file moved.

Live-verified on this host: real 👍 (journaled), real 🤔 (appended to `needs-review.jsonl`, second rating on same run correctly rejected 400), real 👎 on an approved `scratch_toggle` run — correctly started a fresh bug-intake run whose context's `last_run_id` matched the *rated* run exactly despite other runs happening in between. Rating a **denied** run correctly 409s (denied runs never executed anything — no outcome to rate), which is intentional, not a gap.

## Out of scope
Training a local reward model. Auto-dispatch to Claude. Changing approval_mode defaults.

## Notes for the coding agent
Reuse `/report` / `start_intake` rather than a second bug pipeline. Redact secrets. Don’t block desktop follow-along from A-004.
