# Start here — Omarchy Jarvis

If told to work on Omarchy Jarvis, read this fully before other docs or code.

Jarvis is a local, keyboard-first Omarchy assistant. Super+Shift+J opens its chat overlay.
Ollama turns requests into reviewed actions or skills. The normal flow is
prompt → plan → approve → execute; chitchat needs no approval.
The overlay shows the plan and live results. Open console follows a run.
Actions are CLI tools; skills compose reviewed tools. Keybindings come from the live catalog.
Bug and feature intake drafts issues deterministically and waits for approval.
Dispatch prepares a prompt file; it never contacts an agent.
See [README](README.md) for product usage and installation.

## Pick a job

- **Fix open issues / backlog:** follow the Issue Loop below; bugs before enhancements.
- **Implement a pass:** select only from [passes/INDEX](docs/passes/INDEX.md) and active/.
- **Feature from backlog:** read its [feature record](docs/backlog/README.md) and GitHub issue.
- **Explore / debug:** find run_id in the [run journal](docs/LOGGING.md), follow prompt → process → done → eval, and use Open console. Enable module debug only for deeper investigation.

## Issue Loop

```bash
cd ~/Work/omarchy-jarvis
./scripts/agent-status.sh
gh issue list --repo Avdbergnmf/omarchy-jarvis --state open
gh issue list --repo Avdbergnmf/omarchy-jarvis --label jarvis-reported --state open
```

Read the issue and local mirror. Fix bugs before enhancements. One PR per issue with
`Fixes #N`, acceptance evidence and PROGRESS. Record blockers on the issue when authorized
to comment. Never close without evidence. Reports and handoffs link run_id, journal/console
path and jarvis_version. Do not silently expand a pass into unrelated open issues.

## Parallel work

Areas are `area:overlay`, `area:brain`, `area:actions`, `area:skills`, `area:docs`.
Use one agent ↔ one issue ↔ one area where possible. Parallel work requires `parallel-ok`
and explicit `Allowed paths:` and `Forbidden paths:` entries in the issue. Different areas,
no path overlap. `single-writer` is the default for brain/control-plane work.
Never parallelize approve/execute or brain/server.py redesign. Merge before handing off
contested files. agent-status groups issues by area and warns about shared areas, path
collisions and missing scope; warnings require human review, not automatic scheduling.
Labels permit coordination; they do not authorize agent spending or spawning.

## Passes and handoffs

[Passes](docs/passes/README.md) and [handoffs](docs/backlog/handoffs/README.md) each have
INDEX.md, active/ and archive/. New scoped briefs enter active/. On merge/close, move to
archive/ and mark done. Replaced briefs become superseded. Archive rather than delete;
never follow archive as current instructions. Issues, backlog, ADRs and PROGRESS are durable.

## Safety and session done

Read [AGENTS](AGENTS.md) for invariants. Preserve plan → approve → execute, redact secrets
in logs/issues, ask before persisting new skills, keep IPC local, and prepare handoffs only.
Run doctor and CI checks, update PROGRESS with results and limitations, link the PR, check
INDEX statuses and keep active passes small. Document journal schema changes.
On a version bump or big behavior change, change VERSION and restart the service:
the first journal write archives CURRENT and starts a fresh file. Record the reset in
PROGRESS; see [LOGGING](docs/LOGGING.md) for recovery and matching old code to evidence.

## Docs map

[START](START.md) · [AGENTS](AGENTS.md) · [README](README.md) ·
[DECISIONS](docs/DECISIONS.md) · [PROGRESS](docs/PROGRESS.md) · [HOST](docs/HOST.md) ·
[MILESTONES](docs/MILESTONES.md) · [backlog](docs/backlog/README.md) ·
[passes](docs/passes/INDEX.md) · [logging](docs/LOGGING.md)
