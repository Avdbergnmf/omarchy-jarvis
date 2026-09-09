# Validation catalog schema

Store one YAML or Markdown section per feature (implementation may use `docs/validation/items/*.md` or a single `catalog.yaml`).

```yaml
id: feat-open-planning
title: Open planning workspace
area: skills
status: unvalidated   # unvalidated | validated | failed
jarvis_version_shipped: "0.4.x"
steps:
  - "Press Super+Shift+J"
  - "Type: open my planning in a new workspace"
  - "Approve with Run"
  - "Confirm four apps on a fresh workspace"
expected: "Todoist, Google Calendar, Outlook, WhatsApp visible on one new workspace"
last_human_run: null    # ISO date when validated/failed
notes: ""
```

Training mode loads `status: unvalidated` (and optionally `failed`) into the human test queue.
