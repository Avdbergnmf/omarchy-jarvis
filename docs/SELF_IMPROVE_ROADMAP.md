# Self-improve roadmap (desk decisions 2026-09-10)

Sources: ChatGPT 70-point plan → Firsty audit → **ChatGPT answers to 8 questions (pasted by Alex)**.

## North-star sentence

> Jarvis may autonomously discover, design, implement, test and refine improvements.  
> Jarvis may **not** autonomously redefine what counts as safe, what counts as successful, or what becomes trusted production Jarvis.

Architecture stays **Runtime + Desk + Forge (worktree coding agents) + Control Plane** — not in-process self-rewrite.

| Subsystem | Role |
|-----------|------|
| **Runtime** | Personal assistant (overlay/Training UI, Ollama, actions/skills) |
| **Desk** | Planning/orchestration (Firsty, QUEUE, filing) |
| **Forge** | Coding agents in isolated worktrees; candidate PRs |
| **Control Plane** | Approvals, policies, evals, promotion, deployment gates |

Forge may modify Runtime. Forge must **not** freely modify Control Plane authorization/evaluation mechanisms.

## Decisions (from ChatGPT answers)

| Question | Decision |
|----------|----------|
| What is Jarvis? | Whole system with explicit subsystems (table above). |
| Ledger vs QUEUE | **Wrap/evolve** QUEUE. Ledger = durable audit (`improvement_id`); QUEUE = operational tasks (`assignment_id`). Ledger item may spawn queue tasks. |
| Gitignored journals? | **Three tiers:** ephemeral scratch gitignore OK; operational traces durable backed-up outside git OK; decisions/approved improvements/eval defs/behavioral rules **versioned in git**. If losing it prevents explaining current behavior → not gitignore-only. |
| Eval investment | Human + deterministic tests first; targeted VM E2E next on dangerous Omarchy boundaries. |
| Unattended PRs? | **Yes, strongly** once `main` is protected. Hard gate = merge/promotion. Credentials must not bypass rulesets. |
| Memory now? | Small correct schema now (provenance + explicit≠inferred). No giant vector memory yet. |
| Safety/eval in same PR as features? | **Block by default** for protected evals/safety/auth/promotion. Feature unit tests may ride along. CODEOWNERS + rulesets. |
| Omarchy snapshots? | **Yes for system-affecting** deploys; **no for every /home app commit**. Snapshots ≠ `/home` backup. |

## Build order

### Gate before Wave 0
**A-032** — plan vs codebase review.  
**A-036 / A-037** — Training agent-monitor usability + **gates/`blocked-by` visibility** (not stage integers; see A-037). Prefer before grinding Wave 0 from the window.

### Gate before Wave 0 (plan)
**A-032** — ChatGPT/Sol deep review of this roadmap vs the codebase (docs-only). Do not implement Wave 0 until A-032 lands and Alex accepts deltas.

### Wave 0 — now (after A-032)
1. **A-027** Protect `main` externally  
2. **A-026** Improvement Ledger v0 (`IMP-*` → assignments)  
3. **A-028** Capability vs regression evals  
4. **A-030** Protect safety/eval/control-plane paths  
5. **A-031** Stochastic evals v0 (~10–20 behaviors)  
6. **A-029** Memory v0 provenance  

### Wave 1 — Text latency profiler (after Wave 0)
1. **A-033** traces/spans/store + instrumentation
2. **A-034** Training profiler UI
3. **A-035** distributions / version compare / ledger hooks

Brief: `docs/audits/chatgpt-latency-profiler-brief-2026-09-10.md`.

### Wave 2+ — backlog after Wave 0/1
Secrets broker; deployment ladder + health/rollback; friction metrics; rejection memory; resource budgets; skill manifests; VM candidates; …

### Deprioritized
In-process self-rewrite; heavy autonomous self-reflection machinery; vanity single score.
