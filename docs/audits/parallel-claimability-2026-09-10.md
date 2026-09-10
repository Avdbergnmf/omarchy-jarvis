# Parallel claimability audit — why the second agent has nothing to take

Date: 2026-09-10
Claim state read from: `origin/main` @ `638c144` (`docs: claim A-028 on main before opening worktree`)
Reconciled through: `origin/main` @ `19ca6c7` (A-028 merged, A-027 cancelled, A-029 claimed) —
see "The queue moved while this pass was open" below.
Scope: claim policy, authoring defaults and the tooling that reads them. No product behavior,
no Agent Monitor UI (A-041), no change to worktree isolation or the claim-on-`origin/main` rule.
**Nothing in this audit depends on branch protection, a protected `main`, or A-027** (cancelled —
[ADR-046](../DECISIONS.md#adr-046--no-github-branch-protection-for-now-a-027-cancelled-2026-09-10)).

## The complaint

A second agent, following `prompts/PARALLEL.txt` exactly, reported:

> Nothing safely claimable right now. A-028 is actively in progress with uncommitted work in its
> isolated worktree, and every queued assignment is marked parallel-ok: NO.

That is a correct reading of the rules. It is also a wrong outcome: three of the queued rows are
in areas nobody is touching.

Live state at the time of filing (`638c144`; it has since moved — see the reconciliation section):

| id | status | area | parallel-ok | unmet Blocked-by | actually contended? |
|----|--------|------|-------------|------------------|---------------------|
| A-028 | in_progress | `area:docs` | NO | none | — (holder) |
| A-029 | queued | `area:actions` | NO | none | no |
| A-033 | queued | `area:brain` | NO | none | no |
| A-041 | queued | `area:overlay` | NO | none | no |
| A-034 | queued | `area:overlay` | NO | A-033 | gated by dependency |
| A-035 | queued | `area:overlay` | NO | A-034 | gated by dependency |
| A-027 | blocked | `area:docs` | NO | none (human) | yes — control plane |
| A-030 | blocked | `area:docs` | NO | A-027, A-028 | yes — control plane |
| A-031 | blocked | `area:docs` | NO | A-028, A-030 | yes — control plane |

Three rows (A-029, A-033, A-041) are dependency-free, in three distinct areas, none of them the
area being worked. Every one of them was refused for one reason only: a `NO` in the
`parallel-ok` column that nobody had revisited since the row was filed.

## How the default drifted to all-NO

This is not one mistake. Six forces all push the same direction, and nothing pushes back.

### 1. The code hardcodes `NO` and the editor cannot undo it

`brain/training.py::prepare_assignment_save` writes the flag as a literal for every
Training-authored assignment:

```python
body = '# '+aid+' — '+fields['title']+'\n\n- **Status:** queued\n- **parallel-ok:** NO\n'
```

and again into the QUEUE/INDEX row (`assignment_row(aid, fields, 'queued', 'NO', path)`).
`parallel-ok` is deliberately absent from `META_FIELDS`/`assignment_fields`, and every later edit
preserves `current['parallel']` — ADR-031 put "status and parallel policy" outside the editor on
purpose. The result is a one-way ratchet: a Training-drafted row is born `NO` and can only become
`YES` if a human hand-edits two files. Nothing in the UI or the desk workflow prompts anyone to.

### 2. The only written default says NO, and there is no matching "otherwise YES"

`docs/assignments/README.md` — "Constraints for good assignments" — says:

> Mark `parallel-ok: NO` for `area:brain` / control-plane by default.

That rule is narrow and correct on its own terms, but it is the *only* guidance in the file, so a
filer reading it infers "NO is the responsible answer." `TEMPLATE.md` reinforces it by listing the
values as `NO | YES`, NO first, in the position every other template field uses for the default.

### 3. The flag asks an unanswerable question at the wrong moment

Parallel safety is a property of a **pair** — this candidate against the set of rows that happen
to be in progress — and it is only knowable at claim time. `parallel-ok` is a property of **one
row**, fixed at filing time, before anyone knows what will be running later. Asked "is this safe
against unknown future work?", the only defensible answer is NO. The field is structurally biased
toward NO no matter who fills it in.

### 4. It silently became a second, unparsed dependency field

The historical values are the proof. From `done/`:

- A-040: `NO while A-039 (docs) is in_progress; claim after A-039 (or PARALLEL only if A-039 done)`
- A-025: `NO (follows A-024)`
- A-007: `NO (serialize before training-mode UI that adds more / commands)`
- A-004: `NO (touches overlay + post-run focus behavior; serialize with A-005 if both in flight — A-004 first)`

Every one of those is an **ordering** statement, not a parallel-safety statement. Since A-037 /
ADR-041 that job belongs to `Blocked-by:`, which *is* parsed and *is* recomputed as blockers
complete. `parallel-ok`'s prose reason lives in the brief where no tool reads it; only the bare
`NO` reaches `QUEUE.md`, where it outlives the situation that justified it forever.

### 5. It is redundant with the check that actually works, and it wins the AND

Since ADR-034 the machine-checked safety property is area disjointness, computed fresh at claim
time from canonical `origin/main` (A-039/ADR-038). `parallel-ok: YES` is a second gate over the
same decision, set by hand, never revisited, ANDed with the first — `assignment-status.sh`'s
claim-hint loop:

```bash
if echo "$row" | grep -qi '| queued |' && echo "$row" | grep -qi '| YES |'; then
```

An AND of a fresh correct check and a stale conservative one always yields the stale one. All
three genuinely-claimable rows today are refused by the stale half.

### 6. `area:docs` is a catch-all, so the fresh check is coarse too

Five areas exist, but `docs` absorbs product documentation, eval specifications, CI, the paste
prompts, ADRs, and the queue itself. Wave 0 is almost entirely `area:docs` (A-027/A-028/A-030/
A-031, plus the process rows A-023/A-037/A-039/A-040). One docs row in progress serializes every
other docs row — correctly when both rewrite `START.md`, incorrectly when one is writing
`docs/evals/` and `ci.yml`. That over-serialization is part of why filers reach for `NO`: they
have watched docs rows block each other and generalized the wrong lesson.

## The thing ADR-034 got right, and the thing it left unfixed

ADR-034's evidence was real: A-020 and A-021 both ran `area:overlay` in separate worktrees, both
landed good code, and merging them produced conflicts in `docs/PROGRESS.md`, `docs/SESSION.md`,
`docs/assignments/QUEUE.md` and `INDEX.md` that a later session had to stop and untangle.

But look at *which* files conflicted. Not `overlay/app.js` versus `overlay/validation.js` — those
merged fine. The conflicts were entirely in **shared bookkeeping**, and shared bookkeeping is
touched by every assignment regardless of area. Area disjointness did not fix that problem; it
only reduced how often two agents were running at all, which hid it.

Two independent pieces of evidence confirm the bookkeeping problem is not about parallelism:

- **The ADR-number collision.** A-026 had to renumber its ADR from 043 to 044 at merge time
  because A-041's stub had already taken 043 (`ffde097 fix: renumber ADR-043 -> ADR-044`). Both
  were appending to the end of `docs/DECISIONS.md` with no reservation step.
- **Conflicts with no parallel agent at all.** PROGRESS records "Rebased onto main after A-038
  merge + A-026 claim (PR #18 had conflicts against stale branch base)" — a purely *serial*
  workflow, conflicting on the same shared docs, because the branch base was stale.

So the honest decomposition of parallel risk is four separate problems, only one of which
`parallel-ok` was ever suited to express:

| risk | what actually protects against it today |
|------|------------------------------------------|
| Two agents writing the same product surface | `area:` disjointness (ADR-034) — works |
| One assignment needs another's output first | `Blocked-by:` (ADR-041) — works, recomputed live |
| Two agents redefining the claim/approval/promotion machinery | nothing structural; this is the *only* legitimate job for `parallel-ok: NO` |
| Merge conflicts in QUEUE/INDEX/SESSION/PROGRESS/DECISIONS | nothing; every agent hand-merges and hopes |

`parallel-ok` has been carrying all four, and the way a single binary flag carries four
responsibilities is by being `NO`.

## Options considered

### Option 1 — Computed claimability with a reasoned kill-switch (recommended)

Stop treating the *absence* of `YES` as a refusal. Claimability is computed from the three things
already machine-readable on `origin/main`: status, unmet `Blocked-by`, and area disjointness. The
`parallel-ok` column stays exactly where it is, but its default inverts to `YES`, and `NO` narrows
to a short closed vocabulary of reasons that describe a property of the row itself rather than a
guess about future pairings.

- **Cost:** docs and flag flips. The claim algorithm's *shape* does not change, so
  `assignment-status.sh` and the prompts keep working unmodified — flipping the flags alone
  restores relief today. Tooling changes (default in `training.py`, reason display, stale-NO
  warning) are follow-up polish, not prerequisites.
- **Pros:** one authoring decision, answerable at filing time ("does this row redefine the control
  plane?"). Ordering moves to `Blocked-by` where it is already recomputed. No table churn, no new
  column, no rename of a field five files parse positionally.
- **Cons:** the flag still exists and can still be set wrongly; the forcing function is a required
  reason plus a tooling warning, not an impossibility. Does not by itself fix `area:docs` breadth.

### Option 2 — Split `area:docs` into `area:docs` + `area:control-plane`

Make the area check itself precise enough that no flag is needed: product docs and eval specs stay
`area:docs`; `START.md`, `AGENTS.md`, the paste prompts, the assignment machinery, CODEOWNERS and
promotion policy become `area:control-plane`. "Single writer for the control plane" then falls out
of the existing area rule as a machine-checked consequence.

- **Cost:** `AREAS` is a closed tuple in `brain/training.py` and `scripts/agent-status.py`; the
  five GitHub area labels exist on the real repository; every open row's area needs review, and
  a docs row in progress must never be re-areaed underneath its agent (true of A-028 when this
  was written, of A-030 whenever it is claimed).
- **Pros:** strictly better precision than any flag, and it retires the "is this control plane?"
  judgment call by encoding it once in the area. Worth more now that A-027 is cancelled: with no
  ruleset behind `control-plane`, the label's only value is telling a human reviewer where to
  look, and an `area:` does that at claim time without anyone having to remember to write it.
- **Cons:** not safe to do while a docs row is in progress, and it re-opens ADR-034's "one simple
  check" simplicity. Right idea, wrong week. Recommended as an evaluated follow-up inside A-042,
  with the decision deferred to Alex rather than taken unilaterally.

### Option 3 — Leave the policy alone; add an explicit Alex override

Keep every flag as-is and let Alex say a phrase ("force parallel A-033") that authorizes claiming
an area-disjoint `NO` row, mirrored later by a Training "force parallel" control.

- **Cost:** near zero.
- **Pros:** immediate, reversible, no policy argument needed.
- **Cons:** it makes Alex the scheduler for every parallel claim — precisely the friction he is
  complaining about — and it legitimizes leaving the flags permanently wrong. It also teaches
  agents that the written rule is advisory, which is corrosive for every *other* rule in START.
  Worth keeping as a documented escape hatch; not worth adopting as the policy.

### Also evaluated, folded into the recommendation rather than run as options

- **Drop the flag entirely, no kill-switch.** Attractive, but there is one genuine case the area
  rule cannot see: two agents in different areas both redefining the claim/approval/promotion
  machinery (this audit's own A-042 versus a hypothetical `brain/training.py` redesign). Keeping a
  narrow, reasoned `NO` costs one column that already exists and preserves the "single writer for
  brain/control plane" invariant that AGENTS.md requires.
- **A dedicated bookkeeping-writer role.** One agent owning all QUEUE/SESSION merges reintroduces
  a serialization point and needs that agent to be online. The cheaper fix for the same problem is
  an append-only discipline plus reserving the ADR number in the claim commit — the two observed
  failures (ADR-043/044, PR #18's stale base) are both prevented by protocol, not by an owner.
- **Making `parallel-ok: NO` mutually exclusive** (an in-progress `NO` row blocks everything).
  Rejected: it is strictly worse for today's situation, since A-028 is `NO` and would then block
  the very rows we are trying to free. `NO` stays *self*-restricting — a statement about when this
  row may be claimed, not a lock on the repository.

## Recommendation

**Adopt Option 1 now; carry Option 2 into A-042 as an evaluated proposal; keep Option 3 as a
documented escape hatch.**

Claimability is **computed, not declared**. A row is claimable when the queue says it is ready,
its dependencies are met, and nobody is working its area. `parallel-ok: YES` becomes the default
and stops being a gate for ordinary work. `parallel-ok: NO` survives as a narrow, *reasoned*
kill-switch for rows that would race the control plane itself, and every `NO` must name which of
three reasons applies:

- `control-plane` — the change redefines authorization, promotion, evaluation, trust, or the claim
  rules themselves (A-030, A-031, and A-042).
- `single-writer` — the change redesigns a shared runtime seam that cannot tolerate a concurrent
  writer even from another area (`brain/server.py`'s approve/execute or planner routing, the
  journal writer).
- `human-serial` — Alex asked for this one to run alone.

A bare `NO` with no reason is a filing bug. Tooling should print it as a warning and the desk
should treat it as `YES` pending review — not silently honor it for six weeks, which is exactly
how we got here.

`control-plane` here means **single-writer-by-review**, not "a ruleset will catch it." A-027 is
cancelled and `main` will not be API-enforced (ADR-046), so human review is the only enforcement
this repository has. That makes the written reason load-bearing rather than decorative: an
unexplained `NO` gives a reviewer nothing to review, and there is no second line of defence behind
them.

### Exact claim algorithm

Canonical inputs come from `origin/main` only (A-039/ADR-038); `index_status` reads `INDEX.md`,
not `QUEUE.md`, because `done` rows leave the queue table (ADR-041).

```
claim_candidates(queue, index, in_progress):
    for row in queue in queue order:
        if row.status != "queued":                      continue   # not offered
        if any(index[b] != "done" for b in row.blocked_by): continue   # ADR-041
        if in_progress is empty:                        return row     # first ready row wins
        if row.parallel_ok == "NO":                     continue   # reasoned kill-switch only
        if row.area in {p.area for p in in_progress}:   continue   # ADR-034
        yield row                                                  # claimable in parallel
```

Unchanged around it: the claim commit lands on `origin/main` *before* `git worktree add`; each
concurrent agent gets its own worktree and branch; an in-progress `NO` row does not block anyone
else; `Allowed paths:`/`Forbidden paths:` never gate a claim.

The only structural change to the algorithm versus today is that `row.parallel_ok == "NO"` is now
rare and reasoned instead of universal and inherited. That is deliberate: the shape stays
identical so the existing `assignment-status.sh` and paste prompts keep producing correct answers
the moment the flags are corrected, with no code change on the critical path.

### One risk the area rule still cannot see

`brain/server.py` and `brain/training.py` are reached into from more than one area. A-029
(`area:actions`) says it may touch `brain/server.py` "only if run provenance is required";
A-033 (`area:brain`) instruments the same request path; A-041 (`area:overlay`) edits
`brain/training.py`; A-042 (`area:docs`) changes two lines in the same file. Under the area rule
several of those pairs may legally run at once.

The right response is *not* to re-harden path lists into a gate — ADR-034 settled that, and both
files are additive-friendly. It is to make the overlap **visible at claim time**: the claim hint
should compare the candidate's soft path hints against every in-progress row's and print a
non-blocking `HEADS-UP` line. That restores the useful half of path lists (a human noticing) without
restoring the half that mis-fired for A-021 (a machine deciding). It is a checklist item in A-042.

## Immediate relief applied in this pass

Flipped to `parallel-ok: YES` in `QUEUE.md`, `INDEX.md` and each brief:

| id | area | why it is safe against A-028 (`area:docs`, in progress) |
|----|------|----------------------------------------------------------|
| A-029 | `area:actions` | Preference memory in `actions/core.py` + `~/.config/jarvis/`; no docs/control-plane surface. Its `Gate: control-plane` label is informational grouping (ADR-041), not an authority change. |
| A-033 | `area:brain` | Additive latency spans/store; disjoint from docs. `area:brain` alone is not a reason for `NO` — the reason must name a single-writer surface, and diagnostic instrumentation is not one. |
| A-034 | `area:overlay` | Still gated by `Blocked-by: A-033`; flipped for consistency so the flag stops doubling as ordering. |
| A-035 | `area:overlay` | Still gated by `Blocked-by: A-034`; same reasoning. |
| A-041 | `area:overlay` | Agent Monitor UI. Overlaps `brain/training.py` with A-042 — recorded as a soft hint in both briefs, not a gate. |

Left at `NO`, with reasons now written in:

- **A-030** `NO (control-plane: CODEOWNERS and authority-surface classification)`
- **A-031** `NO (control-plane: protected evaluator, oracles and baselines)`
- **A-028** untouched while it was in flight in a dirty worktree — re-classifying a live row's flag
  from another branch is exactly the shared-bookkeeping race this audit is about, and its `NO` was
  self-restricting so leaving it cost nothing. It has since merged.
- **A-027** was `NO (control-plane)` and is now cancelled outright (ADR-046); its row moved to
  `done/` on `main`.

Net effect with A-028 in progress: **three claimable rows (A-029, A-033, A-041) instead of zero**,
using the unmodified `assignment-status.sh` and paste prompts.

Verified end to end rather than by inspection. This branch was pushed as `main` into a throwaway
bare origin and cloned, so the real script read a real `origin/main`:

```
Candidate (area:actions differs from every in_progress area):   | A-029 | … | queued | area:actions | YES | …
Candidate (area:brain differs from every in_progress area):     | A-033 | … | queued | area:brain   | YES | …
Skipping A-034 (queued but Blocked-by A-033 not done yet)
Skipping A-035 (queued but Blocked-by A-034 not done yet)
Candidate (area:overlay differs from every in_progress area):   | A-041 | … | queued | area:overlay | YES | …
```

A-042 is correctly withheld (`NO`), and the same script against a clone of `638c144` still prints
`No assignment in queue is possible right now` — the reported bug, reproduced and then fixed by
flag values alone, with no code on the critical path.

## The queue moved while this pass was open

Between filing and merge, `origin/main` advanced from `638c144` to `19ca6c7`: **A-028 merged**
(taking ADR-045), **A-027 was cancelled** (ADR-046 — Alex will not buy Pro and will not make the
repo public, so branch protection is unavailable, not pending), **A-030 became `queued`**, and
**A-029 was claimed** and is now `in_progress`. Everything above was re-derived against that
state; the tables dated `638c144` are kept as the evidence for the original complaint.

Current claim set with A-029 (`area:actions`) in progress, re-verified the same way against the
merged branch:

| id | area | verdict |
|----|------|---------|
| A-033 | `area:brain` | **claimable** |
| A-041 | `area:overlay` | **claimable** |
| A-034 / A-035 | `area:overlay` | skipped — unmet `Blocked-by` (A-033 / A-034) |
| A-030 | `area:docs` | withheld — `NO (control-plane)`; also same area as A-042 |
| A-042 | `area:docs` | withheld — `NO (control-plane)`, by design; it rewrites the claim rules |

Three things this changes, and one it does not:

- **A-029 is now the in-flight row, and it keeps the `YES` this pass gave it.** The flag was
  corrected before the claim landed, and an `in_progress` row's `parallel-ok` is never read by the
  algorithm — it filters candidates only. So the value is behaviourally inert here and the edit is
  a one-line metadata correction on a line its working agent does not touch. Reverting it would be
  a larger edit to the same live file *and* wrong on the merits.
- **A-030 is claimable-by-status but still correctly `NO (control-plane)`.** A-027's cancellation
  removed its dependency, not its nature: producing the authority/ownership map is exactly one
  writer's job. That it will never be mechanically enforced afterwards is an argument for keeping
  the single-writer discipline, not for dropping it.
- **The `control-plane` reason class must not be read as "protected."** Post-ADR-046 there is no
  ruleset behind it. See the note under the recommendation.
- **Nothing in the recommendation moved.** No part of this policy waited on A-027, protected
  `main`, CODEOWNERS-as-a-gate, or unattended Forge, so the cancellation removes text but changes
  no decision. Human-reviewed merges continue unchanged.

## Shared bookkeeping: the protocol the flag was standing in for

Adopted alongside the claim rule, because "we will conflict on the shared docs" is the real fear
behind most `NO`s and it needs its own answer:

1. **Reserve your ADR number in the claim commit.** The same push to `origin/main` that flips your
   row to `in_progress` appends a one-line reserved stub to `docs/DECISIONS.md`. It has already
   bitten once (A-026 renumbered 043 → 044 at merge time) and would have bitten again here: A-028
   is in flight and will want the next free number, so this pass had to step around it by hand.
2. **QUEUE/INDEX: your own row only.** Never reorder rows and never rewrite the prose block under
   the table while in flight; add your narrative line at merge time. Row-per-assignment means git
   merges cleanly on its own.
3. **SESSION: your own lines only.** Your Active-goal bullet, your checklist line, your
   `## Parallel agent` entry. Never rewrite another agent's.
4. **PROGRESS: append at the end.** A new dated `## YYYY-MM-DD — A-NNN …` section. Never edit an
   existing section, even to fix it.
5. **Rebase immediately before merging.** PR #18's conflicts came from a stale base, with no
   parallel agent involved at all.

This pass then proved rule 1 in both directions inside a single day. It reserved **ADR-045** for
in-flight A-028, and A-028 took exactly that number when it merged — the reservation worked.
Meanwhile the A-027 cancellation was written straight onto `main` with no reservation and took
**046**, the number this pass was already using, forcing a renumber to **047** at merge time.
That is the second ADR renumber in two days (A-026's 043 → 044 was the first), both caused by the
same missing step, and it is the entire argument for the rule.

## Out of scope / not done here

- No Agent Monitor UI work (A-041 stays queued and unimplemented).
- No change to worktree isolation (ADR-024), claim-on-`origin/main` (ADR-038), `Blocked-by`/`Gate`
  (ADR-041), or the no-silent-spend rules.
- No product code. The `brain/training.py` hardcoded `NO`, the `assignment-status.sh` reason
  display and stale-NO warning, the `scripts/agent-status.py` issue-side rules that still
  contradict ADR-034, and the paste-prompt rewrites are all filed as **A-042**.
- Observed but not fixed: `tests/test_journal.py::test_write_prunes_journal_archive_on_rotation`
  fails roughly half the time on clean `main` — 9 of 10 runs at `638c144` in a fresh checkout,
  4 of 10 on this branch, same machine and filesystem, so it is a race and not a regression from
  this pass. `journal.prune` orders candidates by `p.stat().st_mtime`, a Python float whose usable
  precision at current epoch values is about a microsecond; two archives written closer together
  than that compare equal and sort arbitrarily, so `prune` can delete the *newest* archive and
  keep an older one. Switching the sort key to `st_mtime_ns` looks like the whole fix. It is real
  (bounded retention silently keeping the wrong file) and it is `area:brain` — so it wants its own
  row rather than a drive-by from a docs pass.
- Nothing here waits on, assumes, or restores branch protection. A-027 is cancelled (ADR-046):
  `main` stays human-reviewed and is not API-enforced, unattended Forge and auto-merge stay off,
  and no rule in this audit would behave differently if protection existed.

## Follow-up proposal (A-042): split `area:docs` → `area:docs` + `area:control-plane`

**Decision: deferred to Alex. A-042 does not change `AREAS`, GitHub labels, or any row's `area:`.**

Option 2 of this audit is still the right precision fix: product documentation and eval
*specifications-as-docs* stay `area:docs`; the claim/approval/promotion machinery becomes
`area:control-plane`, so "single writer for the control plane" falls out of the existing
area-disjointness check instead of living in a flag.

### What would move (open and recently closed)

Live queue at A-042 closeout is empty after this row lands. The interesting set is historical
Wave 0 / process rows that were `area:docs` because that was the catch-all:

| id | current area | proposed | why |
|----|--------------|----------|-----|
| A-027 | docs (cancelled) | control-plane | promotion / Forge actor |
| A-028 | docs (done) | control-plane | candidate-eval foundation, oracles |
| A-030 | docs (done) | control-plane | CODEOWNERS + authority map |
| A-031 | docs (done) | control-plane | protected evaluator / stochastic cases |
| A-037 | docs (done) | control-plane | Blocked-by/Gate claim machinery |
| A-039 | docs (done) | control-plane | claim-on-`origin/main` protocol |
| A-040 | docs (done) | docs *or* control-plane | test-suite policy / CI wrappers — Alex's call |
| A-042 | docs (this row) | control-plane | claim-rule / Training default tooling |
| A-026 | docs (done) | control-plane | ledger schema is Control Plane (ADR-050) |
| A-001 / A-002 / A-013 / A-023 | docs (done) | docs | process prose, not the machinery |
| A-032 | docs (done) | docs | review artifact |

No currently queued product-docs row would move. Future filings that rewrite `START.md`,
`AGENTS.md`, paste prompts, `assignment-status.sh`, CODEOWNERS, promotion policy, or the
ledger/eval schemas should be born `area:control-plane`.

### Code and labels that would have to change

- `AREAS` is a closed tuple in **two** places: `brain/training.py` and `scripts/agent-status.py`
  (`('overlay', 'brain', 'actions', 'skills', 'docs')`). Adding `control-plane` is a coordinated
  edit of both, plus Training's area picker UI (A-041's Agent Monitor is out of this proposal's
  implement scope; it would start accepting the new value the moment `AREAS` grows).
- Five GitHub area labels exist on the real repository (`area:overlay`, `area:brain`,
  `area:actions`, `area:skills`, `area:docs`). A sixth (`area:control-plane`) has to be created
  **before** any issue or assignment uses it, or `agent-status.py` will park those issues under
  `unassigned`.
- `docs/assignments/TEMPLATE.md`, `START.md`'s area list, `.github/ISSUE_TEMPLATE/*`, and
  `docs/templates/ISSUE_{BUG,FEATURE}.md` all enumerate the five areas.

### Safe migration for in-flight rows

Do **not** re-area a row while it is `in_progress`. That is the shared-bookkeeping race this
audit already named: another agent's claim hint would change under them. Sequence:

1. Create the GitHub label. Land the `AREAS` tuple + template/START enumeration in one PR with
   no row-area edits (queued rows keep `area:docs` and remain serialized with each other until
   step 2).
2. Desk pass: retag **queued** (not `in_progress`) rows whose briefs are control-plane work.
   `done/` / `cancelled` rows stay historical; rewriting them is optional and must not be
   mixed with a live claim.
3. Only after step 2 has been on `origin/main` may a new `area:control-plane` row be claimed
   beside an `area:docs` row.

Until Alex takes this, `parallel-ok: NO (control-plane)` remains the kill-switch that covers
the same set, at the cost of a flag instead of an area.
