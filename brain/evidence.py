"""A-038: evidence identity + durable operational bundles v0.

Turns a run's already-logged journal phases (logs/runs/<id>.log) into a stable,
bounded, redacted-by-default, content-addressed bundle under XDG state — a private
identity for comparing results across code/model revisions (the future Improvement
Ledger and candidate-eval work, A-026/A-028/A-031, consume this shape).

Not a backup: "backed up" is true only once Alex selects and verifies a destination
for $XDG_STATE_HOME/jarvis/evidence/ (see docs/evidence/README.md). Not the ledger
itself, not a candidate-eval runner, not continuous telemetry — this module only
turns one already-recorded run into one durable, addressable file, on request.
"""
import hashlib
import json
import os
from pathlib import Path
from urllib.request import urlopen

from journal import clean

SCHEMA_VERSION = 1
MAX_BUNDLE_BYTES = 65536
TIERS = ('reference', 'summary', 'full')
EVIDENCE_DIR = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'jarvis/evidence'


def read_run_phases(logs, run_id):
    """Ordered journal phase records for run_id from logs/runs/<id>.log. Missing,
    unsafe (symlinked) or unreadable sources return [] — never raise; a caller
    treats an empty result as "no evidence found", not a crash."""
    path = Path(logs) / 'runs' / (str(run_id) + '.log')
    try:
        if not path.is_file() or path.is_symlink():
            return []
        text = path.read_text(errors='replace')
    except OSError:
        return []
    phases = []
    for line in text.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue  # a damaged line is skipped, not fatal to the rest of the run
        if isinstance(record, dict) and isinstance(record.get('phase'), str):
            phases.append(record)
    return phases


def sha256_hex(data):
    return hashlib.sha256(data if isinstance(data, bytes) else str(data).encode()).hexdigest()


def ollama_model_digest(model, timeout=2):
    """Best-effort exact model digest via the local Ollama daemon's /api/tags. Never
    raises: offline, unreachable, or an unexpected response all yield None — a
    fingerprint with model_digest=None is still valid, just less precise."""
    try:
        with urlopen('http://127.0.0.1:11434/api/tags', timeout=timeout) as response:
            data = json.loads(response.read(1_000_000))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    for entry in data.get('models') or []:
        if isinstance(entry, dict) and model in (entry.get('name'), entry.get('model')):
            digest = entry.get('digest')
            return digest if isinstance(digest, str) else None
    return None


def fingerprint(*, jarvis_version, git_revision, planner_mode, model, model_digest,
                 system_prompt_hash, schema_hash, options, case_id=None, case_version=None):
    """The exact code/model/planner inputs needed to compare two runs' results —
    the whole reason this schema exists (A-038 goal). Every field is optional at
    the call site; a missing input is recorded as 'unknown'/None, never guessed."""
    return dict(
        jarvis_version=jarvis_version or 'unknown',
        git_revision=git_revision or 'unknown',
        planner_mode=planner_mode or 'unknown',
        model=model or 'unknown',
        model_digest=model_digest,
        system_prompt_hash=system_prompt_hash,
        schema_hash=schema_hash,
        options=clean(options or {}),
        case_id=case_id,
        case_version=case_version,
    )


def build_envelope(phases, fp, tier='summary'):
    """phases: ordered journal records for one run (prompt/process/done/eval, any
    subset — a source disappearing mid-run still yields a valid, honestly partial
    envelope, never a crash). tier: 'reference' (fingerprint + which phases exist,
    no content at all) | 'summary' (default: redacted, bounded) | 'full' (adds raw
    prompt/reply — still redacted of secrets via journal.clean, still bounded;
    opt-in only, never the default)."""
    if tier not in TIERS:
        raise ValueError('Unknown evidence tier: ' + str(tier))
    by_phase = {p['phase']: p for p in phases}
    prompt_rec = by_phase.get('prompt', {})
    process_rec = by_phase.get('process', {})
    done_rec = by_phase.get('done', {})
    eval_rec = by_phase.get('eval', {})
    run_id = prompt_rec.get('run_id') or done_rec.get('run_id') or eval_rec.get('run_id')
    envelope = dict(
        schema_version=SCHEMA_VERSION,
        kind='run',
        tier=tier,
        fingerprint=fp,
        source=dict(run_id=run_id, phases_present=sorted(by_phase)),
    )
    if tier != 'reference':
        happened = done_rec.get('happened') or {}
        plan = process_rec.get('process') or {}
        envelope['summary'] = dict(
            status=happened.get('status'),
            eval=clean(eval_rec.get('eval')) if eval_rec.get('eval') is not None else None,
            actions=clean(plan.get('actions')) if plan else None,
            step_count=len(happened.get('steps') or []),
        )
        if tier == 'full':
            envelope['private'] = dict(prompt=clean(prompt_rec.get('prompt')), reply=clean(happened.get('reply')))
    return envelope


def build_eval_envelope(fp, counts, trials, tier='summary', source=None):
    """A-028's documented candidate-eval result shape: the same schema_version/fingerprint
    envelope a run bundle uses — `kind: 'eval'` is the extension point A-038 reserved for
    exactly this — plus `counts` (successes out of trials, never a single scalar standing
    in for the whole suite) and one bounded record per trial.

    Raw model text never enters this envelope, at any tier: a trial carries its outcome, a
    bounded reason code and the sha256 of its canonical plan, so two revisions can be
    compared byte-for-byte without the bundle storing what the model said. There is
    deliberately no 'full' tier here (a run bundle's opt-in raw text has no eval
    equivalent), and nothing time-varying is recorded, so identical results under an
    identical fingerprint keep addressing the identical file."""
    if tier not in ('reference', 'summary'):
        raise ValueError("An eval envelope supports tier 'reference' or 'summary'; raw model output is never bundled")
    envelope = dict(
        schema_version=SCHEMA_VERSION,
        kind='eval',
        tier=tier,
        fingerprint=fp,
        source=dict(clean(source or {}), case_id=fp.get('case_id'), case_version=fp.get('case_version')),
        counts=dict(counts),
    )
    if tier == 'summary':
        envelope['trials'] = [dict(clean(trial)) for trial in trials]
    return envelope


def content_id(envelope):
    """Deterministic address for this envelope's logical content: same fingerprint
    + same source + same tier ⇒ same id, regardless of when it's exported. Two
    genuinely different inputs (a code/model change, a different tier) always
    address a different file — that difference IS the point of a fingerprint."""
    canonical = json.dumps(envelope, sort_keys=True, ensure_ascii=False)
    return sha256_hex(canonical)


def write_bundle(dest_dir, envelope):
    """Content-addressed, atomic, mode-0600 write under dest_dir. Returns
    (path, created: bool) — created=False means identical content was already
    durable (collision handling: never silently overwrite, never duplicate)."""
    dest_dir = Path(dest_dir)
    if dest_dir.is_symlink() or any(p.is_symlink() for p in dest_dir.parents if p.exists()):
        raise ValueError('Refusing to write evidence through a symlinked path')
    cid = content_id(envelope)
    body = json.dumps(dict(envelope, id=cid), indent=2, sort_keys=True, ensure_ascii=False) + '\n'
    encoded = body.encode()
    if len(encoded) > MAX_BUNDLE_BYTES:
        raise ValueError('Evidence bundle exceeds the ' + str(MAX_BUNDLE_BYTES) + '-byte bound; use a smaller tier')
    dest_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    final = dest_dir / (cid + '.json')
    if final.exists():
        return final, False
    tmp = dest_dir / ('.' + cid + '.tmp')
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        # Another export of the identical content raced us; its result is ours too.
        if final.exists():
            return final, False
        raise
    try:
        with os.fdopen(fd, 'w') as out:
            out.write(body)
        os.replace(tmp, final)
    finally:
        tmp.unlink(missing_ok=True)
    return final, True
