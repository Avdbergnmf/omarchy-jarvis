"""Human-only feature validation definitions and versioned evidence."""
import datetime
import hashlib
import json
import re
import secrets
from journal import clean

CATALOG = 'docs/validation/catalog.json'
FEATURES = 'docs/FEATURES.md'


def definition_hash(item):
    definition = {k:item[k] for k in ('id','title','area','steps','expected','jarvis_version_shipped')}
    return hashlib.sha256(json.dumps(definition,sort_keys=True).encode()).hexdigest()


def step_text(step):
    """A guided step is a plain string (implicit kind='human') or an object with a
    display 'text' and a 'kind' — 'auto' additionally carries the literal chat 'prompt'
    Training submits on the human's behalf (A-020: pure mechanics, never judgment or
    approval, are the only thing automated)."""
    return step if isinstance(step,str) else step['text']


def step_kind(step):
    return 'human' if isinstance(step,str) else step.get('kind','human')


def load(root):
    path = root/CATALOG
    if not path.exists(): return {'version':1,'features':[]}
    if not path.resolve().is_relative_to(root.resolve()) or path.is_symlink(): raise ValueError('Invalid catalog path')
    if path.stat().st_size > 1_000_000: raise ValueError('Validation catalog exceeds 1 MB')
    data = json.loads(path.read_text())
    if not isinstance(data,dict) or data.get('version') != 1 or not isinstance(data.get('features'),list) or len(data['features'])>200:
        raise ValueError('Invalid validation catalog')
    seen = set()
    for item in data['features']:
        if not isinstance(item,dict): raise ValueError('Invalid feature entry')
        fid = item.get('id')
        if not isinstance(fid,str) or not re.fullmatch(r'feat-[a-z0-9-]{1,70}',fid) or fid in seen:
            raise ValueError('Invalid or duplicate feature id')
        seen.add(fid)
        for field in ('title','expected','jarvis_version_shipped'):
            if not isinstance(item.get(field),str) or not 0<len(item[field])<=1500: raise ValueError('Invalid '+field)
        if item.get('area') not in ('overlay','brain','actions','skills','docs'): raise ValueError('Invalid feature area')
        steps=item.get('steps')
        if not isinstance(steps,list) or not 1<=len(steps)<=20: raise ValueError('Each feature needs 1–20 short guided steps')
        for s in steps:
            if isinstance(s,str):
                if not 0<len(s)<=500: raise ValueError('Each feature needs 1–20 short guided steps')
                continue
            if not isinstance(s,dict) or not isinstance(s.get('text'),str) or not 0<len(s['text'])<=500:
                raise ValueError('Each feature needs 1–20 short guided steps')
            if s.get('kind') not in (None,'human','auto'): raise ValueError('Invalid guided step kind')
            if s.get('kind')=='auto' and (not isinstance(s.get('prompt'),str) or not 0<len(s['prompt'])<=2000):
                raise ValueError('An auto step needs a literal chat prompt (1-2000 characters)')
        if item.get('status') not in ('unvalidated','validated','failed'): raise ValueError('Invalid feature status')
        last=item.get('last_run')
        if last is not None and not isinstance(last,dict): raise ValueError('Invalid last_run')
    return data


def list_features(root):
    features=load(root)['features']
    for item in features:
        item['definition_hash']=definition_hash(item)
        last=item.get('last_run') or {}
        if last.get('definition_hash') != item['definition_hash']:
            item['status']='unvalidated'
    return features


def markdown(catalog):
    lines=['# Jarvis feature catalog','',
           'Source of truth: [validation/catalog.json](validation/catalog.json). Training lists pending and failed human tests.',
           'Agents must update definitions when shipping user-visible behavior. Automated tests never mark a feature human-validated.',
           '', '| id | title | area | status | last tested version |', '|---|---|---|---|---|']
    for item in catalog['features']:
        status=item['status'] if (item.get('last_run') or {}).get('definition_hash')==definition_hash(item) else 'unvalidated'
        fields=[item['id'],item['title'],item['area'],status,(item.get('last_run') or {}).get('jarvis_version','—')]
        lines.append('| '+' | '.join(str(f).replace('|','/').replace('\n',' ') for f in fields)+' |')
    return '\n'.join(lines)+'\n'


def prepare(root, data, version, revision):
    catalog=load(root)
    item=next((i for i in catalog['features'] if i['id']==data.get('feature_id')),None)
    if not item: raise ValueError('Unknown feature')
    definition=definition_hash(item)
    if data.get('definition_hash') != definition: raise ValueError('Feature steps changed; reload and repeat the guided test')
    outcome=data.get('outcome')
    if outcome not in ('validated','failed'): raise ValueError('Choose Verify or Fail')
    if outcome=='validated' and data.get('attempted') is not True: raise ValueError('Complete the guided steps before verifying')
    notes=data.get('notes','')
    if not isinstance(notes,str) or len(notes)>1200 or (outcome=='failed' and not notes.strip()):
        raise ValueError('Failed tests need an actual-outcome note (up to 1200 characters)')
    run_id=data.get('run_id','')
    if not isinstance(run_id,str) or (run_id and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',run_id)):
        raise ValueError('Invalid evidence run id')
    last=dict(id=secrets.token_hex(12),ts=datetime.datetime.now(datetime.timezone.utc).isoformat(),jarvis_version=version,
              git_describe=revision,definition_hash=definition,run_id=run_id or None,notes=clean(notes),result=outcome)
    item.update(status=outcome,last_run=last,jarvis_version=version)
    message=f'Record human test as {outcome} for {item["title"]} on Jarvis {version}.'
    if outcome=='failed': message+=' Then you can draft a bug report; filing still requires Run in chat.'
    changes={CATALOG:json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',FEATURES:markdown(catalog)}
    return changes,message,dict(feature_id=item['id'],record_id=last['id'],outcome=outcome)


def report_evidence(root, feature_id, record_id):
    item=next((i for i in load(root)['features'] if i['id']==feature_id),None)
    last=(item or {}).get('last_run') or {}
    if not item or last.get('id')!=record_id or last.get('result')!='failed':
        raise ValueError('Failed validation changed or is missing; refresh Training')
    # Include the actual failed definition; refuse altered guides rather than misattribute evidence.
    if last.get('definition_hash')!=definition_hash(item): raise ValueError('Feature definition changed since this test')
    seed=f'Human validation failed: {item["title"]}\nFeature: {item["id"]}\nTested Jarvis: {last["jarvis_version"]} ({last["git_describe"]})\nExpected: {item["expected"]}\nActual: {last["notes"]}\nSteps: '+ '; '.join(step_text(s) for s in item['steps'])
    return item,last,seed
