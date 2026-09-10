# A-038 — Evidence identity + durable operational bundles v0

- **Status:** queued
- **Area:** area:brain
- **parallel-ok:** NO (journal/evidence Control Plane is a single-writer surface)
- **Soft path hints:** `brain/journal.py`, `brain/server.py`, `scripts/`, `docs/LOGGING.md`, `docs/evidence/`, `tests/`
- **Blocks / blocked-by:** First claimable assignment after A-032. Blocks A-026 and A-028.
- **Links:** docs/SELF_IMPROVE_ROADMAP.md · A-032 review · ADR-018/021

## Goal

Give selected operational evidence a stable, private identity before the ledger and candidate
evals depend on it. Current journals remain useful ephemeral diagnostics; a deliberate export
creates a bounded, redacted, content-addressed bundle under XDG state. The versioned schema
must identify the exact code/model/planner inputs needed to compare results.

This does not put raw prompts in git and does not claim that local files are backed up.
“Backed up” is true only after Alex selects and verifies a destination.

## Checklist

- [ ] Define the three evidence tiers and a versioned evidence-reference/result-envelope schema in `docs/evidence/`
- [ ] Fingerprint revision plus dirty-byte state, Jarvis version, planner mode, exact Ollama model digest, system prompt, tools/plan schema, generation options and case/version when present
- [ ] Add a bounded callable exporter for a selected run/eval under `$XDG_STATE_HOME/jarvis/evidence/` (default `~/.local/state/jarvis/evidence/`); default to redacted summary + hashes, with private prompt/output inclusion opt-in
- [ ] Use mode 0600, safe paths, atomic creation, content hashes, size limits and collision handling; never follow unsafe symlinks or log secrets
- [ ] Distinguish source disappearance from bundle validity; an ignored `logs/...` path alone is never labelled durable
- [ ] Document retention and a user-owned backup verification procedure; do not silently add cloud/network sync
- [ ] Tests cover stable fingerprints, mutable model tags/digests, dirty state, redaction, atomicity, bounds, malformed source and no-network behavior
- [ ] Update LOGGING/START and expose the reference shape A-026/A-028 consume
- [ ] On acceptance, deliberately unblock A-026 and A-028 in QUEUE/INDEX
- [ ] ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Out of scope

Uploading or committing raw journals/prompts; choosing a backup provider for Alex; continuous
telemetry; a general artifact database; the ledger itself; candidate eval cases/runners;
changing approval behavior; restarting the shared service from an isolated worktree.

## A-032 evidence

- `.gitignore` excludes all `logs/`.
- `brain/journal.py` prunes run/debug files at 200 and version archives at 20; no backup exists.
- Journal records contain VERSION + `git_describe`, but not model digest, planner mode,
  prompt/tool/schema hashes or generation options.
- `docs/LOGGING.md` correctly warns that git history does not retain private logs.
