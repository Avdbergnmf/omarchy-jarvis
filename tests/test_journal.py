"""Journal acceptance without Ollama, desktop changes or network calls."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'brain'))
import server
import journal
from journal import Journal, clean, evaluate, prune

spec = importlib.util.spec_from_file_location('agent_status', ROOT / 'scripts/agent-status.py')
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)


class JournalTest(unittest.TestCase):
    def test_rotation_retains_old_evidence_and_console(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp)
            Journal(logs, '1', 'abc').write('old', 'prompt', prompt='hello')
            old = (logs / 'journal/CURRENT.jsonl').read_bytes()
            Journal(logs, '2', 'def').write('new', 'prompt', prompt='hi')
            self.assertEqual(next((logs / 'journal/archive').iterdir()).read_bytes(), old)
            record = json.loads((logs / 'journal/CURRENT.jsonl').read_text())
            self.assertEqual(record['jarvis_version'], '2')
            self.assertEqual(record['git_describe'], 'def')
            self.assertEqual((logs / 'runs/old.log').read_bytes(), old)
            self.assertEqual((logs / 'journal/CURRENT.jsonl').stat().st_mode & 0o777, 0o600)

    def test_damaged_header_is_archived_without_losing_evidence(self):
        for header in ('{"jarvis_version":', '{}', '[]', '{"jarvis_version":null}'):
            with self.subTest(header=header), tempfile.TemporaryDirectory() as tmp:
                logs = Path(tmp)
                current = logs / 'journal/CURRENT.jsonl'
                current.parent.mkdir()
                original = (header + '\nold evidence\n').encode()
                current.write_bytes(original)
                Journal(logs, '2', 'abc').write('recovery', 'prompt', prompt='hi')
                self.assertEqual(next((current.parent / 'archive').iterdir()).read_bytes(), original)
                self.assertEqual(json.loads(current.read_text())['run_id'], 'recovery')

    def test_http_access_logging_is_quiet(self):
        with patch('sys.stderr') as stderr:
            server.Handler.log_message(None, 'GET /v1/runs/%s', 'test')
        stderr.write.assert_not_called()

    def test_prune_keeps_newest_and_deletes_oldest(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for i in range(5):
                path = directory / f'{i}.log'
                path.write_text('x')
                os.utime(path, (i, i))  # distinct, ascending mtimes: 4.log is newest
            removed = prune(directory, '*.log', 2)
            remaining = {p.name for p in directory.iterdir()}
        self.assertEqual(remaining, {'4.log', '3.log'})
        self.assertEqual(set(removed), {'0.log', '1.log', '2.log'})

    def test_prune_missing_directory_is_a_noop(self):
        self.assertEqual(prune(Path('/nonexistent-jarvis-test-dir'), '*.log', 5), [])

    def test_prune_under_the_cap_removes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / 'only.log').write_text('x')
            self.assertEqual(prune(directory, '*.log', 5), [])

    def test_write_prunes_run_logs_only_on_a_new_run(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(journal, 'RUN_LOG_KEEP', 2):
            logs = Path(tmp)
            runs = logs / 'runs'; runs.mkdir(parents=True)
            for i in range(4):
                path = runs / f'old-{i}.log'
                path.write_text('x'); os.utime(path, (i, i))
            j = Journal(logs, '1', 'abc')
            j.write('current-run', 'prompt', prompt='hi')  # new run -> should trigger prune
            self.assertEqual(len(list(runs.glob('*.log'))), 2, 'RUN_LOG_KEEP=2 must include the just-created run')
            self.assertTrue((runs / 'current-run.log').exists())
            j.write('current-run', 'process', process={'actions': [], 'reply': 'hi'})  # not a 'prompt' phase
            self.assertEqual(len(list(runs.glob('*.log'))), 2, 'a non-prompt phase must not re-scan/prune')

    def test_write_prunes_journal_archive_on_rotation(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(journal, 'ARCHIVE_KEEP', 1):
            logs = Path(tmp)
            Journal(logs, '1', 'a').write('r1', 'prompt', prompt='hi')
            Journal(logs, '2', 'b').write('r2', 'prompt', prompt='hi')  # archives v1
            Journal(logs, '3', 'c').write('r3', 'prompt', prompt='hi')  # archives v2, prunes v1
            archived = list((logs / 'journal/archive').glob('*.jsonl'))
        self.assertEqual(len(archived), 1)
        self.assertIn('v2', archived[0].name)

    def test_redaction_and_bounds(self):
        value = clean({'password': 'private', 'prompt': 'token=private sk-1234567890123456', 'list': ['a'*2000]*20})
        self.assertNotIn('private', json.dumps(value))
        self.assertNotIn('sk-1234567890123456', json.dumps(value))
        self.assertNotIn('private', clean('{"token":"private"}'))
        self.assertEqual(len(value['list']), 12)
        self.assertEqual(len(value['list'][0]), 1500)

    def test_mismatch_partial_and_uncertainty(self):
        plan = {'actions': [{'tool': 'open_webapp', 'arguments': {'name': 'Outlook'}}]}
        run = {'status': 'done', 'plan': plan, 'steps': [{'tool': 'scratch_toggle', 'arguments': {}, 'status': 'done'}]}
        self.assertEqual(evaluate(run)['flag'], 'mismatch')
        run['status'] = 'error'
        self.assertEqual(evaluate(run)['flag'], 'partial')
        run.update(status='done', steps=[dict(plan['actions'][0], status='done')])
        self.assertEqual(evaluate(run)['flag'], 'suspicious')
        run['status'] = 'denied'
        self.assertIsNone(evaluate(run)['flag'])

    def test_terminal_paths_have_four_phases_and_no_eval_subprocess(self):
        for outcome in ('chat', 'deny', 'timeout', 'error', 'execute', 'tools_chat'):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as tmp, patch.object(server, 'LOGS', Path(tmp)), patch.dict(server.CONFIG, show_notifications=False, log_level='info'):
                rid = 'journal-' + outcome
                server.RUNS[rid] = {'status': 'planning', 'steps': [], 'prompt': 'hello', 'plan': None}
                server.BUSY.acquire()
                server.BUSY_RUN_ID = rid
                server.journal_event(rid, 'prompt', prompt='hello')
                try:
                    if outcome == 'chat':
                        server.commit_plan(rid, {'actions': [], 'reply': 'Hi'}, None)
                    elif outcome == 'tools_chat':
                        with patch.object(server, 'ollama_chat', return_value={'role': 'assistant', 'content': 'Hi'}):
                            server.plan_tools_run(rid, 'hello', None)
                    elif outcome == 'error':
                        server.fail_run(rid, ValueError('planning failed'))
                    elif outcome == 'execute':
                        plan = {'actions': [{'tool': 'list_backlog', 'arguments': {}}], 'reply': 'List'}
                        server.commit_plan(rid, plan, None)
                        from subprocess import CompletedProcess
                        with patch.object(server.subprocess, 'run', return_value=CompletedProcess([], 0, '{"ok":true}', '')) as call:
                            server.run_pending(rid)
                        self.assertEqual(call.call_count, 1)
                    else:
                        server.RUNS[rid].update(status='awaiting_answer', awaiting_since=time.monotonic()-1000)
                        if outcome == 'deny': server.handle_deny(rid)
                        else: server.expire_stale()
                    records = [json.loads(line) for line in (Path(tmp) / 'journal/CURRENT.jsonl').read_text().splitlines()]
                    self.assertEqual([r['phase'] for r in records], ['prompt', 'process', 'done', 'eval'])
                    self.assertTrue(all(r['jarvis_version'] and r['ts'] and r['run_id'] == rid for r in records))
                    self.assertFalse((Path(tmp) / 'debug').exists())
                    self.assertFalse(server.BUSY.locked())
                finally:
                    if server.BUSY.locked(): server.BUSY.release()
                    server.RUNS.pop(rid, None)
                    server.PENDING.pop(rid, None)
                    server.BUSY_RUN_ID = None

    def test_write_failure_releases_busy(self):
        rid = 'journal-io-error'
        server.RUNS[rid] = {'status': 'done', 'plan': None}
        server.BUSY.acquire()
        server.BUSY_RUN_ID = rid
        try:
            with patch.object(Journal, 'write', side_effect=OSError('disk full')), patch('sys.stderr'):
                server.release_busy()
            self.assertFalse(server.BUSY.locked())
        finally:
            server.RUNS.pop(rid)
            if server.BUSY.locked(): server.BUSY.release()

    def test_debug_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(server, 'LOGS', Path(tmp)):
            with patch.dict(server.CONFIG, log_level='info'):
                server.log('debug-test', 'stdout', 'token=private')
            self.assertFalse((Path(tmp) / 'debug').exists())
            with patch.dict(server.CONFIG, log_level='debug'):
                server.log('debug-test', 'stdout', 'token=private')
            record = json.loads((Path(tmp) / 'debug/debug-test.jsonl').read_text())
            self.assertEqual(record['module'], 'brain')
            self.assertNotIn('private', record['value'])

    def test_status_scope_collisions(self):
        def issue(number, area, body):
            return dict(number=number, title='test', labels=[{'name': 'area:' + area}, {'name': 'parallel-ok'}], body=body)
        rows = status.overview([
            issue(1, 'docs', 'Allowed paths: docs/\nForbidden paths: brain/'),
            issue(2, 'overlay', 'Allowed paths: docs/LOGGING.md\nForbidden paths: actions/'),
            issue(3, 'brain', '')])
        self.assertTrue(any('#1 / #2: potential collision' in row for row in rows))
        self.assertTrue(any('#3: control-plane' in row for row in rows))
        self.assertTrue(any('#3: parallel-ok requires' in row for row in rows))
