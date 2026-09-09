# A-012 — Open YouTube (webapp/browser) + no false “opening…” plans

- **Status:** done
- **Area:** area:actions (+ light `area:brain` planner honesty)
- **parallel-ok:** YES
- **Allowed paths:** `actions/`, `brain/tools.json`, `brain/system_prompt.md`, `brain/server.py` (plan validation / empty-action guards), `skills/examples/`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/validation/`, `tests/`, `README.md`
- **Forbidden paths:** `overlay/` training/slash work (A-009 etc.) unless a one-line README note
- **Blocks / blocked-by:** Coordinate with **A-011** (open-by-name). Prefer sharing the same resolver; this assignment’s fixture is YouTube + **honest plans**.
- **Converted from:** GitHub #12 / `docs/backlog/bugs/converted/bug-open-youtube.md`
- **Links:** run_id `fad6f832-8cc1-4abe-ad96-f2da1173b7ff`; prompt `open youtube` → reply “Opening YouTube.” with **zero tools**

## Goal
1. **`open youtube` / `youtube`** opens the YouTube **webapp** if installed, else a **browser tab** to `https://www.youtube.com/` (Alex’s expected fallback).
2. **Never** emit a success-ish reply like “Opening YouTube.” with an **empty action list**. If it can’t open, say so; if it will open, the plan must include a real tool call (eval already flagged `suspicious`).

## Checklist
- [x] Reproduce empty-plan “Opening YouTube.” lie — found in the live journal: run `fad6f832` shows exactly `{"actions": [], "reply": "Opening YouTube."}`, reached the user as already `done` (zero-action plans skip approval), rated "bad". Also reproduced a *related* live failure: the model sometimes picks a real but wrong target (a plan to open Google Calendar) for the same prompt — a different reliability gap, noted in ADR-024, not fully solved by this assignment.
- [x] Implement/extend open path (align with A-011 resolver if present; else minimal YouTube webapp/`xdg-open`/browser helper) — added `YouTube` to `open_webapp`'s `APPS` map instead of relying on A-011's `.desktop` resolver: `open_webapp` always launches the URL directly (no `.desktop` dependency), which is the correct mechanism for the "even if not installed" fallback this goal explicitly asks for.
- [x] Planner/server guard: action-like open requests cannot complete with `actions: []` and a claiming reply — `FALSE_ACTION_CLAIM_RE` in both `json_plan()` and `plan_tools_run`, rewrites the reply to an honest one instead of erroring out or lying.
- [x] Live: YouTube webapp or browser tab actually appears after approve — `./actions/open_webapp --name YouTube` opened a real webapp window (`brave-www.youtube.com__-Default`); a second call focused the same window.
- [x] Regression tests (empty-plan guard + open youtube fixture) — 5 new tests, including the exact `fad6f832` reply text.
- [x] FEATURES/validation touch if required; PROGRESS; QUEUE → done — `docs/FEATURES.md` rows + two `docs/validation/items/*.md`; ADR-024.

## Out of scope
Installing YouTube webapp for the user (document how if missing). Full fuzzy app matrix (A-011) beyond what’s needed for YouTube.

## Notes
Keep approve-before-execute. If A-011 lands first, rebase this onto that resolver and focus on YouTube URL fallback + honesty guard.
