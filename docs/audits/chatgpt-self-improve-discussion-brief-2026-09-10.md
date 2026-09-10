# ChatGPT self-improve discussion brief (for agents without chat history)

Desk distilled this from Alex ↔ ChatGPT ↔ Firsty (2026-09-10). **You do not have that chat.** Treat this file + `docs/SELF_IMPROVE_ROADMAP.md` as the discussion record.

## What Alex wants
A persistent Omarchy “Jarvis” that learns from instructions/experience, grows skills, and improves its own codebase — but **proposes** changes like excellent PRs, and does **not** unilaterally own authorization, evaluation, or recovery.

## Architecture ChatGPT endorsed (keep)
Do **not** redesign around in-process self-rewriting. Current model is stronger:

**Runtime** (assistant) · **Desk** (orchestrate/file work) · **Forge** (coding agents in worktrees) · **Control Plane** (approvals, policies, evals, promotion).

Forge may change Runtime. Forge must not freely change Control Plane (what counts as safe/successful/trusted).

## North-star sentence
Jarvis may autonomously discover, design, implement, test and refine improvements.  
Jarvis may **not** autonomously redefine what counts as safe, what counts as successful, or what becomes trusted production Jarvis.

## Answers to the eight design questions (authoritative)
1. **Jarvis scope** — whole system with explicit subsystems (table above).  
2. **Ledger vs QUEUE** — wrap/evolve QUEUE; ledger = durable `improvement_id` audit; queue = disposable/operational `assignment_id` tasks; ledger items spawn queue work.  
3. **Gitignored journals** — three tiers: ephemeral gitignore OK; operational traces durable backed-up outside git OK; decisions/approved improvements/eval defs/behavioral rules **in git**. If losing it prevents explaining current behavior → too important for gitignore-only.  
4. **Eval order** — human + deterministic tests first; targeted VM E2E next on dangerous Omarchy/system boundaries.  
5. **Unattended PRs** — yes, strongly, **after** protected `main`; hard gate is merge/promotion; credentials must not bypass rulesets.  
6. **Memory** — small correct provenance schema now; no giant vector platform yet; explicit_instruction ≠ inferred preference ≠ observation.  
7. **Safety/eval edits in feature PRs** — block by default for protected eval/safety/auth/promotion; ordinary feature tests may ride with features; CODEOWNERS + rulesets.  
8. **Omarchy snapshots** — yes for system-affecting deploys; no for every `/home` app commit; snapshots ≠ `/home` backup.

## ChatGPT’s recommended sequence (pre–codebase review)
1. Protect `main` externally  
2. QUEUE as front-end of Improvement Ledger  
3. Split capability vs regression evals  
4. Stochastic evals on ~10–20 critical behaviors  
5. Protect safety/eval/control-plane files  
6. Minimal provenance-aware memory  
7. Secrets/privileged-operation broker (later)  
8. Small deployment ladder (later)  
Then increase unattended self-improvement.

Deprioritize elaborate autonomous “self-reflection” machinery — the valuable primitive (assignment → worktree → PR) already exists; missing piece is evidence, provenance, boundaries, promotion discipline.

## What Firsty already did in-repo
- Audit stub + Wave 0 assignments A-026…A-031 + `feat-self-improve-*` backlog  
- Roadmap at `docs/SELF_IMPROVE_ROADMAP.md`  
- Your job (**A-032**): ground/improve that plan against the **actual tree**, then revise roadmap/queue briefs — **docs only**

## Firsty TL;DR ChatGPT was reacting to
Strong: ADRs, worktrees, plan→approve→execute, run journal, Training, assignment factory.  
Partial/missing: formal ledger, protected main, capability/regression split, stochastic evals, protected graders, provenance memory, secrets broker, staged deploy.  
Differently: self-improve is Desk+Forge, not in-process rewrite; path allowlists deliberately softened; journals privacy-first/gitignored.
