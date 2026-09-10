"""On-demand Training dashboard and explicitly confirmed local work preparation."""
import datetime
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import threading
import time

from journal import clean
import validation

LOCK = threading.RLock()
PREVIEWS = {}
KINDS = ('claude-code', 'cursor', 'human')
AREAS = ('overlay', 'brain', 'actions', 'skills', 'docs')
QUEUE = 'docs/assignments/QUEUE.md'
INDEX = 'docs/assignments/INDEX.md'
SLOTS = 'logs/training/agents.json'


def read(root, path):
    target = root / path
    if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != root.parent):
        raise ValueError('Symlinked training paths are not supported')
    return target.read_text() if target.exists() else ''


def short(value, name, limit=600, empty=False):
    if not isinstance(value, str) or len(value) > limit or (not empty and not value.strip()):
        raise ValueError(f'{name} must be {1 if not empty else 0}–{limit} characters')
    return clean(value.strip())


def assignments(root):
    result = []
    for line in read(root, QUEUE).splitlines():
        cols = [c.strip() for c in line.split('|')]
        if len(cols) >= 7 and re.fullmatch(r'A-\d{3,}', cols[1]):
            result.append(dict(id=cols[1], title=cols[2], status=cols[3], area=cols[4], parallel=cols[5]))
    return result


def slots(root):
    data = json.loads(read(root, SLOTS) or '{"version":1,"agents":[]}')
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('agents'), list) or len(data['agents']) > 32:
        raise ValueError('Invalid agent registry')
    seen = set()
    for slot in data['agents']:
        if not isinstance(slot, dict): raise ValueError('Invalid agent slot')
        sid = slot.get('id')
        if not isinstance(sid, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', sid) or sid in seen:
            raise ValueError('Invalid or duplicate agent slot id')
        seen.add(sid)
        if slot.get('kind') not in KINDS or slot.get('status') not in ('idle','busy'):
            raise ValueError('Invalid agent kind or status')
        short(slot.get('label'), 'Agent label', 60)
        queued = slot.get('queued_assignment_ids')
        if not isinstance(queued, list) or len(queued)>200 or any(not isinstance(a,str) or not re.fullmatch(r'A-\d{3,}',a) for a in queued):
            raise ValueError('Invalid agent assignment queue')
        current = slot.get('current_assignment')
        if current is not None and (not isinstance(current,str) or not re.fullmatch(r'A-\d{3,}',current)):
            raise ValueError('Invalid current assignment')
    return data


def busy(slot, queue):
    return slot.get('status') == 'busy' or any(a['id'] == slot.get('current_assignment') and a['status'] == 'in_progress' for a in queue)


def tail_json(root, path, limit=2_000_000):
    target = root / path
    if not target.exists(): return [], False
    with target.open('rb') as src:
        size = target.stat().st_size
        src.seek(max(0, size-limit))
        if size > limit: src.readline()
        lines = src.read(limit).splitlines()
    records = []
    for line in lines:
        try: records.append(json.loads(line))
        except ValueError: continue
    return records, size > limit


def dashboard(root, version, revision):
    # Invoked only when Training opens or Refresh is pressed, never by run polls.
    queue = assignments(root)
    registry = slots(root)
    records, sampled = tail_json(root, 'logs/journal/CURRENT.jsonl')
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    records = [r for r in records if r.get('ts', '').startswith(today)]
    metrics = dict(runs=0, good=0, neutral=0, bad=0, flags=0, executed=0, denied=0)
    flags = []
    for r in records:
        phase = r.get('phase')
        if phase == 'prompt': metrics['runs'] += 1
        if phase == 'feedback' and r.get('feedback', {}).get('rating') in ('good', 'neutral', 'bad'):
            metrics[r['feedback']['rating']] += 1
        if phase == 'eval' and r.get('eval', {}).get('flag'):
            metrics['flags'] += 1
            flags.append(dict(id='run:'+r['run_id'], title=r['eval']['note'], run_id=r['run_id'], version=r.get('jarvis_version'), source='Journal eval'))
        if phase == 'done':
            happened = r.get('happened', {})
            if happened.get('status') == 'denied': metrics['denied'] += 1
            if happened.get('steps'): metrics['executed'] += 1
    problems, warnings = [], []
    try:
        response = subprocess.run(['gh','issue','list','--repo','Avdbergnmf/omarchy-jarvis','--state','open','--limit','100','--json','number,title,url'], capture_output=True, text=True, timeout=5, check=True)
        for i in json.loads(response.stdout):
            problems.append(dict(id='issue:'+str(i['number']), title=i['title'], source='GitHub', url=i['url']))
    except (OSError, ValueError, subprocess.SubprocessError):
        warnings.append('GitHub unavailable; local problems remain available.')
    for folder in ('bugs', 'features'):
        for path in sorted((root / 'docs/backlog' / folder).glob('*.md'))[:100]:
            problems.append(dict(id='backlog:'+path.stem, title=path.stem, source='Local '+folder, path=str(path.relative_to(root))))
    neutral, _ = tail_json(root, 'logs/feedback/needs-review.jsonl', 200_000)
    for r in neutral[-30:]:
        problems.append(dict(id='neutral:'+r.get('run_id','unknown'), title=r.get('prompt','Review run'), source='Neutral feedback', run_id=r.get('run_id')))
    problems.extend(flags[-30:])
    validations = validation.list_features(root)
    problems.extend(dict(id='validation:'+v['id'], title=v['title'], source='Failed human test') for v in validations if v['status']=='failed')
    for slot in registry['agents']:
        slot['busy'] = busy(slot, queue)
    return dict(version=version, revision=revision, metrics=metrics, sampled=sampled, period='Today UTC, current journal only', problems=problems,
                assignments=queue, agents=registry['agents'], warnings=warnings, validations=validations,
                context=['START.md','docs/SESSION.md',QUEUE,'docs/DECISIONS.md','docs/LOGGING.md'], session=read(root, 'docs/SESSION.md')[:5000])


def append_row(text, row):
    lines = text.splitlines()
    position = max((i for i,line in enumerate(lines) if line.startswith('|')), default=len(lines)-1)+1
    lines.insert(position, row)
    return '\n'.join(lines)+'\n'



def preview(root, data, version='unknown', revision='unknown'):
    if not isinstance(data, dict): raise ValueError('Expected an object')
    with LOCK:
        if data.get('operation') == 'validation':
            changes, message, result = validation.prepare(root, data, version, revision)
            before = {p:read(root,p) for p in changes}
            return store_preview(root, before, changes, message, validation_result=result)
        queue = assignments(root)
        registry = slots(root)
        before = {p: read(root, p) for p in (QUEUE, INDEX, SLOTS, 'docs/SESSION.md')}
        changes = {}
        operation = data.get('operation')
        if operation not in ('assignment','work','slot'):
            raise ValueError('Unknown preparation operation')
        slot_id = data.get('slot_id')
        if slot_id == 'new':
            label = short(data.get('label'), 'Agent label', 60)
            kind = data.get('kind')
            if kind not in KINDS: raise ValueError('Unknown agent kind')
            if len(registry['agents']) >= 32: raise ValueError('Agent slot limit reached')
            slot = dict(id='slot-'+secrets.token_hex(6), label=label, kind=kind, status='idle', current_assignment=None, queued_assignment_ids=[])
            registry['agents'].append(slot)
        else:
            slot = next((s for s in registry['agents'] if s['id'] == slot_id), None)
            if slot is None: raise ValueError('Select an existing or new agent slot')
        if operation == 'slot':
            if slot_id != 'new':
                if data.get('status') not in ('idle','busy'): raise ValueError('Expected idle or busy')
                slot['status'] = data['status']
            message = 'Save local agent slot. This does not start or contact an agent.'
            handoff = ''
        else:
            mode = data.get('mode')
            if mode not in ('queue','now'): raise ValueError('Choose queue or prepare now')
            if mode == 'now' and busy(slot, queue): raise ValueError('Agent slot is busy; queue until free instead')
            if operation == 'assignment':
                title = short(data.get('title'), 'Title', 140).replace('\n',' ').replace('|','/')
                comments = short(data.get('comments',''), 'Comments', 1200, empty=True)
                source = short(data.get('source','Manual training observation'), 'Source', 500)
                area = data.get('area')
                if area not in AREAS: raise ValueError('Unknown area')
                ids = [int(n) for n in re.findall(r'\bA-(\d+)\b', before[INDEX] + before[QUEUE])]
                aid = f'A-{max(ids, default=0)+1:03d}'
                path = f'docs/assignments/active/{aid}-training.md'
                if (root/path).exists(): raise ValueError('Assignment id already exists; refresh')
                forbidden = ', '.join(a+'/' for a in AREAS if a != area and a != 'docs')
                body = f'''# {aid} — {title}

- **Status:** queued
- **Area:** area:{area}
- **parallel-ok:** NO
- **Allowed paths:** {area}/, tests/, docs/assignments/, docs/SESSION.md, docs/PROGRESS.md, docs/DECISIONS.md
- **Forbidden paths:** {forbidden}; approval bypass; real agent dispatch
- **Links:** {source}
- **Prepared for:** {slot['label']} ({slot['kind']}); human must paste the handoff

## Goal
{title}

## Human comments / evidence
{comments or '(No additional comments)'}

## Checklist
- [ ] Read START, SESSION and QUEUE; check ownership before claiming
- [ ] Reproduce and document expected vs actual behavior from the linked problem
- [ ] Implement the scoped change; clarify acceptance with Alex if evidence is insufficient
- [ ] Verify relevant tests and Doctor; add/update human validation entry
- [ ] Update SESSION, PROGRESS, QUEUE and INDEX; move to done/ on acceptance

## Out of scope
Unrelated queue work, unreviewed skills, silent cloud spending.
'''
                changes[path] = body
                changes[QUEUE] = append_row(before[QUEUE], f'| {aid} | {title} | queued | area:{area} | NO | [active/{aid}-training.md](active/{aid}-training.md) |')
                changes[INDEX] = append_row(before[INDEX], f'| {aid} | queued | {title} |')
            else:
                aid = data.get('assignment_id')
                item = next((a for a in queue if a['id'] == aid), None)
                if item is None or item['status'] not in ('queued','in_progress','blocked'):
                    raise ValueError('Select an open assignment')
            if mode == 'queue':
                if aid not in slot['queued_assignment_ids']: slot['queued_assignment_ids'].append(aid)
                message = f'{aid} queued locally for {slot["label"]}. Nothing is sent automatically when the slot becomes free.'
            else:
                slot['queued_assignment_ids'] = [a for a in slot['queued_assignment_ids'] if a != aid]
                slot['current_assignment'] = aid
                message = f'Handoff prepared for {slot["label"]}. Paste it yourself; no agent was contacted or started.'
            template = data.get('template', 'NEW_AGENT')
            if template not in ('NEW_AGENT','CONTINUE'): raise ValueError('Unknown prompt template')
            prompt = read(root, f'docs/assignments/prompts/{template}.txt')
            handoff = f'# Prepared handoff — {aid} → {slot["label"]}\n\n{message}\n\nRead START.md first. Work on **{aid} only** after checking QUEUE/SESSION ownership. Never override an in-progress owner.\n\n{prompt}\n'
            hp = f'docs/backlog/handoffs/active/{aid}-{slot["id"]}-{secrets.token_hex(4)}.md'
            changes[hp] = handoff
            hi = 'docs/backlog/handoffs/INDEX.md'
            changes[hi] = read(root, hi).rstrip()+f'\n- [{aid} → {slot["label"]}](active/{Path(hp).name}) — active\n'
            slot['last_handoff'] = hp
        changes[SLOTS] = json.dumps(registry, indent=2)+'\n'
        for path in changes: before.setdefault(path, read(root, path))
        return store_preview(root, before, changes, message, handoff)


def store_preview(root, before, changes, message, handoff='', validation_result=None):
    now = time.monotonic()
    for key in list(PREVIEWS):
        if PREVIEWS[key]['expires'] < now: PREVIEWS.pop(key)
    if len(PREVIEWS) >= 32: PREVIEWS.pop(next(iter(PREVIEWS)))
    token = secrets.token_urlsafe(24)
    PREVIEWS[token] = dict(root=str(root), before=before, changes=changes, message=message, handoff=handoff, expires=now+900, validation=validation_result)
    return dict(preview_id=token, message=message, files=[dict(path=p, content=v) for p,v in changes.items()], handoff=handoff)


def confirm(root, token):
    with LOCK:
        proposal = PREVIEWS.pop(token, None) if isinstance(token,str) else None
        if not proposal or proposal['root'] != str(root) or proposal['expires'] < time.monotonic():
            raise ValueError('Preview expired or already used; prepare again')
        if any(read(root,p) != old for p,old in proposal['before'].items()):
            raise ValueError('Files or ownership changed since preview; refresh and review again')
        written = []
        try:
            for path, content in proposal['changes'].items():
                target = root/path
                target.parent.mkdir(parents=True, exist_ok=True)
                temp = target.with_name(target.name+'.'+secrets.token_hex(4)+'.tmp')
                try:
                    with temp.open('x') as out:
                        os.chmod(temp, 0o600)
                        out.write(content)
                    temp.replace(target)
                finally:
                    temp.unlink(missing_ok=True)
                written.append(path)
        except OSError:
            for path in reversed(written):
                old = proposal['before'][path]
                if old: (root/path).write_text(old)
                else: (root/path).unlink(missing_ok=True)
            raise
        return dict(message=proposal['message'], handoff=proposal['handoff'], paths=list(proposal['changes']), validation=proposal.get('validation'))
