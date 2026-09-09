"""Bounded local run evidence. No subprocesses or model calls on the write path."""
import datetime
import json
import os
from pathlib import Path
import re
import threading

LOCK = threading.Lock()


def clean(value):
    if isinstance(value, dict):
        return {str(k)[:80]: ('[REDACTED]' if re.search(r'password|token|secret|api.?key|authorization', str(k), re.I) else clean(v)) for k, v in list(value.items())[:30]}
    if isinstance(value, list):
        return [clean(v) for v in value[:12]]
    if isinstance(value, str):
        # Tool summaries can themselves be JSON strings. Redact nested keys before truncation.
        if value.lstrip().startswith(('{', '[')):
            try:
                return json.dumps(clean(json.loads(value)), ensure_ascii=False)[:1500]
            except ValueError:
                pass
        value = re.sub(r'(?i)(bearer\s+|(?:api[_-]?key|password|token|secret)\s*[=:]\s*)[^\s,}"\']+', r'\1[REDACTED]', value)
        value = re.sub(r'\b(sk-[\w-]{10,}|gh[ops]_[\w]{20,})\b', '[REDACTED]', value)
        return value[:1500]
    return value


def evaluate(run):
    steps = run.get('steps', [])
    actions = (run.get('plan') or {}).get('actions', [])
    flag, note = None, 'No inconsistency in recorded results; desktop effects are not independently verified.'
    if run.get('status') == 'denied':
        note = 'Cancelled; no actions executed.'
    elif run.get('status') == 'error':
        flag, note = ('partial' if any(s.get('status') == 'done' for s in steps) else 'suspicious'), 'Execution failed; inspect happened.'
    elif [(a['tool'], a.get('arguments', {})) for a in actions] != [(s['tool'], s.get('arguments', {})) for s in steps]:
        flag, note = 'mismatch', 'Executed tools differ from the approved plan.'
    elif any(s.get('status') != 'done' for s in steps):
        flag, note = 'partial', 'Some planned steps did not complete.'
    elif steps:
        flag, note = 'suspicious', 'Tools reported completion; desktop side effects have not been independently verified.'
    elif re.search(r'\b(open|move|switch|toggle)\b', run.get('prompt', ''), re.I):
        flag, note = 'suspicious', 'Action-like request produced no tools; review the reply.'
    return {'ok': flag is None, 'flag': flag, 'note': note}


class Journal:
    def __init__(self, logs, version, revision):
        self.logs, self.version, self.revision = Path(logs), version, revision

    def append(self, path, record):
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, 'a') as out:
            out.write(json.dumps(record, ensure_ascii=False) + '\n')

    def write(self, run_id, phase, **fields):
        record = dict(ts=datetime.datetime.now(datetime.timezone.utc).isoformat(), jarvis_version=self.version,
                      git_describe=self.revision, run_id=run_id, phase=phase, **clean(fields))
        with LOCK:
            current = self.logs / 'journal/CURRENT.jsonl'
            if current.exists() and current.stat().st_size:
                with current.open() as src:
                    old = json.loads(src.readline())['jarvis_version']
                if old != self.version:
                    archive = current.parent / 'archive'
                    archive.mkdir(parents=True, exist_ok=True, mode=0o700)
                    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                    safe = re.sub(r'[^\w.-]', '_', old)
                    current.rename(archive / f'v{safe}-{stamp}.jsonl')
            self.append(current, record)
            # Console-compatible projection; only the four journal phases at info.
            path = self.logs / 'runs' / (run_id + '.log')
            self.append(path, record)
        return record
