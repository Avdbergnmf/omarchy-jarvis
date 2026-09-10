```yaml
id: feat-honest-plans
title: Common empty-plan action claims are rewritten honestly
area: brain
status: unvalidated
jarvis_version_shipped: "0.4.2"
steps:
  - "Press Super+Shift+J"
  - "Ask for something Jarvis has no tool for, e.g. an obscure/uninstalled app name"
  - "Read the reply"
expected: "The reply either proposes a real action (visible in the plan before Run) or honestly says no actions were run — never a claim like \"Opening X.\" with nothing to approve and no desktop change"
last_human_run: null
notes: "Lexical guard only: arbitrary paraphrases and wrong-target plans are not prevented. Blank replies, bare completion and common first-person claims are also covered in A-014. Hard to force deterministically since it depends on the local model's output; regression is unit-tested directly against the exact reply that shipped in run fad6f832 (see ADR-024)."
```
