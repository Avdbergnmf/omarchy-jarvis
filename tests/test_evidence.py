"""A-038: evidence identity + durable bundles — no network/desktop calls except the
explicitly mocked or no-network-behavior cases."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'brain'))
import evidence


def phases(run_id='r1', mode='json_plan', model='qwen2.5:3b', version='0.5.9', revision='v0.5.0-1-gabc'):
    common = dict(jarvis_version=version, git_describe=revision, run_id=run_id)
    return [
        dict(common, phase='prompt', prompt='open bitwarden', mode=mode, model=model),
        dict(common, phase='process', process={'actions': [{'tool': 'open_app_by_name', 'arguments': {'name': 'bitwarden'}}], 'reply': 'Opening Bitwarden.'}),
        dict(common, phase='done', happened={'status': 'done', 'reply': 'Opened Bitwarden.', 'steps': [{'tool': 'open_app_by_name', 'status': 'done'}]}, ok=True),
        dict(common, phase='eval', eval={'ok': True, 'flag': None, 'note': 'No inconsistency.'}, ok=True),
    ]


def fp(**overrides):
    base = dict(jarvis_version='0.5.9', git_revision='v0.5.0-1-gabc', planner_mode='json_plan', model='qwen2.5:3b',
                model_digest='deadbeef', system_prompt_hash='sp-hash', schema_hash='schema-hash', options={'temperature': 0})
    base.update(overrides)
    return evidence.fingerprint(**base)


class ReadRunPhasesTest(unittest.TestCase):
    def test_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(evidence.read_run_phases(tmp, 'nope'), [])

    def test_skips_damaged_lines_keeps_good_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp)
            path = logs / 'runs' / 'r1.log'
            path.parent.mkdir(parents=True)
            path.write_text('not json\n' + json.dumps({'phase': 'prompt', 'run_id': 'r1'}) + '\n{"incomplete":\n')
            result = evidence.read_run_phases(logs, 'r1')
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['phase'], 'prompt')

    def test_refuses_symlinked_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp)
            real = logs / 'elsewhere.log'
            real.write_text(json.dumps({'phase': 'prompt', 'run_id': 'r1'}) + '\n')
            (logs / 'runs').mkdir()
            (logs / 'runs' / 'r1.log').symlink_to(real)
            self.assertEqual(evidence.read_run_phases(logs, 'r1'), [])


class FingerprintAndEnvelopeTest(unittest.TestCase):
    def test_stable_fingerprint_and_content_id_for_identical_inputs(self):
        env_a = evidence.build_envelope(phases(), fp(), tier='summary')
        env_b = evidence.build_envelope(phases(), fp(), tier='summary')
        self.assertEqual(env_a['fingerprint'], env_b['fingerprint'])
        self.assertEqual(evidence.content_id(env_a), evidence.content_id(env_b))

    def test_mutable_model_digest_changes_the_address(self):
        env_a = evidence.build_envelope(phases(), fp(model_digest='digest-old'), tier='summary')
        env_b = evidence.build_envelope(phases(), fp(model_digest='digest-new'), tier='summary')
        self.assertNotEqual(evidence.content_id(env_a), evidence.content_id(env_b),
                             'a mutated model tag/digest must address a different bundle')

    def test_dirty_revision_is_carried_through_unchanged(self):
        env = evidence.build_envelope(phases(), fp(git_revision='v0.5.0-1-gabc-dirty'), tier='summary')
        self.assertEqual(env['fingerprint']['git_revision'], 'v0.5.0-1-gabc-dirty')

    def test_reference_tier_has_no_content_only_fingerprint(self):
        env = evidence.build_envelope(phases(), fp(), tier='reference')
        self.assertNotIn('summary', env)
        self.assertNotIn('private', env)
        self.assertEqual(env['source']['phases_present'], ['done', 'eval', 'process', 'prompt'])

    def test_summary_tier_redacts_and_omits_private(self):
        secret_phases = phases()
        secret_phases[0]['prompt'] = 'use api_key=sk-should-not-leak-anywhere-at-all please'
        env = evidence.build_envelope(secret_phases, fp(), tier='summary')
        self.assertNotIn('private', env)
        self.assertNotIn('sk-should-not-leak-anywhere-at-all', json.dumps(env))

    def test_full_tier_includes_redacted_private_prompt_and_reply(self):
        secret_phases = phases()
        secret_phases[0]['prompt'] = 'token=sk-shouldnotleakanywhereatall12345 please open bitwarden'
        env = evidence.build_envelope(secret_phases, fp(), tier='full')
        self.assertIn('private', env)
        self.assertIn('[REDACTED]', env['private']['prompt'])
        self.assertNotIn('sk-shouldnotleakanywhereatall12345', env['private']['prompt'])
        self.assertEqual(env['private']['reply'], 'Opened Bitwarden.')

    def test_malformed_source_missing_phases_does_not_crash(self):
        only_prompt = [p for p in phases() if p['phase'] == 'prompt']
        env = evidence.build_envelope(only_prompt, fp(), tier='full')
        self.assertEqual(env['source']['phases_present'], ['prompt'])
        self.assertIsNone(env['summary']['status'])
        self.assertEqual(env['summary']['step_count'], 0)
        self.assertIsNone(env['private']['reply'])

    def test_unknown_tier_rejected(self):
        with self.assertRaises(ValueError):
            evidence.build_envelope(phases(), fp(), tier='ultra')


class WriteBundleTest(unittest.TestCase):
    def test_atomicity_no_partial_file_on_interrupted_write(self):
        env = evidence.build_envelope(phases(), fp(), tier='summary')
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'evidence'
            with patch('os.fdopen', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    evidence.write_bundle(dest, env)
            leftovers = list(dest.glob('*')) if dest.exists() else []
            self.assertEqual(leftovers, [], 'an interrupted write must leave no partial or temp file behind')

    def test_bounds_reject_oversized_bundle(self):
        env = evidence.build_envelope(phases(), fp(), tier='full')
        env['private']['prompt'] = 'x' * 200_000
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'bound'):
                evidence.write_bundle(Path(tmp) / 'evidence', env)

    def test_collision_handling_identical_content_is_not_rewritten(self):
        env = evidence.build_envelope(phases(), fp(), tier='summary')
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'evidence'
            path_a, created_a = evidence.write_bundle(dest, env)
            path_b, created_b = evidence.write_bundle(dest, env)
            self.assertTrue(created_a)
            self.assertFalse(created_b, 'identical content must not create a second file')
            self.assertEqual(path_a, path_b)
            self.assertEqual(len(list(dest.glob('*.json'))), 1)

    def test_file_and_directory_mode_are_owner_only(self):
        env = evidence.build_envelope(phases(), fp(), tier='summary')
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'evidence'
            path, _ = evidence.write_bundle(dest, env)
            self.assertEqual(oct(path.stat().st_mode)[-3:], '600')
            self.assertEqual(oct(dest.stat().st_mode)[-3:], '700')

    def test_refuses_symlinked_destination(self):
        env = evidence.build_envelope(phases(), fp(), tier='summary')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / 'real'; real.mkdir()
            link = root / 'evidence'; link.symlink_to(real)
            with self.assertRaises(ValueError):
                evidence.write_bundle(link, env)

    def test_id_field_matches_the_addressed_filename(self):
        env = evidence.build_envelope(phases(), fp(), tier='summary')
        with tempfile.TemporaryDirectory() as tmp:
            path, _ = evidence.write_bundle(Path(tmp) / 'evidence', env)
            on_disk = json.loads(path.read_text())
            self.assertEqual(path.stem, on_disk['id'])


class OllamaDigestTest(unittest.TestCase):
    def test_no_network_behavior_never_raises(self):
        with patch('evidence.urlopen', side_effect=OSError('offline')):
            self.assertIsNone(evidence.ollama_model_digest('qwen2.5:3b'))

    def test_finds_matching_model_digest(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self, n=None): return json.dumps({'models': [{'name': 'qwen2.5:3b', 'digest': 'abc123'}]}).encode()
        with patch('evidence.urlopen', return_value=FakeResponse()):
            self.assertEqual(evidence.ollama_model_digest('qwen2.5:3b'), 'abc123')

    def test_unmatched_model_returns_none(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self, n=None): return json.dumps({'models': [{'name': 'other:1b', 'digest': 'xyz'}]}).encode()
        with patch('evidence.urlopen', return_value=FakeResponse()):
            self.assertIsNone(evidence.ollama_model_digest('qwen2.5:3b'))


if __name__ == '__main__':
    unittest.main()
