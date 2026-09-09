# Human validation catalog schema

`docs/validation/catalog.json` is the source of truth: a version-1 object containing a
`features` array. JSON keeps the runtime dependency-free. `docs/FEATURES.md` is its readable
index; Training loads definitions and human evidence on demand.

Each feature has:

- `id`: stable unique `feat-...` identifier.
- `title`, `area`: display name and overlay/brain/actions/skills/docs ownership.
- `steps`: 1–20 short, concrete instructions that a human performs. They are never executed by the UI.
- `expected`: observable success criterion.
- `jarvis_version_shipped`: version that introduced or last changed these instructions/behavior.
- `status`: unvalidated, validated or failed. New/changed behavior starts unvalidated.
- `jarvis_version`: last human-tested version, or null.
- `last_run`: null initially; after explicit human confirmation, an object with unique `id`,
  UTC `ts`, tested `jarvis_version`, `git_describe`, `definition_hash`, optional evidence
  `run_id`, redacted `notes`, and `result` (validated or failed).

`definition_hash` covers id/title/area/steps/expected/shipped version. If the guide changes,
Training treats the feature as unvalidated until the human repeats it, preserving prior
result metadata for reference. A prior validation applies to its recorded version; the UI
shows that version rather than claiming it validates every future release.

## Authoring rule

When shipping a user-visible feature, add/update its JSON entry and reproducible steps.
Set status unvalidated when behavior changes and update jarvis_version_shipped. Do not
invent human evidence from unit tests, agent smoke checks or the run evaluator. Retain the
previous last_run as historical context, or leave null for a new entry. Regenerate the index:

```bash
python3 -c 'import sys; from pathlib import Path; sys.path.insert(0,"brain"); import validation; r=Path.cwd(); (r/validation.FEATURES).write_text(validation.markdown(validation.load(r)))'
```

## Human flow

Training → Validate features → select a guide → follow steps. Check off all steps to enable
Verify. Fail requires an actual-outcome note and is available even if a step could not be
completed. An optional run id must be the run tested, not an unrelated later run.
Both choices preview exact catalog/index changes; only Confirm records the result.
Cancel/back writes nothing. Confirmation checks for intervening catalog edits.

After a confirmed failure, **Draft bug report in chat** starts the existing deterministic
Q&A/plan flow with the failed feature, tested version, expected/actual and optional run id.
No issue is filed by recording the failure. The normal reviewed Run action files it; Cancel
files nothing. If another chat run is active, the failed result remains saved and the user
can retry drafting after that run finishes. No issues are auto-closed by Verify.
