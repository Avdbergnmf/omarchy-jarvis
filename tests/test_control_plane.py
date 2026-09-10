import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'check_control_plane', ROOT / 'scripts/check-control-plane.py'
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ControlPlaneBoundaryTest(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        manifest = {
            'version': 1,
            'owner': '@alex',
            'boundary_roots': ['brain/', 'docs/evals/'],
            'required_paths': ['brain/server.py', 'tests/oracle.py'],
            'classifications': [
                {'pattern': 'brain/**', 'class': 'runtime-mixed'},
                {'pattern': 'docs/evals/**', 'class': 'success-definition'},
                {'pattern': 'tests/oracle.py', 'class': 'protected-oracle-source'},
            ],
        }
        manifest_path = root / 'manifest.json'
        manifest_path.write_text(json.dumps(manifest))
        owners = root / 'CODEOWNERS'
        owners.write_text('/brain/** @alex\n/docs/evals/** @alex\n/tests/oracle.py @alex\n')
        cases = root / 'cases.json'
        cases.write_text(json.dumps({'cases': [{
            'protection_class': 'protected-regression',
            'reference': 'tests/oracle.py::Case::test_rule',
        }]}))
        paths = {'brain/server.py', 'docs/evals/cases.json', 'tests/oracle.py'}
        return tmp, root, manifest_path, owners, cases, paths

    def run_check(self, mutate=None):
        tmp, root, manifest, owners, cases, paths = self.fixture()
        self.addCleanup(tmp.cleanup)
        if mutate:
            mutate(root, manifest, owners, cases, paths)
        return mod.check(root, manifest, owners, cases, paths)

    def test_valid_inventory(self):
        self.assertEqual([], self.run_check())

    def test_new_file_under_boundary_root_fails(self):
        def mutate(_root, _manifest, _owners, _cases, paths):
            paths.add('brain/new/authority.toml')
            data = json.loads(_manifest.read_text())
            data['classifications'][0]['pattern'] = 'brain/*.py'
            _manifest.write_text(json.dumps(data))
        self.assertTrue(any('unclassified' in p for p in self.run_check(mutate)))

    def test_missing_required_path_fails(self):
        def mutate(_root, _manifest, _owners, _cases, paths):
            paths.remove('brain/server.py')
        self.assertTrue(any('missing or untracked' in p for p in self.run_check(mutate)))

    def test_new_protected_oracle_source_fails(self):
        def mutate(_root, _manifest, _owners, cases, paths):
            paths.add('tests/new_oracle.py')
            cases.write_text(json.dumps({'cases': [{
                'protection_class': 'protected-regression',
                'reference': 'tests/new_oracle.py::Case::test_rule',
            }]}))
        self.assertTrue(any('protected-oracle-source' in p for p in self.run_check(mutate)))

    def test_codeowners_drift_fails(self):
        def mutate(_root, _manifest, owners, _cases, _paths):
            owners.write_text('/brain/** @alex\n')
        self.assertTrue(any('CODEOWNERS' in p for p in self.run_check(mutate)))

    def test_malformed_manifest_fails_cleanly(self):
        def mutate(_root, manifest, _owners, _cases, _paths):
            manifest.write_text('{')
        self.assertTrue(any('invalid JSON' in p for p in self.run_check(mutate)))


if __name__ == '__main__':
    unittest.main()
