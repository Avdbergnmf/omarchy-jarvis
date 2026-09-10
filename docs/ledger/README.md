# Improvement Ledger (A-026, v0)

The ledger explains **why** Jarvis's behavior changed. `docs/assignments/QUEUE.md` is
disposable execution work — claimed, done, moved to `done/`, forgotten. The ledger is the
durable record that survives that churn: one **improvement** (`IMP-NNN`) may span several
assignments, a rejected idea, and — eventually — the eval/ledger evidence that justified
shipping it. If you want "what changed and why" across months, read here, not `PROGRESS.md`
(which is a chronological session log, not indexed by improvement) or `QUEUE.md` (which only
ever shows current/recent work).

**v0 is manual and schema-first.** Only **Desk** (a human or the desk-role agent acting for
Alex) creates or mutates ledger records. Runtime, Training, and Forge never allocate an
`IMP-*` id or write to `docs/ledger/` — that integration is explicitly a later assignment (see
Out of scope below). This keeps the ledger a small, deliberate, human-reviewed audit trail
instead of another system that can drift or double-write.

## Layout

```
docs/ledger/
  README.md      ← you are here (authoring rules)
  TEMPLATE.md     ← copy for a new record
  INDEX.md        ← every IMP-*, one row each
  records/        ← IMP-NNN-slug.md, one file per improvement
```

## Record shape

See `TEMPLATE.md` for the exact fields. Two parts to every record:

- **Current summary** — one paragraph, kept up to date. This is what a reader sees first;
  it should never require reading the whole event log to understand where things stand.
- **Events** — append-only. Never edit or delete a past line, even when a later event
  supersedes it (a rejected hypothesis's line stays; a new line records the rejection and why).
  This is what "preserve rejection/abandonment history" means in practice.

## State vocabulary

`hypothesis` → `in_progress` → `shipped` | `rejected` | `abandoned`

This is a small, informal vocabulary for humans to read at a glance — **not** an enforced
state machine. Nothing in this repo validates that a transition is "legal"; Desk sets `Status:`
by hand, same as an assignment's `Status:` field. A record can also sit at `hypothesis`
indefinitely if nothing happened yet, or move straight to `rejected` without ever being
`in_progress`.

## Id allocation (Desk-only, collision-resistant)

`IMP-NNN` ids are monotonic integers, but allocated the same careful way A-039 fixed
assignment claims (see [ADR-038](../DECISIONS.md#adr-038--originmain-is-the-only-place-an-assignment-claim-counts-2026-09-10)):
**never** compute "max id in my local checkout + 1" and write — that's exactly the
branch-local race A-039 exists to prevent, just for a different file. Instead:

```bash
git fetch origin
python3 scripts/ledger-status.py          # validates docs/ledger/INDEX.md and prints the next id
# ... write docs/ledger/records/IMP-NNN-slug.md, add its INDEX.md row ...
git add docs/ledger/
git commit -m "ledger: add IMP-NNN <title>"
git push origin main   # or your current branch, immediately — don't let this sit uncommitted
```

If the push is rejected because `origin/main` moved, `git fetch && git pull --ff-only`,
re-run `scripts/ledger-status.py` for the current next id, and retry — never force-push over
a concurrent ledger write. `scripts/ledger-status.py` also fails loudly (non-zero exit) if
`INDEX.md` and `records/*.md` disagree (duplicate id, an `INDEX.md` row with no matching file,
a record file whose own `# IMP-NNN` header doesn't match its filename, or an `Assignment ids:`
entry that names an id absent from `docs/assignments/INDEX.md`) — run it before trusting the
next-id suggestion, and again before committing.

## Evidence

`Evidence refs:` must be one of:
- `none` — nothing shipped yet, or genuinely no evidence beyond the assignment's own PROGRESS note.
- One or more [A-038](../evidence/README.md) evidence-bundle content-addressed `id`s.
- A bounded inline summary in the record's own Events (a few lines, not a dump) — used for
  everything shipped before A-038 existed, or when exporting a bundle isn't warranted.

An ignored `logs/...` path mentioned in prose is **never** durable evidence on its own —
the whole reason A-038 exists. If you want to actually reference durable evidence, either link
a real bundle `id` or write the bounded summary directly into the record; don't point at a path
that retention (A-006) can delete out from under the claim.

## PERF notes from Training (A-035)

Training → Latency can **Copy PERF note**: a paste-ready Events line with n,
with_mrl, p50/p90/p95/p99, optional version/SHA compare, and a reminder that
budget keys are placeholders. **Desk** pastes that line into an existing IMP
when the numbers belong on the audit trail. Runtime and Training still must
not allocate an `IMP-*` id or write files under `docs/ledger/`. Next id is
whatever `python3 scripts/ledger-status.py` prints after fetching origin/main
(IMP-007 if Desk files one).

## Linking an assignment to an improvement

An assignment brief may set the optional `- **Improvement:** IMP-NNN` metadata field (same
optional-hint pattern as `Blocked-by`/`Gate`, A-037) to point back at the ledger record it's
part of. The ledger record's own `Assignment ids:` field is the forward link (one improvement,
many assignments) — set both directions when you know the improvement before filing the
assignment; it's fine to add the assignment-side link later via a normal edit.

This is **not** the same relationship as A-037's `Gate:` — `Gate` groups assignments for queue
sequencing (a scheduling concern); `Improvement` groups them for "why did we do this" history
(an audit concern). An assignment can have both, neither, or either alone.

## Milestones

A record may optionally note `- **Milestone:** M#` (see `docs/MILESTONES.md`) purely as a
cross-reference for a reader — never an enforced integer stage. Leave it `none` unless the
improvement is genuinely tied to one of the M0–M5 release milestones.

## Out of scope for v0

Runtime or Training writing/allocating ledger records; auto-linking from GitHub issues or
Training's problem queue; enforcing the state vocabulary as a real state machine; a Training
UI for the ledger; replacing `QUEUE.md`/assignments with the ledger — assignments remain the
unit of work, the ledger is the durable record of why.
