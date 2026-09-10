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
Self-improve foundations/roadmap: [docs/SELF_IMPROVE_ROADMAP.md](docs/SELF_IMPROVE_ROADMAP.md).

## Pick a job

- **Fix open issues / backlog:** follow the Issue Loop below; bugs before enhancements.
- **Implement an assignment / pass:** prefer [assignments/QUEUE](docs/assignments/QUEUE.md); large briefs still under [passes/INDEX](docs/passes/INDEX.md) active/.
- **Feature from backlog:** read its [feature record](docs/backlog/README.md) and GitHub issue.
- **Explore / debug:** find run_id in the [run journal](docs/LOGGING.md), follow prompt → process → done → eval, and use Open console. Enable module debug only for deeper investigation.

## Assignments (preferred work orders)

Ongoing “Alex asked for X” work lives in [docs/assignments/QUEUE.md](docs/assignments/QUEUE.md).
**Paste prompts (easy find):** [docs/assignments/prompts/](docs/assignments/prompts/README.md)
— CONTINUE · PARALLEL · NEW_AGENT.

Desk agents (Firsty or anyone authoring work) follow [docs/assignments/README.md](docs/assignments/README.md).

**Why something changed, across assignments:** [docs/ledger/README.md](docs/ledger/README.md) —
the Desk-owned Improvement Ledger (A-026). Assignments stay disposable execution work; the
ledger is the durable "why." Only Desk writes `docs/ledger/`; run
`python3 scripts/ledger-status.py` before allocating a new `IMP-NNN` id.

**Default:** one assignment → report to Alex (include the **next** QUEUE row’s recommended **depth**). If nothing is claimable: **stop with minimal tokens** (short “nothing possible” reply only) unless Alex explicitly overrides; if unclear, ask once. **Batch / keep going** only when Alex says so (`batch N`, `keep going`, `until queue empty`) — see [prompts/README](docs/assignments/prompts/README.md).

## Token & context discipline

- Continue from the **repo**: QUEUE, [SESSION](docs/SESSION.md), git status/diff, PROGRESS, active assignments/passes — **never** paste Codex/Claude/Cursor session logs.
- Read large files once; afterward prefer diffs.
- Default: one assignment chunk per session; explicit batch/keep-going overrides this.
  After each chunk, check off boxes, commit, and flush SESSION “Next action”.
- No drive-by refactors; keep `logs/` out of context unless a specific run_id; don’t re-echo huge tool outputs.
- Prefer Sonnet-class models for implementation unless stuck.
- **Tests (A-040/ADR-039):** default to `./scripts/test-smoke.sh` (critical-path subset: honesty/
  plan-approve, open-app, journal, training, validation, ~0.4s) for docs-only or small changes.
  Run `./scripts/test-full.sh` (mirrors CI) before landing to `main` or when touching
  `brain`/`overlay`/`actions`. Both write a full log under `logs/tests/` and print only a
  pass/fail summary — **never** paste `-v`/full suite output into context; quote at most the
  `FAIL:`/`ERROR:` lines the script already extracts, or point at the log path.

## Resumable session

Maintain [docs/SESSION.md](docs/SESSION.md) while working: active assignment id, checklist mirror, evidence, **one** Next action. Next agent: START → SESSION → QUEUE → git.

## Issue Loop

```bash
# Stay in your assigned Jarvis checkout/worktree.
./scripts/agent-status.sh
gh issue list --repo Avdbergnmf/omarchy-jarvis --state open
gh issue list --repo Avdbergnmf/omarchy-jarvis --label jarvis-reported --state open
```

Read the issue and local mirror. Fix bugs before enhancements. One PR per issue with
`Fixes #N`, acceptance evidence and PROGRESS. Record blockers on the issue when authorized
to comment. Never close without evidence. Reports and handoffs link run_id, journal/console
path and jarvis_version. Do not silently expand a pass into unrelated open issues.

## GitHub branch protection (read this)

This private Free repo **cannot** enable GitHub branch protection/rulesets unless it becomes
public or the account gets Pro. Alex decided (2026-09-10, ADR-046 / cancelled A-027): **neither
for now**. Do not block assignments on A-027, do not change visibility/billing, do not invent a
fake hard gate. Unattended Forge/auto-merge stay off; use human-reviewed merges.

## Parallel work

Areas are `area:overlay`, `area:brain`, `area:actions`, `area:skills`, `area:docs`.
Use one agent ↔ one issue ↔ one area where possible. Parallel work requires `parallel-ok`
and a **different `area:`** from every in-progress issue/assignment, plus the mandatory
separate worktree/branch below — that's the isolation, not a path allowlist. `Allowed
paths:`/`Forbidden paths:` entries are optional soft hints for context, never a gate; same
area, no path list makes it parallel-safe (see ADR-034). `single-writer` is the default for
brain/control-plane work. Never parallelize approve/execute or brain/server.py redesign.
Merge before handing off contested files. agent-status groups issues by area and warns about
shared areas and missing scope; warnings require human review, not automatic scheduling.
Labels permit coordination; they do not authorize agent spending or spawning.

### Required isolation for concurrent agents

Each parallel coding agent must use its own git worktree and dedicated branch,
even when the shared checkout is clean. Single-agent serial work may stay in the
canonical `~/Work/omarchy-jarvis`. If Alex supplied an isolated working directory,
stay there; do not create another or switch back to the canonical checkout.
Never checkout, stash, reset, clean, or edit another agent's tree. See
[ADR-024](docs/DECISIONS.md#adr-024--isolated-worktrees-for-concurrent-agents-2026-09-09).

#### Step 1 — claim on `origin/main` before you create a worktree

`origin/main` is the **only** place a claim counts (A-039). A status edit that
lives only on your feature branch is invisible to every other agent and to
`assignment-status.sh` until it is pushed — that is exactly how A-036 got
claimed on its worktree while `main` still said `queued`. From your current
checkout (not yet the new worktree):

```bash
git fetch origin
./scripts/assignment-status.sh   # canonical claim hint, reads origin/main
```

If the id you want is still `queued`/claimable there (no conflicting
`in_progress` area), edit `docs/assignments/QUEUE.md` + `INDEX.md` (status →
`in_progress`) and `docs/SESSION.md` (owner/branch/worktree) **on `main`**,
commit, and push straight to `origin/main`:

```bash
git add docs/assignments/QUEUE.md docs/assignments/INDEX.md docs/SESSION.md
git commit -m "docs: claim A-NNN on main before opening worktree"
git push origin main
```

If the push is rejected (someone raced you), `git fetch && git pull --ff-only`
and re-check — do not force-push over another agent's claim; pick a different
claimable id instead. Only after the claim commit is on `origin/main` do you
open the worktree:

```bash
# Run from the current Jarvis checkout; replace slug/branch with your assignment.
git worktree list
git status --short --branch
git fetch origin
jarvis_task=a014-example
jarvis_tree="$HOME/Work/omarchy-jarvis-$jarvis_task"
git worktree add -b "$jarvis_task" "$jarvis_tree" origin/main
cd "$jarvis_tree"
git status --short --branch
```

Use a unique branch based on `origin/main` (or an explicitly agreed base).
If offline, use locally verified `main` and report that it may be stale — say so,
and treat the claim as provisional until you can push it once back online.
For an existing assigned tree, verify its branch and resume there; do not use
`--force` or `-B` to bypass an occupied branch/path. Worktree creation needs
writable access to both the destination and the repository's shared git metadata.

Before claiming, also inspect QUEUE/SESSION and active scopes in the other
listed trees **read-only** and coordinate with the desk agent — a worktree's own
copy can still be behind `origin/main` between fetches, so `origin/main` (via
`assignment-status.sh`) is the tiebreaker, not any one tree's local file. A
stale `queued` row on `origin/main` older than your own successful push does
not free a task you just claimed; a `queued` row that is actually stale
(crashed agent, abandoned worktree) is released per **Recovering a stale
claim** below, not silently reclaimed. Scope rules still apply; isolation does
not make overlapping product work safe. Shared bookkeeping
(QUEUE/INDEX/SESSION/PROGRESS/ADRs) must be reconciled on merge, preserving
other assignments' statuses and evidence; never overwrite another agent's
SESSION. Live services/ports and the desktop are shared too: coordinate live
testing; do not restart another track's service.

#### Recovering a stale claim

An `in_progress` row can outlive its agent (crash, abandoned worktree, Alex
closed the session). Before reclaiming an `in_progress` id:

1. Check `git worktree list` and the tree named in `docs/SESSION.md`/the QUEUE
   row for that id. If the tree is gone or has no unpushed commits ahead of
   `origin/main` for that branch, and there has been no activity (no new
   commits on its branch, no SESSION update) for a stretch that makes it clearly
   abandoned, it is safe to release.
2. Release on `origin/main` directly: set the row back to `queued` in
   `QUEUE.md`/`INDEX.md`, note the release in `docs/SESSION.md` and
   `docs/PROGRESS.md` (who released it, why, evidence checked), commit, push.
3. If the branch has unpushed work you can still see (a live worktree with
   commits or uncommitted changes), do **not** discard it — flag it to Alex
   instead of releasing or deleting.

Commit only your assignment's files, push your branch, then **land on `main` before you stop**:

```bash
git push -u origin HEAD
# Then merge into main (gh pr create + gh pr merge, or merge locally) and:
git fetch origin && git checkout main && git pull origin main
```

Do not report "done" while the only copy of the work lives on a feature branch.
If merge is blocked, say **BLOCKED ON MERGE** with the PR URL.

After merge, **remove your worktree, delete the merged branch, and return to the canonical `main` checkout before stopping or taking a new CONTINUE/NEW_AGENT prompt** (substitute your slug/branch):

```bash
git -C "$HOME/Work/omarchy-jarvis-a014-example" status --short
git worktree remove "$HOME/Work/omarchy-jarvis-a014-example"
git branch -d a014-example
cd "$HOME/Work/omarchy-jarvis"
git checkout main
git pull origin main
```

Do not claim the next assignment while still inside a finished feature worktree.

Never force removal; retain trees with WIP or an active owner. Squash merges may
make `branch -d` refuse: leave the branch for human review. No helper script is
needed for this small, explicit lifecycle.

## Passes and handoffs

[Passes](docs/passes/README.md) and [handoffs](docs/backlog/handoffs/README.md) each have
INDEX.md, active/ and archive/. New scoped briefs enter active/. On merge/close, move to
archive/ and mark done. Replaced briefs become superseded. Archive rather than delete;
never follow archive as current instructions. Issues, backlog, ADRs and PROGRESS are durable.

## Safety and session done

Read [AGENTS](AGENTS.md) for invariants. Preserve plan → approve → execute, redact secrets
in logs/issues, ask before persisting new skills, keep IPC local, and prepare handoffs only.
For every user-visible feature, add/update [human validation steps](docs/validation/catalog.schema.md) and [FEATURES](docs/FEATURES.md); only the human can mark validation.
Closing behavior work (not docs/process-only) needs a relevant regression artifact — a new or
updated `tests/` case, and a [`docs/evals/`](docs/evals/README.md) entry when it's a named
capability/regression worth pinning — or a documented reason only human/VM validation is
possible (A-028). Run doctor and CI checks, update PROGRESS with results and limitations, link
the PR, check INDEX statuses and keep active passes small. Document journal schema changes.
On a version bump or big behavior change, change VERSION and restart the service (`./scripts/restart.sh`):
the first journal write archives CURRENT and starts a fresh file. Record the reset in
PROGRESS; see [LOGGING](docs/LOGGING.md) for recovery and matching old code to evidence.
For a durable, comparable-across-revisions record of one specific run (not the ephemeral
journal), use `scripts/export-evidence.py <run_id>` — see [docs/evidence/README.md](docs/evidence/README.md).

## Docs map

[START](START.md) · [AGENTS](AGENTS.md) · [README](README.md) ·
[DECISIONS](docs/DECISIONS.md) · [PROGRESS](docs/PROGRESS.md) · [HOST](docs/HOST.md) ·
[MILESTONES](docs/MILESTONES.md) · [backlog](docs/backlog/README.md) ·
[passes](docs/passes/INDEX.md) · [logging](docs/LOGGING.md) · [evidence bundles](docs/evidence/README.md) ·
[improvement ledger](docs/ledger/README.md) · [candidate evals](docs/evals/README.md)
