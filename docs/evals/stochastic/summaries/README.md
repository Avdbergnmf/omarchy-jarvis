# Redacted summaries

These JSON files are **redacted, content-hashed** runner reports: counts, fingerprints, reason
codes, output-digest prefixes. They do **not** contain model replies.

They are **not** a human-approved baseline. `docs/evals/stochastic/baseline.json` stays
`unapproved` until Alex reads a specific summary of a specific fingerprint and fills
tolerances. `--gate` will keep refusing until then.

| file | what it is |
|---|---|
| `routers.json` | Deterministic `route_prompt` cases (no model). 6/6 pass is the whole truth for this revision. |
| `stub-planner.json` | `--backend stub` against `fixtures/stub-replies.json`. Proves the runner, oracles, isolation and evidence shape. **Not** a measurement of qwen. |
