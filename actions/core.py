"""Reviewed desktop actions. No model-generated shell commands are evaluated."""
import argparse
import datetime
import difflib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'logs'
APPS = {'Todoist': 'https://app.todoist.com/app', 'Google Calendar': 'https://calendar.google.com/', 'Outlook': 'https://outlook.live.com/mail/', 'WhatsApp': 'https://web.whatsapp.com/', 'YouTube': 'https://www.youtube.com/'}
REPO = 'Avdbergnmf/omarchy-jarvis'
BACKLOG_KIND = {'bug': {'labels': ['bug', 'jarvis-reported'], 'dir': 'bugs'}, 'feature': {'labels': ['enhancement', 'backlog'], 'dir': 'features'}}
HANDOFF_AGENTS = ('claude-code', 'cursor', 'human')
# A-011: installed desktop apps by .desktop location, standard + common Flatpak export dirs.
DESKTOP_DIRS = (Path.home() / '.local/share/applications', Path('/usr/share/applications'),
                Path('/var/lib/flatpak/exports/share/applications'), Path.home() / '.local/share/flatpak/exports/share/applications')
FIELD_CODE_RE = re.compile(r'%[fFuUdDnNickvm]')

def redact(value):
    text = str(value)
    text = re.sub(r'(?i)(bearer\s+|(?:api[_-]?key|password|token|secret)\s*[=:]\s*)[^\s,}"\']+', r'\1[REDACTED]', text)
    return re.sub(r'\b(sk-[A-Za-z0-9_-]{10,}|gh[ops]_[A-Za-z0-9]{20,})\b', '[REDACTED]', text)

def slugify(text, maxlen=50):
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return (slug[:maxlen].rstrip('-')) or 'item'

def fill_template(name, values):
    text = (ROOT / 'docs/templates' / name).read_text()
    for key, val in values.items():
        text = text.replace('{{' + key + '}}', str(val) if val not in (None, '') else '—')
    return text

def is_overlay(client):
    # Chromium has historically derived a different class on repeat launches
    # (ADR-013) rather than honoring --class; matching the literal known-good
    # class OR any class containing it survives a variant we haven't seen yet,
    # without risking a false match against an unrelated window (nothing else
    # would coincidentally embed this literal string).
    cls = client.get('class') or ''
    return cls == 'jarvis-overlay' or 'jarvis-overlay' in cls

def command(argv, dry=False):
    if dry:
        return {'argv': argv, 'dry_run': True}
    result = subprocess.run(argv, capture_output=True, text=True, timeout=40)
    if result.returncode:
        raise RuntimeError(f'{argv[0]} failed: {result.stderr.strip() or result.stdout.strip()}')
    return {'argv': argv, 'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}

def hypr(what):
    return json.loads(command(['hyprctl', '-j', what])['stdout'])

def dispatch(name, arg, dry=False):
    arg = str(arg)
    if name == 'workspace': expression = 'hl.dsp.focus({ workspace = ' + json.dumps(arg) + ' })'
    elif name == 'focuswindow': expression = 'hl.dsp.focus({ window = ' + json.dumps(arg) + ' })'
    elif name == 'togglespecialworkspace': expression = 'hl.dsp.workspace.toggle_special(' + json.dumps(arg) + ')'
    elif name == 'movetoworkspacesilent':
        workspace, _, address = arg.partition(',')
        expression = 'hl.dsp.window.move({ workspace = ' + json.dumps(workspace) + ', follow = false' + (', window = ' + json.dumps(address) if address else '') + ' })'
    elif name == 'closewindow': expression = 'hl.dsp.window.close({ window = ' + json.dumps(arg) + ' })'
    else: raise ValueError('Unsupported dispatcher')
    result = command(['hyprctl', 'dispatch', expression], dry)
    if not dry and result['stdout'] != 'ok':
        raise RuntimeError(f'Hyprland rejected dispatch: {result["stdout"]}')
    return result

def chord(value):
    return ' '.join(sorted(value.upper().replace('+', ' ').split()))

def catalog(refresh=False, query=''):
    LOGS.mkdir(exist_ok=True, mode=0o700)
    cache = LOGS / 'bindings.cache.txt'
    if refresh or not cache.exists():
        raw = command(['omarchy', 'menu', 'keybindings', '--print'])['stdout']
        if len(raw.splitlines()) < 10:
            raise RuntimeError('Live catalog is incomplete; check Hyprland/session access')
        tmp = cache.with_suffix('.tmp')
        tmp.write_text(raw + '\n')
        tmp.replace(cache)
    rows = []
    for line in cache.read_text().splitlines():
        if '→' in line:
            key, desc = (x.strip() for x in line.split('→', 1))
            if not query or query.casefold() in line.casefold() or chord(query) == chord(key):
                rows.append({'chord': key, 'description': desc})
    return {'bindings': rows}

def app_url(name):
    # Only extract literal URLs for these two reviewed personal overrides.
    if name in ('Outlook', 'WhatsApp'):
        source = (Path.home() / '.config/hypr/bindings.lua').read_text()
        matches = re.findall(r'o\.bind\([^\n]*"' + name + r'"[^\n]*webapp\s*=\s*"([^"\n]+)"', source)
        if matches:
            return matches[-1]
    return APPS[name]

def open_app(name, url=None, workspace=None, dry=False):
    if workspace is not None and not 1 <= workspace < 10000:
        raise ValueError('Workspace must be 1..9999')
    if name not in APPS:
        raise ValueError('Supported webapps: ' + ', '.join(APPS))
    url = url or app_url(name)
    # The Omarchy focus wrapper evals a command string. Keep URLs literal and
    # use its argv-safe launcher directly for new windows.
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or re.search(r'[\s\x00-\x1f`$;|<>\\"\']', url):
        raise ValueError('Expected a literal HTTPS webapp URL')
    app_class = 'jarvis-' + name.lower().replace(' ', '-')
    argv = ['omarchy-launch-webapp', url, '--class=' + app_class]
    if dry:
        return {**command(argv, True), 'workspace': workspace, 'name': name}
    def matches_app(c):
        return c['class'] == app_class or parsed.hostname.casefold() in c['class'].casefold()
    existing = hypr('clients')
    matches = [c for c in existing if matches_app(c)]
    if matches:
        client = matches[0]
    else:
        before = {c['address'] for c in existing}
        LOGS.mkdir(exist_ok=True, mode=0o700)
        with (LOGS / 'webapps.log').open('a') as out:
            subprocess.Popen(argv, stdout=out, stderr=out, start_new_session=True)
        deadline = time.monotonic() + 30
        client = None
        while time.monotonic() < deadline:
            candidates = [c for c in hypr('clients') if c['address'] not in before and matches_app(c)]
            if candidates:
                client = candidates[0]
                break
            time.sleep(.2)
        if client is None:
            raise RuntimeError(f'{name} launched but its window was not found within 30s')
    address = client['address']
    if workspace is not None:
        dispatch('movetoworkspacesilent', f'{workspace},address:{address}')
    dispatch('focuswindow', f'address:{address}')
    actual = next(c for c in hypr('clients') if c['address'] == address)
    if workspace is not None and actual['workspace']['id'] != workspace:
        raise RuntimeError(f'{name} did not arrive on workspace {workspace}')
    return {'name': name, 'address': address, 'workspace': actual['workspace']['id'], 'class': actual['class']}

def run_binding(binding, dry=False):
    rows = catalog(refresh=True)['bindings']
    matches = [r for r in rows if chord(r['chord']) == chord(binding) or r['description'].casefold() == binding.casefold()]
    if not matches:
        raise ValueError('No exact binding description/chord found; query catalog_bindings first')
    descs = {r['description'] for r in matches}
    if len(descs) != 1:
        raise ValueError('Ambiguous binding; specify its chord')
    desc = matches[0]['description']
    if desc == 'Toggle scratchpad':
        return dispatch('togglespecialworkspace', 'scratchpad', dry)
    if desc == 'Move window to scratchpad':
        return scratch_move(dry)
    if desc in ('Outlook', 'WhatsApp'):
        return open_app(desc, dry=dry)
    match = re.fullmatch(r'Switch to workspace (\d+)', desc)
    if match:
        return dispatch('workspace', int(match[1]), dry)
    raise ValueError(f'Binding {desc!r} is catalogued but has no reviewed execution mapping')

def scratch_move(dry=False):
    if not dry:
        current = hypr('activewindow')
        if not current or (is_overlay(current) or current.get('title','').startswith('Jarvis ·')):
            raise ValueError('Focus a regular application window before moving to scratchpad')
    result = dispatch('movetoworkspacesilent', 'special:scratchpad', dry)
    if not dry:
        moved = next(c for c in hypr('clients') if c['address'] == current['address'])
        if moved['workspace']['name'] != 'special:scratchpad':
            raise RuntimeError('Window did not move to scratchpad')
        result['address'] = current['address']
    return result

def workspace_new(dry=False):
    used = {w['id'] for w in hypr('workspaces')}
    number = next(n for n in range(1, 10000) if n not in used)
    return {**dispatch('workspace', number, dry), 'workspace': number}

def run_skill(skill, dry=False):
    if skill not in ('open-planning', 'scratch-and-mail', 'report-last-failure', 'add-feature-request'):
        raise ValueError('Unknown/unapproved skill id')
    argv = [str(ROOT / 'skills/examples' / skill / 'run.sh')]
    if dry:
        argv.append('--dry-run')
    result = subprocess.run(argv, capture_output=True, text=True, timeout=150)
    if result.returncode:
        raise RuntimeError(result.stdout.strip() + '\n' + result.stderr.strip())
    return {'skill': skill, 'results': [json.loads(line) for line in result.stdout.splitlines() if line.strip()]}

def desktop_entries():
    """Installed .desktop launchers (Name/Exec/StartupWMClass), most-local dir wins on
    a duplicate stem. Skips NoDisplay entries (helpers not meant to be launched by name)
    and non-Application types (links, dirs)."""
    entries, seen = [], set()
    for d in DESKTOP_DIRS:
        if not d.is_dir():
            continue
        for f in sorted(d.glob('*.desktop')):
            if f.stem in seen:
                continue
            try:
                text = f.read_text(errors='ignore')
            except OSError:
                continue
            fields, in_entry = {}, False
            for line in text.splitlines():
                stripped = line.strip()
                if stripped == '[Desktop Entry]':
                    in_entry = True; continue
                if stripped.startswith('[') and stripped != '[Desktop Entry]':
                    in_entry = False; continue
                if not in_entry or '=' not in stripped or stripped.startswith('#'):
                    continue
                key, _, val = stripped.partition('=')
                fields.setdefault(key.strip(), val.strip())
            name, exec_line = fields.get('Name'), fields.get('Exec')
            if not name or not exec_line: continue
            if fields.get('NoDisplay', '').lower() == 'true': continue
            if fields.get('Type', 'Application') != 'Application': continue
            seen.add(f.stem)
            entries.append({'name': name, 'exec': exec_line, 'stem': f.stem, 'wmclass': fields.get('StartupWMClass') or f.stem})
    return entries

def resolve_app(name, entries=None):
    """Exact match wins outright; otherwise an unambiguous prefix/substring match;
    otherwise the single closest fuzzy match. Ties raise rather than guess."""
    query = (name or '').strip().lower()
    if not query:
        raise ValueError('App name required')
    entries = desktop_entries() if entries is None else entries
    exact = [e for e in entries if e['name'].lower() == query]
    if len(exact) == 1: return exact[0]
    starts = [e for e in entries if e['name'].lower().startswith(query)]
    if len(starts) == 1: return starts[0]
    contains = [e for e in entries if query in e['name'].lower()]
    if len(contains) == 1: return contains[0]
    ambiguous = exact or starts or contains
    if len(ambiguous) > 1:
        raise ValueError('Multiple installed apps match ' + repr(name) + ': ' + ', '.join(sorted({e['name'] for e in ambiguous})) + ' — be more specific')
    close = difflib.get_close_matches(query, [e['name'].lower() for e in entries], n=1, cutoff=0.6)
    if close:
        return next(e for e in entries if e['name'].lower() == close[0])
    raise ValueError('No installed app matches ' + repr(name))

def launch_command_for(entry):
    # .desktop field codes (%u/%f/...) are for file-manager-style invocation; a bare
    # by-name launch has no file/URL argument to fill them with — drop the whole token
    # (not just the code) so "--uri=%u" disappears instead of leaving a dangling "--uri=".
    try:
        raw_parts = shlex.split(entry['exec'])
    except ValueError as e:
        raise ValueError('Could not parse Exec line for ' + entry['name'] + ': ' + str(e))
    parts = [cleaned for cleaned in (FIELD_CODE_RE.sub('', p) for p in raw_parts) if cleaned and not cleaned.endswith('=')]
    if not parts:
        raise ValueError('Empty Exec line for ' + entry['name'])
    return ' '.join(shlex.quote(p) for p in parts)

def open_by_name(name, dry=False):
    entry = resolve_app(name)
    pattern = entry['wmclass']
    # omarchy-launch-or-focus focuses a matching window if one exists, else launches
    # (via `eval exec setsid …`, which *replaces* its own process — never wait on it
    # synchronously the way command() does, or a real launch blocks until the app exits).
    argv = ['omarchy-launch-or-focus', pattern, 'uwsm-app -- ' + launch_command_for(entry)]
    if dry:
        return {'argv': argv, 'name': entry['name'], 'dry_run': True}
    LOGS.mkdir(exist_ok=True, mode=0o700)
    with (LOGS / 'webapps.log').open('a') as out:
        subprocess.Popen(argv, stdout=out, stderr=out, start_new_session=True)
    deadline = time.monotonic() + 20
    client = None
    while time.monotonic() < deadline:
        candidates = [c for c in hypr('clients') if pattern.casefold() in (c.get('class') or '').casefold()
                      or pattern.casefold() in (c.get('title') or '').casefold() or entry['name'].casefold() in (c.get('title') or '').casefold()]
        if candidates:
            client = candidates[0]; break
        time.sleep(.3)
    if client is None:
        raise RuntimeError(entry['name'] + ' launched but no matching window appeared within 20s')
    return {'name': entry['name'], 'address': client['address'], 'workspace': client['workspace']['id'], 'class': client['class']}

def notify(run_id, message, dry=False):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}', run_id):
        raise ValueError('Invalid run id')
    if not dry:
        (LOGS / 'runs').mkdir(parents=True, exist_ok=True, mode=0o700)
        (LOGS / 'runs' / (run_id + '.log')).touch(mode=0o600)
    return command(['omarchy-notification-send', '--app-name', 'jarvis', '-u', 'normal', '-t', '12000', 'Jarvis', message[:300], '--exec', str(ROOT / 'console/jarvis-console'), run_id], dry)

def index_rows():
    lines = (ROOT / 'docs/backlog/INDEX.md').read_text().splitlines()
    return [l for l in lines if l.startswith('|') and not l.startswith('| id') and not re.fullmatch(r'\|[-\s|]+\|', l)]

def index_ids():
    ids = set()
    for row in index_rows():
        cells = [c.strip() for c in row.strip('|').split('|')]
        if cells and cells[0]:
            ids.add(cells[0])
    return ids

def index_append(id_, kind, title, difficulty, status, issue_ref):
    row = '| {} | {} | {} | {} | {} | {} |\n'.format(id_, kind, redact(title).replace('|', '\\|')[:80], difficulty, status, issue_ref)
    with (ROOT / 'docs/backlog/INDEX.md').open('a') as f:
        f.write(row)

def backlog_slug(title):
    base = slugify(title)
    existing = index_ids()
    slug, n = base, 2
    while slug in existing:
        slug = f'{base}-{n}'; n += 1
    return slug

LABEL_COLORS = {'bug': 'd73a4a', 'jarvis-reported': '5319e7', 'enhancement': 'a2eeef', 'backlog': '0e8a16'}

def ensure_labels(labels):
    # gh issue create fails outright if a --label doesn't exist yet in the repo;
    # --force makes this idempotent (create-or-update) so it's safe every time.
    for label in labels:
        subprocess.run(['gh', 'label', 'create', label, '--repo', REPO, '--color', LABEL_COLORS.get(label, 'ededed'), '--force'], capture_output=True, text=True, timeout=15)

def report_record(kind, title, body, difficulty='M', dry=False):
    if kind not in BACKLOG_KIND:
        raise ValueError('Unknown backlog kind')
    title = redact(title).strip()[:200]
    if not title:
        raise ValueError('Title required')
    if difficulty not in ('S', 'M', 'L'):
        raise ValueError('Difficulty must be S, M or L')
    body = redact(body)
    meta = BACKLOG_KIND[kind]
    slug = backlog_slug(title)
    argv = ['gh', 'issue', 'create', '--repo', REPO, '--title', title, '--body', body]
    for label in meta['labels']:
        argv += ['--label', label]
    if dry:
        return {'kind': kind, 'slug': slug, 'title': title, 'labels': meta['labels'], 'argv': argv, 'dry_run': True}
    ensure_labels(meta['labels'])
    result = command(argv)
    url = next((line for line in reversed(result['stdout'].splitlines()) if line.startswith('http')), '')
    if not url:
        raise RuntimeError('gh issue create did not return a URL: ' + result['stdout'])
    number = url.rstrip('/').rsplit('/', 1)[-1]
    mirror = ROOT / 'docs/backlog' / meta['dir'] / (slug + '.md')
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_text('# ' + title + '\n\nGitHub issue: ' + url + '\n\n' + body + '\n')
    index_append(slug, kind, title, difficulty, 'open', '#' + number)
    return {'kind': kind, 'slug': slug, 'title': title, 'url': url, 'number': int(number), 'mirror': str(mirror.relative_to(ROOT))}

def extract_acceptance(body):
    match = re.search(r'##\s*Acceptance criteria.*?\n(.*?)(\n##|\Z)', body, re.S)
    text = match.group(1).strip() if match else ''
    return text or '(see issue body above)'

def list_backlog(dry=False):
    argv = ['gh', 'issue', 'list', '--repo', REPO, '--state', 'open', '--json', 'number,title,labels,url', '--limit', '100']
    if dry:
        return {'argv': argv, 'dry_run': True}
    result = command(argv)
    issues = json.loads(result['stdout'] or '[]')
    relevant = [i for i in issues if any(l['name'] in ('bug', 'jarvis-reported', 'enhancement', 'backlog') for l in i.get('labels', []))]
    index = []
    for row in index_rows():
        cells = [c.strip() for c in row.strip('|').split('|')]
        if len(cells) == 6:
            index.append(dict(zip(['id', 'type', 'title', 'difficulty', 'status', 'gh_issue'], cells)))
    return {'issues': relevant, 'index': index}

def prepare_handoff(issue, agent, dry=False):
    if agent not in HANDOFF_AGENTS:
        raise ValueError('Unknown agent; use claude-code, cursor or human')
    if not 1 <= issue <= 999999:
        raise ValueError('Invalid issue number')
    argv = ['gh', 'issue', 'view', str(issue), '--repo', REPO, '--json', 'title,body,url,labels']
    if dry:
        return {'argv': argv, 'issue': issue, 'agent': agent, 'dry_run': True}
    result = command(argv)
    data = json.loads(result['stdout'])
    slug = slugify(data['title'])
    branch = ('issue-' + str(issue) + '-' + slug)[:60]
    values = {
        'ISSUE': issue, 'AGENT': agent, 'REPO': REPO, 'BRANCH': branch,
        'TITLE': data['title'], 'ISSUE_URL': data['url'],
        'LABELS': ', '.join(l['name'] for l in data.get('labels', [])) or 'none',
        'ISSUE_BODY': redact(data.get('body') or '(no body)'),
        'ACCEPTANCE': redact(extract_acceptance(data.get('body') or '')),
        'DATE': datetime.date.today().isoformat(),
    }
    text = fill_template('HANDOFF_AGENT.md', values)
    path = ROOT / 'docs/backlog/handoffs/active' / ('issue-' + str(issue) + '-' + agent + '.md')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        archive = path.parent.parent / 'archive'
        archive.mkdir(parents=True, exist_ok=True)
        old = archive / (path.stem + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.md')
        path.rename(old)
    path.write_text(text)
    index = path.parent.parent / 'INDEX.md'
    entries = index.read_text() if index.exists() else '# Handoff index\n\nStatuses: active | done | superseded.\n'
    # Replace only this handoff's active row; preserve the superseded evidence.
    lines = [line for line in entries.splitlines() if '](' + 'active/' + path.name + ')' not in line]
    if 'old' in locals():
        lines.append(f'- [{old.name}](archive/{old.name}) — superseded')
    lines.append(f'- [{path.name}](active/{path.name}) — active')
    index.write_text('\n'.join(lines) + '\n')
    return {'issue': issue, 'agent': agent, 'path': str(path.relative_to(ROOT)), 'branch': branch}

def main():
    name = Path(sys.argv[0]).name
    p = argparse.ArgumentParser(description='Jarvis ' + name + ': JSON stdout, nonzero on failure')
    p.add_argument('--dry-run', action='store_true', help='Describe actions without changing desktop state')
    if name == 'catalog_bindings':
        p.add_argument('--refresh', action='store_true'); p.add_argument('--query', default='')
    elif name == 'run_binding': p.add_argument('binding')
    elif name == 'workspace_switch': p.add_argument('workspace', type=int)
    elif name == 'open_webapp':
        p.add_argument('--name', required=True, choices=list(APPS)); p.add_argument('--url'); p.add_argument('--workspace', type=int)
    elif name == 'notify_thought':
        p.add_argument('--run-id', required=True); p.add_argument('--message', required=True)
    elif name == 'run_skill': p.add_argument('skill')
    elif name in ('report_bug', 'report_feature'):
        p.add_argument('--title', required=True); p.add_argument('--body', required=True)
        p.add_argument('--difficulty', default='M', choices=['S', 'M', 'L'])
    elif name == 'prepare_handoff':
        p.add_argument('--issue', required=True, type=int); p.add_argument('--agent', required=True, choices=list(HANDOFF_AGENTS))
    elif name == 'open_app_by_name':
        p.add_argument('--name', required=True)
    a = p.parse_args()
    try:
        if name == 'catalog_bindings': result = catalog(a.refresh, a.query)
        elif name == 'run_binding': result = run_binding(a.binding, a.dry_run)
        elif name == 'workspace_new': result = workspace_new(a.dry_run)
        elif name == 'workspace_switch':
            if not 1 <= a.workspace < 10000: raise ValueError('Workspace must be 1..9999')
            result = dispatch('workspace', a.workspace, a.dry_run)
        elif name == 'scratch_toggle': result = dispatch('togglespecialworkspace', 'scratchpad', a.dry_run)
        elif name == 'scratch_move_here': result = scratch_move(a.dry_run)
        elif name == 'open_webapp': result = open_app(a.name, a.url, a.workspace, a.dry_run)
        elif name == 'notify_thought': result = notify(a.run_id, a.message, a.dry_run)
        elif name == 'run_skill': result = run_skill(a.skill, a.dry_run)
        elif name == 'report_bug': result = report_record('bug', a.title, a.body, a.difficulty, a.dry_run)
        elif name == 'report_feature': result = report_record('feature', a.title, a.body, a.difficulty, a.dry_run)
        elif name == 'list_backlog': result = list_backlog(a.dry_run)
        elif name == 'prepare_handoff': result = prepare_handoff(a.issue, a.agent, a.dry_run)
        elif name == 'open_app_by_name': result = open_by_name(a.name, a.dry_run)
        else: raise ValueError('Unknown action')
        print(json.dumps({'ok': True, **result}))
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, StopIteration) as e:
        print(json.dumps({'ok': False, 'error': str(e)})); sys.exit(1)

if __name__ == '__main__': main()
