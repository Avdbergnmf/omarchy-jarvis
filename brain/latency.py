"""A-033: InteractionTrace + hierarchical spans + a local SQLite store.

Diagnostic timings for how a chat turn felt — submit → first meaningful visible
content — without storing prompts or payloads. Core emits traces; Training UI
(A-034) is a later consumer. GET polls never write here.
"""
import json
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path

SCHEMA_VERSION = 1
TRACE_KEEP = 200
DONE_KEEP = 32
MAX_ATTRS = 16
MAX_ATTR_CHARS = 80
SPAN_VOCABULARY = (
    'interaction',
    'http.request',
    'route',
    'ack',
    'plan',
    'model.chat',
    'commit_plan',
    'await_approval',
    'execute',
    'tool',
    'persist.journal',
    'overlay.submit',
    'overlay.render.ack',
    'overlay.render.meaningful',
)
PLACEHOLDER_REPLIES = (
    'Thinking…', 'Thinking...',
    'Planning your request… Click for live console.',
    'Preparing…',
    'Preparing validation report…',
    'Gathering context for your bug report…',
    'Gathering context for your feature report…',
)
PRIVATE_ATTR_KEYS = (
    'password', 'token', 'secret', 'api_key', 'authorization',
    'prompt', 'reply', 'body', 'content', 'message', 'arguments',
)
DEFAULT_DIR = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'jarvis/latency'


def store_dir():
    override = os.environ.get('JARVIS_LATENCY_DIR')
    if override:
        return Path(override)
    return DEFAULT_DIR


def is_placeholder(text):
    if not isinstance(text, str) or not text.strip():
        return True
    stripped = text.strip()
    if stripped in PLACEHOLDER_REPLIES:
        return True
    return stripped.startswith('Planning your request') or stripped.startswith('Preparing')


def is_meaningful(text):
    return not is_placeholder(text)


def _clean_attrs(attrs):
    if not attrs:
        return {}
    out = {}
    for key, value in list(attrs.items())[:MAX_ATTRS]:
        name = str(key)[:40]
        if any(part in name.lower() for part in PRIVATE_ATTR_KEYS):
            continue
        if isinstance(value, (int, float, bool)) or value is None:
            out[name] = value
        else:
            out[name] = str(value)[:MAX_ATTR_CHARS]
    return out


def _new_id():
    return uuid.uuid4().hex


class Span:
    def __init__(self, trace, name, parent_id=None, attrs=None, start_ns=None):
        self.trace = trace
        self.span_id = _new_id()
        self.parent_id = parent_id
        self.name = name if name in SPAN_VOCABULARY else name[:40]
        self.attrs = _clean_attrs(attrs)
        self.start_ns = trace._now() if start_ns is None else start_ns
        self.end_ns = None
        self.status = 'ok'
        trace.spans.append(self)

    def span(self, name, attrs=None):
        return Span(self.trace, name, parent_id=self.span_id, attrs=attrs)

    def end(self, status='ok'):
        if self.end_ns is None:
            self.end_ns = self.trace._now()
            self.status = status
        return self

    @property
    def duration_ns(self):
        if self.end_ns is None:
            return None
        return max(0, self.end_ns - self.start_ns)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.end('error' if exc_type else 'ok')
        return False


class InteractionTrace:
    def __init__(self, tracer, run_id, planner_mode=None):
        self.tracer = tracer
        self.trace_id = _new_id()
        self.run_id = run_id
        self.planner_mode = planner_mode or 'unknown'
        self.started_ns = tracer._now()
        self.ended_ns = None
        self.status = 'ok'
        self.spans = []
        self.ack_ns = None
        self.meaningful_ns = None
        self.ttft_ns = None
        self.client_submit_ms = None
        self.client_ack_ms = None
        self.client_meaningful_ms = None
        self.root = Span(self, 'interaction', start_ns=self.started_ns)
        self.finished = False

    def _now(self):
        return self.tracer._now()

    def span(self, name, parent=None, attrs=None):
        parent_id = parent.span_id if isinstance(parent, Span) else (parent or self.root.span_id)
        return Span(self, name, parent_id=parent_id, attrs=attrs)

    def start_span(self, name, parent=None, attrs=None):
        return self.span(name, parent=parent, attrs=attrs)

    def mark_ack(self, at_ns=None, source='server'):
        if self.ack_ns is None:
            self.ack_ns = at_ns if at_ns is not None else self._now()
        if source == 'client' and self.client_ack_ms is None:
            self.client_ack_ms = at_ns

    def mark_meaningful(self, at_ns=None, source='server'):
        if self.meaningful_ns is None:
            self.meaningful_ns = at_ns if at_ns is not None else self._now()
        if source == 'client' and self.client_meaningful_ms is None:
            self.client_meaningful_ms = at_ns

    def mark_ttft(self, at_ns=None):
        if self.ttft_ns is None:
            self.ttft_ns = at_ns if at_ns is not None else self._now()

    def metrics(self):
        client_mrl = None
        if self.client_submit_ms is not None and self.client_meaningful_ms is not None:
            client_mrl = max(0, int(self.client_meaningful_ms) - int(self.client_submit_ms)) * 1_000_000
        client_ack = None
        if self.client_submit_ms is not None and self.client_ack_ms is not None:
            client_ack = max(0, int(self.client_ack_ms) - int(self.client_submit_ms)) * 1_000_000
        return {
            'ack_latency_ns': (self.ack_ns - self.started_ns) if self.ack_ns is not None else None,
            'meaningful_response_latency_ns': (
                client_mrl if client_mrl is not None
                else ((self.meaningful_ns - self.started_ns) if self.meaningful_ns is not None else None)
            ),
            'ttft_ns': (self.ttft_ns - self.started_ns) if self.ttft_ns is not None else None,
            'client_ack_latency_ns': client_ack,
            'used_client_clock_for_mrl': client_mrl is not None,
        }

    def finish(self, status='ok'):
        if self.finished:
            return self.snapshot()
        self.status = status
        self.ended_ns = self._now()
        self.root.end(status=status)
        for span in self.spans:
            if span.end_ns is None:
                span.end(status='unfinished' if status != 'error' else 'error')
        self.finished = True
        return self.tracer._persist(self)

    def snapshot(self):
        metrics = self.metrics()
        return {
            'schema_version': SCHEMA_VERSION,
            'trace_id': self.trace_id,
            'run_id': self.run_id,
            'planner_mode': self.planner_mode,
            'jarvis_version': self.tracer.jarvis_version,
            'git_revision': self.tracer.git_revision,
            'model': self.tracer.model,
            'started_ns': self.started_ns,
            'ended_ns': self.ended_ns,
            'status': self.status,
            'ack_latency_ns': metrics['ack_latency_ns'],
            'meaningful_response_latency_ns': metrics['meaningful_response_latency_ns'],
            'ttft_ns': metrics['ttft_ns'],
            'used_client_clock_for_mrl': metrics['used_client_clock_for_mrl'],
            'spans': [
                {
                    'span_id': s.span_id,
                    'parent_id': s.parent_id,
                    'name': s.name,
                    'start_ns': s.start_ns,
                    'end_ns': s.end_ns,
                    'duration_ns': s.duration_ns,
                    'status': s.status,
                    'attrs': s.attrs,
                }
                for s in self.spans
            ],
        }


class NullSpan:
    span_id = None

    def span(self, name, attrs=None):
        return self

    def end(self, status='ok'):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class NullTrace:
    enabled = False
    trace_id = None
    spans = ()

    def span(self, name, parent=None, attrs=None):
        return NullSpan()

    def start_span(self, name, parent=None, attrs=None):
        return NullSpan()

    def mark_ack(self, at_ns=None, source='server'):
        return None

    def mark_meaningful(self, at_ns=None, source='server'):
        return None

    def mark_ttft(self, at_ns=None):
        return None

    def finish(self, status='ok'):
        return None

    def snapshot(self):
        return None

    def metrics(self):
        return {}


NULL_TRACE = NullTrace()


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.path.parent, 0o700)
        except OSError:
            pass
        if not self.path.exists():
            self.path.touch(mode=0o600)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass
        self._init()

    def _connect(self):
        conn = sqlite3.connect(str(self.path), timeout=2)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._lock, self._connect() as conn:
            conn.executescript(
                'CREATE TABLE IF NOT EXISTS traces ('
                'trace_id TEXT PRIMARY KEY, run_id TEXT, planner_mode TEXT,'
                'jarvis_version TEXT, git_revision TEXT, model TEXT,'
                'started_ns INTEGER, ended_ns INTEGER, status TEXT,'
                'ack_latency_ns INTEGER, meaningful_response_latency_ns INTEGER, ttft_ns INTEGER);'
                'CREATE TABLE IF NOT EXISTS spans ('
                'span_id TEXT PRIMARY KEY, trace_id TEXT, parent_id TEXT, name TEXT,'
                'start_ns INTEGER, end_ns INTEGER, duration_ns INTEGER, status TEXT, attrs_json TEXT);'
                'CREATE INDEX IF NOT EXISTS traces_started ON traces(started_ns DESC);'
            )

    def write(self, snapshot):
        if not snapshot:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO traces '
                '(trace_id, run_id, planner_mode, jarvis_version, git_revision, model, '
                'started_ns, ended_ns, status, ack_latency_ns, '
                'meaningful_response_latency_ns, ttft_ns) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (snapshot['trace_id'], snapshot['run_id'], snapshot['planner_mode'],
                 snapshot['jarvis_version'], snapshot['git_revision'], snapshot['model'],
                 snapshot['started_ns'], snapshot['ended_ns'], snapshot['status'],
                 snapshot['ack_latency_ns'], snapshot['meaningful_response_latency_ns'],
                 snapshot['ttft_ns']))
            conn.execute('DELETE FROM spans WHERE trace_id=?', (snapshot['trace_id'],))
            conn.executemany(
                'INSERT INTO spans (span_id, trace_id, parent_id, name, start_ns, end_ns, '
                'duration_ns, status, attrs_json) VALUES (?,?,?,?,?,?,?,?,?)',
                [(s['span_id'], snapshot['trace_id'], s['parent_id'], s['name'],
                  s['start_ns'], s['end_ns'], s['duration_ns'], s['status'],
                  json.dumps(s['attrs'], ensure_ascii=False)) for s in snapshot['spans']])
            stale = conn.execute(
                'SELECT trace_id FROM traces ORDER BY started_ns DESC LIMIT -1 OFFSET ?',
                (TRACE_KEEP,)).fetchall()
            if stale:
                ids = [(row[0],) for row in stale]
                conn.executemany('DELETE FROM traces WHERE trace_id=?', ids)
                conn.executemany('DELETE FROM spans WHERE trace_id=?', ids)

    def get(self, trace_id):
        with self._lock, self._connect() as conn:
            row = conn.execute('SELECT * FROM traces WHERE trace_id=?', (trace_id,)).fetchone()
            if not row:
                return None
            spans = conn.execute(
                'SELECT * FROM spans WHERE trace_id=? ORDER BY start_ns', (trace_id,)).fetchall()
        return self._hydrate(row, spans)

    def get_by_run(self, run_id):
        with self._lock, self._connect() as conn:
            row = conn.execute(
                'SELECT * FROM traces WHERE run_id=? ORDER BY started_ns DESC LIMIT 1',
                (run_id,)).fetchone()
            if not row:
                return None
            spans = conn.execute(
                'SELECT * FROM spans WHERE trace_id=? ORDER BY start_ns',
                (row['trace_id'],)).fetchall()
        return self._hydrate(row, spans)

    def recent(self, limit=20):
        limit = max(1, min(int(limit), 100))
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM traces ORDER BY started_ns DESC LIMIT ?', (limit,)).fetchall()
        return [self._hydrate(row, []) for row in rows]

    def _hydrate(self, row, span_rows):
        data = dict(row)
        data['spans'] = []
        for span in span_rows:
            item = dict(span)
            try:
                item['attrs'] = json.loads(item.pop('attrs_json') or '{}')
            except ValueError:
                item['attrs'] = {}
            data['spans'].append(item)
        return data


class Tracer:
    def __init__(self, store=None, enabled=True, clock=None,
                 jarvis_version='unknown', git_revision='unknown', model='unknown'):
        self.store = store
        self.enabled = bool(enabled)
        self.clock = clock or time.monotonic_ns
        self.jarvis_version = jarvis_version
        self.git_revision = git_revision
        self.model = model
        self._by_run = {}
        self._done = {}
        self._tls = threading.local()
        self._lock = threading.Lock()

    def _now(self):
        return int(self.clock())

    def start_interaction(self, run_id, planner_mode=None):
        if not self.enabled:
            return NULL_TRACE
        trace = InteractionTrace(self, run_id, planner_mode=planner_mode)
        with self._lock:
            self._by_run[run_id] = trace
        return trace

    def attach(self, run_id):
        trace = self.get(run_id)
        self._tls.trace = trace
        return trace

    def detach(self):
        self._tls.trace = None

    def current(self):
        if not self.enabled:
            return NULL_TRACE
        return getattr(self._tls, 'trace', None)

    def get(self, run_id):
        with self._lock:
            return self._by_run.get(run_id)

    def _lookup(self, run_id):
        with self._lock:
            return self._by_run.get(run_id) or self._done.get(run_id)

    def apply_client_mark(self, run_id, mark, client_ms=None):
        trace = self._lookup(run_id)
        if not trace or isinstance(trace, NullTrace):
            return None
        if mark == 'submit' and client_ms is not None:
            trace.client_submit_ms = int(client_ms)
        elif mark == 'ack':
            trace.mark_ack(source='client')
            if client_ms is not None:
                trace.client_ack_ms = int(client_ms)
        elif mark == 'meaningful':
            trace.mark_meaningful(source='client')
            if client_ms is not None:
                trace.client_meaningful_ms = int(client_ms)
        if trace.finished:
            self._persist(trace)
        return trace

    def finish(self, run_id, status='ok'):
        with self._lock:
            trace = self._by_run.get(run_id)
        if not trace or isinstance(trace, NullTrace):
            return None
        snapshot = trace.finish(status=status)
        with self._lock:
            self._by_run.pop(run_id, None)
            self._done[run_id] = trace
            stale = list(self._done)[:-DONE_KEEP]
            for rid in stale:
                self._done.pop(rid, None)
        if getattr(self._tls, 'trace', None) is trace:
            self._tls.trace = None
        return snapshot

    def _persist(self, trace):
        snapshot = trace.snapshot()
        if self.store is not None:
            self.store.write(snapshot)
        return snapshot
