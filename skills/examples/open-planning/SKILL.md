---
name: open-planning
description: Open Todoist, Google Calendar, Outlook and WhatsApp together when asked for a planning workspace.
---

# open-planning

Run workspace_new, then open_webapp for all four apps on that workspace. Existing app windows move there. Use Google Calendar, never the stock HEY calendar binding.

Execute `./run.sh` from this directory, or `actions/run_skill open-planning` from the repository root. Preview with `./run.sh --dry-run`. Output is JSON lines; a nonzero exit stops the recipe and reports partial progress.

Triggers: “open my planning in a new workspace”, “planning workspace”.

Safety: opens/focuses webapps only; does not send messages or modify account data. These examples were explicitly requested; future generated skills stay in drafts until the user approves promotion.
