## Request (verbatim)
{{SEED}}

## Clarifying Q&A
{{QA}}

## Context pack
- Last plan (tools + args): {{LAST_PLAN}}
- Approval choice: {{LAST_APPROVAL}}
- Jarvis version: {{JARVIS_VERSION}}
- Run id: {{LAST_RUN_ID}}
- Run log: {{LAST_LOG_PATH}}
- Log excerpt (last steps): {{LOG_EXCERPT}}
- Host facts: {{HOST_FACTS}}
- Binding catalog hits: {{BINDING_HITS}}

## What it should do
{{EXPECTED}}

## Why (problem it solves)
{{ACTUAL}}

## Suspected layer
{{LAYER}}

## Acceptance criteria (done when…)
{{ACCEPTANCE}}

## Area ownership
Choose area:overlay | area:brain | area:actions | area:skills | area:docs during triage.
Default single-writer for brain/control plane; parallel-ok requires explicit scope.
Allowed paths: (fill during triage)
Forbidden paths: (fill during triage)

## Suggested milestone / difficulty
- Milestone: {{MILESTONE}}
- Difficulty: {{DIFFICULTY}}

## Recommended solver
{{SOLVER}} — {{SOLVER_WHY}}

---
Filed by Jarvis (`report_feature`) so a cold agent can act without chat history. Secrets are redacted before filing. A local mirror of this record lives at `docs/backlog/features/{{SLUG}}.md`.
