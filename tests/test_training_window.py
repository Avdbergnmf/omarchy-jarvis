import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('training_window', ROOT/'scripts/open-training.py')
window = importlib.util.module_from_spec(spec)
spec.loader.exec_module(window)


class TrainingWindowTest(unittest.TestCase):
    def test_existing_training_focuses_without_toggling_chat(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(window, 'ROOT', Path(tmp)), patch.object(window, 'urlopen', return_value=io.BytesIO(b'{"service":"omarchy-jarvis"}')), patch.object(window, 'hypr', return_value=[dict(address='0x1', **{'class':'jarvis-overlay'}), dict(address='0x2', **{'class':'chrome-jarvis-training'})]), patch.object(window, 'dispatch') as dispatch, patch.object(window.subprocess, 'Popen') as launch:
            window.open_training()
            dispatch.assert_called_once_with('focuswindow', 'address:0x2')
            launch.assert_not_called()

    def test_new_training_has_separate_profile_and_addressed_float(self):
        client = dict(address='0x2', floating=False, **{'class':'jarvis-training'})
        with tempfile.TemporaryDirectory() as tmp, patch.object(window, 'ROOT', Path(tmp)), patch.object(window, 'urlopen', return_value=io.BytesIO(b'{"service":"omarchy-jarvis"}')), patch.object(window, 'hypr', side_effect=[[], [client]]), patch.object(window, 'dispatch') as dispatch, patch.object(window.subprocess, 'Popen') as launch, patch.object(window.subprocess, 'run') as commands:
            window.open_training()
            args = launch.call_args.args[0]
            self.assertIn('--app=http://127.0.0.1:7421/jarvis-training', args)
            self.assertIn('--user-data-dir='+tmp+'/logs/training-profile', args)
            self.assertEqual(commands.call_count, 2)
            for call in commands.call_args_list:
                self.assertIn('address:0x2', call.args[0][-1])
            dispatch.assert_called_once_with('focuswindow', 'address:0x2')
