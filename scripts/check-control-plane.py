#!/usr/bin/env python3
"""Validate A-030's versioned Control Plane inventory without executing repo code."""
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/control-plane/boundary-v1.json'
CODEOWNERS = ROOT / '.github/CODEOWNERS'
CASES = ROOT / 'docs/evals/cases.json'


def matches(path, pattern):
    return fnmatch.fnmatchcase(path, pattern)


def tracked_files(root):
    result = subprocess.run(
        ['git', 'ls-files'], cwd=root, check=True, text=True, capture_output=True
    )
    return set(result.stdout.splitlines())


def codeowners_entries(path):
    entries = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            entries[parts[0].lstrip('/')] = parts[1:]
    return entries


def check(root=ROOT, manifest_path=MANIFEST, codeowners_path=CODEOWNERS,
          cases_path=CASES, paths=None):
    problems = []
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError) as error:
        return [f'{manifest_path}: unreadable or invalid JSON ({error})']
    if manifest.get('version') != 1:
        problems.append('boundary manifest version must be 1')
    owner = manifest.get('owner')
    roots = manifest.get('boundary_roots', [])
    required = manifest.get('required_paths', [])
    classes = manifest.get('classifications', [])
    patterns = [item.get('pattern') for item in classes if isinstance(item, dict)]
    if not owner or not roots or not required or not patterns or any(not p for p in patterns):
        problems.append('manifest requires owner, boundary_roots, required_paths, and classification patterns')
        return problems

    paths = set(paths) if paths is not None else tracked_files(root)
    for path in sorted(paths):
        in_root = any(path.startswith(prefix) for prefix in roots)
        if in_root and not any(matches(path, pattern) for pattern in patterns):
            problems.append(f'{path}: boundary-root file is unclassified')
    for path in required:
        if path not in paths:
            problems.append(f'{path}: required authority-bearing path is missing or untracked')
        elif not any(matches(path, pattern) for pattern in patterns):
            problems.append(f'{path}: required authority-bearing path is unclassified')

    try:
        cases = json.loads(cases_path.read_text()).get('cases', [])
    except (OSError, ValueError) as error:
        problems.append(f'{cases_path}: cannot inspect protected oracles ({error})')
        cases = []
    protected_sources = {
        case.get('reference', '').split('::', 1)[0]
        for case in cases if isinstance(case, dict)
        and case.get('protection_class') == 'protected-regression'
    }
    protected_patterns = {
        item.get('pattern') for item in classes
        if isinstance(item, dict) and item.get('class') == 'protected-oracle-source'
    }
    for path in sorted(protected_sources):
        if not any(matches(path, pattern) for pattern in protected_patterns):
            problems.append(f'{path}: protected-regression oracle source lacks protected-oracle-source classification')

    try:
        owners = codeowners_entries(codeowners_path)
    except OSError as error:
        problems.append(f'{codeowners_path}: unreadable ({error})')
        owners = {}
    for pattern in patterns:
        if owner not in owners.get(pattern, []):
            problems.append(f'{pattern}: CODEOWNERS must map classification to {owner}')
    return problems


def main():
    problems = check()
    for problem in problems:
        print('PROBLEM: ' + problem, file=sys.stderr)
    if problems:
        print(f'{len(problems)} Control Plane boundary problem(s) found.', file=sys.stderr)
        return 1
    print('Control Plane boundary v1 is complete and CODEOWNERS-aligned.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
