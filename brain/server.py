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
    try: notify(run_id, message)
    except Exception as e: log(run_id, 'notification-error', e)

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

def json_plan(prompt):
    instructions = (ROOT/'brain/system_prompt.md').read_text() + '\nReturn a JSON object with actions (tool + arguments) and reply. Choose at most ONE action. Compound requests MUST use a complete run_skill recipe. Never combine a recipe with its individual steps. Use these exact examples:\n' + json.dumps([
        {'user':'open my planning in a new workspace','plan':{'actions':[{'tool':'run_skill','arguments':{'skill':'open-planning'}}],'reply':'Opening your planning apps.'}},
        {'user':'move this window to scratchpad and open email','plan':{'actions':[{'tool':'run_skill','arguments':{'skill':'scratch-and-mail'}}],'reply':'Moving the window to scratchpad and opening Outlook.'}},
        {'user':'hello','plan':{'actions':[],'reply':'Hello! How can I help?'}}]) + '\nOther single actions: catalog_bindings(query), run_binding(binding), workspace_new(), workspace_switch(workspace integer), scratch_toggle(), scratch_move_here(), open_webapp(name). For compound scratch + email requests the ONE action is run_skill with skill=scratch-and-mail. For planning the ONE action is run_skill with skill=open-planning.'
    request = Request('http://127.0.0.1:11434/api/chat',data=json.dumps({'model':MODEL,'messages':[{'role':'system','content':instructions},{'role':'user','content':prompt}],'format':PLAN_SCHEMA,'stream':False,'options':{'temperature':0,'num_ctx':8192}}).encode(),headers={'Content-Type':'application/json'})
    with urlopen(request,timeout=180) as response: plan=json.loads(json.load(response)['message']['content'])
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

def execute_json_run(run_id,prompt,target):
    try:
        announce(run_id,'Planning your request… Click for live console.')
        plan=json_plan(prompt)
        log(run_id,'plan',json.dumps(plan))
        if plan['actions']: restore_target(target)
        summaries=[]
        for action in plan['actions']:
            name=action['tool']; args=action['arguments']
            log(run_id,'tool-call',json.dumps({'name':name,'arguments':args}))
            announce(run_id,'Running '+args.get('skill',name).replace('_',' ')+'…')
            result=subprocess.run(tool_argv(name,args),capture_output=True,text=True,timeout=160)
            log(run_id,'stdout',result.stdout)
            if result.stderr: log(run_id,'stderr',result.stderr)
            if result.returncode: raise RuntimeError('Action failed: '+result.stdout.strip())
            summaries.append(args.get('skill',name).replace('_',' '))
        # Completion text is derived from successful actions, not model claims.
        reply='Completed: '+', '.join(summaries)+'.' if summaries else plan['reply'][:1000]
        announce(run_id,reply)
        with STATE_LOCK: RUNS[run_id].update(status='done',reply=reply)
    except Exception as e:
        reply=redact(str(e)); announce(run_id,'Stopped: '+reply[:200])
        with STATE_LOCK: RUNS[run_id].update(status='error',reply=reply)
    finally: BUSY.release()

def execute_run(run_id, prompt, target):
    try:
        announce(run_id, 'Planning your request… Click for live console.')
        messages = [{'role':'system','content':(ROOT / 'brain/system_prompt.md').read_text()}, {'role':'user','content':prompt}]
        seen = set(); restored = False; total = 0
        for _ in range(6):
            request = Request('http://127.0.0.1:11434/api/chat', data=json.dumps({'model':MODEL,'messages':messages,'tools':TOOLS,'stream':False,'options':{'temperature':0,'num_ctx':8192}}).encode(), headers={'Content-Type':'application/json'})
            with urlopen(request, timeout=180) as response: msg = json.load(response)['message']
            # Retain public content and calls, never model-internal thinking fields.
            msg = {k:v for k,v in msg.items() if k in ('role','content','tool_calls')}
            messages.append(msg)
            calls = msg.get('tool_calls') or []
            if not calls:
                reply = msg.get('content', '').strip() or 'Done.'
                announce(run_id, reply[:250])
                with STATE_LOCK: RUNS[run_id].update(status='done', reply=reply)
                return
            for call in calls:
                name = call['function']['name']; args = call['function'].get('arguments', {})
                if isinstance(args, str): args = json.loads(args)
                argv = tool_argv(name, args)
                signature = json.dumps([name,args],sort_keys=True)
                if signature in seen: raise ValueError('Model repeated a completed action; stopped to prevent duplicate work')
                seen.add(signature); total += 1
                if total > 10: raise ValueError('Action limit reached')
                log(run_id, 'tool-call', json.dumps({'name':name,'arguments':args}))
                if name != 'catalog_bindings' and not restored:
                    restore_target(target); restored = True
                announce(run_id, 'Running ' + (args.get('skill') or name).replace('_',' ') + '…')
                result = subprocess.run(argv, capture_output=True, text=True, timeout=160)
                log(run_id, 'stdout', result.stdout)
                if result.stderr: log(run_id, 'stderr', result.stderr)
                if result.returncode: raise RuntimeError('Action failed: ' + result.stdout.strip())
                messages.append({'role':'tool','tool_name':name,'content':result.stdout[:16000]})
        raise RuntimeError('Model exceeded the six-turn limit')
    except Exception as e:
        reply = redact(str(e))
        announce(run_id, 'Stopped: ' + reply[:200])
        with STATE_LOCK: RUNS[run_id].update(status='error', reply=reply)
    finally: BUSY.release()

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
    def do_GET(self):
        if not self.host_ok(): return self.reply(403, {'error':'Invalid host'})
        if self.path == '/health': return self.reply(200, {'service':'omarchy-jarvis','model':MODEL})
        if self.path in ('/','/jarvis-overlay','/app.js','/style.css'):
            name, mime = {'/':('index.html','text/html'),'/jarvis-overlay':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css')}[self.path]
            return self.reply(200,(ROOT/'overlay'/name).read_text(),mime)
        if self.path == '/v1/session': return self.reply(200, {'token':TOKEN})
        if self.path.startswith('/v1/runs/'):
            if self.headers.get('X-Jarvis-Token') != TOKEN: return self.reply(403, {'error':'Invalid token'})
            with STATE_LOCK: state = RUNS.get(self.path.rsplit('/',1)[-1])
            return self.reply(200 if state else 404,state or {'error':'Unknown run'})
        return self.reply(404, {'error':'Not found'})
    def do_POST(self):
        if not self.host_ok() or self.headers.get('Origin') not in (None,'http://127.0.0.1:7421') or self.headers.get('X-Jarvis-Token') != TOKEN:
            return self.reply(403, {'error':'Invalid origin or token'})
        if self.path not in ('/v1/run','/v1/close'): return self.reply(404, {'error':'Not found'})
        if self.path == '/v1/close':
            try:
                for c in hypr('clients'):
                    if is_overlay(c): dispatch('closewindow','address:'+c['address'])
                return self.reply(200, {'ok':True})
            except Exception as e: return self.reply(500, {'error':str(e)})
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
            with STATE_LOCK:
                if len(RUNS)>200: RUNS.pop(next(iter(RUNS)))
                RUNS[run_id] = {'run_id':run_id,'status':'running','reply':'Thinking…'}
            threading.Thread(target=execute_run if os.environ.get('JARVIS_PLANNER') == 'tools' else execute_json_run,args=(run_id,prompt.strip(),target),daemon=True).start()
            return self.reply(202, {'run_id':run_id,'reply':'Thinking…'})
        except Exception as e:
            BUSY.release(); return self.reply(500, {'error':str(e)})

if __name__ == '__main__':
    os.umask(0o077)
    (LOGS/'runs').mkdir(parents=True, exist_ok=True)
    catalog(refresh=True)
    server = ThreadingHTTPServer(('127.0.0.1',7421),Handler)
    server.timeout = 10
    print('Jarvis listening on 127.0.0.1:7421; model=' + MODEL,flush=True)
    server.serve_forever()
