"""A-042: assignment-status.sh claim hint matches ADR-048 (synthetic origin/main)."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/assignment-status.sh'

QUEUE_HEADER = """# Queue

| id | title | status | area | parallel-ok | depth | path |
|----|-------|--------|------|-------------|-------|------|
"""
INDEX_HEADER = """# Index

| id | title | status | area | parallel-ok | path |
|----|-------|--------|------|-------------|------|
"""


def brief(aid, area, parallel, blocked='none', allowed='', forbidden='', soft=''):
    lines = [
        f'# {aid} — {aid}',
        f'- **Status:** queued',
        f'- **Area:** {area}',
        f'- **parallel-ok:** {parallel}',
        f'- **Blocked-by:** {blocked}',
        '- **Gate:** none',
    ]
    if soft:
        lines.append(f'- **Soft path hints:** {soft}')
    else:
        lines.append(f'- **Allowed paths (optional soft hint):** {allowed}')
        lines.append(f'- **Forbidden paths (optional soft hint):** {forbidden or "none"}')
    return '\n'.join(lines) + '\n'


def queue_row(aid, status, area, parallel, depth='medium'):
    rel = f'active/{aid}-x.md'
    return f'| {aid} | {aid} | {status} | {area} | {parallel} | {depth} | [{rel}]({rel}) |'


def index_row(aid, status, area, parallel):
    rel = f'active/{aid}-x.md'
    return f'| {aid} | {aid} | {status} | {area} | {parallel} | [{rel}]({rel}) |'


class AssignmentStatusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name) / 'work'
        self.work.mkdir()
        (self.work / 'scripts').mkdir()
        shutil.copy(SCRIPT, self.work / 'scripts/assignment-status.sh')
        (self.work / 'docs/assignments/active').mkdir(parents=True)
        (self.work / 'docs/SESSION.md').write_text(
            '# Session\n## Active goal\n- none\n\n## Checklist\n- none\n')
        subprocess.run(['git', 'init', '-b', 'main'], cwd=self.work, check=True,
                       capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 't@example'], cwd=self.work, check=True)
        subprocess.run(['git', 'config', 'user.name', 'test'], cwd=self.work, check=True)

    def tearDown(self):
        self.temp.cleanup()

    def write_queue(self, rows, briefs):
        qlines, ilines = [QUEUE_HEADER], [INDEX_HEADER]
        for row in rows:
            qlines.append(row)
            # Reconstruct an INDEX row from the QUEUE row (drop depth).
            parts = [c.strip() for c in row.split('|')[1:-1]]
            aid, title, status, area, parallel = parts[:5]
            rel = f'active/{aid}-x.md'
            ilines.append(f'| {aid} | {title} | {status} | {area} | {parallel} | [{rel}]({rel}) |')
        (self.work / 'docs/assignments/QUEUE.md').write_text('\n'.join(qlines) + '\n')
        (self.work / 'docs/assignments/INDEX.md').write_text('\n'.join(ilines) + '\n')
        for aid, body in briefs.items():
            (self.work / 'docs/assignments/active' / f'{aid}-x.md').write_text(body)

    def run_status(self):
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'
        result = subprocess.run(['bash', 'scripts/assignment-status.sh'], cwd=self.work,
                                capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return result.stdout

    def test_original_bug_offers_three_disjoint_bare_no_rows(self):
        # A-028 in_progress area:docs; A-029/A-033/A-041 queued disjoint with bare NO.
        # Tooling must treat bare NO as YES and offer all three (the original complaint).
        self.write_queue([
            queue_row('A-028', 'in_progress', 'area:docs', 'NO'),
            queue_row('A-029', 'queued', 'area:actions', 'NO'),
            queue_row('A-033', 'queued', 'area:brain', 'NO'),
            queue_row('A-041', 'queued', 'area:overlay', 'NO'),
            queue_row('A-034', 'queued', 'area:overlay', 'YES'),
            queue_row('A-035', 'queued', 'area:overlay', 'YES'),
        ], {
            'A-028': brief('A-028', 'area:docs', 'NO', allowed='docs/'),
            'A-029': brief('A-029', 'area:actions', 'NO', allowed='actions/'),
            'A-033': brief('A-033', 'area:brain', 'NO', soft='brain/, tests/'),
            'A-041': brief('A-041', 'area:overlay', 'NO', allowed='overlay/, brain/training.py'),
            'A-034': brief('A-034', 'area:overlay', 'YES', blocked='A-033', allowed='overlay/'),
            'A-035': brief('A-035', 'area:overlay', 'YES', blocked='A-034', allowed='overlay/'),
        })
        out = self.run_status()
        self.assertIn('WARNING: A-029 is parallel-ok: NO with no reason — treat as YES pending desk review', out)
        self.assertIn('WARNING: A-033 is parallel-ok: NO with no reason — treat as YES pending desk review', out)
        self.assertIn('WARNING: A-041 is parallel-ok: NO with no reason — treat as YES pending desk review', out)
        self.assertIn('Candidate (area:actions differs from every in_progress area):', out)
        self.assertIn('| A-029 |', out.split('=== Claim hint')[-1])
        self.assertIn('| A-033 |', out.split('=== Claim hint')[-1])
        self.assertIn('| A-041 |', out.split('=== Claim hint')[-1])
        self.assertIn('Skipping A-034 (queued but Blocked-by A-033 not done yet)', out)
        self.assertIn('Skipping A-035 (queued but Blocked-by A-034 not done yet)', out)
        # Same-area as the holder is not a candidate even when treated as YES.
        claim = out.split('=== Claim hint')[-1]
        self.assertNotIn('Candidate (area:docs', claim)

    def test_reasoned_no_withheld_when_other_area_in_progress(self):
        # Current-shape check from the audit: A-029 in_progress area:actions → A-033 and
        # A-041 offered; A-030/A-042 withheld as reasoned NO.
        self.write_queue([
            queue_row('A-029', 'in_progress', 'area:actions', 'YES'),
            queue_row('A-033', 'queued', 'area:brain', 'YES'),
            queue_row('A-041', 'queued', 'area:overlay', 'YES'),
            queue_row('A-030', 'queued', 'area:docs', 'NO'),
            queue_row('A-042', 'queued', 'area:docs', 'NO'),
            queue_row('A-034', 'queued', 'area:overlay', 'YES'),
            queue_row('A-035', 'queued', 'area:overlay', 'YES'),
        ], {
            'A-029': brief('A-029', 'area:actions', 'YES', allowed='actions/core.py, brain/server.py'),
            'A-033': brief('A-033', 'area:brain', 'YES', soft='brain/, docs/LOGGING.md, tests/'),
            'A-041': brief('A-041', 'area:overlay', 'YES',
                           allowed='overlay/agents.js, brain/training.py, tests/'),
            'A-030': brief('A-030', 'area:docs', 'NO (control-plane: CODEOWNERS)', allowed='docs/'),
            'A-042': brief('A-042', 'area:docs',
                           'NO (control-plane: claim-rule / Training default tooling — ADR-048)',
                           allowed='scripts/assignment-status.sh, brain/training.py'),
            'A-034': brief('A-034', 'area:overlay', 'YES', blocked='A-033', allowed='overlay/'),
            'A-035': brief('A-035', 'area:overlay', 'YES', blocked='A-034', allowed='overlay/'),
        })
        out = self.run_status()
        self.assertIn('NO: A-030 — NO (control-plane: CODEOWNERS)', out)
        self.assertIn('NO: A-042 — NO (control-plane: claim-rule', out)
        self.assertNotIn('WARNING: A-030', out)
        self.assertNotIn('WARNING: A-042', out)
        claim = out.split('=== Claim hint')[-1]
        self.assertIn('| A-033 |', claim)
        self.assertIn('| A-041 |', claim)
        self.assertIn('Skipping A-030 (queued but parallel-ok: NO (control-plane: CODEOWNERS))', claim)
        self.assertIn('Skipping A-042 (queued but parallel-ok: NO (control-plane:', claim)
        self.assertNotIn('Candidate (area:docs', claim)
        # HEADS-UP must fire for A-033 vs A-029 (brain/ vs brain/server.py) and must not drop A-033.
        self.assertIn('HEADS-UP: A-033 soft path hints intersect in_progress A-029', out)
        self.assertIn('human notice only, not a gate', out)
        # Reasoned-NO rows are skipped, so they never get a HEADS-UP either.
        self.assertNotIn('HEADS-UP: A-042', out)

    def test_heads_up_does_not_remove_overlapping_candidate(self):
        self.write_queue([
            queue_row('A-041', 'in_progress', 'area:overlay', 'YES'),
            queue_row('A-033', 'queued', 'area:brain', 'YES'),
        ], {
            'A-041': brief('A-041', 'area:overlay', 'YES',
                           allowed='overlay/agents.js, brain/training.py'),
            'A-033': brief('A-033', 'area:brain', 'YES',
                           allowed='brain/training.py, tests/'),
        })
        out = self.run_status()
        claim = out.split('=== Claim hint')[-1]
        self.assertIn('| A-033 |', claim)
        self.assertIn('HEADS-UP: A-033 soft path hints intersect in_progress A-041 (brain/training.py)', out)
        self.assertNotIn('No assignment in queue is possible right now', claim)
