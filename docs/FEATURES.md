# Jarvis feature catalog (agent-friendly)

Coding agents: when you ship a user-visible feature, **add/update a row** and a matching validation entry under `docs/validation/` (see `docs/validation/catalog.schema.md`). Training mode (A-008/A-009) lists `status: unvalidated` items for Alex.

| id | title | area | status | notes |
|----|-------|------|--------|-------|
| feat-overlay-chat | Overlay chat + plan/approve/execute | overlay | unvalidated | Super+Shift+J |
| feat-open-planning | open-planning skill | skills | unvalidated | Todoist+GCal+Outlook+WhatsApp |
| feat-scratch-mail | scratch-and-mail skill | skills | unvalidated | |
| feat-report-feature | /report /feature intake | brain | unvalidated | |
| feat-rlhf | Post-run +/neutral/− feedback | overlay | unvalidated | A-005 |
| feat-follow-along | Overlay stays through execute / follow-along | overlay | unvalidated | A-004 |
| feat-slash | Slash autocomplete | overlay | unvalidated | A-007 (when done) |
| feat-train | Training mode | overlay | unvalidated | A-008 |
| feat-validate | Human validation queue in Training | overlay | unvalidated | A-009 |
| feat-open-by-name | Open any installed app by name (open_app_by_name) | actions | unvalidated | A-011, e.g. "open spotify" |
| feat-open-youtube | Open YouTube webapp (works even without a local .desktop) | actions | unvalidated | A-012 |
| feat-honest-plans | Planner never claims an action with an empty action list | brain | unvalidated | A-012 |

Status values: `unvalidated` | `validated` | `failed`.
