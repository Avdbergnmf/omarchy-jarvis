import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'brain'))
import training
import server

spec = importlib.util.spec_from_file_location('open_agent', ROOT/'scripts/open-agent.py')
open_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(open_agent_module)


class OpenAgentScriptTest(unittest.TestCase):
    """A-018: launching/focusing a real Hyprland window for a slot's CLI agent."""

    def test_focuses_existing_window_without_launching(self):
        client = dict(address='0xabc', **{'class': 'jarvis-agent-slot-a1'})
        with tempfile.TemporaryDirectory() as tmp, patch.object(open_agent_module, 'ROOT', Path(tmp)), \
             patch.object(open_agent_module, 'urlopen', return_value=io.BytesIO(b'{"service":"omarchy-jarvis"}')), \
             patch.object(open_agent_module, 'hypr', return_value=[client]), \
             patch.object(open_agent_module, 'dispatch') as dispatch, \
             patch.object(open_agent_module.subprocess, 'Popen') as launch:
            open_agent_module.open_agent('slot-a1', 'claude-code')
            dispatch.assert_called_once_with('focuswindow', 'address:0xabc')
            launch.assert_not_called()

    def test_launches_claude_code_with_a_per_slot_app_id(self):
        client = dict(address='0xdef', **{'class': 'jarvis-agent-slot-a1'})
        with tempfile.TemporaryDirectory() as tmp, patch.object(open_agent_module, 'ROOT', Path(tmp)), \
             patch.object(open_agent_module, 'urlopen', return_value=io.BytesIO(b'{"service":"omarchy-jarvis"}')), \
             patch.object(open_agent_module, 'hypr', side_effect=[[], [client]]), \
             patch.object(open_agent_module, 'dispatch') as dispatch, \
             patch.object(open_agent_module.subprocess, 'Popen') as launch:
            open_agent_module.open_agent('slot-a1', 'claude-code')
            args = launch.call_args.args[0]
            self.assertEqual(args, ['omarchy-launch-or-focus-tui', '--app-id=jarvis-agent-slot-a1', 'claude'])
            dispatch.assert_called_once_with('focuswindow', 'address:0xdef')

    def test_cursor_kind_launches_codex(self):
        client = dict(address='0x1', **{'class': 'jarvis-agent-slot-b2'})
        with tempfile.TemporaryDirectory() as tmp, patch.object(open_agent_module, 'ROOT', Path(tmp)), \
             patch.object(open_agent_module, 'urlopen', return_value=io.BytesIO(b'{"service":"omarchy-jarvis"}')), \
             patch.object(open_agent_module, 'hypr', side_effect=[[], [client]]), \
             patch.object(open_agent_module, 'dispatch'), \
             patch.object(open_agent_module.subprocess, 'Popen') as launch:
            open_agent_module.open_agent('slot-b2', 'cursor', 'xhigh')
            self.assertEqual(launch.call_args.args[0], ['omarchy-launch-or-focus-tui', '--app-id=jarvis-agent-slot-b2', 'codex', '-c', 'model_reasoning_effort="xhigh"'])

    def test_reasoning_effort_is_bounded_to_codex_slots(self):
        with self.assertRaisesRegex(ValueError, 'only for Cursor / Codex'):
            open_agent_module.open_agent('slot-a1', 'claude-code', 'high')
        with self.assertRaisesRegex(ValueError, 'only for Cursor / Codex'):
            open_agent_module.open_agent('slot-b2', 'cursor', 'ultra')

    def test_human_kind_has_nothing_to_launch(self):
        with patch.object(open_agent_module.subprocess, 'Popen') as launch:
            with self.assertRaisesRegex(ValueError, 'own terminal'):
                open_agent_module.open_agent('slot-c3', 'human')
            launch.assert_not_called()

    def test_invalid_slot_id_rejected(self):
        for bad in ('../../etc', 'slot-', 'not-a-slot', ''):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                open_agent_module.open_agent(bad, 'claude-code')

    def test_window_never_appearing_raises_with_log_hint(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(open_agent_module, 'ROOT', Path(tmp)), \
             patch.object(open_agent_module, 'urlopen', return_value=io.BytesIO(b'{"service":"omarchy-jarvis"}')), \
             patch.object(open_agent_module, 'hypr', return_value=[]), \
             patch.object(open_agent_module, 'dispatch') as dispatch, \
             patch.object(open_agent_module.subprocess, 'Popen'), \
             patch.object(open_agent_module.time, 'sleep'):
            with self.assertRaisesRegex(RuntimeError, 'agent-windows/slot-a1.log'):
                open_agent_module.open_agent('slot-a1', 'claude-code')
            dispatch.assert_not_called()


class AgentWindowRouteTest(unittest.TestCase):
    """A-018: the HTTP route always launches the slot's own recorded kind, never a
    client-supplied one, and never for an id that isn't a real registered slot."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        path = self.root/training.SLOTS
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'version': 1, 'agents': [
            dict(id='slot-a1', label='My coding agent', kind='claude-code', status='idle', current_assignment=None, queued_assignment_ids=[]),
            dict(id='slot-b2', label='Codex', kind='cursor', status='idle', current_assignment=None, queued_assignment_ids=[], reasoning_effort='high')]}))

    def tearDown(self):
        self.temp.cleanup()

    def request(self, body):
        handler = object.__new__(server.Handler)
        handler.path = '/v1/training/agent-window'
        payload = json.dumps(body).encode()
        handler.headers = {'Host': '127.0.0.1:7421', 'Content-Type': 'application/json',
                            'Content-Length': str(len(payload)), 'X-Jarvis-Token': server.TOKEN}
        handler.rfile = io.BytesIO(payload)
        handler.reply = lambda status, resp: (status, resp)
        return handler.do_POST()

    def test_launches_using_the_registered_slot_kind_not_the_request_body(self):
        with patch.object(server, 'ROOT', self.root), patch.object(server.subprocess, 'run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, '', '')
            status, body = self.request({'slot_id': 'slot-a1', 'kind': 'cursor'})
        self.assertEqual(status, 200)
        argv = run.call_args.args[0]
        self.assertIn('--slot-id', argv); self.assertEqual(argv[argv.index('--slot-id')+1], 'slot-a1')
        self.assertIn('--kind', argv); self.assertEqual(argv[argv.index('--kind')+1], 'claude-code')

    def test_unknown_slot_is_rejected_before_any_launch(self):
        with patch.object(server, 'ROOT', self.root), patch.object(server.subprocess, 'run') as run:
            status, body = self.request({'slot_id': 'slot-does-not-exist'})
        self.assertEqual(status, 400)
        run.assert_not_called()

    def test_registered_codex_effort_is_passed_to_launcher(self):
        with patch.object(server, 'ROOT', self.root), patch.object(server.subprocess, 'run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, '', '')
            status, body = self.request({'slot_id': 'slot-b2', 'reasoning_effort': 'low'})
        self.assertEqual(status, 200)
        argv = run.call_args.args[0]
        self.assertEqual(argv[argv.index('--reasoning-effort')+1], 'high')

    def test_script_failure_surfaces_as_conflict(self):
        with patch.object(server, 'ROOT', self.root), patch.object(server.subprocess, 'run') as run:
            run.return_value = subprocess.CompletedProcess([], 1, '', 'Agent window did not appear')
            status, body = self.request({'slot_id': 'slot-a1'})
        self.assertEqual(status, 409)
        self.assertIn('did not appear', body['error'])


class FindSlotTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        path = self.root/training.SLOTS
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'version': 1, 'agents': [
            dict(id='slot-a1', label='Tester', kind='human', status='idle', current_assignment=None, queued_assignment_ids=[])]}))

    def tearDown(self):
        self.temp.cleanup()

    def test_returns_the_matching_slot(self):
        self.assertEqual(training.find_slot(self.root, 'slot-a1')['label'], 'Tester')

    def test_unknown_id_raises(self):
        with self.assertRaisesRegex(ValueError, 'Unknown agent slot'):
            training.find_slot(self.root, 'slot-nope')

    def test_codex_config_effort_is_bounded(self):
        config = self.root/'config.toml'
        config.write_text('model_reasoning_effort = "medium"\n')
        self.assertEqual(training.codex_default_reasoning_effort(config), 'medium')
        config.write_text('model_reasoning_effort = "ultra"\n')
        self.assertIsNone(training.codex_default_reasoning_effort(config))

    def test_dashboard_reports_config_default_and_slot_override(self):
        path = self.root/training.SLOTS
        path.write_text(json.dumps({'version': 1, 'agents': [
            dict(id='slot-a1', label='Default', kind='cursor', status='idle', current_assignment=None, queued_assignment_ids=[]),
            dict(id='slot-b2', label='Override', kind='cursor', status='idle', current_assignment=None, queued_assignment_ids=[], reasoning_effort='high')]}))
        with patch.object(training, 'codex_default_reasoning_effort', return_value='medium'), \
             patch.object(training.subprocess, 'run', side_effect=OSError('offline')):
            agents = training.dashboard(self.root, 'test', 'abc')['agents']
        self.assertEqual((agents[0]['effective_reasoning_effort'], agents[0]['reasoning_effort_source']), ('medium', 'Codex config'))
        self.assertEqual((agents[1]['effective_reasoning_effort'], agents[1]['reasoning_effort_source']), ('high', 'slot launch setting'))


if __name__ == '__main__':
    unittest.main()
