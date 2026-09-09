# Claude Code — agent entrypoint, Issue Loop, pass lifecycle, multi-agent & structured logs

Work in **`~/Work/omarchy-jarvis`** (`Avdbergnmf/omarchy-jarvis`). Read `AGENTS.md`, `README.md`, `docs/backlog/`, open issues, and skim `brain/server.py` `log()` + `logs/runs/*.log` before changing things.

## Why
Front door for agents, issue-driven work, disposable passes, safe parallel modules, and **structured action logs** so Alex and coding agents can debug fast without slowing the hot path.

Durable truth = issues + backlog + ADRs + PROGRESS.  
Passes/handoffs = disposable.  
Logs = **append-only evidence** (JSONL), not a second docs system.

---

## Part A — `START.md` (repo root front door)
First lines: if told to work on Omarchy Jarvis, read this fully before other docs/code.

### 1. What this is (~10 lines)
Overlay (Super+Shift+J) → Ollama → plan/approve/execute → actions/skills. Link README.

### 2. Job modes
| Mode | User says… | You do… |
|------|------------|---------|
| **Fix open issues** | “fix outstanding issues / backlog” | Issue Loop + multi-agent rules |
| **Implement a pass** | “do the X pass” | Only `docs/passes/active/` |
| **Feature from backlog** | “build feature X” | backlog feature doc + GH issue |
| **Explore / debug** | “why did X fail” | Run journal (prompt→done→eval) + Open console; module debug if needed (Part C) |

### 3. Issue Loop
```bash
cd ~/Work/omarchy-jarvis
./scripts/agent-status.sh
gh issue list --repo Avdbergnmf/omarchy-jarvis --state open
gh issue list --repo Avdbergnmf/omarchy-jarvis --label jarvis-reported --state open
```
Bugs before enhancements; one PR per issue; `Fixes #N`; PROGRESS; comment blockers; no close without evidence. Bug reports / handoffs should **link `run_id` + log path**.

### 4. Multi-agent & parallel
Seams → labels: `area:overlay|brain|actions|skills|docs`.  
Also: `parallel-ok` (issue must list allowed + **forbidden** paths), `single-writer` (default for `area:brain` / control plane).  
One agent ↔ one issue ↔ one area when possible. Parallel only across different areas with no path overlap. **Never** parallelize approve/execute / `brain/server.py` redesign. Merge before handing contested files. `agent-status.sh` groups by area and **warns on collisions**.

### 5. Pass & handoff lifecycle
```
docs/passes/{README,INDEX,active/,archive/}
docs/backlog/handoffs/   # same lifecycle
```
INDEX status: `active|done|superseded`. New briefs → `active/` (keep small). On merge/close → `done` + move to `archive/`. Replaced → `superseded`. Default **archive not delete**. Never follow `archive/` as current. Migrate existing `CLAUDE_*_PASS`, `PROMPT_*`, `ASTRA_HANDOFF` into this layout.

### 6. Docs map + safety + session DoD
Link START, AGENTS, README, DECISIONS, PROGRESS, HOST, MILESTONES, backlog, passes, **logging doc**.  
Safety: plan→approve→execute; redact secrets in logs/issues; skills confirm; handoffs prepare-only unless approved.  
Done: doctor/tests, PROGRESS, PR links, INDEX ok, active passes small, logs schema documented.

---

## Part B — Repo hygiene to implement
1. Slim `AGENTS.md` → invariants + “read START.md first”.
2. `README.md` → Agents: START.md; Debugging: logs.
3. `scripts/agent-status.sh` — issues by area, parallel warnings, active passes, recent run_ids, doctor one-liner.
4. Create GH labels if missing; update issue templates (`area:*`, forbidden paths for `parallel-ok`, run_id field).
5. ADRs for START door, pass lifecycle, multi-agent seams, **structured logging**.
6. Update PROGRESS.md.

---

## Part C — Run journal (primary) + module debug (secondary)

### Clarify intent (Alex)
The **useful** log is a **run journal**: what the user asked → what Jarvis decided/processed → what actually happened → a **small evaluation** (flag if something looks off). Include **Jarvis version + timestamp** on every entry.

**Module/internals logging** (per-action argv spam, poll noise, overlay clicks) is **`debug` only** — off by default, for deep dives. Do not make module chatter the main log.

### Current state
`logs/runs/<run_id>.log` already has coarse text. Upgrade the *primary* artifact to a structured **journal**; keep console tail working.

### Primary: run journal (JSONL)
Path convention (pick one, document in `docs/LOGGING.md`):
- `logs/journal/CURRENT.jsonl` — active journal for this Jarvis version
- On version bump / big change: **reset** = rename `CURRENT.jsonl` → `logs/journal/archive/v<version>-<date>.jsonl` (or stop writing and start fresh `CURRENT.jsonl`). Old journals remain reachable via **git history** on the commit that produced them; do not rewrite history. Optionally gitignore `logs/journal/` and rely on local archive + commits of schema/docs only — if journals are gitignored, still keep `archive/` on disk and record the jarvis version + git describe in each line so agents can check out the matching commit.

Each **run** appends a small number of journal records (not hundreds):

| Field | Meaning |
|-------|---------|
| `ts` | ISO-8601 UTC |
| `jarvis_version` | from repo version file / git describe / `pyproject`/`VERSION` — must change when you reset the journal |
| `run_id` | correlation |
| `phase` | `prompt` \| `process` \| `done` \| `eval` |
| `prompt` | user text (truncated, redacted) — on prompt phase |
| `process` | plan/tools/skill chosen (short) — on process phase |
| `happened` | actual side effects / tool results summary — on done phase |
| `eval` | `{ "ok": bool, "flag": null\|"suspicious"\|"mismatch"\|"partial", "note": "…" }` — on eval phase |
| `ok` | overall run success when known |

**Eval (lightweight, local):** after `done`, heuristics and/or a tiny local check — e.g. plan said open Outlook but no matching client; skill reported ok but hypr workspace unchanged; user said “move to scratch” but scratch toggle didn’t fire. Prefer **rules + hyprctl snapshots**, not a second cloud LLM call. If unsure, `flag: suspicious` with a one-line note — never block the UI on eval. Eval failures are **flags for humans/agents**, not automatic GitHub issues (unless user later `/report`).

### Secondary: module debug
- `log_level = info|debug` in `~/.config/jarvis/config.toml` (default `info`).
- At `debug`, modules may emit JSONL to `logs/debug/<run_id>.jsonl` or stderr with `module=` field.
- Hot paths (`GET /v1/runs` polls) never log at `info`.

### Performance
Append-only; truncate fields; redact secrets; batched flush only if needed; rotate/archive on version bump; don’t dual-write megabyte model dumps.

### Version bump → journal reset
Document in START + LOGGING + a one-line note in release/PROGRESS when bumping:
1. Set new `jarvis_version` (maintain `VERSION` or git tag).
2. Archive/reset `CURRENT.jsonl`.
3. Old behavior remains on old commits; agents debugging an old issue check out that version’s code + use archived journal if present.

### Wire-in
Brain writes prompt/process/done/eval journal lines; actions stay quiet at info except result summaries folded into `happened`; Open console can follow journal for a run_id or the text run log derived from it. Bug intake attaches `run_id` + journal excerpt + `jarvis_version`.

### Logging acceptance
1. `docs/LOGGING.md` — journal schema, debug vs journal, version-reset procedure, how to `jq` a flagged eval.
2. Demo run shows prompt → process → done → eval with version+ts; a deliberate mismatch can set `flag`.
3. Module debug off by default; enabling it doesn’t break doctor.
4. Version bump script or documented steps resets CURRENT journal.
5. START “Explore / debug” points at the journal, not module spam.

## Acceptance (whole pass)
1. Cold agent “fix outstanding issues” → START → agent-status → issues.
2. Parallel labels + collision warnings work as documented.
3. Passes under active/archive with INDEX; archive not treated as current.
4. Run journal live (prompt→process→done→eval + jarvis_version); module logs debug-only; LOGGING.md + version-reset procedure.
5. Doctor/CI green; commit/PR.

## Non-goals
OpenTelemetry/cloud log ships; logging every Hyprland event system-wide; rewriting product features beyond logging hooks; auto-spending multi-agent credits; changing approval_mode default.

## One-liner when done
“Hook: START.md. Issues by area. Passes archive when done. Debug: run journal prompt→process→done→eval (+ version); module detail is debug-only.”
