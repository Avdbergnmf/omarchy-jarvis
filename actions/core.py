"""Reviewed desktop actions. No model-generated shell commands are evaluated."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'logs'
APPS = {'Todoist': 'https://app.todoist.com/app', 'Google Calendar': 'https://calendar.google.com/', 'Outlook': 'https://outlook.live.com/mail/', 'WhatsApp': 'https://web.whatsapp.com/'}

def is_overlay(client):
    return client.get('class') in ('jarvis-overlay', 'chrome-127.0.0.1__jarvis-overlay-Default')

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
    if skill not in ('open-planning', 'scratch-and-mail'):
        raise ValueError('Unknown/unapproved skill id')
    argv = [str(ROOT / 'skills/examples' / skill / 'run.sh')]
    if dry:
        argv.append('--dry-run')
    result = subprocess.run(argv, capture_output=True, text=True, timeout=150)
    if result.returncode:
        raise RuntimeError(result.stdout.strip() + '\n' + result.stderr.strip())
    return {'skill': skill, 'results': [json.loads(line) for line in result.stdout.splitlines() if line.strip()]}

def notify(run_id, message, dry=False):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}', run_id):
        raise ValueError('Invalid run id')
    if not dry:
        (LOGS / 'runs').mkdir(parents=True, exist_ok=True, mode=0o700)
        (LOGS / 'runs' / (run_id + '.log')).touch(mode=0o600)
    return command(['omarchy-notification-send', '--app-name', 'jarvis', '-u', 'normal', '-t', '12000', 'Jarvis', message[:300], '--exec', str(ROOT / 'console/jarvis-console'), run_id], dry)

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
        else: raise ValueError('Unknown action')
        print(json.dumps({'ok': True, **result}))
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, StopIteration) as e:
        print(json.dumps({'ok': False, 'error': str(e)})); sys.exit(1)

if __name__ == '__main__': main()
