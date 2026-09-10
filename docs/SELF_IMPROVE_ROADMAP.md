# Self-improve roadmap (desk decisions 2026-09-10)

Informed by ChatGPT’s 70-point plan + Firsty audit of omarchy-jarvis @ 0.5.9.
ChatGPT’s full reply was not pasted into chat; decisions below are explicit defaults Alex can override.

## Scope decisions

| Question | Decision |
|----------|----------|
| What is “Jarvis”? | **Runtime** (`omarchy-jarvis`) **plus** the coding-agent factory (desk/assignments/Training handoffs). Control plane spans both. |
| Improvement Ledger vs QUEUE | Ledger **indexes** issues/assignments/Training problems — does **not** replace QUEUE. |
| Run journals in git? | Stay **gitignored** (privacy). Ledger/PROGRESS hold redacted promotion evidence; local journals remain source for forensics. |
| First eval investment | Deepen **unit + human validation**; split capability vs regression. Disposable VM e2e later. |
| Unattended PRs | Allowed **after** protected `main` exists; merge remains human gate. Until then: branches/worktrees only; no silent main. |
| Memory now? | **Memory v0** = extend preference/correction store with typed records + provenance — not full episodic memory yet. |
| Safety/eval in same PR as behavior? | **No** — policy: eval/safety/control-plane file changes need separate review/assignment (or explicit Alex OK). |
| Omarchy snapshots in-loop? | **Human/ops** for now; document in runbook, don’t automate yet. |

## Build order

### Wave 0 — assignments (now)
1. **A-026** Improvement Ledger v0  
2. **A-027** Protected promotion path (`main` rules + checklist)  
3. **A-028** Eval harness v0 (capability vs regression + bug→regression rule)  
4. **A-029** Memory v0 (typed prefs/memory with provenance)

### Wave 1+ — backlog features (draw later)
See `docs/backlog/features/feat-self-improve-*.md` and INDEX.

## Non-goals (near term)
In-process Jarvis rewriting its running code; passwordless sudo for Jarvis; single vanity quality score; replacing Training/QUEUE with a greenfield system.
