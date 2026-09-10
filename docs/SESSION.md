# Session (in-flight agent work)

> Continuations: SESSION + [QUEUE](assignments/QUEUE.md) — not chat logs.

## Active goal
- Assignment: _(none — A-020 done and merged this session; queue has A-019/A-021/A-022/A-023)_
- Branch: `main` (a020-validate-features-ux merged at 791577d and removed)
- Batch: 1 (default; stop and report after each assignment)

## Checklist
- [x] Read START, SESSION, QUEUE; claimed A-020 (priority row)
- [x] Reproduce Verify/Fail; confirm catalog/FEATURES persistence; fix list refresh/removal
- [x] Include-validated: readable report history; re-test without losing history
- [x] Surface/pre-fill/optional run id end-to-end (overlay + API)
- [x] Auto-drive mechanical guided steps; keep judgment + Run approval human
- [x] Tests + ADR; PROGRESS; SESSION; QUEUE/INDEX → done

## Done this session (evidence)
- Desk (Firsty): filed A-020 from Alex Validate-features feedback (persist results, run ids, automate mechanical steps)
- Committed a live bug report (bug-open-cliamp) that was sitting uncommitted in the canonical checkout
- A-020 done: persistence was already correct (existing tests proved it); real bug was the
  guide staying open after a confirmed result. Fixed: guide closes + inline list report on
  confirm; run id now visible in chat footer (copy) + auto-captured by new `kind:"auto"`
  guided steps, which submit their literal prompt via the same `/v1/run` a chat send uses
  (never approves/denies). `feat-overlay-chat` migrated as the reference guide.
- 141 Python tests + all 5 JS suites pass, doctor.sh --syntax passes. VERSION 0.5.6 → 0.5.7;
  ADR-033. Merged latest main (A-021 queued by desk) into this branch during the work.
- Desk also queued A-022 (fix "open cliamp", area:brain) and A-023 (simplify path-scope
  policy, area:docs, `parallel-ok: YES`) while A-020 was in progress; both are open, unclaimed.

## Also queued
- A-019 Proposed-action bubble UX (same overlay area as A-020 → serial)
- A-021 Empty Enter → Skip on report Q&A (`parallel-ok: YES`)
- A-022 Fix open cliamp plan/tooling, issue #15 (area:brain)
- A-023 Simplify path-scope policy (`parallel-ok: YES`, area:docs)

## Next action (one concrete step)
- Queue has four open rows (A-019/A-021/A-022/A-023); no primary in_progress. Claim the next
  claimable one per NEW_AGENT rules and report to Alex and stop per default batch size of 1.

## Parallel agent
- none (overlay serial)

## Blockers
- none

## Training preparation
- Last confirmed assignment save: A-022. Preparation only; no ownership claimed or agent contacted.

