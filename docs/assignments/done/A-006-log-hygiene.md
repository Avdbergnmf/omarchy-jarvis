# A-006 — Log hygiene (gitignore, retention, temp cleanup)

- **Status:** done
- **Area:** area:docs (plus small `scripts/` / journal retention helpers)
- **parallel-ok:** YES
- **Allowed paths:** `.gitignore`, `logs/` (local only — should stay untracked), `docs/LOGGING.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `README.md`, `scripts/` (cleanup/retention helpers, doctor notes), `brain/journal.py` (retention/rotation only), `tests/test_journal.py` if needed
- **Forbidden paths:** `overlay/` product UI; A-004/A-005 feature work; rewriting report/intake flows
- **Blocks / blocked-by:** none — can run parallel with overlay work if paths respected
- **Links:** Alex 2026-09-09 — cleaner logging; don’t push logs to git; max count; wipe temps on new build/commit

## Goal
Logging should stay useful for debug/agents **without** polluting git or growing forever.

1. **Git:** almost no runtime logs in git. Tighten `.gitignore` so `logs/**` (runs, journal CURRENT, debug, overlay-profile, caches, demo-evidence, etc.) stay local. If anything under `logs/` is tracked, untrack it (`git rm --cached`). Only allow tiny **non-secret** fixtures under something like `testdata/` if tests truly need them — never plentiful run journals.
2. **Retention:** hard caps — e.g. max N run logs, max journal archive files / size; delete oldest first. Document knobs in `docs/LOGGING.md` (and optional `~/.config/jarvis/config.toml`).
3. **Ephemeral / temp:** classify “temp any time” artifacts (doctor scraps, demo-evidence, clients-after-*.json, overlay-profile caches if safe, `__pycache__`, etc.). Remove them on **new build/commit** via a small script hooked from doctor or a `scripts/clean-temp-logs.sh` that agents/CI run; document in START/README that commits should be preceded by temp clean (or add a trivial git pre-commit local hook **optional**, not mandatory for all clones).

## Checklist
- [x] Audit what’s in `logs/` today + `git check-ignore` / `git ls-files logs` — `git ls-files logs/` was empty; `logs/` (bare, in `.gitignore`) already covers everything recursively.
- [x] Fix `.gitignore`; remove any tracked log artifacts from the index (keep files on disk) — nothing to fix or untrack; already fully covered.
- [x] Implement retention for run logs + journal archives (defaults sane; document) — `brain/journal.py::prune()`, `RUN_LOG_KEEP=200`/`DEBUG_KEEP=200`/`ARCHIVE_KEEP=20`, checked once per new run / per rotation. Documented in `docs/LOGGING.md`.
- [x] Implement temp cleanup script + when it runs (doctor / explicit / optional hook) — `scripts/clean-temp-logs.sh`, explicit/manual (not wired into doctor or a mandatory hook, per the note allowing that to stay optional); `--profile` for the overlay Chromium cache, gated on a live `hyprctl` open-overlay check.
- [x] Update `docs/LOGGING.md` + short README pointer — done.
- [x] ADR + PROGRESS; tests for retention if non-trivial — ADR-021; PROGRESS.md entry; 6 new tests in `tests/test_journal.py`.
- [x] QUEUE/INDEX → done; move this file to `docs/assignments/done/`

Live-verified on this host: ran `clean-temp-logs.sh` for real (removed 5 stray scratch files + 4 `__pycache__` dirs), then `--profile` with the overlay closed (cleared the 154MB `logs/overlay-profile/`, confirmed the overlay still opens/toggles/closes correctly afterward with a freshly recreated profile). Caught and fixed a real bug in the safety check itself along the way: an initial `pgrep -f` guard false-positived by matching the checking shell's own command-line text; replaced with the same `hyprctl`-based check the rest of the codebase uses.

## Out of scope
Changing journal schema phases; RLHF; follow-along overlay behavior.

## Notes for the coding agent
Do not commit journal contents or overlay-profile. Redaction rules stay. If A-004 has uncommitted overlay/server edits in the tree, **don’t touch those files**.
