#!/usr/bin/env python3
"""Local-only authenticated HTTP UI and bounded Ollama tool loop; stdlib only."""
import datetime
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import threading
import time
import tomllib
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'actions'))
from core import catalog, dispatch, hypr, notify, is_overlay
LOGS = ROOT / 'logs'
MODEL = os.environ.get('JARVIS_MODEL', 'qwen2.5:3b')
TOOLS = json.loads((ROOT / 'brain/tools.json').read_text())
SCHEMAS = {t['function']['name']: t['function']['parameters'] for t in TOOLS}
TOKEN = secrets.token_urlsafe(32)
BUSY = threading.Lock()
STATE_LOCK = threading.Lock()
RUNS = {}
PENDING = {}
BUSY_RUN_ID = None
AWAIT_TIMEOUT = 900  # seconds an awaiting-approval run may sit idle before auto-deny
RUN_ID_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}')

def load_config():
    defaults = {'approval_mode': 'always', 'show_notifications': True}
    path = Path(os.environ.get('JARVIS_CONFIG', str(Path.home() / '.config/jarvis/config.toml')))
    if not path.exists():
        return defaults
    try:
        data = tomllib.loads(path.read_text())
    except Exception:
        return defaults
    mode = data.get('approval_mode', defaults['approval_mode'])
    if mode not in ('always', 'skills_trusted', 'off'):
        mode = defaults['approval_mode']
    return {'approval_mode': mode, 'show_notifications': bool(data.get('show_notifications', defaults['show_notifications']))}

CONFIG = load_config()

def redact(value):
    text = str(value)
    return re.sub(r'(?i)(bearer\s+|(?:api[_-]?key|password|token|secret)\s*[=:]\s*)[^\s,}"\']+', r'\1[REDACTED]', text)

def log(run_id, event, value):
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    line = ''.join(stamp + ' ' + event + ' ' + part + '\n' for part in (redact(value).splitlines() or ['']))
    with (LOGS / 'runs' / (run_id + '.log')).open('a') as out:
        out.write(line); out.flush()

def announce(run_id, message):
    message = redact(message)
    log(run_id, 'status', message)
    if not CONFIG['show_notifications']:
        return
    try: notify(run_id, message)
    except Exception as e: log(run_id, 'notification-error', e)

def release_busy():
    global BUSY_RUN_ID
    with STATE_LOCK: BUSY_RUN_ID = None
    BUSY.release()

def expire_stale():
    with STATE_LOCK:
        rid = BUSY_RUN_ID
        run = RUNS.get(rid) if rid else None
        if not (run and run.get('status') == 'awaiting_approval' and time.monotonic() - run.get('awaiting_since', 0) > AWAIT_TIMEOUT):
            return
        run.update(status='denied', reply='Cancelled: approval timed out.')
        PENDING.pop(rid, None)
    try:
        log(rid, 'status', 'Cancelled: approval timed out (no response).')
    finally:
        release_busy()

def validate_call(name, args):
    if name not in SCHEMAS or not isinstance(args, dict):
        raise ValueError('Unknown tool or invalid arguments')
    spec = SCHEMAS[name]
    if set(args) - set(spec['properties']) or set(spec['required']) - set(args):
        raise ValueError('Unexpected or missing tool arguments')
    for key, val in args.items():
        rule = spec['properties'][key]
        if rule['type'] == 'string' and (not isinstance(val, str) or len(val) > 250): raise ValueError('Expected short string')
        if rule['type'] == 'integer' and (type(val) is not int or not rule['minimum'] <= val <= rule['maximum']): raise ValueError('Invalid integer')
        if 'enum' in rule and val not in rule['enum']: raise ValueError('Invalid choice')
    return args

def tool_argv(name, args):
    validate_call(name, args)
    argv = [str(ROOT / 'actions' / name)]
    if name == 'catalog_bindings': argv += ['--refresh', '--query', args.get('query', '')]
    elif name == 'run_binding': argv.append(args['binding'])
    elif name == 'workspace_switch': argv.append(str(args['workspace']))
    elif name == 'open_webapp': argv += ['--name', args['name']]
    elif name == 'run_skill': argv.append(args['skill'])
    return argv

def action_label(name, args):
    return (args.get('skill') or name).replace('_', ' ')

def restore_target(target):
    clients = hypr('clients')
    if target and not any(c['address'] == target for c in clients):
        raise ValueError('Original window closed; focus a window and try again')
    for c in clients:
        if is_overlay(c): dispatch('closewindow', 'address:' + c['address'])
    if target: dispatch('focuswindow', 'address:' + target)

PLAN_SCHEMA = {'type':'object','properties':{
    'actions':{'type':'array','maxItems':1,'items':{'anyOf':[
        {'type':'object','properties':{'tool':{'const':name},'arguments':schema},
         'required':['tool','arguments'],'additionalProperties':False}
        for name,schema in SCHEMAS.items()]}},
    'reply':{'type':'string'}},'required':['actions','reply'],'additionalProperties':False}

def ollama_chat(payload):
    request = Request('http://127.0.0.1:11434/api/chat', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
    with urlopen(request, timeout=180) as response: return json.load(response)['message']

def json_plan(prompt):
    instructions = (ROOT/'brain/system_prompt.md').read_text() + '\nReturn a JSON object with actions (tool + arguments) and reply. Choose at most ONE action. Compound requests MUST use a complete run_skill recipe. Never combine a recipe with its individual steps. Use these exact examples:\n' + json.dumps([
        {'user':'open my planning in a new workspace','plan':{'actions':[{'tool':'run_skill','arguments':{'skill':'open-planning'}}],'reply':'Opening your planning apps.'}},
        {'user':'move this window to scratchpad and open email','plan':{'actions':[{'tool':'run_skill','arguments':{'skill':'scratch-and-mail'}}],'reply':'Moving the window to scratchpad and opening Outlook.'}},
        {'user':'hello','plan':{'actions':[],'reply':'Hello! How can I help?'}}]) + '\nOther single actions: catalog_bindings(query), run_binding(binding), workspace_new(), workspace_switch(workspace integer), scratch_toggle(), scratch_move_here(), open_webapp(name). For compound scratch + email requests the ONE action is run_skill with skill=scratch-and-mail. For planning the ONE action is run_skill with skill=open-planning.'
    plan = json.loads(ollama_chat({'model':MODEL,'messages':[{'role':'system','content':instructions},{'role':'user','content':prompt}],'format':PLAN_SCHEMA,'stream':False,'options':{'temperature':0,'num_ctx':8192}})['content'])
    if not isinstance(plan,dict) or set(plan)!={'actions','reply'} or not isinstance(plan['actions'],list) or len(plan['actions'])>1 or not isinstance(plan['reply'],str):
        raise ValueError('Invalid JSON action plan')
    seen=set()
    for action in plan['actions']:
        if not isinstance(action,dict) or set(action)!={'tool','arguments'}: raise ValueError('Invalid plan action')
        tool_argv(action['tool'],action['arguments'])
        signature=json.dumps(action,sort_keys=True)
        if signature in seen: raise ValueError('Duplicate action in plan')
        seen.add(signature)
    if any(a['tool']=='run_skill' for a in plan['actions']) and len(plan['actions'])!=1:
        raise ValueError('A complete recipe cannot be combined with other actions')
    return plan

def execute_plan(run_id, plan, target):
    try:
        with STATE_LOCK: RUNS[run_id].update(status='running', steps=[])
        if plan['actions']: restore_target(target)
        summaries = []
        for action in plan['actions']:
            name = action['tool']; args = action['arguments']
            label = action_label(name, args)
            step = {'tool': name, 'arguments': args, 'label': label, 'status': 'running'}
            with STATE_LOCK: RUNS[run_id]['steps'].append(step)
            log(run_id, 'tool-call', json.dumps({'name':name,'arguments':args}))
            announce(run_id, 'Running ' + label + '…')
            result = subprocess.run(tool_argv(name, args), capture_output=True, text=True, timeout=160)
            log(run_id, 'stdout', result.stdout)
            if result.stderr: log(run_id, 'stderr', result.stderr)
            if result.returncode:
                with STATE_LOCK: step.update(status='error', summary=result.stdout.strip()[:300])
                raise RuntimeError('Action failed: ' + result.stdout.strip())
            with STATE_LOCK: step.update(status='done', summary=result.stdout.strip()[:300])
            summaries.append(label)
        reply = 'Completed: '+', '.join(summaries)+'.' if summaries else plan['reply'][:1000]
        announce(run_id,reply)
        with STATE_LOCK: RUNS[run_id].update(status='done',reply=reply)
    except Exception as e:
        reply=redact(str(e)); announce(run_id,'Stopped: '+reply[:200])
        with STATE_LOCK: RUNS[run_id].update(status='error',reply=reply)
    finally: release_busy()

def plan_and_maybe_run(run_id, prompt, target):
    try:
        announce(run_id, 'Planning your request… Click for live console.')
        plan = json_plan(prompt)
        log(run_id, 'plan', json.dumps(plan))
        if not plan['actions']:
            reply = plan['reply'][:1000]
            try:
                announce(run_id, reply)
            finally:
                with STATE_LOCK: RUNS[run_id].update(status='done', reply=reply, plan=plan)
                release_busy()
            return
        with STATE_LOCK: RUNS[run_id].update(plan=plan, reply=plan['reply'][:1000])
        auto = CONFIG['approval_mode'] == 'off' or (CONFIG['approval_mode'] == 'skills_trusted' and all(a['tool'] == 'run_skill' for a in plan['actions']))
        if auto:
            if CONFIG['approval_mode'] == 'off': log(run_id, 'status', 'approval_mode=off: auto-running without confirmation')
            execute_plan(run_id, plan, target)  # releases busy itself, on every path
        else:
            with STATE_LOCK: PENDING[run_id] = {'target': target, 'planner': 'json'}
            with STATE_LOCK: RUNS[run_id].update(status='awaiting_approval', awaiting_since=time.monotonic())
            announce(run_id, 'Awaiting approval — open Jarvis to review the plan.')
    except Exception as e:
        reply = redact(str(e))
        try:
            announce(run_id, 'Stopped: ' + reply[:200])
        finally:
            with STATE_LOCK:
                RUNS[run_id].update(status='error', reply=reply)
                PENDING.pop(run_id, None)
            release_busy()

def calls_to_actions(calls):
    actions = []
    for call in calls:
        name = call['function']['name']; args = call['function'].get('arguments', {})
        if isinstance(args, str): args = json.loads(args)
        tool_argv(name, args)  # validate before showing the plan to the user
        actions.append({'tool': name, 'arguments': args})
    return actions

def plan_tools_run(run_id, prompt, target):
    try:
        announce(run_id, 'Planning your request… Click for live console.')
        messages = [{'role':'system','content':(ROOT / 'brain/system_prompt.md').read_text()}, {'role':'user','content':prompt}]
        msg = ollama_chat({'model':MODEL,'messages':messages,'tools':TOOLS,'stream':False,'options':{'temperature':0,'num_ctx':8192}})
        msg = {k:v for k,v in msg.items() if k in ('role','content','tool_calls')}
        messages.append(msg)
        calls = msg.get('tool_calls') or []
        if not calls:
            reply = msg.get('content', '').strip() or 'Done.'
            try:
                announce(run_id, reply[:250])
            finally:
                with STATE_LOCK: RUNS[run_id].update(status='done', reply=reply)
                release_busy()
            return
        actions = calls_to_actions(calls)
        plan = {'actions': actions, 'reply': msg.get('content', '').strip()}
        log(run_id, 'plan', json.dumps(plan))
        with STATE_LOCK: RUNS[run_id].update(plan=plan, reply=(plan['reply'][:1000] or 'Reviewing proposed actions…'))
        if CONFIG['approval_mode'] == 'off':
            log(run_id, 'status', 'approval_mode=off: auto-running without confirmation')
            execute_tools_plan(run_id, target, messages)  # releases busy itself, on every path
        else:
            with STATE_LOCK: PENDING[run_id] = {'target': target, 'planner': 'tools', 'messages': messages}
            with STATE_LOCK: RUNS[run_id].update(status='awaiting_approval', awaiting_since=time.monotonic())
            announce(run_id, 'Awaiting approval — open Jarvis to review the plan.')
    except Exception as e:
        reply = redact(str(e))
        try:
            announce(run_id, 'Stopped: ' + reply[:200])
        finally:
            with STATE_LOCK:
                RUNS[run_id].update(status='error', reply=reply)
                PENDING.pop(run_id, None)
            release_busy()

def execute_tools_plan(run_id, target, messages):
    try:
        with STATE_LOCK: RUNS[run_id].update(status='running', steps=[])
        restore_target(target)
        seen = set(); total = 0
        pending_calls = messages[-1].get('tool_calls') or []
        for _ in range(6):
            for call in pending_calls:
                name = call['function']['name']; args = call['function'].get('arguments', {})
                if isinstance(args, str): args = json.loads(args)
                argv = tool_argv(name, args)
                signature = json.dumps([name,args],sort_keys=True)
                if signature in seen: raise ValueError('Model repeated a completed action; stopped to prevent duplicate work')
                seen.add(signature); total += 1
                if total > 10: raise ValueError('Action limit reached')
                label = action_label(name, args)
                step = {'tool': name, 'arguments': args, 'label': label, 'status': 'running'}
                with STATE_LOCK: RUNS[run_id]['steps'].append(step)
                log(run_id, 'tool-call', json.dumps({'name':name,'arguments':args}))
                announce(run_id, 'Running ' + label + '…')
                result = subprocess.run(argv, capture_output=True, text=True, timeout=160)
                log(run_id, 'stdout', result.stdout)
                if result.stderr: log(run_id, 'stderr', result.stderr)
                if result.returncode:
                    with STATE_LOCK: step.update(status='error', summary=result.stdout.strip()[:300])
                    raise RuntimeError('Action failed: ' + result.stdout.strip())
                with STATE_LOCK: step.update(status='done', summary=result.stdout.strip()[:300])
                messages.append({'role':'tool','tool_name':name,'content':result.stdout[:16000]})
            msg = ollama_chat({'model':MODEL,'messages':messages,'tools':TOOLS,'stream':False,'options':{'temperature':0,'num_ctx':8192}})
            msg = {k:v for k,v in msg.items() if k in ('role','content','tool_calls')}
            messages.append(msg)
            pending_calls = msg.get('tool_calls') or []
            if not pending_calls:
                reply = msg.get('content', '').strip() or 'Done.'
                announce(run_id, reply[:250])
                with STATE_LOCK: RUNS[run_id].update(status='done', reply=reply)
                return
        raise RuntimeError('Model exceeded the six-turn limit')
    except Exception as e:
        reply = redact(str(e)); announce(run_id, 'Stopped: ' + reply[:200])
        with STATE_LOCK: RUNS[run_id].update(status='error', reply=reply)
    finally: release_busy()

def run_pending(run_id):
    with STATE_LOCK: pending = PENDING.pop(run_id, None)
    if not pending:
        release_busy(); return
    if pending['planner'] == 'tools':
        execute_tools_plan(run_id, pending['target'], pending['messages'])
    else:
        with STATE_LOCK: plan = RUNS[run_id]['plan']
        execute_plan(run_id, plan, pending['target'])

def handle_approve(run_id):
    with STATE_LOCK:
        run = RUNS.get(run_id)
        if not run or run.get('status') != 'awaiting_approval': return None
        run['status'] = 'running'
    threading.Thread(target=run_pending, args=(run_id,), daemon=True).start()
    return run

def handle_deny(run_id):
    with STATE_LOCK:
        run = RUNS.get(run_id)
        if not run or run.get('status') != 'awaiting_approval': return None
        run.update(status='denied', reply='Cancelled — no actions were run.')
        PENDING.pop(run_id, None)
    try:
        log(run_id, 'status', 'Denied by user; no actions were run.')
    finally:
        release_busy()
    return run

def ollama_health():
    try:
        with urlopen('http://127.0.0.1:11434/api/tags', timeout=2): return 'ok'
    except Exception: return 'fail'

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def reply(self, status, value, content_type='application/json'):
        data = json.dumps(value).encode() if content_type == 'application/json' else value.encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")
        self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def host_ok(self): return self.headers.get('Host') == '127.0.0.1:7421'
    def run_id_from(self, suffix):
        if not self.path.startswith('/v1/runs/') or not self.path.endswith(suffix): return None
        run_id = self.path[len('/v1/runs/'):-len(suffix)]
        return run_id if RUN_ID_RE.fullmatch(run_id) else None
    def do_GET(self):
        if not self.host_ok(): return self.reply(403, {'error':'Invalid host'})
        if self.path == '/health': return self.reply(200, {'service':'omarchy-jarvis','model':MODEL,'ollama':ollama_health(),'approval_mode':CONFIG['approval_mode']})
        if self.path in ('/','/jarvis-overlay','/app.js','/style.css'):
            name, mime = {'/':('index.html','text/html'),'/jarvis-overlay':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css')}[self.path]
            return self.reply(200,(ROOT/'overlay'/name).read_text(),mime)
        if self.path == '/v1/session': return self.reply(200, {'token':TOKEN})
        if self.path.startswith('/v1/runs/'):
            if self.headers.get('X-Jarvis-Token') != TOKEN: return self.reply(403, {'error':'Invalid token'})
            expire_stale()
            run_id = self.path.rsplit('/',1)[-1]
            with STATE_LOCK: state = RUNS.get(run_id)
            return self.reply(200 if state else 404,state or {'error':'Unknown run'})
        return self.reply(404, {'error':'Not found'})
    def do_POST(self):
        if not self.host_ok() or self.headers.get('Origin') not in (None,'http://127.0.0.1:7421') or self.headers.get('X-Jarvis-Token') != TOKEN:
            return self.reply(403, {'error':'Invalid origin or token'})
        if self.path == '/v1/close':
            try:
                for c in hypr('clients'):
                    if is_overlay(c): dispatch('closewindow','address:'+c['address'])
                return self.reply(200, {'ok':True})
            except Exception as e: return self.reply(500, {'error':str(e)})
        approve_id = self.run_id_from('/approve')
        if approve_id:
            expire_stale()
            run = handle_approve(approve_id)
            return self.reply(202, run) if run else self.reply(409, {'error':'Run is not awaiting approval'})
        deny_id = self.run_id_from('/deny')
        if deny_id:
            run = handle_deny(deny_id)
            return self.reply(200, run) if run else self.reply(409, {'error':'Run is not awaiting approval'})
        console_id = self.run_id_from('/console')
        if console_id:
            try:
                subprocess.Popen([str(ROOT/'console/jarvis-console'), console_id], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                return self.reply(200, {'ok':True})
            except Exception as e: return self.reply(500, {'error':str(e)})
        if self.path != '/v1/run': return self.reply(404, {'error':'Not found'})
        expire_stale()
        try:
            length = int(self.headers.get('Content-Length','0'))
            if not 0 < length <= 8192: raise ValueError('Invalid request size')
            if self.headers.get('Content-Type') != 'application/json': raise ValueError('Expected application/json')
            body = json.loads(self.rfile.read(length)); prompt = body.get('prompt')
            if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>2000: raise ValueError('Prompt must be 1–2000 characters')
        except (ValueError,AttributeError) as e: return self.reply(400, {'error':str(e)})
        if not BUSY.acquire(blocking=False): return self.reply(409, {'error':'A desktop run is already active'})
        try:
            active = hypr('activewindow'); target = active.get('address')
            if is_overlay(active):
                target = json.loads((LOGS/'overlay-target.json').read_text()).get('address')
            run_id = str(uuid.uuid4())
            (LOGS/'runs'/(run_id+'.log')).touch(mode=0o600)
            global BUSY_RUN_ID
            with STATE_LOCK:
                if len(RUNS)>200: RUNS.pop(next(iter(RUNS)))
                RUNS[run_id] = {'run_id':run_id,'status':'planning','reply':'Thinking…','plan':None,'steps':[]}
                BUSY_RUN_ID = run_id
            threading.Thread(target=plan_tools_run if os.environ.get('JARVIS_PLANNER') == 'tools' else plan_and_maybe_run,args=(run_id,prompt.strip(),target),daemon=True).start()
            return self.reply(202, {'run_id':run_id,'status':'planning','reply':'Thinking…'})
        except Exception as e:
            BUSY.release(); return self.reply(500, {'error':str(e)})

if __name__ == '__main__':
    os.umask(0o077)
    (LOGS/'runs').mkdir(parents=True, exist_ok=True)
    catalog(refresh=True)
    server = ThreadingHTTPServer(('127.0.0.1',7421),Handler)
    server.timeout = 10
    print('Jarvis listening on 127.0.0.1:7421; model=' + MODEL + '; approval_mode=' + CONFIG['approval_mode'],flush=True)
    server.serve_forever()
