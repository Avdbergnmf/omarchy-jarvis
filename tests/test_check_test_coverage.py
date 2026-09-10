"""A-028: scripts/check-test-coverage.py — the "no quiet suite omission" CI contract."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_test_coverage', ROOT / 'scripts/check-test-coverage.py')
check_test_coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_test_coverage)

CI_YML = "name: checks\njobs:\n  test:\n    steps:\n      - run: python3 -m unittest discover -s tests -v\n      - run: node tests/overlay.test.cjs\n"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class CheckTestCoverageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tests = Path(self.temp.name) / 'tests'
        self.ci = Path(self.temp.name) / 'ci.yml'
        write(self.ci, CI_YML)

    def tearDown(self):
        self.temp.cleanup()

    def test_entrypoint_and_its_requires_are_all_reachable(self):
        write(self.tests / 'overlay.test.cjs', "require('./training.test.cjs');\nrequire('./agents.test.cjs');\n")
        write(self.tests / 'training.test.cjs', "// ok\n")
        write(self.tests / 'agents.test.cjs', "// ok\n")
        write(self.tests / 'test_thing.py', "# ok\n")
        self.assertEqual(check_test_coverage.check(self.tests, self.ci), [])

    def test_orphan_cjs_file_is_a_problem(self):
        write(self.tests / 'overlay.test.cjs', "// no requires\n")
        write(self.tests / 'orphan.test.cjs', "// never required, never a direct entrypoint\n")
        problems = check_test_coverage.check(self.tests, self.ci)
        self.assertTrue(any('orphan.test.cjs' in p and 'not reachable' in p for p in problems))

    def test_transitively_required_file_is_reachable(self):
        # overlay requires training, which requires a deeper file two hops away.
        write(self.tests / 'overlay.test.cjs', "require('./training.test.cjs');\n")
        write(self.tests / 'training.test.cjs', "require('./deep.test.cjs');\n")
        write(self.tests / 'deep.test.cjs', "// ok\n")
        self.assertEqual(check_test_coverage.check(self.tests, self.ci), [])

    def test_misnamed_python_file_is_a_problem(self):
        write(self.tests / 'overlay.test.cjs', "// ok\n")
        write(self.tests / 'checks_something.py', "# unittest discover would never find this\n")
        problems = check_test_coverage.check(self.tests, self.ci)
        self.assertTrue(any('checks_something.py' in p and 'test_*.py' in p for p in problems))

    def test_no_cjs_entrypoint_in_ci_is_a_problem(self):
        write(self.ci, "name: checks\njobs:\n  test:\n    steps:\n      - run: python3 -m unittest discover -s tests -v\n")
        write(self.tests / 'overlay.test.cjs', "// ok\n")
        problems = check_test_coverage.check(self.tests, self.ci)
        self.assertTrue(any('no "node tests' in p for p in problems))


if __name__ == '__main__':
    unittest.main()
