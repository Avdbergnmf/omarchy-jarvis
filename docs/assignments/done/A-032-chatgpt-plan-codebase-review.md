# A-032 — ChatGPT deep review: self-improve plan vs codebase (plan perfection)

- **Status:** done
- **Area:** area:docs
- **parallel-ok:** NO (serial — **do this before** Wave 0 implementation A-026…A-031)
- **Soft path hints:** `docs/SELF_IMPROVE_ROADMAP.md`, `docs/audits/`, `START.md`, `docs/DECISIONS.md`, `docs/assignments/`, `docs/validation/`, `docs/LOGGING.md`, `docs/backlog/features/feat-self-improve-*`, skim `brain/`, `overlay/`, `actions/`, `tests/`, `scripts/` for evidence only
- **Reserved for:** ChatGPT / Sol 5.6 (ultra-high depth) — Alex 2026-09-10
- **Links:** ChatGPT 70-point plan + 8 answers; Firsty audit; current Wave 0 queue

## Goal

## Important: no prior chat history

You were **not** in the Alex↔ChatGPT↔Firsty discussion. Do **not** expect paste of that thread.

Read first:
1. [`docs/audits/chatgpt-self-improve-discussion-brief-2026-09-10.md`](../../audits/chatgpt-self-improve-discussion-brief-2026-09-10.md) — distilled discussion + 8 answers + sequence
2. [`docs/SELF_IMPROVE_ROADMAP.md`](../../SELF_IMPROVE_ROADMAP.md) — current adopted decisions / Wave 0
3. Then the rest of the “Must read” list below against the **codebase**

Your job is to **stress-test and improve** that plan using repo evidence, not to rediscover product goals from scratch.

**Batch size = 1:** complete **only A-032**, then stop and report. Do not start A-026…A-031 implementation.

Read the **self-improve roadmap and related docs next to the real omarchy-jarvis tree**, then produce an **improved, codebase-grounded plan** Alex can adopt before implementing Wave 0.

You are **not** implementing Runtime/Forge features in this assignment. Output is planning artifacts + recommended queue edits.

### Must read (in order)
1. `docs/SELF_IMPROVE_ROADMAP.md` (authoritative decisions)
2. `docs/audits/chatgpt-self-improve-plan-audit-2026-09-10.md` (stub — expand if thin)
3. `START.md`, `docs/DECISIONS.md` (esp. worktrees, Training, validation, honesty, preferences)
4. `docs/assignments/QUEUE.md` + active A-026…A-031 briefs
5. `docs/LOGGING.md`, `docs/validation/` (+ FEATURES), `docs/backlog/features/feat-self-improve-*`
6. Skim implementation evidence: `brain/server.py`/`journal.py`, Training overlay modules, `actions/` open-app prefs, `scripts/restart.sh`/`doctor.sh`, test layout

### Deliverables (write into the repo)
1. **`docs/audits/chatgpt-plan-vs-codebase-review-2026-09-10.md`** — structured review:
   - What the roadmap gets right (with file evidence)
   - Gaps, contradictions, or overreach vs current code
   - Per Wave 0 assignment (A-026…A-031): keep / reshape / split / defer + why
   - Missing prerequisites discovered only by reading the tree
   - Risks if we implement Wave 0 “as written”
2. **`docs/SELF_IMPROVE_ROADMAP.md`** — propose a concrete patch (edit in place **or** add `docs/SELF_IMPROVE_ROADMAP.proposed.md` if you want Alex to diff-approve first; prefer in-place if changes are clearly better and call them out in PROGRESS)
3. **Queue recommendation** — update `docs/assignments/QUEUE.md` / active briefs **only** where the review proves a change (reorder, tighten checklists, add A-033+ stubs if needed). Do not start implementing ledger/CI/memory code.
4. **PROGRESS + SESSION** — what changed; next action = implement revised Wave 0 (or Alex sign-off)

### Review lens (from ChatGPT north star)
- Runtime / Desk / Forge / Control Plane boundaries
- Ledger wraps QUEUE (`improvement_id` vs `assignment_id`)
- Journal tiers (ephemeral vs durable vs git-versioned truth)
- Unattended PRs + protected promotion
- Capability vs regression + stochastic consistency
- Protected eval/safety paths
- Memory provenance (explicit ≠ inferred)
- Snapshots only when system-affecting
- Prefer evidence, provenance, boundaries, promotion discipline over more “self-reflection” machinery

## Checklist
- [x] Read roadmap + assignments + key code/docs listed above (cite paths in the audit)
- [x] Write `docs/audits/chatgpt-plan-vs-codebase-review-2026-09-10.md`
- [x] Revise roadmap (in place or `.proposed.md`) with clear delta from prior version
- [x] Adjust QUEUE / A-026…A-031 briefs only as justified by the review
- [x] PROGRESS + SESSION; mark this assignment done; **do not** implement Wave 0 product code here
- [x] **Stop after A-032** — report to Alex; do not claim A-027/A-026/…

## Resolution

- Kept the four-subsystem north star, but grounded its boundaries and autonomy gates in the
  current approval, Training, journal, validation, action, skill, CI and deployment code.
- Reshaped A-026…A-031, blocked dependencies explicitly, and added A-038 for exact evidence
  identity and durable private bundles. Concurrent mainline A-033…A-037 assignments were
  preserved during rebase.
- Verified the external A-027 blocker through GitHub's live ruleset and branch-protection
  APIs. No repository visibility, hosting, Runtime behavior or shared service was changed.
- Evidence: 153 Python tests, all five JavaScript test suites, shellcheck,
  `./scripts/doctor.sh --syntax`, assignment status and `git diff --check` pass.

## Out of scope
Implementing ledger/CI/CODEOWNERS/memory/stochastic runners beyond docs/plan; rewriting Runtime features; spending other agents; silent push to bypass future main protection discussions.

## Notes for the coding agent
- Model: Sol 5.6 ultra-high depth — prefer thorough evidence over speed.
- Token discipline still applies: read large files once; quote sparingly; prefer path+symbol citations.
- Worktree OK; this is docs-only so canonical checkout is acceptable if alone on docs.
