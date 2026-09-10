"""A-026: docs/ledger validator (scripts/ledger-status.py). No network/desktop calls."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ledger_status', ROOT / 'scripts/ledger-status.py')
ledger_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger_status)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class LedgerStatusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.ledger = self.root / 'docs/ledger'
        self.assignments_index = self.root / 'docs/assignments/INDEX.md'
        write(self.assignments_index, '| id | title | status | area | parallel-ok | path |\n|----|----|----|----|----|----|\n| A-024 | x | done | area:actions | YES | done/A-024-x.md |\n')

    def tearDown(self):
        self.temp.cleanup()

    def index_line(self, imp_id='IMP-001', status='shipped', assignments='A-024', filename='IMP-001-x.md'):
        return f'| {imp_id} | Some title | {status} | {assignments} | [records/{filename}](records/{filename}) |\n'

    def write_record(self, filename='IMP-001-x.md', header_id='IMP-001'):
        write(self.ledger / 'records' / filename, f'# {header_id} — Some title\n\n- **Status:** shipped\n')

    def test_consistent_ledger_has_no_problems_and_computes_next_id(self):
        write(self.ledger / 'INDEX.md', self.index_line())
        self.write_record()
        problems, next_id = ledger_status.check(self.ledger, self.assignments_index)
        self.assertEqual(problems, [])
        self.assertEqual(next_id, 'IMP-002')

    def test_empty_ledger_next_id_is_001(self):
        write(self.ledger / 'INDEX.md', '# Improvement Ledger index\n\n| id | ... |\n')
        problems, next_id = ledger_status.check(self.ledger, self.assignments_index)
        self.assertEqual(problems, [])
        self.assertEqual(next_id, 'IMP-001')

    def test_duplicate_id_is_a_problem(self):
        write(self.ledger / 'INDEX.md', self.index_line() + self.index_line())
        self.write_record()
        problems, _ = ledger_status.check(self.ledger, self.assignments_index)
        self.assertTrue(any('duplicate id IMP-001' in p for p in problems))

    def test_missing_record_file_is_a_problem(self):
        write(self.ledger / 'INDEX.md', self.index_line())
        problems, _ = ledger_status.check(self.ledger, self.assignments_index)
        self.assertTrue(any('does not exist' in p for p in problems))

    def test_header_id_mismatch_is_a_problem(self):
        write(self.ledger / 'INDEX.md', self.index_line())
        self.write_record(header_id='IMP-002')
        problems, _ = ledger_status.check(self.ledger, self.assignments_index)
        self.assertTrue(any('record file header does not start with "# IMP-001"' in p for p in problems))

    def test_unknown_assignment_reference_is_a_problem(self):
        write(self.ledger / 'INDEX.md', self.index_line(assignments='A-999'))
        self.write_record()
        problems, _ = ledger_status.check(self.ledger, self.assignments_index)
        self.assertTrue(any('A-999' in p and 'absent from docs/assignments/INDEX.md' in p for p in problems))

    def test_orphan_record_file_is_a_problem(self):
        write(self.ledger / 'INDEX.md', '# empty\n')
        self.write_record()
        problems, _ = ledger_status.check(self.ledger, self.assignments_index)
        self.assertTrue(any('has no INDEX.md row' in p for p in problems))

    def test_unknown_status_is_a_problem(self):
        write(self.ledger / 'INDEX.md', self.index_line(status='done'))
        self.write_record()
        problems, _ = ledger_status.check(self.ledger, self.assignments_index)
        self.assertTrue(any("unknown status 'done'" in p for p in problems))

    def test_no_assignment_ids_is_allowed(self):
        write(self.ledger / 'INDEX.md', self.index_line(assignments=''))
        self.write_record()
        problems, _ = ledger_status.check(self.ledger, self.assignments_index)
        self.assertEqual(problems, [])


if __name__ == '__main__':
    unittest.main()
