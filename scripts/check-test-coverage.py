#!/usr/bin/env python3
"""A-028: fail loudly if a tests/ file exists that CI would silently never run — the
"quiet suite omission" contract the candidate-eval foundation requires. Read-only.

Two checks:
1. Every tests/*.test.cjs file is reachable from a CI-invoked `node tests/X.test.cjs`
   step in .github/workflows/ci.yml, either directly or transitively via require('./Y.test.cjs').
2. Every tests/*.py file matches unittest discover's default test_*.py pattern, so
   `python3 -m unittest discover -s tests` (CI's own invocation) actually finds it.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / 'tests'
CI_WORKFLOW = ROOT / '.github/workflows/ci.yml'
REQUIRE_RE = re.compile(r"require\(['\"]\./([\w.-]+\.test\.cjs)['\"]\)")
CI_ENTRYPOINT_RE = re.compile(r'run:\s*node\s+tests/([\w.-]+\.test\.cjs)\b')


def reachable_cjs(tests, entrypoints):
    seen = set(entrypoints)
    queue = list(entrypoints)
    while queue:
        name = queue.pop()
        path = tests / name
        if not path.is_file():
            continue
        for match in REQUIRE_RE.finditer(path.read_text()):
            required = match.group(1)
            if required not in seen:
                seen.add(required)
                queue.append(required)
    return seen


def check(tests=TESTS, ci_workflow=CI_WORKFLOW):
    problems = []
    all_cjs = {p.name for p in tests.glob('*.test.cjs')}
    ci_text = ci_workflow.read_text() if ci_workflow.exists() else ''
    entrypoints = set(CI_ENTRYPOINT_RE.findall(ci_text))
    if not entrypoints:
        problems.append(f'{ci_workflow}: no "node tests/*.test.cjs" step found — nothing runs the JS suites at all')
    reached = reachable_cjs(tests, entrypoints)
    for missing in sorted(all_cjs - reached):
        problems.append(f'tests/{missing}: not reachable from any CI entrypoint ({sorted(entrypoints)}) directly or via require() — CI would silently never run it')
    all_py = {p.name for p in tests.glob('*.py') if p.name != '__init__.py'}
    for name in sorted(all_py):
        if not re.fullmatch(r'test_.*\.py', name):
            problems.append(f'tests/{name}: does not match unittest discover\'s "test_*.py" pattern — CI\'s `unittest discover` would silently skip it')
    return problems


def main():
    problems = check()
    for p in problems:
        print('PROBLEM: ' + p, file=sys.stderr)
    if problems:
        print(f'{len(problems)} problem(s) found — a test file would be silently skipped by CI.', file=sys.stderr)
        return 1
    print('Every tests/*.test.cjs and tests/*.py file is reachable by CI.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
