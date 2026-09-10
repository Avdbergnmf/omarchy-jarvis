"""A-031: stochastic planner-eval runner — registry, oracles, isolation, evidence shape."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stochastic_evals', ROOT / 'scripts/stochastic-evals.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def planner_case(**overrides):
    case = dict(
        id='SEVAL-001', version=1, kind='regression', title='t', surface='planner-json',
        owner='control-plane', protection_class='protected-regression', prompt='hello',
        expect={'actions': 'none', 'reply': 'must-not-claim-action'},
    )
    case.update(overrides)
    return case


def router_case(**overrides):
    case = dict(
        id='SEVAL-015', version=1, kind='regression', title='t', surface='router',
        owner='control-plane', protection_class='protected-regression', prompt='no, the other one',
        expect={'route': 'correction', 'detail': {'query': None}},
    )
    case.update(overrides)
    return case


UNAPPROVED = {'status': 'unapproved', 'approved_by': None, 'approved_at': None,
              'approved_summary': None, 'trials': None, 'tolerance': {}}


class RegistryTest(unittest.TestCase):
    def test_shipped_registry_is_valid(self):
        cases = json.loads((ROOT / 'docs/evals/stochastic/cases.json').read_text())['cases']
        baseline = json.loads((ROOT / 'docs/evals/stochastic/baseline.json').read_text())
        self.assertEqual(mod.validate(cases, baseline), [])
        self.assertGreaterEqual(len(cases), 10)
        self.assertLessEqual(len(cases), 20)
        self.assertEqual(sum(1 for c in cases if c['surface'] == 'planner-json'), 14)
        self.assertEqual(sum(1 for c in cases if c['surface'] == 'router'), 6)

    def test_validate_cli_exits_zero(self):
        self.assertEqual(mod.main(['--validate']), 0)

    def test_unknown_tool_is_a_problem(self):
        problems = mod.validate([planner_case(expect={'actions': ['not_a_tool']})], UNAPPROVED)
        self.assertTrue(any('unknown tool' in p for p in problems))

    def test_excluded_tool_cannot_be_an_expected_action(self):
        problems = mod.validate([planner_case(expect={'actions': ['report_bug']})], UNAPPROVED)
        self.assertTrue(any('planner-excluded' in p for p in problems))

    def test_argument_must_belong_to_the_named_tool(self):
        problems = mod.validate([planner_case(expect={
            'actions': ['scratch_toggle'], 'arguments': {'name': 'x'},
        })], UNAPPROVED)
        self.assertTrue(any('has no argument' in p for p in problems))

    def test_duplicate_id_is_a_problem(self):
        problems = mod.validate([planner_case(), planner_case()], UNAPPROVED)
        self.assertTrue(any('duplicate' in p for p in problems))

    def test_approved_baseline_requires_every_planner_tolerance(self):
        approved = dict(UNAPPROVED, status='approved', approved_by='Alex',
                        approved_at='2026-09-10', approved_summary='docs/x.json', trials=3)
        problems = mod.validate([planner_case(), router_case()], approved)
        self.assertTrue(any('SEVAL-001' in p and 'tolerance' in p for p in problems))
        self.assertFalse(any('SEVAL-015' in p for p in problems))


class OracleTest(unittest.TestCase):
    def test_empty_plan_that_claims_an_action_fails(self):
        outcome, reason = mod.grade_plan(
            planner_case(), {'actions': [], 'reply': 'Opening YouTube.'})
        self.assertEqual(outcome, 'fail')
        self.assertIn('claims an action', reason)

    def test_honest_chitchat_passes(self):
        outcome, _ = mod.grade_plan(
            planner_case(), {'actions': [], 'reply': 'Hello! How can I help?'})
        self.assertEqual(outcome, 'pass')

    def test_wrong_tool_fails(self):
        case = planner_case(expect={'actions': ['open_webapp'], 'arguments': {'name': 'youtube'}})
        outcome, reason = mod.grade_plan(case, {
            'actions': [{'tool': 'open_app_by_name', 'arguments': {'name': 'YouTube'}}],
            'reply': 'Opening YouTube.',
        })
        self.assertEqual(outcome, 'fail')
        self.assertIn('open_app_by_name', reason)

    def test_argument_regex_is_case_insensitive(self):
        case = planner_case(expect={'actions': ['open_webapp'], 'arguments': {'name': 'youtube'}})
        outcome, _ = mod.grade_plan(case, {
            'actions': [{'tool': 'open_webapp', 'arguments': {'name': 'YouTube'}}],
            'reply': 'Opening YouTube.',
        })
        self.assertEqual(outcome, 'pass')

    def test_planner_rejection_can_be_the_correct_answer(self):
        case = planner_case(expect={'forbidden_tools': ['report_bug'], 'planner_rejection': 'pass'})
        outcome, _ = mod.grade_plan(case, {}, error='ValueError: intake flow')
        self.assertEqual(outcome, 'pass')

    def test_forbidden_tool_fails_even_without_an_actions_clause(self):
        case = planner_case(expect={'forbidden_tools': ['report_bug']})
        outcome, _ = mod.grade_plan(case, {
            'actions': [{'tool': 'report_bug', 'arguments': {'title': 'x', 'body': 'y', 'difficulty': 'S'}}],
            'reply': 'Filing.',
        })
        self.assertEqual(outcome, 'fail')

    def test_router_grades_mode_and_detail(self):
        outcome, _ = mod.grade_route(router_case(), {'mode': 'correction', 'correction': {'query': None}})
        self.assertEqual(outcome, 'pass')
        outcome, reason = mod.grade_route(router_case(), {'mode': 'json_plan'})
        self.assertEqual(outcome, 'fail')
        self.assertIn('json_plan', reason)


class IsolationAndRunnerTest(unittest.TestCase):
    def test_non_local_url_is_blocked(self):
        tripped, seen = [], []
        guarded = mod.local_only(lambda *a, **k: 'ok', tripped, seen)

        class Req:
            full_url = 'https://example.com/api'
        with self.assertRaises(mod.ExecutionAttempted):
            guarded(Req())
        self.assertEqual(tripped[0]['surface'], 'urlopen')
        self.assertEqual(seen, [])

    def test_local_ollama_url_is_allowed(self):
        tripped, seen = [], []
        guarded = mod.local_only(lambda *a, **k: 'ok', tripped, seen)

        class Req:
            full_url = 'http://127.0.0.1:11434/api/chat'
        self.assertEqual(guarded(Req()), 'ok')
        self.assertEqual(seen, ['http://127.0.0.1:11434/api/chat'])
        self.assertEqual(tripped, [])

    def test_tripwire_records_the_surface_and_raises(self):
        tripped = []
        guard = mod.tripwire('server.execute_plan', tripped)
        with self.assertRaises(mod.ExecutionAttempted):
            guard('rid', {'actions': []}, None)
        self.assertEqual(tripped[0]['surface'], 'server.execute_plan')

    def test_stub_planner_trial_does_not_execute_or_write_logs(self):
        stub = ROOT / 'docs/evals/stochastic/fixtures/stub-replies.json'
        options = mod.parse_args([
            '--backend', 'stub', '--stub', str(stub), '--trials', '2', '--quiet', '--no-evidence',
            '--case', 'SEVAL-001',
        ])
        result, trials, private = mod.run_case(planner_case(), options)
        self.assertEqual(result['successes'], 2)
        self.assertEqual(result['trials'], 2)
        self.assertEqual(result['tripwires'], [])
        self.assertEqual(result['state_notes'], [])
        self.assertTrue(result['consistent_output'])
        self.assertEqual(private, [None, None])
        self.assertEqual({t['outcome'] for t in trials}, {'pass'})

    def test_flaky_stub_reports_mixed_successes_and_honesty_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp) / 'stub.json'
            stub.write_text(json.dumps({'open youtube': [
                {'actions': [{'tool': 'open_webapp', 'arguments': {'name': 'YouTube'}}], 'reply': 'Opening YouTube.'},
                {'actions': [], 'reply': 'Opening YouTube.'},
                {'actions': [{'tool': 'open_webapp', 'arguments': {'name': 'YouTube'}}], 'reply': 'Opening YouTube.'},
            ]}))
            options = mod.parse_args([
                '--backend', 'stub', '--stub', str(stub), '--trials', '3', '--quiet', '--no-evidence',
            ])
            case = planner_case(
                id='SEVAL-002', prompt='open youtube',
                expect={'actions': ['open_webapp'], 'arguments': {'name': 'youtube'}},
            )
            result, _, _ = mod.run_case(case, options)
        self.assertEqual(result['successes'], 2)
        self.assertEqual(result['failures'], 1)
        self.assertFalse(result['consistent_actions'])
        self.assertEqual(result['honesty_guard_rewrites'], 1)

    def test_router_surface_is_unanimous_without_a_model(self):
        options = mod.parse_args(['--surface', 'router', '--quiet', '--no-evidence'])
        result, trials, _ = mod.run_case(router_case(), options)
        self.assertEqual(result['trials'], 1)
        self.assertEqual(result['successes'], 1)
        self.assertEqual(result['tripwires'], [])
        self.assertEqual(trials[0]['model_calls'], 0)

    def test_gate_refuses_an_unapproved_baseline(self):
        self.assertEqual(mod.main(['--gate', '--surface', 'router', '--quiet', '--no-evidence']), 1)

    def test_ollama_backend_without_a_daemon_fails_closed(self):
        with patch.object(mod, 'ollama_reachable', return_value=False):
            self.assertEqual(mod.main(['--case', 'SEVAL-001', '--quiet', '--no-evidence']), 1)

    def test_eval_envelope_is_kind_eval_and_never_stores_raw_text(self):
        fp = __import__('evidence', fromlist=['fingerprint']).fingerprint(
            jarvis_version='0.5.10', git_revision='abc', planner_mode='json_plan', model='stub',
            model_digest=None, system_prompt_hash='sp', schema_hash='sc', options={'temperature': 0},
            case_id='SEVAL-001', case_version=1)
        import evidence
        env = evidence.build_eval_envelope(
            fp, {'total': 3, 'passed': 2, 'failed': 1, 'errored': 0},
            [{'index': 0, 'outcome': 'pass', 'output_digest': 'aaa'},
             {'index': 1, 'outcome': 'fail', 'output_digest': 'bbb'},
             {'index': 2, 'outcome': 'pass', 'output_digest': 'aaa'}],
            source={'host': {'ollama': 'stub'}})
        self.assertEqual(env['kind'], 'eval')
        dumped = json.dumps(env)
        self.assertNotIn('Opening', dumped)
        self.assertNotIn('reply', dumped)
        with self.assertRaises(ValueError):
            evidence.build_eval_envelope(fp, {}, [], tier='full')
        with tempfile.TemporaryDirectory() as tmp:
            path, created = evidence.write_bundle(Path(tmp), env)
            self.assertTrue(created)
            on_disk = json.loads(path.read_text())
            self.assertEqual(on_disk['id'], path.stem)
            self.assertEqual(on_disk['counts']['passed'], 2)

    def test_private_out_is_mode_0600_and_absent_from_summary(self):
        stub = ROOT / 'docs/evals/stochastic/fixtures/stub-replies.json'
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / 'private'
            summary = Path(tmp) / 'summary.json'
            rc = mod.main([
                '--backend', 'stub', '--stub', str(stub), '--case', 'SEVAL-001',
                '--trials', '1', '--quiet', '--no-evidence',
                '--private-out', str(private), '--summary-out', str(summary),
            ])
            self.assertEqual(rc, 0)
            raw = json.loads((private / 'SEVAL-001.json').read_text())
            self.assertIn('Hello', json.dumps(raw))
            self.assertEqual(oct((private / 'SEVAL-001.json').stat().st_mode)[-3:], '600')
            body = summary.read_text()
            self.assertNotIn('Hello! How can I help?', body)
            self.assertIn('private directory', json.loads(body)['raw_model_output'])


if __name__ == '__main__':
    unittest.main()
