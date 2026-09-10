# A-023 — Simplify assignment scope: area + worktree, not hard path fences

- **Status:** queued
- **Area:** area:docs
- **parallel-ok:** YES
- **Links:** Alex 2026-09-10 JARVIS — allowed/forbidden paths force constant scope-expansion asks; worktrees already isolate checkouts

## Goal
Stop treating **Allowed paths / Forbidden paths** as hard gates. Isolation for parallel agents is **git worktree + branch** (already mandatory). Assignment scope should be:

1. **Primary:** `area:` + goal/checklist/out-of-scope  
2. **Parallel safety:** `parallel-ok` + **disjoint areas** (and separate worktrees) — not a brittle path allowlist  
3. **Paths (optional):** soft hints only (“likely touch …”), never a reason to block a one-line fix next door or spam AskUserQuestion for expansion  

Update START.md, `docs/assignments/TEMPLATE.md`, `docs/assignments/README.md`, paste prompts (`NEW_AGENT` / `CONTINUE` / `PARALLEL`), and any Training generate-assignment copy that still emits hard path fences. Add a short ADR. Agents should prefer noting “expanded into X because …” in PROGRESS over stopping for permission when the change is still in-repo and doesn’t violate out-of-scope / plan→approve→execute.

## Checklist
- [ ] Audit START, assignment README/TEMPLATE, prompts, Training handoff text for hard Allowed/Forbidden requirements
- [ ] Rewrite policy: worktree isolation + area; paths optional soft hints; remove “required if parallel-ok YES”
- [ ] parallel-ok = disjoint areas + own worktree (not path lists)
- [ ] ADR + PROGRESS; tweak assignment-status hint text if it mentions path fences
- [ ] SESSION; QUEUE/INDEX → done

## Out of scope
- Changing how worktrees are created
- Product code (overlay/brain/actions)
- Deleting historical Allowed/Forbidden lines from old done/ assignments

## Notes for the coding agent
- Desk/Training assignment generators that still require path lists should be softened in the same pass if they live under docs/ or clearly documented brain/training strings — prefer docs-first; if Training UI hardcodes fences, a minimal string change is OK and note it.
- Token discipline: read the policy files once; then diffs.
