# A-022 — Fix open cliamp plan/tooling (issue #15)
- **Links:** issue:15
- **Forbidden paths:** overlay/, actions/, skills/; approval bypass; automatic agent dispatch
- **Allowed paths:** brain/, tests/, docs/assignments/, docs/SESSION.md, docs/PROGRESS.md, docs/DECISIONS.md
- **Priority:** P2
- **Area:** area:brain

- **Status:** queued
- **parallel-ok:** NO

## Goal
Alex reports Bug: open cliamp (GitHub issue #15, priority P2). When he asks Jarvis to open CLI Amp / cliamp, the brain should produce a correct, approvable plan that opens or focuses that app—not an empty plan, a false success reply, or the wrong target. Stay in allowed paths (brain/, tests/, assignment bookkeeping docs). Preserve plan → approve → execute: planning only proposes; desktop launch happens only after explicit Run/approve. Done when a prompt like “open cliamp” yields a truthful plan with the right tool/args, unit coverage guards the regression, and issue #15 evidence is addressed in PROGRESS.

## Checklist
- [ ] Reproduce from issue #15: prompt “open cliamp” (and close variants); record actual plan JSON, reply, and whether approval was skipped
- [ ] Identify brain gap (system prompt / tools.json / planner examples / action_label or app-resolution wiring in brain only—not actions/)
- [ ] Fix brain so cliamp resolves to a real open/focus action with honest reply; never claim success with zero actions
- [ ] Add/adjust tests under tests/ for the cliamp (or generic amp) open path and empty-plan honesty
- [ ] Note outcome in docs/PROGRESS.md; leave plan→approve→execute unchanged

## Human comments / evidence

## Out of scope
overlay/ UI changes; actions/ or skills/ implementations; approval bypass or auto-Run; automatic agent dispatch; notifications/messaging; spending cloud credits; unrelated open-app features beyond what’s required for cliamp; rewriting Training validation.

## Original problem context (read-only evidence)
{
  "id": "issue:15",
  "title": "Bug: open cliamp",
  "source": "GitHub",
  "url": "https://github.com/Avdbergnmf/omarchy-jarvis/issues/15"
}

