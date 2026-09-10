"""A-028: scripts/eval-status.py — docs/evals/cases.json schema + reference validator."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('eval_status', ROOT / 'scripts/eval-status.py')
eval_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eval_status)


def valid_case(**overrides):
    case = dict(id='EVAL-001', version=1, kind='regression', title='x',
                oracle_type='unit-test-reference', execution_level='unit',
                mutation_policy='side-effect-free', owner='control-plane',
                protection_class='protected-regression',
                reference='tests/test_thing.py::ThingTest::test_it_works',
                expected_result='pass')
    case.update(overrides)
    return case


class EvalStatusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cases_path = self.root / 'docs/evals/cases.json'
        self.cases_path.parent.mkdir(parents=True)
        (self.root / 'tests').mkdir()
        (self.root / 'tests/test_thing.py').write_text(
            'import unittest\nclass ThingTest(unittest.TestCase):\n    def test_it_works(self):\n        pass\n')

    def tearDown(self):
        self.temp.cleanup()

    def write_cases(self, cases):
        self.cases_path.write_text(json.dumps({'cases': cases}))

    def test_valid_case_has_no_problems(self):
        self.write_cases([valid_case()])
        self.assertEqual(eval_status.check(self.cases_path, self.root), [])

    def test_missing_required_field_is_a_problem(self):
        case = valid_case()
        del case['owner']
        self.write_cases([case])
        problems = eval_status.check(self.cases_path, self.root)
        self.assertTrue(any('missing required field' in p for p in problems))

    def test_unknown_field_is_a_problem(self):
        self.write_cases([valid_case(unexpected='nope')])
        problems = eval_status.check(self.cases_path, self.root)
        self.assertTrue(any('unknown field' in p for p in problems))

    def test_bad_id_format_is_a_problem(self):
        self.write_cases([valid_case(id='not-an-id')])
        problems = eval_status.check(self.cases_path, self.root)
        self.assertTrue(any('id must match' in p for p in problems))

    def test_duplicate_id_is_a_problem(self):
        self.write_cases([valid_case(), valid_case()])
        problems = eval_status.check(self.cases_path, self.root)
        self.assertTrue(any('duplicate case id' in p for p in problems))

    def test_invalid_enum_value_is_a_problem(self):
        self.write_cases([valid_case(kind='not_a_kind')])
        problems = eval_status.check(self.cases_path, self.root)
        self.assertTrue(any("kind='not_a_kind'" in p for p in problems))

    def test_nonexistent_reference_is_a_problem(self):
        self.write_cases([valid_case(reference='tests/test_thing.py::ThingTest::test_missing')])
        problems = eval_status.check(self.cases_path, self.root)
        self.assertTrue(any('does not resolve' in p for p in problems))

    def test_class_only_reference_is_valid(self):
        self.write_cases([valid_case(reference='tests/test_thing.py::ThingTest')])
        self.assertEqual(eval_status.check(self.cases_path, self.root), [])

    def test_malformed_json_is_a_problem(self):
        self.cases_path.write_text('{not json')
        problems = eval_status.check(self.cases_path, self.root)
        self.assertTrue(any('unreadable or invalid JSON' in p for p in problems))


if __name__ == '__main__':
    unittest.main()
