#!/usr/bin/env python3
"""Read-only issue/pass/journal overview; accepts saved GitHub JSON for offline checks."""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AREAS = ('overlay', 'brain', 'actions', 'skills', 'docs')


def paths(body, name):
    match = re.search(r'(?im)^\s*(?:[-*]\s*)?' + name + r' paths:\s*([^\n]+)', body)
    if not match:
        return []
    return [p.strip().strip('`').removeprefix('./') for p in match[1].split(',') if p.strip()]


def overlap(a, b):
    # Conservative prefix comparison, including glob roots. Review warnings manually.
    a, b = re.split(r'[?*\[]', a)[0].rstrip('/'), re.split(r'[?*\[]', b)[0].rstrip('/')
    return not a or not b or a == b or a.startswith(b + '/') or b.startswith(a + '/')


def overview(issues):
    rows, warnings = [], []
    for area in (*AREAS, 'unassigned'):
        selected = [i for i in issues if ('area:' + area in [l['name'] for l in i['labels']]) or
                    (area == 'unassigned' and not any(l['name'].startswith('area:') for l in i['labels']))]
        rows.append(area + ': ' + (', '.join(f"#{i['number']} {i['title']}" for i in selected) or '(none)'))
    for i, issue in enumerate(issues):
        labels = {l['name'] for l in issue['labels']}
        allowed, forbidden = paths(issue.get('body', ''), 'Allowed'), paths(issue.get('body', ''), 'Forbidden')
        if 'parallel-ok' in labels:
            if not allowed or not forbidden:
                warnings.append(f"#{issue['number']}: parallel-ok requires Allowed paths: and Forbidden paths: comma-separated lines")
            if 'single-writer' in labels or 'area:brain' in labels or any(overlap(p, 'brain/server.py') for p in allowed):
                warnings.append(f"#{issue['number']}: control-plane/single-writer scope cannot be parallel-ok")
            if any(overlap(a, f) for a in allowed for f in forbidden):
                warnings.append(f"#{issue['number']}: allowed and forbidden paths overlap; narrow the scope")
        for other in issues[i+1:]:
            other_labels = {l['name'] for l in other['labels']}
            shared = labels & other_labels & {'area:' + a for a in AREAS}
            collision = any(overlap(a, b) for a in allowed for b in paths(other.get('body', ''), 'Allowed'))
            if shared or collision:
                warnings.append(f"#{issue['number']} / #{other['number']}: potential collision ({', '.join(sorted(shared)) or 'allowed paths'})")
    return rows + ['WARNING: ' + w for w in warnings]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--issues-json', type=Path)
    args = parser.parse_args()
    try:
        raw = args.issues_json.read_text() if args.issues_json else subprocess.run(
            ['gh', 'issue', 'list', '--repo', 'Avdbergnmf/omarchy-jarvis', '--state', 'open', '--limit', '1000',
             '--json', 'number,title,labels,body'], capture_output=True, text=True, check=True, timeout=15).stdout
        issues = json.loads(raw)
        print('\n'.join(overview(issues)))
        if len(issues) == 1000:
            print('WARNING: issue listing may be truncated at 1000.')
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print('WARNING: GitHub unavailable; not an empty issue list (' + type(error).__name__ + ').')
    for location in ('docs/passes', 'docs/backlog/handoffs'):
        print(location + ' active: ' + (', '.join(p.name for p in sorted((ROOT / location / 'active').glob('*')) if p.is_file()) or '(none)'))
    current = ROOT / 'logs/journal/CURRENT.jsonl'
    if current.exists():
        # Bound reads even when the journal is large.
        with current.open('rb') as src:
            src.seek(max(0, current.stat().st_size - 65536))
            lines = src.read().splitlines()
        ids = []
        for line in lines:
            try:
                record = json.loads(line)
                rid = record['run_id']
                if rid not in ids: ids.append(rid)
            except (ValueError, KeyError):
                continue
        print('Recent run_ids: ' + ', '.join(ids[-5:]))
    else:
        print('Recent run_ids: no current journal yet')
    print('Doctor: ./scripts/doctor.sh (host) | ./scripts/doctor.sh --syntax (CI)')


if __name__ == '__main__':
    main()
