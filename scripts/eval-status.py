#!/usr/bin/env python3
"""Validate docs/evals/cases.json against docs/evals/schema.json's constraints, and confirm
each case's `reference` actually resolves to an existing test class/method — parsed via `ast`,
never imported or executed (A-028). Read-only."""
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'docs/evals/cases.json'

REQUIRED = ['id', 'version', 'kind', 'title', 'oracle_type', 'execution_level', 'mutation_policy', 'owner', 'protection_class', 'reference', 'expected_result']
ENUMS = {
    'kind': {'capability', 'regression'},
    'oracle_type': {'unit-test-reference'},
    'execution_level': {'planner-only', 'unit'},
    'mutation_policy': {'side-effect-free'},
    'owner': {'control-plane'},
    'protection_class': {'protected-regression', 'candidate-capability'},
    'expected_result': {'pass'},
}
ID_RE = re.compile(r'^EVAL-\d{3,}$')
REF_RE = re.compile(r'^tests/(test_\w+\.py)::(\w+)(?:::(\w+))?$')


def reference_exists(root, ref):
    match = REF_RE.match(ref or '')
    if not match:
        return False
    filename, cls, method = match.groups()
    path = root / 'tests' / filename
    if not path.is_file():
        return False
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            if method is None:
                return True
            return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == method for n in node.body)
    return False


def check(cases_path=CASES, root=ROOT):
    problems = []
    try:
        data = json.loads(cases_path.read_text())
    except (OSError, ValueError) as error:
        return [f'{cases_path}: unreadable or invalid JSON ({error})']
    cases = data.get('cases')
    if not isinstance(cases, list):
        return [f'{cases_path}: "cases" must be a list']
    seen_ids = {}
    for i, case in enumerate(cases):
        label = case.get('id', f'#{i}') if isinstance(case, dict) else f'#{i}'
        if not isinstance(case, dict):
            problems.append(f'{label}: case must be an object')
            continue
        missing = [k for k in REQUIRED if k not in case]
        if missing:
            problems.append(f'{label}: missing required field(s) {missing}')
            continue
        extra = set(case) - set(REQUIRED) - {'notes'}
        if extra:
            problems.append(f'{label}: unknown field(s) {sorted(extra)}')
        cid = case['id']
        if not ID_RE.match(cid):
            problems.append(f'{label}: id must match EVAL-NNN')
        if cid in seen_ids:
            problems.append(f'duplicate case id {cid}')
        seen_ids[cid] = True
        if not isinstance(case.get('version'), int) or case['version'] < 1:
            problems.append(f'{cid}: version must be an integer >= 1')
        for field, allowed in ENUMS.items():
            if case.get(field) not in allowed:
                problems.append(f'{cid}: {field}={case.get(field)!r} not in {sorted(allowed)}')
        if not reference_exists(root, case.get('reference', '')):
            problems.append(f'{cid}: reference {case.get("reference")!r} does not resolve to an existing test class/method')
    return problems


def main():
    problems = check()
    for p in problems:
        print('PROBLEM: ' + p, file=sys.stderr)
    if problems:
        print(f'{len(problems)} problem(s) found in docs/evals/cases.json.', file=sys.stderr)
        return 1
    print('docs/evals/cases.json is schema-valid and every reference resolves to an existing test.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
