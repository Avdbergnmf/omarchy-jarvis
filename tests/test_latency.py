"""A-033: InteractionTrace, spans, store, privacy, off-switch."""
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'brain'))
import latency


class Clock:
    def __init__(self, start=1_000_000_000):
        self.t = start

    def __call__(self):
        self.t += 1_000_000
        return self.t

    def jump(self, ns):
        self.t += ns


class TraceApiTest(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.tracer = latency.Tracer(enabled=True, clock=self.clock, jarvis_version='0.5.10',
                                     git_revision='abc', model='qwen2.5:3b')

    def test_nested_spans_have_parent_links_and_positive_durations(self):
        trace = self.tracer.start_interaction('r1', planner_mode='json_plan')
        with trace.span('plan') as plan:
            with trace.span('model.chat', parent=plan):
                pass
        snap = trace.finish()
        names = [s['name'] for s in snap['spans']]
        self.assertIn('interaction', names)
        self.assertIn('plan', names)
        self.assertIn('model.chat', names)
        plan_span = next(s for s in snap['spans'] if s['name'] == 'plan')
        model = next(s for s in snap['spans'] if s['name'] == 'model.chat')
        root = next(s for s in snap['spans'] if s['name'] == 'interaction')
        self.assertEqual(plan_span['parent_id'], root['span_id'])
        self.assertEqual(model['parent_id'], plan_span['span_id'])
        self.assertGreater(plan_span['duration_ns'], 0)
        self.assertGreater(model['duration_ns'], 0)

    def test_parallel_spans_share_a_parent_and_overlap(self):
        trace = self.tracer.start_interaction('r2')
        with trace.span('execute') as exe:
            a = trace.start_span('tool', parent=exe, attrs={'tool': 'scratch_toggle'})
            b = trace.start_span('tool', parent=exe, attrs={'tool': 'workspace_new'})
            a.end()
            b.end()
        snap = trace.finish()
        tools = [s for s in snap['spans'] if s['name'] == 'tool']
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0]['parent_id'], tools[1]['parent_id'])
        self.assertLess(tools[0]['start_ns'], tools[1]['end_ns'])
        self.assertLess(tools[1]['start_ns'], tools[0]['end_ns'])

    def test_reaction_metric_is_submit_to_meaningful_not_ttft(self):
        trace = self.tracer.start_interaction('r3')
        trace.mark_ack()
        self.clock.jump(5_000_000)
        trace.mark_ttft()
        self.clock.jump(20_000_000)
        trace.mark_meaningful()
        snap = trace.finish()
        self.assertGreater(snap['meaningful_response_latency_ns'], snap['ttft_ns'])
        self.assertGreater(snap['ttft_ns'], snap['ack_latency_ns'])
        self.assertGreater(snap['ack_latency_ns'], 0)

    def test_client_clock_wins_for_meaningful_response_latency(self):
        trace = self.tracer.start_interaction('r4')
        trace.client_submit_ms = 1000
        trace.mark_meaningful()
        self.tracer.apply_client_mark('r4', 'meaningful', client_ms=1040)
        snap = trace.finish()
        self.assertEqual(snap['meaningful_response_latency_ns'], 40_000_000)
        self.assertTrue(snap['used_client_clock_for_mrl'])

    def test_late_client_mark_after_finish_rewrites_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = latency.Store(Path(tmp) / 't.sqlite')
            tracer = latency.Tracer(store=store, clock=self.clock, enabled=True)
            trace = tracer.start_interaction('r-late')
            trace.client_submit_ms = 1000
            trace.mark_meaningful()
            tracer.finish('r-late', status='done')
            self.assertIsNone(tracer.get('r-late'))
            tracer.apply_client_mark('r-late', 'meaningful', client_ms=1080)
            loaded = store.get_by_run('r-late')
            self.assertEqual(loaded['meaningful_response_latency_ns'], 80_000_000)

    def test_incomplete_spans_are_closed_unfinished_on_finish(self):
        trace = self.tracer.start_interaction('r5')
        open_span = trace.start_span('plan')
        snap = trace.finish(status='denied')
        self.assertEqual(open_span.status, 'unfinished')
        self.assertIsNotNone(open_span.end_ns)
        self.assertEqual(snap['status'], 'denied')
        root = next(s for s in snap['spans'] if s['name'] == 'interaction')
        self.assertEqual(root['status'], 'denied')

    def test_error_status_marks_open_spans_error(self):
        trace = self.tracer.start_interaction('r6')
        with self.assertRaises(RuntimeError):
            with trace.span('execute'):
                raise RuntimeError('tool failed')
        snap = trace.finish(status='error')
        exe = next(s for s in snap['spans'] if s['name'] == 'execute')
        self.assertEqual(exe['status'], 'error')
        self.assertEqual(snap['status'], 'error')

    def test_privacy_strips_prompt_payloads_from_attrs_and_snapshot(self):
        trace = self.tracer.start_interaction('r7')
        with trace.span('plan', attrs={'prompt': 'open bitwarden', 'tool': 'open_app_by_name', 'arguments': {'name': 'x'}}):
            pass
        snap = trace.finish()
        dumped = json.dumps(snap)
        self.assertNotIn('open bitwarden', dumped)
        self.assertNotIn('prompt', dumped)
        plan = next(s for s in snap['spans'] if s['name'] == 'plan')
        self.assertEqual(plan['attrs'].get('tool'), 'open_app_by_name')
        self.assertNotIn('arguments', plan['attrs'])

    def test_placeholder_replies_are_not_meaningful(self):
        self.assertTrue(latency.is_placeholder('Thinking…'))
        self.assertTrue(latency.is_placeholder('Planning your request… Click for live console.'))
        self.assertFalse(latency.is_meaningful(''))
        self.assertTrue(latency.is_meaningful('Review the plan below.'))
        self.assertTrue(latency.is_meaningful('Hello! How can I help?'))

    def test_off_switch_persists_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = latency.Store(Path(tmp) / 't.sqlite')
            tracer = latency.Tracer(store=store, enabled=False, clock=self.clock)
            trace = tracer.start_interaction('r8')
            with trace.span('plan'):
                trace.mark_meaningful()
            self.assertIsNone(trace.finish())
            self.assertEqual(store.recent(), [])


class StoreTest(unittest.TestCase):
    def test_round_trip_and_retention_and_no_prompt_column(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 't.sqlite'
            store = latency.Store(path)
            tracer = latency.Tracer(store=store, clock=clock, jarvis_version='0.5.10',
                                    git_revision='abc', model='qwen2.5:3b')
            keep = latency.TRACE_KEEP
            for i in range(3):
                t = tracer.start_interaction('run-' + str(i), planner_mode='json_plan')
                with t.span('plan'):
                    t.mark_meaningful()
                tracer.finish('run-' + str(i), status='done')
            loaded = store.get_by_run('run-1')
            self.assertEqual(loaded['run_id'], 'run-1')
            self.assertEqual(loaded['jarvis_version'], '0.5.10')
            self.assertTrue(any(s['name'] == 'plan' for s in loaded['spans']))
            self.assertNotIn('prompt', loaded)
            dumped = json.dumps(loaded)
            self.assertNotIn('password', dumped)
            recent = store.recent(limit=2)
            self.assertEqual(len(recent), 2)
            self.assertEqual(oct(path.stat().st_mode)[-3:], '600')

    def test_prune_keeps_newest(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as tmp, patch.object(latency, 'TRACE_KEEP', 2):
            store = latency.Store(Path(tmp) / 't.sqlite')
            tracer = latency.Tracer(store=store, clock=clock)
            for i in range(4):
                tracer.start_interaction('run-' + str(i))
                tracer.finish('run-' + str(i))
            ids = {row['run_id'] for row in store.recent(limit=10)}
            self.assertEqual(ids, {'run-2', 'run-3'})


class ThreadAttachTest(unittest.TestCase):
    def test_current_is_thread_local(self):
        tracer = latency.Tracer(clock=Clock())
        tracer.start_interaction('r-main')
        tracer.attach('r-main')
        self.assertEqual(tracer.current().run_id, 'r-main')
        seen = []

        def worker():
            seen.append(tracer.current())
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        self.assertIsNone(seen[0])
        tracer.detach()
        self.assertIsNone(tracer.current())


class ServerHookTest(unittest.TestCase):
    def test_announce_marks_ack_then_meaningful(self):
        sys.path.insert(0, str(ROOT / 'brain'))
        import server
        from unittest.mock import patch
        tracer = latency.Tracer(clock=Clock(), enabled=True)
        tracer.start_interaction('h1', planner_mode='json_plan')
        original = server.TRACER
        server.TRACER = tracer
        try:
            with patch.object(server, 'log'), patch.dict(server.CONFIG, {'show_notifications': False}):
                server.announce('h1', 'Planning your request… Click for live console.')
                self.assertIsNotNone(tracer.get('h1').ack_ns)
                self.assertIsNone(tracer.get('h1').meaningful_ns)
                server.announce('h1', 'Hello! How can I help?')
                self.assertIsNotNone(tracer.get('h1').meaningful_ns)
        finally:
            server.TRACER = original


class ConfigTest(unittest.TestCase):
    def test_load_config_accepts_falsey_profiler_strings(self):
        import os
        import server
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.toml'
            path.write_text('latency_profiler = "off"\n')
            with patch.dict(os.environ, {'JARVIS_CONFIG': str(path)}):
                cfg = server.load_config()
            self.assertFalse(cfg['latency_profiler'])
            path.write_text('latency_profiler = true\n')
            with patch.dict(os.environ, {'JARVIS_CONFIG': str(path)}):
                self.assertTrue(server.load_config()['latency_profiler'])


if __name__ == '__main__':
    unittest.main()
