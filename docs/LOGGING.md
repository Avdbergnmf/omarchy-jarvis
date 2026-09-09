# Run journal

The primary artifact is `logs/journal/CURRENT.jsonl`: append-only UTF-8 JSONL,
with four records per terminal run: **prompt → process → done → eval**.
While waiting for a plan/approval, a run may only have its first one or two records.
Intake questions and raw module output belong to debug, not the journal.

Every record includes `ts` (ISO-8601 UTC), `jarvis_version` (VERSION), `git_describe`
(cached at process startup), `run_id`, and `phase`. Phase payloads are:

- prompt: `prompt`, redacted user text.
- process: `process`, short plan (actions/tools/arguments/reply), or no-plan explanation.
- done: `happened` with terminal status, reply and tool steps/results; `ok` reports execution success.
- eval: `eval: {ok, flag, note}`, where flag is null, suspicious, mismatch or partial;
  top-level `ok` still reports execution success. A successful tool may have a flagged evaluation.

Strings are limited to 1,500 characters, lists to 12 entries, dictionaries to 30 keys.
Secret-shaped strings and sensitive dictionary values are redacted before writing.
This is best-effort redaction, not a guarantee arbitrary private prose is safe to publish.
No raw model reasoning or megabyte responses are journaled. Files are created mode 0600,
new directories 0700. All logs are gitignored and stay local.

## Evaluation and console

Rules compare the approved tools/arguments against executed steps. Errors after completed
steps are partial; other failures suspicious; differing executions mismatch. Action-like
prompts with no tools are suspicious. Cancellation is recorded as intentional, with no
executed actions. Successful desktop tools are conservatively suspicious because return
codes alone cannot establish that the intended window moved/opened. Review their results
and collect a live snapshot when needed; this pass does not claim independent desktop verification.
No model, cloud service, subprocess or desktop snapshot runs during eval. These bounded
rules finish with the run; polling does no routine logging or evaluation (except finalizing
a stale run once). Flags never create issues, change approval or block on external work.

Open console still follows `logs/runs/<run_id>.log` with tail -F. That file is now a
JSONL projection of the same four records, so existing console buttons keep working.
Bug intake includes the previous run's versioned journal excerpt and run/log paths.
An I/O failure is reported to service stderr and must not keep the run busy lock held.

```bash
jq -c 'select(.phase == "eval" and .eval.flag != null)' logs/journal/CURRENT.jsonl
jq -c --arg id RUN_ID 'select(.run_id == $id)' logs/journal/CURRENT.jsonl
./console/jarvis-console RUN_ID
```

## Secondary module debug

In `~/.config/jarvis/config.toml`, `log_level = "info"` is the default. Set
`log_level = "debug"` and restart Jarvis to enable bounded internal events in
`logs/debug/<run_id>.jsonl`, with module, event, value, timestamp and version.
Invalid levels fall back to info. GET polls stay quiet at either level.
Actions keep their machine-readable stdout contract; the brain folds short results
into happened, and records raw details only at debug. Debug files are local and ignored.

## Version reset / old runs

1. Stop the service before changing runtime code for a release or big behavior change.
2. Change `VERSION` to a distinct version (for example `0.4.1`); commit code and schema/docs.
3. Restart the service. Its first journal entry atomically renames the old CURRENT to
   `logs/journal/archive/v<old-version>-<UTC timestamp>.jsonl`, then creates CURRENT.
4. Note the version/reset in PROGRESS. Archive rather than delete. Do not reset without
   changing VERSION; editing VERSION while the service is running takes effect on restart.

This assumes one brain process per checkout, matching the single local service. Writes
are serialized in-process. Archive filenames include microseconds. Rotation reads only
the first record, not the whole file. Version and git revision are cached at startup;
no git calls occur during runs or polls. To investigate old behavior, use the archived
journal's git_describe to find the producing commit (a dirty suffix means uncommitted
changes were present). Git history retains code/schema, **not** ignored private logs;
keep local archives if old run evidence is needed. Per-run console projections survive rotation.
