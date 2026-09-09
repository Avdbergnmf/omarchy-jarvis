# Agent invariants — Omarchy Jarvis

Read [START.md](START.md) fully first. It defines job modes, the Issue Loop, area ownership,
pass/handoff lifecycle and session completion. [README](README.md) covers usage;
[HOST](docs/HOST.md) records host details.

- Local, keyboard-first overlay → Ollama → reviewed actions/skills. No cloud evaluator.
- Preserve plan → approve → execute and default approval_mode=always. No arbitrary model shell.
- Keybindings are live data; do not hardcode Super combinations in the model.
- IPC/HTTP stays local. Never put API keys or unredacted secrets in logs or issues.
- New persisted skills require explicit human confirmation of reviewable bytes.
- Self-improvement is deterministic issue drafting plus local backlog, approved before filing.
  Dispatch prepares a paste-ready prompt; it never sends, contacts or spends agent credits.
- Primary evidence is the bounded run journal. Internal logs are debug-only; polls stay quiet.
- Concurrent coding agents require separate worktrees and branches; reuse assigned trees.
  Follow START isolation/claim reconciliation rules; never mutate another agent’s checkout.
- Single writer for brain/control plane; no parallel approve/execute redesign.
- Update docs/PROGRESS.md each session (worked/failed); record non-obvious choices in
  docs/DECISIONS.md. Keep actions and skills callable without the UI.
- Verify Hyprland/window changes with hyprctl clients/workspaces. Keep host-specific choices
  in HOST/ADRs (Google Calendar is not the stock Super+Shift+C HEY binding).
- Milestones and version tags track releases. Archive merged/closed passes and handoffs;
  never treat archived briefs as current instructions.

- Work orders: [docs/assignments/QUEUE.md](docs/assignments/QUEUE.md). Paste prompts: [docs/assignments/prompts/](docs/assignments/prompts/README.md).
  Update [docs/SESSION.md](docs/SESSION.md) checkboxes / Next action before stopping.
