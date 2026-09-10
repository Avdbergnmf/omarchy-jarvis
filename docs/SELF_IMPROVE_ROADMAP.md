# Self-improve roadmap (codebase-grounded 2026-09-10)

Sources: ChatGPT 70-point plan → Firsty audit → ChatGPT answers to 8 questions →
[A-032 plan-vs-codebase review](audits/chatgpt-plan-vs-codebase-review-2026-09-10.md).

This is the proposed roadmap after A-032. Alex's acceptance/merge is the gate to begin the
revised Wave 0. The roadmap establishes foundations; it does not enable unattended Forge.

## North star

> Jarvis may autonomously discover, design, implement, test and refine improvements.  
> Jarvis may **not** autonomously redefine what counts as safe, what counts as successful,
> or what becomes trusted production Jarvis.

Architecture remains **Runtime + Desk + Forge + Control Plane**, not in-process self-rewrite.

| Subsystem | Role | Current reality |
|---|---|---|
| **Runtime** | Personal assistant: overlay, Ollama, actions and skills | Local brain already plans typed actions and defaults to review-before-execute. |
| **Desk** | Evidence triage, improvement planning and work preparation | Training and assignments prepare exact bytes; a human still confirms, claims and sends work. |
| **Forge** | Coding agents in isolated worktrees; candidate branches/PRs | Visible Claude/Codex terminals and paste-ready handoffs exist; no unattended controller exists. |
| **Control Plane** | Authorization, evaluation, ownership, promotion and deployment gates | Present but spread through Runtime/Training code, CI and policy docs; not yet externally protected. |

Forge may modify Runtime through reviewed candidate changes. Forge must not freely modify the
Control Plane or decide its own promotion. Conceptual subsystems do not imply process or file
isolation; A-030 owns the first enforceable boundary inventory.

## Adopted decisions

| Question | Decision |
|---|---|
| What is Jarvis? | The whole system, with the four explicit subsystems above. |
| Ledger vs QUEUE | **Wrap/evolve** QUEUE. Ledger is durable improvement audit (`improvement_id`); QUEUE is operational work (`assignment_id`). One improvement may spawn multiple assignments. |
| Gitignored journals? | **Three tiers:** ephemeral scratch may be ignored; selected operational evidence must have a durable private home and identity; decisions, accepted improvements, eval definitions and behavioral rules are versioned in git. Raw private prompts do not belong in git. |
| Eval investment | Deterministic tests and human acceptance first; planner consistency next; targeted disposable-VM E2E only for dangerous Omarchy/system boundaries. |
| Unattended PRs? | **Parked** ([FUTURE.md](FUTURE.md)) — the PR + `test` rule exists, but there is no agent budget or required human/code-owner approval. Prerequisites live under Wave 2; do not build the loop yet. |
| Memory now? | A narrow preference-memory schema with provenance and explicit-over-inferred authority. No generic episodic/vector platform yet. |
| Safety/eval in feature PRs? | Ordinary feature tests may ride with a feature. Existing protected regression oracles, authorization, trusted-skill, ledger-integrity and promotion policy changes require separate/explicit Alex review. The ruleset enforces PR + `test`, but not approving or code-owner review. |
| Omarchy snapshots? | Snapshot before system-affecting deployment only. Repo-only `/home` changes use git rollback; a root snapshot is never described as `/home` backup. |

## Evidence model

Keep these artifacts separate:

| Artifact | Purpose | Promotion authority |
|---|---|---|
| CI/unit/syntax checks | Deterministic code contracts on one revision | Required check after A-027; necessary, never sufficient for desktop intent |
| Runtime journal evaluator | Conservative anomaly and approved-vs-executed record | Diagnostic only; never a candidate pass/fail gate |
| Human validation catalog | Alex's observation of a versioned feature guide | Human acceptance evidence; never auto-produced or auto-graduated |
| Candidate eval suites | Capability exploration and protected regression comparison | Control Plane evidence after A-028/A-030; does not authorize merge by itself |

Every durable candidate/eval reference uses A-038's provenance envelope: revision and dirty
identity, Jarvis version, planner mode, exact model digest, prompt/tool/schema hashes,
generation options, case version, result summary and content hash. Private raw outputs remain
outside git; versioned summaries must be sufficient to understand the decision.

## Dispatch usability gate

A-036 (Agent monitor usability) and then A-037 (release gates and claimability visibility)
remain queued ahead of self-improve implementation. They make Training dispatch and dependency
reasons usable; they do not replace the dependency graph or authorize later work. A-037 must
represent sequencing with `blocked-by` and gate labels, not a second numeric stage system.

## Branch protection: enabled on public `main` (ADR-049; A-027 cancelled brief stays closed)

The repository is now **public**. Its active default-branch ruleset requires a PR plus the
`test` check and blocks bypass, deletion and force-push. It requires zero approvals and no
code-owner review ([ADR-049](DECISIONS.md#adr-049--github-main-ruleset-enabled-public-repo-a-027-outcome-revisited-2026-09-10)).

**Agents and humans must not** wait on A-027 or mistake CODEOWNERS for required human review.
Unattended Forge / auto-merge / auto-deploy stay **off**. Merges are human-reviewed by policy
and CI-gated by the ruleset. Stronger approval enforcement gets a **new** assignment.

## Revised Wave 0 dependency order

### External promotion track

**A-027 — Protected promotion path** *(cancelled — ADR-046)*

Not actionable on this remote right now. Do not reopen; file new work if Pro/another host appears.

### Evidence and audit track

1. **A-038 — Evidence identity + durable operational bundles v0**
   Give selected private evidence a stable content hash and XDG-state home; add the exact
   model/planner/prompt/tool/options envelope needed by ledger and evals. Do not claim backup
   until Alex configures and verifies a destination.
2. **A-026 — Improvement Ledger v0** *(after A-038)*
   Versioned per-improvement audit plus a generated/validated index. QUEUE stays operational.
   Desk alone allocates/records v0 entries; runtime issue/Training auto-linking is deferred.
3. **A-028 — Deterministic candidate-eval foundation** *(after A-038)*
   Define candidate eval schemas and capability/regression lifecycle separately from human
   validation and runtime anomaly flags. Make CI run all current Python and JavaScript suites.

### Enforcement and consistency track

4. **A-030 — Protect Control Plane paths** *(A-028 done; A-027 cancelled)*
   Inventory authority-bearing surfaces and add CODEOWNERS as an ownership **map**. Without
   GitHub protection (ADR-046), review remains human policy — document that limit; do not claim
   an enforceable gate.
5. **A-031 — Stochastic planner evals v0** *(after A-028 + A-030; done, ADR-051)*
   Run 10–20 critical planner-only behaviors repeatedly under A-038's pinned envelope.
   Never approve/execute desktop actions. Report successes/trials and all-trials consistency;
   calibrate with Alex before making thresholds promotional.
6. **A-029 — Preference memory v0** *(after A-026; last in Wave 0)*
   Migrate the existing app-choice weights into a typed, inspectable and revocable provenance
   model. Explicit instruction outranks inference; observations do not alter behavior in v0.

Dependency status lives in QUEUE/briefs. A blocked row must be deliberately unblocked when
all named prerequisites are accepted; queue order alone is not dependency enforcement.

## Wave 0 exit criteria

Wave 0 is complete only when:

- Accepted: the public remote enforces PR + `test` but not approval/code-owner review (ADR-049); unattended Forge stays off;
- deterministic CI covers every current suite and its check is required;
- selected operational evidence has durable private identity, while raw prompts stay private;
- ledger records distinguish observations, assignments, evidence, Alex decisions and outcomes;
- candidate capability/regression definitions are separate from human validation and journal
  anomaly flags;
- authorization, evaluator, trusted-skill, workflow, ledger and promotion surfaces are owned
  and protected;
- stochastic planner results are reproducible enough to compare and explicitly calibrated;
- preference memory is narrow, provenance-aware, inspectable, revocable and migration-safe.

Even then, Wave 0 only makes unattended candidate PRs *eligible for a separately reviewed
implementation*. It does not itself add a scheduler, auto-merge, auto-deploy, privileged
broker or agent-spending loop.

## Wave 1 — text latency profiler (after Wave 0)

1. **A-033** — traces, spans, storage and core instrumentation.
2. **A-034** — Training history and trace inspector.
3. **A-035** — distributions, version comparison and ledger hooks.

Brief: `docs/audits/chatgpt-latency-profiler-brief-2026-09-10.md`.

## Wave 2 — bounded autonomy prerequisites (parked / not funded)

Unattended Forge itself is a **future idea**, not an active goal — see [FUTURE.md](FUTURE.md).
Alex parked it (2026-09-10): interesting to write down, no credits for an unattended loop now.
ADR-049 later added PR + `test` protection, but not required human/code-owner approval. Do **not**
start Wave 2 work unless Alex explicitly reopens it.

If/when revisited, prerequisites would include:

1. secrets/privileged-operation broker and non-bypass Forge credential delivery;
2. resource/time/spend budgets and an external kill switch;
3. small deployment ladder with post-deploy health and rollback;
4. disposable VM tests for system-affecting changes;
5. trusted skill manifests/digests and sharper architectural boundary modules;
6. rejection memory and friction metrics;
7. dependency locking where external application dependencies actually appear.

Later still: episodic-memory consolidation, heavier maintainability gates, shadow deployment, and
larger eval matrices.

## Deprioritized

In-process self-rewrite, generic agent-observation memory, heavy autonomous reflection,
LLM-as-judge as a primary gate, a vanity single score, N-run execution against Alex's live
desktop, and snapshots for ordinary repo commits.
