# Milestones

Track the same set as GitHub Milestones. Tags follow semver.

| ID | Tag | Goal | Exit criteria |
|----|-----|------|---------------|
| M0 | v0.0.1 | Skeleton | Overlay toggles; Ollama hello; thought notification; live console opens on click; doctor script green |
| M1 | v0.1.0 | Bindings tools | `actions/run_binding` works for SUPER+S and SUPER+M; catalog refresh command |
| M2 | v0.2.0 | Workspaces | new/switch/move window; scratch toggle + move-to-scratch tools |
| M3 | v0.3.0 | Planning recipe | Skill opens Todoist + Google Calendar + Outlook + WhatsApp on a fresh workspace |
| M4 | v0.4.0 | Skill workflow | Draft → confirm → install path; 2+ example skills tested |
| M5 | later | Expand | More bindings-as-skills; optional voice |

Validate in order M0→M4 before expanding scope.

## Implementation status — 2026-09-09

M0–M3 exit behavior is implemented and verified on the host; detailed evidence and UI-automation limits are in PROGRESS.md. Workstream issues: #1 (M0), #2 (M1), #3 (M2), #4 (M3). M4 (#5) has a tested CLI draft/review/digest-confirm stub; its full overlay workflow remains open. M5 remains future scope. Release tags are created only after final CI and host checks pass.
