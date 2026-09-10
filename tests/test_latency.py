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
            path.write_text('latency_budget_p50_ms = 0\nlatency_budget_p90_ms = 250\n')
            with patch.dict(os.environ, {'JARVIS_CONFIG': str(path)}):
                cfg = server.load_config()
            self.assertIsNone(cfg['latency_budget_p50_ms'])
            self.assertEqual(cfg['latency_budget_p90_ms'], 250)


class PercentileTest(unittest.TestCase):
    def test_nearest_rank_ceil(self):
        values = [i * 1_000_000 for i in range(1, 11)]
        self.assertEqual(latency.percentile_ns(values, 50), 5_000_000)
        self.assertEqual(latency.percentile_ns(values, 90), 9_000_000)
        self.assertEqual(latency.percentile_ns(values, 95), 10_000_000)
        self.assertEqual(latency.percentile_ns(values, 99), 10_000_000)
        self.assertEqual(latency.percentile_ns([42], 90), 42)
        self.assertIsNone(latency.percentile_ns([], 50))

    def test_filter_and_summarize_compare_and_ledger_note_has_no_prompt(self):
        traces = [
            {'trace_id': 'a', 'run_id': 'run-a', 'status': 'done', 'planner_mode': 'json_plan',
             'jarvis_version': '0.5.10', 'git_revision': 'abc',
             'meaningful_response_latency_ns': 80_000_000, 'prompt': 'open bitwarden'},
            {'trace_id': 'b', 'run_id': 'run-b', 'status': 'done', 'planner_mode': 'tools',
             'jarvis_version': '0.5.11', 'git_revision': 'def',
             'meaningful_response_latency_ns': 40_000_000},
            {'trace_id': 'c', 'run_id': 'run-c', 'status': 'error', 'planner_mode': 'json_plan',
             'jarvis_version': '0.5.10', 'git_revision': 'abc',
             'meaningful_response_latency_ns': None},
        ]
        only_tools = latency.filter_traces(traces, planner_mode='tools')
        self.assertEqual([t['trace_id'] for t in only_tools], ['b'])
        summary = latency.summarize(
            traces, budgets={'p50_ms': 10, 'p90_ms': 100},
            left='0.5.10', right='0.5.11', left_key='jarvis_version', right_key='jarvis_version')
        self.assertEqual(summary['count'], 3)
        self.assertEqual(summary['with_mrl'], 2)
        self.assertEqual(summary['p50_ns'], 40_000_000)
        self.assertEqual(summary['p90_ns'], 80_000_000)
        self.assertEqual(summary['slow_tail'][0]['trace_id'], 'a')
        self.assertEqual(summary['compare']['left']['count'], 2)
        self.assertEqual(summary['compare']['right']['with_mrl'], 1)
        self.assertTrue(summary['flags']['over_p50'])
        self.assertFalse(summary['flags']['over_p90'])
        self.assertFalse(summary['budgets']['enforced'])
        dumped = json.dumps(summary)
        self.assertNotIn('open bitwarden', dumped)
        self.assertNotIn('prompt', dumped)
        self.assertIn('PERF', summary['ledger_note'])
        self.assertIn('compare 0.5.10', summary['ledger_note'])
        self.assertNotIn('open bitwarden', summary['ledger_note'])

    def test_summarize_window_keeps_unfiltered_options(self):
        traces = [
            {'trace_id': 'a', 'planner_mode': 'json_plan', 'status': 'done',
             'jarvis_version': '0.5.10', 'git_revision': 'abc',
             'meaningful_response_latency_ns': 10_000_000},
            {'trace_id': 'b', 'planner_mode': 'tools', 'status': 'done',
             'jarvis_version': '0.5.11', 'git_revision': 'def',
             'meaningful_response_latency_ns': 20_000_000},
        ]
        summary, filtered = latency.summarize_window(
            traces, {'planner_mode': 'tools', 'limit': 20, 'left': '0.5.10', 'right': '0.5.11',
                     'left_key': 'jarvis_version', 'right_key': 'jarvis_version'})
        self.assertEqual([t['trace_id'] for t in filtered], ['b'])
        self.assertEqual(summary['options']['planner_mode'], ['json_plan', 'tools'])
        self.assertEqual(summary['count'], 1)

    def test_parse_query_bounds_limit_and_keys(self):
        q = latency.parse_query({
            'limit': ['500'], 'left_key': ['prompt'], 'right_key': ['git_revision'],
            'planner_mode': [' json_plan '], 'status': [''],
        })
        self.assertEqual(q['limit'], 100)
        self.assertEqual(q['left_key'], 'jarvis_version')
        self.assertEqual(q['right_key'], 'git_revision')
        self.assertEqual(q['planner_mode'], 'json_plan')
        self.assertIsNone(q['status'])


class SummaryApiTest(unittest.TestCase):
    def test_get_traces_accepts_query_string(self):
        import server
        clock = Clock()
        handler = object.__new__(server.Handler)
        handler.path = '/v1/latency/traces?limit=50&planner_mode=tools'
        handler.headers = {'Host': '127.0.0.1:7421', 'X-Jarvis-Token': server.TOKEN}
        captured = []
        handler.reply = lambda status, body, mime=None: captured.append((status, body)) or (status, body)
        with tempfile.TemporaryDirectory() as tmp:
            store = latency.Store(Path(tmp) / 't.sqlite')
            tracer = latency.Tracer(store=store, clock=clock, enabled=True,
                                    jarvis_version='0.5.11', git_revision='def')
            for run_id, mode in (('run-j', 'json_plan'), ('run-t', 'tools')):
                trace = tracer.start_interaction(run_id, planner_mode=mode)
                trace.mark_meaningful()
                tracer.finish(run_id, status='done')
            original = server.TRACER
            server.TRACER = tracer
            try:
                handler.do_GET()
                handler.path = '/v1/latency/summary?limit=50&left=0.5.11&right=0.5.11&left_key=jarvis_version&right_key=jarvis_version'
                handler.do_GET()
            finally:
                server.TRACER = original
        self.assertEqual(captured[0][0], 200)
        ids = {row['run_id'] for row in captured[0][1]['traces']}
        self.assertEqual(ids, {'run-t'})
        self.assertEqual(captured[1][0], 200)
        self.assertIn('p50_ns', captured[1][1])
        self.assertIn('PERF', captured[1][1]['ledger_note'])
        self.assertNotIn('prompt', json.dumps(captured[1][1]))


if __name__ == '__main__':
    unittest.main()
