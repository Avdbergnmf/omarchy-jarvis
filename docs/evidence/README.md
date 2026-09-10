# Evidence bundles (A-038)

A **bundle** is one durable, private, content-addressed JSON file that gives a single run a
stable identity — the exact code/model/planner inputs needed to compare it against another run
later, from a different revision or model. It exists because `logs/journal/` (see
[../LOGGING.md](../LOGGING.md)) is deliberately ephemeral: bounded, pruned, rotated on every
`VERSION` bump. Journals are the right tool for "what happened today"; bundles are the right
tool for "does this still behave the same after that change" — the foundation the Improvement
Ledger (A-026) and candidate evals (A-028/A-031) build on.

**Not a backup.** Writing a bundle to `$XDG_STATE_HOME/jarvis/evidence/` (default
`~/.local/state/jarvis/evidence/`, gitignored, local disk) does not mean the data survives a
disk failure. "Backed up" becomes true only once Alex selects and verifies an actual backup
destination for that directory — this tool creates the durable, addressable *source* file, not
a backup pipeline. Never uploaded, synced, or committed by anything in this repo.

## How to create one

```bash
./scripts/export-evidence.py <run_id> [--tier reference|summary|full] [--out DIR]
```

Reads only the already-written `logs/runs/<run_id>.log` journal projection — read-only against
the journal, no mutation of the run, no service restart, no network call except a best-effort,
short-timeout local Ollama digest lookup that never fails the export if it can't reach it.

## The three tiers

| Tier | Contains | Default |
|---|---|---|
| `reference` | Fingerprint + which journal phases exist. No run content at all. | — |
| `summary` | Fingerprint + redacted, bounded status/eval/actions/step-count. | **yes** |
| `full` | Everything in `summary`, plus the raw prompt/reply — still passed through the same secret redaction (`journal.clean`) as everything else in this codebase, still size-bounded. | opt-in only |

`full` is for the rare case a human reviewing a regression genuinely needs the exact text. It is
never the default and nothing in this codebase selects it automatically.

## Envelope shape (`schema_version: 1`)

```jsonc
{
  "schema_version": 1,
  "kind": "run",              // "eval" is a future A-028/A-031 extension point
  "id": "<sha256 of the envelope's own canonical content>",
  "tier": "reference|summary|full",
  "fingerprint": {
    "jarvis_version": "0.5.9",
    "git_revision": "v0.5.0-9-gabc1234[-dirty]",   // git describe --always --dirty
    "planner_mode": "json_plan|tools_run|correction|intake|fixed_plan|unknown",
    "model": "qwen2.5:3b",
    "model_digest": "357c53fb...|null",            // null only when Ollama was unreachable
    "system_prompt_hash": "sha256 of brain/system_prompt.md at export time",
    "schema_hash": "sha256 of the active PLAN_SCHEMA or TOOLS_FOR_MODEL",
    "options": {"temperature": 0, "num_ctx": 8192},
    "case_id": null,          // set by a future candidate-eval runner (A-028/A-031)
    "case_version": null
  },
  "source": {"run_id": "...", "phases_present": ["done", "eval", "process", "prompt"]},
  "summary": {"status": "done", "eval": {...}, "actions": [...], "step_count": 1},
  "private": {"prompt": "...", "reply": "..."}   // tier "full" only
}
```

**Content-addressed:** the filename (and the `id` field) is the sha256 of the envelope's own
canonical JSON. Two exports of the *same* run at the *same* tier under the *same* fingerprint
always produce the identical file — re-running the exporter is a safe no-op ("Already durable"),
never a duplicate. A changed fingerprint (different code revision, different model digest,
different tier) always addresses a *different* file — that difference is the entire point: it's
what lets a later comparison tell "did the input change" from "did the behavior change under the
same input."

## Source disappearance vs. bundle validity

A bundle is self-contained: it copies the fields it needs out of the journal at export time and
never stores a path back to `logs/runs/<run_id>.log`, only the bare `run_id`. If that source
journal is later pruned (A-006 retention) or the run is gone entirely, an *already-written*
bundle stays exactly as valid as it ever was — validity was never a property of the source file
continuing to exist. The only thing source disappearance affects is whether a **new** export can
be created: `export-evidence.py` on a missing/unreadable source reports "no journal evidence
found" and creates nothing, rather than silently treating an absent or ignored `logs/...` path as
if it were durable evidence on its own.

## Bounds and safety

- Mode `0600` files, `0700` directories, atomic creation (write to a temp file, `os.replace`).
- Hard 64KB size cap per bundle — an oversized `full` export is rejected outright rather than
  silently truncated; use `summary` or a shorter case if you hit it.
- Refuses to write through a symlinked destination, or read a symlinked journal source.
- No network calls beyond the local, best-effort, 2-second-timeout Ollama digest lookup; offline
  or unreachable Ollama yields `model_digest: null`, never a failure.

## Retention and your own backup

Nothing in this tool prunes `$XDG_STATE_HOME/jarvis/evidence/` — content-addressed files never
collide or grow unboundedly *per run*, but every distinct fingerprint/tier combination you
export stays until you remove it yourself. If you want these bundles backed up, pick a real
destination (a synced folder, a dedicated backup tool, cloud storage you control) and verify a
restore actually works before trusting it — this repo does not choose or configure that for you,
and nothing here silently adds cloud/network sync.

## What consumes this shape

A-026 (Improvement Ledger) and A-028/A-031 (candidate evals) are expected to reference bundles
by their content-addressed `id` rather than duplicating fingerprint data. Neither is implemented
by this assignment — v0 only defines the shape and the exporter.
