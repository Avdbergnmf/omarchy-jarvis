#!/usr/bin/env python3
"""Validate docs/ledger/INDEX.md against docs/ledger/records/*.md and print the next
allocatable IMP-NNN id. Read-only; exits non-zero on any inconsistency (A-026)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'docs/ledger'
ASSIGNMENTS_INDEX = ROOT / 'docs/assignments/INDEX.md'
ROW_RE = re.compile(r'^\|\s*(IMP-\d{3,})\s*\|\s*[^|]*\|\s*([a-z_]+)\s*\|\s*([^|]*)\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|$')
HEADER_RE = re.compile(r'^#\s*(IMP-\d{3,})\b')
STATUSES = {'hypothesis', 'in_progress', 'shipped', 'rejected', 'abandoned'}


def index_rows(ledger):
    path = ledger / 'INDEX.md'
    text = path.read_text() if path.exists() else ''
    return [m for line in text.splitlines() if (m := ROW_RE.match(line))]


def assignment_ids(assignments_index):
    text = assignments_index.read_text() if assignments_index.exists() else ''
    return set(re.findall(r'\|\s*(A-\d{3,})\s*\|', text))


def check(ledger=LEDGER, assignments_index=ASSIGNMENTS_INDEX):
    problems = []
    rows = index_rows(ledger)
    seen_ids = {}
    known_assignments = assignment_ids(assignments_index)
    record_files = {p.name: p for p in (ledger / 'records').glob('IMP-*.md')} if (ledger / 'records').exists() else {}
    for row in rows:
        imp_id, status, assignment_field, _title, rel_path = row.groups()
        if imp_id in seen_ids:
            problems.append(f'duplicate id {imp_id} in INDEX.md')
        seen_ids[imp_id] = True
        if status not in STATUSES:
            problems.append(f'{imp_id}: unknown status {status!r} in INDEX.md (expected one of {sorted(STATUSES)})')
        record_path = ledger / rel_path
        if not record_path.is_file():
            problems.append(f'{imp_id}: INDEX.md links {rel_path}, but that file does not exist')
            continue
        record_files.pop(record_path.name, None)
        record_text = record_path.read_text()
        header = HEADER_RE.match(record_text.splitlines()[0]) if record_text else None
        if not header or header.group(1) != imp_id:
            problems.append(f'{imp_id}: record file header does not start with "# {imp_id}"')
        for aid in re.findall(r'A-\d{3,}', assignment_field):
            if aid not in known_assignments:
                problems.append(f'{imp_id}: Assignment ids references {aid}, absent from docs/assignments/INDEX.md')
    for orphan in record_files:
        problems.append(f'{orphan}: record file exists under records/ but has no INDEX.md row')
    next_num = max((int(m.group(1).split('-')[1]) for m in rows), default=0) + 1
    return problems, f'IMP-{next_num:03d}'


def main():
    problems, next_id = check()
    for p in problems:
        print('PROBLEM: ' + p, file=sys.stderr)
    print(f'Next allocatable id: {next_id}')
    if problems:
        print(f'{len(problems)} problem(s) found — fix before allocating.', file=sys.stderr)
        return 1
    print('docs/ledger/INDEX.md is consistent with records/ and docs/assignments/INDEX.md.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
