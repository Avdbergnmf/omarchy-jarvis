# A-032 review — self-improve plan versus the Jarvis codebase

Date: 2026-09-10
Code review base: `4bf8747`
Planning state reconciled through: `8b86cc0` (`origin/main`)
Scope: planning and assignment changes only; no Runtime, Forge, CI, memory, or deployment implementation

## Decision

Keep the north star and the Runtime / Desk / Forge / Control Plane model. They fit this
repository better than an in-process self-rewriter. Do not begin unattended Forge work yet.

Wave 0 was directionally right, but it was not executable as written. The grounded plan
needs four corrections:

1. **Protected promotion is externally blocked.** The repository is private. Live reads of
   both `repos/Avdbergnmf/omarchy-jarvis/rulesets` and
   `repos/Avdbergnmf/omarchy-jarvis/branches/main/protection` returned HTTP 403 with
   “Upgrade to GitHub Pro or make this repository public to enable this feature.” Alex must
   choose Pro, public visibility, or another enforceable host. Documentation and CODEOWNERS
   alone are not a hard gate.
2. **The draft conflated four evidence systems.** Unit/CI verification, the run journal's
   anomaly heuristic, human feature validation, and candidate behavioral evals have
   different authors, oracles, retention, and trust. A-028 must create a separate candidate
   eval registry instead of relabeling `docs/validation/catalog.json`.
3. **Evidence identity and durability are missing prerequisites.** Current journals are
   private and useful, but local-only and intentionally pruned. They also identify only
   Jarvis version and git describe, not exact model/prompt/tool/planner inputs. Add A-038
   before the ledger and candidate eval work.
4. **The Control Plane is conceptual, not physically isolated.** Approval, execution,
   Training writes, human validation, and trusted skills are mixed into Runtime files.
   A-030 must protect the actual authority-bearing surfaces and acknowledge coarse file
   boundaries; a CODEOWNERS file covering only future `docs/evals/` would leave the current
   trust path exposed.

While the review was in progress, `main` added A-033–A-037. Reconciliation preserved the
A-033–A-035 latency wave and Alex's A-036→A-037 dispatch-usability priority. The newly found
evidence prerequisite therefore uses A-038; it does not displace those assignments.

The revised dependency graph is:

```text
Alex accepts A-032
        |
        +--> A-027 hard promotion gate --blocked on external choice/actor--+
        |                                                               |
        +--> A-038 evidence identity + durable bundles --> A-028 -------+--> A-030 --> A-031
                                                    |
                                                    +--> A-026 --> A-029
```

A-038, A-026, and A-028 may be built under today's **current human-only branch/merge
discipline** while A-027 is blocked. This does not authorize unattended PRs. A-030 cannot
claim enforcement until both A-027 and A-028 are complete; A-031 cannot become a promotion
signal until A-030 protects its cases and oracle.

## What the roadmap gets right

### The product already has a real approval boundary

- `brain/server.py::commit_plan` parks executable plans in `awaiting_approval` under the
  default `approval_mode = "always"`; `handle_approve` executes the stored plan and denial
  releases the single-run lock.
- `brain/server.py::validate_call`, `PLAN_SCHEMA`, and `tool_argv` constrain model output to
  typed, known actions. ADR-011 caps normal requests at one action.
- Deterministic report/correction routes are excluded from the model's tools in
  `LLM_EXCLUDED_TOOLS`, matching the principle that weak local planning should not own
  sensitive composition.
- `scripts/skill-draft.py` reviews exact bytes and installs only a matching SHA-256 digest.

This is a strong Runtime safety base. The self-improve plan should extend it rather than
replace it with reflection loops.

### Desk exists and stays human-mediated

- `brain/training.py::prepare_assignment_save` previews exact brief/QUEUE/INDEX/SESSION
  changes. `store_preview` freezes their bytes, and `confirm` rejects stale inputs before
  atomic replacement.
- `brain/training.py::generate_assignment` makes either a local schema-constrained draft or
  a prompt for a manually chosen coding agent; it writes, claims, and sends nothing.
- `scripts/open-agent.py` opens a visible terminal. The handoff remains paste-ready; there is
  no autonomous agent scheduler or sender.
- `START.md`, `docs/assignments/README.md`, and `scripts/assignment-status.sh` already encode
  assignment ownership, batch limits, isolated worktrees, and shared-service coordination.

This validates the Desk/Forge split. “Unattended PRs” are a future autonomy level, not a
description of current behavior.

### Existing evidence is deliberately conservative

- `brain/journal.py::evaluate` compares approved versus executed calls and labels desktop
  success `suspicious` because return codes do not prove effects. It does not silently grade
  user intent as passed.
- `brain/validation.py` hashes each human guide definition and accepts Verify/Fail only
  through Training's reviewed preview. `docs/validation/catalog.schema.md` explicitly says
  automated checks never manufacture human evidence.
- `.github/workflows/ci.yml` runs syntax, Python unit tests, shellcheck, and one browserless
  overlay suite. Recent GitHub workflow runs were green; the latest inspected job was
  `checks / test` in run `34467915129`.
- ADRs, PROGRESS, assignment briefs, issue mirrors, validation definitions, and behavior
  rules are versioned in git while private prompts and logs remain ignored.

The roadmap is correct to invest in evidence quality and provenance before more autonomy.

### A small preference store is the right memory seed

`actions/core.py` already has a narrow, useful memory seam:
`APP_PREFS_PATH`, `load_app_prefs`, `ranked_apps`, and `correct_open`. The store changes only
app-match tie-breaking and keeps a short-lived `last_open`. Extending this specific seam is
safer than introducing general episodic or vector memory.

## Actual subsystem boundary

| Subsystem | Current implementation | Grounded implication |
|---|---|---|
| Runtime | `brain/server.py`, `actions/`, `skills/examples/`, chat overlay | The model proposes typed calls; execution still happens in a process that also holds approval state. |
| Desk | Training portions of `brain/training.py`, Training overlay, assignments/backlog/handoffs | Desk can prepare and confirm repo writes, but it shares the Runtime process and working tree. |
| Forge | Isolated worktrees plus manually opened Claude/Codex terminals | There is no unattended Forge controller, budget, credential boundary, or PR loop today. Keep it that way until promotion is enforceable. |
| Control Plane | Approval/auth code in `brain/server.py`; preview/confirm in `brain/training.py`; `brain/validation.py`; CI; policy docs; skill digest flow | It is spread across mixed-purpose files. Protection must initially be coarse, then later extraction can sharpen boundaries. |

The table is an ownership map, not a claim that processes are isolated. A future agent must
not infer that “Control Plane” is already a separate service or repository.

## Evidence systems that must remain distinct

| Evidence | Current source | What it can establish | What it cannot establish |
|---|---|---|---|
| Deterministic verification | `tests/`, `doctor.sh --syntax`, GitHub `checks / test` | Code-level contracts on a known revision | Real desktop intent or model reliability |
| Runtime anomaly journal | `logs/journal/*.jsonl`, `brain/journal.py::evaluate` | What was requested/planned/reported; plan/execution mismatch | A candidate pass/fail grade or durable audit after local pruning |
| Human feature validation | `docs/validation/catalog.json`, Training Verify/Fail | Alex observed a defined behavior on a recorded version | Repeatable CI, stochastic consistency, or independent evaluation |
| Candidate behavioral evals | Not implemented | Future capability/regression comparisons under a pinned envelope | Human acceptance or authorization to merge/deploy |

`docs/validation/catalog.json` also stores both guide definitions and mutable result state.
That is acceptable for its current human workflow, but it is a poor protected grader: feature
PRs are required to update guides, and confirmed human runs update result fields in the same
file. A-028 should create `docs/evals/` rather than overload this catalog.

## Gaps and contradictions found in the tree

### 1. A-027 cannot currently deliver its stated hard gate

The live repository is `PRIVATE`. GitHub's APIs returned the same plan/visibility 403 for
rulesets and classic branch protection. GitHub documents that both are available for public
repositories on Free and private repositories on Pro/Team/Enterprise:

- [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

Making a private repository public is a material privacy decision and must not be an agent
fallback. Until Alex chooses an enforceable option, A-027 is blocked and unattended Forge
must remain disabled.

There is a second authority issue: current automation uses Alex's local `gh` login. A future
unattended Forge must use an identity/credential that can push candidate branches and open
PRs but cannot bypass protection or supply Alex's approval. Otherwise the same actor proposes
and promotes. A-027 must verify actors and bypass lists, not just settings screenshots.

CODEOWNERS is advisory without an enforced code-owner review rule. GitHub's own documentation
ties required code-owner review to branch protection and recommends owning the CODEOWNERS
file itself: [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

### 2. CI exists, but its JavaScript coverage is incomplete

`.github/workflows/ci.yml` runs `tests/overlay.test.cjs` only. The repository also contains
`agents.test.cjs`, `assignments.test.cjs`, `training.test.cjs`, and `validation.test.cjs`.
Local progress notes routinely claim all suites, but the protected status check would not
run four of them. A-028 must make the deterministic candidate baseline comprehensive before
it is treated as a promotion signal.

The latest green run proves the current workflow runs; it does not prove omitted suites.
The required check should have one stable, unique name (`checks / test`) and workflow changes
must themselves become protected under A-030.

### 3. Runtime evidence is not durable enough for ledger references

`.gitignore` excludes all `logs/`. `docs/LOGGING.md` and `brain/journal.py` intentionally cap
per-run logs at 200, debug logs at 200, and version archives at 20. `CURRENT.jsonl` has no byte
cap and rotates on a version change. There is no configured backup or immutable evidence
bundle. An `IMP-*` record that only points at `logs/runs/<id>.log` can therefore outlive its
evidence, while blindly committing or backing up raw prompts would violate privacy.

The journal envelope records `jarvis_version` and `git_describe`, but not:

- exact Ollama model digest (a mutable model tag is insufficient),
- planner mode,
- system prompt hash,
- tool/schema hash,
- generation options,
- clean/dirty byte identity when `git_describe` ends in `-dirty`.

Those fields are prerequisites for comparing stochastic runs. A-038 should create a bounded,
redacted, content-addressed evidence bundle under XDG state and a versioned schema. A backup
must be reported as configured only after Alex selects and verifies a destination.

### 4. The ledger draft crossed three ownership domains

A-026 was labelled `area:docs`, but “filing bug/feature creates/links IMP row” requires
`actions/core.py`, `brain/server.py` or `brain/training.py`, runtime filesystem writes, and
cross-worktree ID coordination. That is integration work, not a schema-only ledger v0.

Training currently allocates the next `A-NNN` by scanning branch-local files under an
in-process lock. The lock does not coordinate other worktrees or processes. Repeating that
pattern for monotonic `IMP-####` IDs would permit collisions. Ledger v0 should therefore use
a single Desk allocator against reconciled canonical state, or a collision-resistant ID;
Runtime/Forge must not allocate ledger IDs in v0.

Use per-improvement records plus a generated/validated index. Record an append-only event
history and current summary, but do not enforce the full future state machine yet. Store
bounded evidence summaries and durable references, not private raw journals.

### 5. “Protect control-plane paths” needs the real trust inventory

The current authority surface is broader than `.github/` and future eval files:

- `brain/server.py` owns localhost authentication, plan validation, approval modes, pending
  state, approve/deny, and execution.
- `brain/training.py` owns exact-byte preview/confirm writes to assignments, SESSION, agent
  slots, and human validation.
- `brain/validation.py` owns what a human Verify/Fail record means.
- `brain/system_prompt.md` and `brain/tools.json` define model-visible behavior.
- `actions/core.py` maps reviewed calls to desktop, GitHub, and preference mutations.
- `scripts/skill-draft.py` defines skill promotion.
- `skills/examples/*/run.sh` are auto-executable when the user selects
  `approval_mode = "skills_trusted"`; modifying a bundled recipe changes trusted behavior.
- `.github/workflows/ci.yml`, future eval oracles/baselines, ledger schema/history,
  CODEOWNERS, and promotion policy define what may pass.

Because several files mix Runtime and Control Plane code, the first protection pass will
create review friction. That is preferable to a false narrow boundary. A later architecture
assignment can extract policy/authority modules after the rules are proven.

The existing `.github/ISSUE_TEMPLATE/workstream.md` also still says parallel work needs
explicit non-overlapping path lists, contradicting ADR-034's area + worktree rule. A-030
should reconcile policy templates while defining the protected manifest.

### 6. A-031 lacks a comparable and side-effect-free experiment contract

`JARVIS_MODEL` stores only a tag. Planner calls fix `temperature=0`, but that is not a proof
of identical output or model bytes. The live `/v1/run` route captures Hyprland state, writes
journals, takes the global BUSY lock, and can leave action plans awaiting approval. A
stochastic runner must not approve or execute proposed actions on Alex's desktop.

Start with planner-only cases whose deterministic oracle checks action name/arguments or an
honest empty plan. Run each case in fresh context under A-038's fingerprint. Keep raw outputs
private; publish counts and hashes. Report `successes / trials` and “all trials passed.” Do
not call an N=3–5 result statistically conclusive, and do not optimize for pass@k when the
product needs the first answer to be correct.

Dangerous Hyprland/system behavior belongs in targeted human or disposable-VM E2E later.

### 7. A-029's proposed generic memory schema outran its only safe use case

The current app preference file has useful but limited mechanics: atomic replacement, query
weights, and a 15-minute correction target. It has no writer lock, provenance, inspection,
revoke path, strict version validation, or corruption quarantine. Malformed content silently
loads as empty; a later write can replace it. `last_open` (ephemeral interaction state) and
durable weights share one file.

A-029 should become **Preference memory v0**, not a general memory platform. Migrate existing
weights with a backup; represent user corrections as explicit instructions; ensure inferred
preferences and observations cannot outrank explicit instructions; provide inspect/revoke;
and keep free-form content and secrets out. Episodic memory, embeddings, consolidation, and
agent observations that alter behavior remain deferred.

### 8. Promotion/deployment identity is currently manual and partially stale

`VERSION` is `0.5.9`, while repository tags stop at `v0.3.0`. `scripts/restart.sh` restarts the
user service and checks `/health`; `scripts/stop.sh` is a manual kill command; and
`scripts/install-service.sh` points systemd at the checkout used during installation. There
is no staged deploy or automatic rollback, and a restart from an unmerged worktree could run
candidate bytes against shared desktop state.

A-027's promotion document must define the canonical deploy source, verify commit/version/tag
identity, restart only after merge, record health, and document stop/revert/restart. A system
snapshot is required only before a deploy that changes host configuration or system state;
ordinary repo code plus a user-service restart uses git rollback and does not pretend a root
snapshot backs up `/home`.

## Wave 0 assignment decisions

| Assignment | Disposition | Required change |
|---|---|---|
| A-027 | **Keep, reshape, block** | Record the live GitHub capability blocker and require Alex's hosting/plan choice plus separate non-bypass Forge identity. Remove “optional CI”; name the existing check and its coverage gap. Do not mark done until API verification proves the hard gate. |
| A-026 | **Keep, narrow** | Docs/schema/manual Desk ledger only. Single allocator or collision-safe IDs; per-item history; durable evidence references. Defer Runtime/Training/issue auto-link integration. |
| A-028 | **Reshape** | Define the four evidence classes and create a separate candidate eval registry/result envelope. Make CI run every current JS suite. Human Verify must not auto-graduate a case. |
| A-030 | **Keep, expand boundary inventory, block** | Depend on A-027+A-028. Protect actual approval/execution/validation/trusted-skill/workflow/eval/ledger surfaces. Treat CODEOWNERS as advisory until branch rules enforce it. |
| A-031 | **Keep, narrow, block** | Depend on A-028+A-030. Planner-only, no execution; pinned evidence envelope; exact oracles; private raw traces and versioned summaries; calibration before gating. |
| A-029 | **Keep, narrow, defer to end** | Preference memory only. Provenance precedence, migration/backup, locking, inspection and revoke. No generic observation-driven memory. |
| A-038 | **Add prerequisite** | Versioned evidence-reference/fingerprint schema plus selected, private, content-addressed operational bundles under XDG state. Unblocks ledger and eval foundations. |

## Risks if Wave 0 is implemented as originally written

1. A policy document or CODEOWNERS file could be mistaken for enforced promotion while direct
   pushes remain possible.
2. The same credential could propose, approve, merge, and alter its own rules.
3. Relabelling human guides as regression evals would mix mutable evidence with protected
   oracles and create false confidence.
4. Ledger records could point to pruned private logs, or runtime ID allocation could collide
   across worktrees.
5. A feature PR could improve its score by changing the grader, workflow, approval path, or
   a `skills_trusted` recipe in the same change.
6. N-run results could compare different model bytes/prompts/options and still look like a
   trend; tiny samples could be treated as a gate without calibration.
7. A generic memory layer could let repeated inference outweigh one explicit instruction or
   overwrite malformed legacy preferences without recovery.
8. “Deploy” could mean restarting candidate bytes from the wrong worktree, with stale tags
   and no verified rollback identity.

## Acceptance gates for increased autonomy

Wave 0 does **not** itself enable unattended self-improvement. A later, separate autonomy
assignment may allow Forge to open/update candidate PRs only after all of these are true:

- branch protection/ruleset is verified through the API on `main`;
- Forge uses a non-bypass identity and cannot provide Alex's review;
- the complete deterministic CI check is required;
- protected Control Plane ownership is enforced, including its own policy files;
- regression definitions/oracles and promotion thresholds are versioned and protected;
- evidence bundles and ledger links can explain each candidate without publishing private
  prompts;
- promotion, canonical deploy identity, stop, health, and rollback are documented and tested;
- resource budgets and secrets handling are defined before Forge receives unattended
  credentials or privileged operations.

Until then, current behavior remains the safe baseline: Jarvis/Training prepares reviewable
work; a human chooses and runs an agent, reviews the branch/PR, merges, and deploys.

## Files reviewed

- Governance: `START.md`, `AGENTS.md`, `docs/DECISIONS.md`,
  `docs/SELF_IMPROVE_ROADMAP.md`, assignment prompts/QUEUE/briefs
- Evidence: `brain/journal.py`, `docs/LOGGING.md`, `brain/validation.py`,
  `docs/validation/`, `docs/FEATURES.md`, `.gitignore`
- Runtime/control: `brain/server.py`, `brain/system_prompt.md`, `brain/tools.json`,
  `actions/core.py`, `scripts/skill-draft.py`, `skills/examples/`
- Desk/Forge: `brain/training.py`, Training overlay modules, `scripts/open-agent.py`,
  assignment and handoff docs
- Promotion/deploy: `.github/workflows/ci.yml`, `.github/ISSUE_TEMPLATE/workstream.md`,
  `scripts/doctor.sh`, `scripts/restart.sh`, `scripts/start.sh`, `scripts/stop.sh`,
  `scripts/install-service.sh`, `VERSION`, tags and recent workflow runs
- Tests: full test inventory plus representative contracts across the Python and JavaScript
  suites; live GitHub metadata/protection endpoints
