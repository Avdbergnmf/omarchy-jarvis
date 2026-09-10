# Jarvis feature catalog (agent-friendly)

Coding agents: when you ship a user-visible feature, **add/update a row** and a matching validation entry under `docs/validation/` (see `docs/validation/catalog.schema.md`). Training mode and its human queue are planned in A-008/A-009 on the separate overlay track.
`unvalidated` means no recorded human validation; it does not mean the feature is shipped.
Rows marked planned below are not implemented in this branch. The validation catalog
currently contains only the A-011/A-012 items; older shipped rows still need entries.

| id | title | area | status | notes |
|----|-------|------|--------|-------|
| feat-overlay-chat | Overlay chat + plan/approve/execute | overlay | unvalidated | Super+Shift+J |
| feat-open-planning | open-planning skill | skills | unvalidated | Todoist+GCal+Outlook+WhatsApp |
| feat-scratch-mail | scratch-and-mail skill | skills | unvalidated | |
| feat-report-feature | /report /feature intake | brain | unvalidated | |
| feat-rlhf | Post-run +/neutral/− feedback | overlay | unvalidated | A-005 |
| feat-follow-along | Overlay stays through execute / follow-along | overlay | unvalidated | A-004 |
| feat-slash | Slash autocomplete | overlay | unvalidated | planned: A-007 |
| feat-train | Training mode | overlay | unvalidated | planned: A-008 |
| feat-validate | Human validation queue in Training | overlay | unvalidated | planned: A-009 |
| feat-open-by-name | Open any installed app by name (open_app_by_name) | actions | unvalidated | A-011, e.g. "open spotify" |
| feat-open-youtube | Open YouTube webapp (works even without a local .desktop) | actions | unvalidated | A-012 |
| feat-honest-plans | Common empty-plan action claims are rewritten honestly | brain | unvalidated | A-012 |

Status values: `unvalidated` | `validated` | `failed`.
