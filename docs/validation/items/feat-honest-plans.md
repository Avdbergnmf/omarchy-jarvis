```yaml
id: feat-honest-plans
title: Planner never claims an action with an empty action list
area: brain
status: unvalidated
jarvis_version_shipped: "0.4.x"
steps:
  - "Press Super+Shift+J"
  - "Ask for something Jarvis has no tool for, e.g. an obscure/uninstalled app name"
  - "Read the reply"
expected: "The reply either proposes a real action (visible in the plan before Run) or honestly says it can't do that — never a claim like \"Opening X.\" with nothing to approve and no desktop change"
last_human_run: null
notes: "Hard to force deterministically since it depends on the local model's output; regression is unit-tested directly against the exact reply that shipped in run fad6f832 (see ADR-024)."
```
