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
sys.path.insert(0, str(ROOT / 'brain'))
from journal import Journal, evaluate, clean
from core import catalog, dispatch, hypr, notify, is_overlay, redact, fill_template, slugify
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
    defaults = {'approval_mode': 'always', 'show_notifications': True, 'log_level': 'info'}
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
    return {'log_level': data.get('log_level') if data.get('log_level') in ('info', 'debug') else 'info', 'approval_mode': mode, 'show_notifications': bool(data.get('show_notifications', defaults['show_notifications']))}

CONFIG = load_config()

VERSION = (ROOT / 'VERSION').read_text().strip()
try:
    REVISION = subprocess.run(['git', 'describe', '--always', '--dirty'], cwd=ROOT, capture_output=True, text=True, timeout=2).stdout.strip() or 'unknown'
except (OSError, subprocess.TimeoutExpired):
    REVISION = 'unknown'

def journal_event(run_id, phase, **fields):
    try:
        record = Journal(LOGS, VERSION, REVISION).write(run_id, phase, **fields)
        with STATE_LOCK:
            if run_id in RUNS:
                RUNS[run_id].setdefault('journal', []).append(record)
    except (OSError, ValueError) as error:
        print('journal unavailable: ' + type(error).__name__, file=sys.stderr)

def log(run_id, event, value):
    if event == 'plan':
        journal_event(run_id, 'process', process=json.loads(value))
        return
    if CONFIG.get('log_level', 'info') != 'debug':
        return
    try:
        Journal(LOGS, VERSION, REVISION).append(LOGS / 'debug' / (run_id + '.jsonl'),
            dict(ts=datetime.datetime.now(datetime.timezone.utc).isoformat(), jarvis_version=VERSION,
                 git_describe=REVISION, run_id=run_id, module='brain', event=event, value=clean(value)))
    except OSError:
        pass


def announce(run_id, message):
    message = redact(message)
    log(run_id, 'status', message)
    if not CONFIG['show_notifications']:
        return
    try: notify(run_id, message)
    except Exception as e: log(run_id, 'notification-error', e)

def release_busy():
    global BUSY_RUN_ID
    with STATE_LOCK:
        rid = BUSY_RUN_ID
        run = dict(RUNS.get(rid) or {})
        BUSY_RUN_ID = None
    try:
        if rid and run.get('status') in ('done', 'error', 'denied'):
            if not any(r['phase'] == 'process' for r in run.get('journal', [])):
                journal_event(rid, 'process', process=run.get('plan') or {'actions': [], 'reply': 'No executable plan.'})
            journal_event(rid, 'done', happened={'status': run['status'], 'reply': run.get('reply'), 'steps': run.get('steps', [])}, ok=run['status'] == 'done')
            journal_event(rid, 'eval', eval=evaluate(run), ok=run['status'] == 'done')
    finally:
        BUSY.release()

def expire_stale():
    with STATE_LOCK:
        rid = BUSY_RUN_ID
        run = RUNS.get(rid) if rid else None
        if not (run and run.get('status') in ('awaiting_approval', 'awaiting_answer') and time.monotonic() - run.get('awaiting_since', 0) > AWAIT_TIMEOUT):
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
        if rule['type'] == 'string' and (not isinstance(val, str) or len(val) > rule.get('maxLength', 250)): raise ValueError('Expected short string')
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
    elif name in ('report_bug', 'report_feature'): argv += ['--title', args['title'], '--body', args['body'], '--difficulty', args['difficulty']]
    elif name == 'prepare_handoff': argv += ['--issue', str(args['issue']), '--agent', args['agent']]
    elif name == 'open_app_by_name': argv += ['--name', args['name']]
    return argv

def action_label(name, args):
    label = args.get('skill') or args.get('title') or (name == 'prepare_handoff' and 'issue #' + str(args.get('issue'))) or (name == 'open_app_by_name' and args.get('name')) or name
    return str(label).replace('_', ' ')

def restore_target(target):
    """Focus the window that was active before the overlay opened, so actions that read
    hypr('activewindow') (scratch_move_here, some run_binding chords) operate on the
    user's intended window rather than the overlay itself. Deliberately does NOT close
    the overlay (see A-004/ADR-019): it used to, which killed the live step-list view
    the instant Run was pressed. The overlay now stays open through execution — the
    user dismisses it with Escape or by pressing the hotkey again (toggle-overlay.py's
    existing single-instance close-if-focused / re-focus-if-not logic)."""
    clients = hypr('clients')
    if target and not any(c['address'] == target for c in clients):
        raise ValueError('Original window closed; focus a window and try again')
    if target: dispatch('focuswindow', 'address:' + target)

# report_bug/report_feature are only ever placed in a plan by the deterministic
# intake flow (start_intake/finalize_intake), never guessed by the model from raw
# chat text — a 3B model drafting an issue body directly proved unreliable in
# earlier passes (ADR-009), so they're excluded from both planner surfaces below.
LLM_EXCLUDED_TOOLS = {'report_bug', 'report_feature'}
PLAN_SCHEMA = {'type':'object','properties':{
    'actions':{'type':'array','maxItems':1,'items':{'anyOf':[
        {'type':'object','properties':{'tool':{'const':name},'arguments':schema},
         'required':['tool','arguments'],'additionalProperties':False}
        for name,schema in SCHEMAS.items() if name not in LLM_EXCLUDED_TOOLS]}},
    'reply':{'type':'string'}},'required':['actions','reply'],'additionalProperties':False}
TOOLS_FOR_MODEL = [t for t in TOOLS if t['function']['name'] not in LLM_EXCLUDED_TOOLS]

def ollama_chat(payload):
    request = Request('http://127.0.0.1:11434/api/chat', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
    with urlopen(request, timeout=180) as response: return json.load(response)['message']

# A bounded language guard, not semantic verification of arbitrary model prose.
FALSE_ACTION_CLAIM_RE = re.compile(
    r"^(?:(?:sure|okay|ok|certainly)[,!:.]?\s+)?"
    r"(?:(?:i(?:['’](?:ve|m|ll)| have| am| will)?)[ ]+)?"
    r"(?:open(?:ing|ed)?|mov(?:e|ing|ed)|switch(?:ing|ed)?|toggl(?:e|ing|ed)|"
    r"launch(?:ing|ed)?|start(?:ing|ed)?|clos(?:e|ing|ed)|focus(?:ing|ed)?|fil(?:e|ing|ed))\b"
    r"|^(?:done|completed|success(?:ful(?:ly)?)?)[.!\s]*$", re.I)


def empty_plan_reply(reply):
    reply = reply.strip()
    if not reply or FALSE_ACTION_CLAIM_RE.match(reply):
        return "No actions were run. Try rephrasing, or ask for something more specific."
    return reply[:1000]

def json_plan(prompt):
    instructions = (ROOT/'brain/system_prompt.md').read_text() + '\nReturn a JSON object with actions (tool + arguments) and reply. Choose at most ONE action. Compound requests MUST use a complete run_skill recipe. Never combine a recipe with its individual steps. Use these exact examples:\n' + json.dumps([
        {'user':'open my planning in a new workspace','plan':{'actions':[{'tool':'run_skill','arguments':{'skill':'open-planning'}}],'reply':'Opening your planning apps.'}},
        {'user':'move this window to scratchpad and open email','plan':{'actions':[{'tool':'run_skill','arguments':{'skill':'scratch-and-mail'}}],'reply':'Moving the window to scratchpad and opening Outlook.'}},
        {'user':'hello','plan':{'actions':[],'reply':'Hello! How can I help?'}},
        {'user':'open spotify','plan':{'actions':[{'tool':'open_app_by_name','arguments':{'name':'Spotify'}}],'reply':'Opening Spotify.'}},
        {'user':'open youtube','plan':{'actions':[{'tool':'open_webapp','arguments':{'name':'YouTube'}}],'reply':'Opening YouTube.'}}]) + '\nOther single actions: catalog_bindings(query), run_binding(binding), workspace_new(), workspace_switch(workspace integer), scratch_toggle(), scratch_move_here(), open_webapp(name), open_app_by_name(name). For compound scratch + email requests the ONE action is run_skill with skill=scratch-and-mail. For planning the ONE action is run_skill with skill=open-planning. NEVER write a reply that says you are opening/moving/switching/toggling/launching/closing/focusing/filing something unless actions contains the matching tool call — if you cannot fulfill the request, use an empty actions list and say so plainly instead.'
    plan = json.loads(ollama_chat({'model':MODEL,'messages':[{'role':'system','content':instructions},{'role':'user','content':prompt}],'format':PLAN_SCHEMA,'stream':False,'options':{'temperature':0,'num_ctx':8192}})['content'])
    if not isinstance(plan,dict) or set(plan)!={'actions','reply'} or not isinstance(plan['actions'],list) or len(plan['actions'])>1 or not isinstance(plan['reply'],str):
        raise ValueError('Invalid JSON action plan')
    for action in plan['actions']:
        if not isinstance(action,dict) or set(action)!={'tool','arguments'}: raise ValueError('Invalid plan action')
        if action['tool'] in LLM_EXCLUDED_TOOLS:
            raise ValueError('Issue filing requires the reviewed intake flow')
        tool_argv(action['tool'],action['arguments'])
    if not plan['actions']:
        plan['reply'] = empty_plan_reply(plan['reply'])
    return plan

# Backlog/handoff tools file GitHub issues or write local files; they don't touch
# the desktop, so executing them shouldn't depend on (or close) any window.
NON_DESKTOP_TOOLS = {'report_bug', 'report_feature', 'list_backlog', 'prepare_handoff'}

def execute_plan(run_id, plan, target):
    try:
        with STATE_LOCK: RUNS[run_id].update(status='running', steps=[])
        if plan['actions'] and not all(a['tool'] in NON_DESKTOP_TOOLS for a in plan['actions']): restore_target(target)
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

def commit_plan(run_id, plan, target):
    """Given a finished plan (from json_plan, or built deterministically by the
    intake/backlog/dispatch flows), either auto-run it or park it awaiting Run/Cancel.
    Releases the busy lock on every path except the awaiting-approval one, matching
    execute_plan's own contract."""
    log(run_id, 'plan', json.dumps(plan))
    if not plan['actions']:
        reply = empty_plan_reply(plan['reply'])
        plan = {**plan, 'reply': reply}
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

def fail_run(run_id, error):
    reply = redact(str(error))
    try:
        announce(run_id, 'Stopped: ' + reply[:200])
    finally:
        with STATE_LOCK:
            RUNS[run_id].update(status='error', reply=reply)
            PENDING.pop(run_id, None)
        release_busy()

def plan_and_maybe_run(run_id, prompt, target):
    try:
        announce(run_id, 'Planning your request… Click for live console.')
        plan = json_plan(prompt)
        commit_plan(run_id, plan, target)
    except Exception as e:
        fail_run(run_id, e)

def calls_to_actions(calls):
    actions = []
    for call in calls:
        name = call['function']['name']; args = call['function'].get('arguments', {})
        if isinstance(args, str): args = json.loads(args)
        if name in LLM_EXCLUDED_TOOLS:
            raise ValueError('Issue filing requires the reviewed intake flow')
        tool_argv(name, args)  # validate before showing the plan to the user
        actions.append({'tool': name, 'arguments': args})
    return actions

def plan_tools_run(run_id, prompt, target):
    try:
        announce(run_id, 'Planning your request… Click for live console.')
        messages = [{'role':'system','content':(ROOT / 'brain/system_prompt.md').read_text()}, {'role':'user','content':prompt}]
        msg = ollama_chat({'model':MODEL,'messages':messages,'tools':TOOLS_FOR_MODEL,'stream':False,'options':{'temperature':0,'num_ctx':8192}})
        msg = {k:v for k,v in msg.items() if k in ('role','content','tool_calls')}
        messages.append(msg)
        calls = msg.get('tool_calls') or []
        if not calls:
            reply = empty_plan_reply(msg.get('content', ''))
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
        fail_run(run_id, e)

def execute_tools_plan(run_id, target, messages):
    try:
        with STATE_LOCK: RUNS[run_id].update(status='running', steps=[])
        restore_target(target)
        seen = set(); total = 0
        pending_calls = messages[-1].get('tool_calls') or []
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
        msg = ollama_chat({'model':MODEL,'messages':messages,'tools':TOOLS_FOR_MODEL,'stream':False,'options':{'temperature':0,'num_ctx':8192}})
        msg = {k:v for k,v in msg.items() if k in ('role','content','tool_calls')}
        messages.append(msg)
        pending_calls = msg.get('tool_calls') or []
        if pending_calls:
            raise ValueError('Additional model actions were not approved; submit a new request to review them')
        reply = 'Completed: ' + ', '.join(step['label'] for step in RUNS[run_id]['steps']) + '.'
        announce(run_id, reply[:250])
        with STATE_LOCK: RUNS[run_id].update(status='done', reply=reply)
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
        # awaiting_answer has no PENDING entry (nothing to execute yet), but Escape
        # during intake Q&A must still be able to abandon it cleanly.
        if not run or run.get('status') not in ('awaiting_approval', 'awaiting_answer'): return None
        run.update(status='denied', reply='Cancelled — no actions were run.')
        PENDING.pop(run_id, None)
    try:
        log(run_id, 'status', 'Denied by user; no actions were run.')
    finally:
        release_busy()
    return run

# --- Self-improve: bug/feature intake, backlog listing, handoff prep -------
# Deterministic (slash-command / keyword) intent detection and a fixed Q&A
# script, not model-driven: ADR-009 already found the local 3B model unreliable
# at freeform structured output, so drafting an issue is scripted here and the
# model never sees report_bug/report_feature (see LLM_EXCLUDED_TOOLS above).
BUG_SLASH = re.compile(r'^/report\b\s*(.*)$', re.I | re.S)
FEATURE_SLASH = re.compile(r'^/feature\b\s*(.*)$', re.I | re.S)
BUG_NL = re.compile(r"\b(you messed up|that was wrong|that'?s wrong|you broke|doesn'?t work|didn'?t work|wasn'?t right|is broken)\b", re.I)
FEATURE_NL = re.compile(r"\b(i wish it could|add a feature|feature request|it would be nice if|please add|can you add)\b", re.I)
BACKLOG_SLASH = re.compile(r'^/backlog\b', re.I)
DISPATCH_SLASH = re.compile(r'^/dispatch\s+#?(\d+)\s+to\s+(claude-code|cursor|human)\s*$', re.I)

BUG_QUESTIONS = ['What did you expect to happen?', 'What actually happened instead?', 'Any steps to reproduce, or was this a one-off?']
FEATURE_QUESTIONS = ['What should this feature do, in one or two sentences?', 'Why do you want it — what problem does it solve?', 'Any constraints or examples of how it should look/behave?']

def detect_intake(prompt):
    m = BUG_SLASH.match(prompt)
    if m: return 'bug', (m.group(1).strip() or prompt)
    m = FEATURE_SLASH.match(prompt)
    if m: return 'feature', (m.group(1).strip() or prompt)
    if BUG_NL.search(prompt): return 'bug', prompt
    if FEATURE_NL.search(prompt): return 'feature', prompt
    return None, None

def tail_log(run_id, lines=12):
    path = LOGS / 'runs' / (run_id + '.log')
    if not path.exists(): return '(no log)'
    return redact('\n'.join(path.read_text(errors='replace').splitlines()[-lines:]))[:1500] or '(empty)'

def run_info(run_id, run):
    if not run_id or not run:
        return {'jarvis_version': VERSION, 'last_run_id': '(none — this is the first run)', 'last_plan': '(none)', 'last_approval': 'n/a', 'last_log_path': '(none)', 'log_excerpt': '(none)'}
    plan = run.get('plan')
    approval = {'done': 'ran', 'error': 'ran (failed)', 'denied': 'denied', 'awaiting_approval': 'n/a (still pending)', 'awaiting_answer': 'n/a (still in intake)'}.get(run.get('status'), run.get('status', 'n/a'))
    return {
        'jarvis_version': (run.get('journal') or [{}])[0].get('jarvis_version', VERSION), 'last_run_id': run_id, 'last_plan': redact(json.dumps(plan) if plan else '(no actions)')[:600],
        'last_approval': approval, 'last_log_path': 'logs/journal/CURRENT.jsonl (or version archive); console: logs/runs/' + run_id + '.log', 'log_excerpt': json.dumps(run.get('journal', []), ensure_ascii=False)[:6000] or tail_log(run_id),
    }

def previous_run_id(current_id):
    with STATE_LOCK: keys = list(RUNS.keys())
    idx = keys.index(current_id) if current_id in keys else len(keys)
    return keys[idx - 1] if idx > 0 else None

def gather_host_facts(seed):
    text = seed.lower()
    if not any(k in text for k in ('window', 'workspace', 'scratchpad', 'hyprland', 'binding', 'keybind', 'webapp')):
        return '(not window-related; skipped)'
    try:
        clients = [{'class': c.get('class'), 'title': c.get('title'), 'workspace': (c.get('workspace') or {}).get('name')} for c in hypr('clients')[:8]]
        workspaces = [w.get('id') for w in hypr('workspaces')]
        return redact(json.dumps({'clients': clients, 'workspaces': workspaces}))[:1200]
    except Exception as e:
        return '(hyprctl snapshot failed: ' + redact(str(e))[:200] + ')'

def gather_binding_hits(seed):
    text = seed.lower()
    if not any(k in text for k in ('binding', 'keybind', 'chord', 'hotkey', 'super')):
        return '(not binding-related; skipped)'
    try:
        return redact(json.dumps(catalog(query=seed)['bindings'][:8]))[:1000]
    except Exception as e:
        return '(catalog query failed: ' + redact(str(e))[:200] + ')'

def gather_context(current_run_id, seed, source_run_id=None):
    """By default the context references the run immediately before this one (the
    manual /report flow: whatever the user just did). A-005's thumbs-down button
    passes source_run_id explicitly — the *rated* run itself, not whatever else may
    have run since — so the filed issue's LAST_PLAN/LAST_APPROVAL/log excerpt always
    describe the run the user actually flagged."""
    ref_id = source_run_id or previous_run_id(current_run_id)
    with STATE_LOCK: ref_run = dict(RUNS.get(ref_id) or {}) if ref_id else {}
    context = run_info(ref_id, ref_run)
    context['host_facts'] = gather_host_facts(seed)
    context['binding_hits'] = gather_binding_hits(seed)
    return context

def guess_difficulty(seed):
    text = seed.lower()
    if any(k in text for k in ('typo', 'wording', 'copy', 'docs', 'readme', 'documentation')): return 'S'
    if any(k in text for k in ('architecture', 'multi-agent', 'rewrite', 'redesign', 'model swap', 'control plane')): return 'L'
    return 'M'

def guess_layer(seed):
    text = seed.lower()
    if 'overlay' in text or ' ui ' in (' ' + text + ' '): return 'overlay'
    if 'skill' in text or 'recipe' in text: return 'skill'
    if any(k in text for k in ('binding', 'keybind', 'hyprland', 'window', 'workspace', 'omarchy', 'scratchpad', 'webapp')): return 'Hyprland/Omarchy'
    if 'doc' in text or 'readme' in text: return 'docs'
    return 'brain/planner'

SOLVER_FOR = {'S': 'human', 'M': 'claude-code', 'L': 'cursor-agent'}
SOLVER_WHY = {'S': 'docs/UI copy fix, not worth spinning up an agent', 'M': 'contained action/skill change, cheap on Claude Code Sonnet', 'L': 'cross-cutting/architecture, needs more budget and context'}

def answer_by_index(answers, idx, questions):
    if idx >= len(questions): return '(not answered)'
    for a in answers:
        if a['question'] == questions[idx]: return a['answer']
    return '(not answered)'

def start_intake(run_id, kind, seed, target, source_run_id=None):
    try:
        announce(run_id, 'Gathering context for your ' + kind + ' report…')
        context = gather_context(run_id, seed, source_run_id)
        questions = BUG_QUESTIONS if kind == 'bug' else FEATURE_QUESTIONS
        with STATE_LOCK:
            RUNS[run_id]['intake'] = {'kind': kind, 'seed': seed, 'context': context, 'questions': questions, 'index': 0, 'answers': [], 'target': target}
            RUNS[run_id].update(status='awaiting_answer', reply=questions[0], awaiting_since=time.monotonic())
        log(run_id, 'question', questions[0])
        announce(run_id, questions[0] + ' (reply, or type "skip" to file now)')
    except Exception as e:
        fail_run(run_id, e)

def finalize_intake(run_id):
    with STATE_LOCK:
        intake = RUNS[run_id]['intake']
        kind, seed, context, answers, target = intake['kind'], intake['seed'], intake['context'], intake['answers'], intake['target']
    questions = BUG_QUESTIONS if kind == 'bug' else FEATURE_QUESTIONS
    qa_text = '\n'.join('- Q: ' + a['question'] + '\n  A: ' + a['answer'] for a in answers) or '(no answers — filed with the seed text and auto-gathered context only)'
    difficulty = guess_difficulty(seed)
    first_line = next((l.strip() for l in seed.splitlines() if l.strip()), '').strip() or ('Bug report' if kind == 'bug' else 'Feature request')
    title = ((('Bug: ' if kind == 'bug' else 'Feature: ') + first_line))[:120]
    values = {
        'SEED': redact(seed) or '(none)', 'QA': redact(qa_text),
        'LAST_PLAN': context['last_plan'], 'LAST_APPROVAL': context['last_approval'],
        'JARVIS_VERSION': context['jarvis_version'], 'LAST_RUN_ID': context['last_run_id'], 'LAST_LOG_PATH': context['last_log_path'], 'LOG_EXCERPT': context['log_excerpt'],
        'HOST_FACTS': context['host_facts'], 'BINDING_HITS': context['binding_hits'],
        'EXPECTED': redact(answer_by_index(answers, 0, questions)), 'ACTUAL': redact(answer_by_index(answers, 1, questions)),
        'LAYER': guess_layer(seed),
        'ACCEPTANCE': 'Bug is fixed and covered by a regression test.' if kind == 'bug' else 'Feature behaves as described above and is covered by a test.',
        'MILESTONE': 'M5', 'DIFFICULTY': difficulty, 'SOLVER': SOLVER_FOR[difficulty], 'SOLVER_WHY': SOLVER_WHY[difficulty],
        'SLUG': slugify(title),
    }
    body = fill_template('ISSUE_BUG.md' if kind == 'bug' else 'ISSUE_FEATURE.md', values)
    tool = 'report_bug' if kind == 'bug' else 'report_feature'
    plan = {'actions': [{'tool': tool, 'arguments': {'title': title, 'body': body, 'difficulty': difficulty}}], 'reply': 'Draft ready — review before filing.'}
    with STATE_LOCK: RUNS[run_id]['draft'] = {'kind': kind, 'title': title, 'body': body, 'difficulty': difficulty}
    log(run_id, 'draft', json.dumps({'title': title, 'difficulty': difficulty}))
    try:
        commit_plan(run_id, plan, target)
    except Exception as e:
        fail_run(run_id, e)

def handle_answer(run_id, text):
    with STATE_LOCK:
        run = RUNS.get(run_id)
        if not run or run.get('status') != 'awaiting_answer': return None
        intake = run['intake']
        skip = text.strip().lower() == 'skip'
        if not skip:
            intake['answers'].append({'question': intake['questions'][intake['index']], 'answer': redact(text.strip())[:500]})
        intake['index'] += 1
        done = skip or intake['index'] >= len(intake['questions'])
        question = None if done else intake['questions'][intake['index']]
        if not done: run.update(reply=question, awaiting_since=time.monotonic())
    log(run_id, 'answer', 'skip' if skip else '[answer recorded]')
    if done:
        finalize_intake(run_id)
    else:
        log(run_id, 'question', question)
        announce(run_id, question + ' (reply, or type "skip" to file now)')
    with STATE_LOCK: return dict(RUNS[run_id])

# --- A-005: post-run feedback (+/neutral/-) ---------------------------------
# Good/neutral are just a journal record (cheap, no questions per the assignment).
# Neutral additionally gets a local-only "review later" line — never a GitHub issue,
# so a stream of "meh" clicks can't spam the tracker (see ADR-020). Bad reuses the
# existing deterministic bug-intake flow (start_intake) with the *rated* run's own
# prompt as the seed and its own context pre-attached via source_run_id, instead of
# guessing from freeform chat text like the manual /report path does.
FEEDBACK_RATINGS = ('good', 'neutral', 'bad')

def record_needs_review(run_id, run):
    record = {'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'jarvis_version': VERSION,
              'run_id': run_id, 'prompt': redact(run.get('prompt', ''))[:500], 'reply': redact(run.get('reply', ''))[:500]}
    Journal(LOGS, VERSION, REVISION).append(LOGS / 'feedback' / 'needs-review.jsonl', record)

def handle_feedback(run_id, rating):
    if rating not in FEEDBACK_RATINGS:
        raise ValueError('Rating must be good, neutral or bad')
    with STATE_LOCK:
        run = RUNS.get(run_id)
        if not run or run.get('status') not in ('done', 'error'):
            return None
        if run.get('feedback'):
            raise ValueError('Feedback already recorded for this run')
        run['feedback'] = rating
        seed, snapshot = run.get('prompt', ''), dict(run)
    journal_event(run_id, 'feedback', feedback={'rating': rating})
    if rating == 'neutral':
        record_needs_review(run_id, snapshot)
    if rating != 'bad':
        with STATE_LOCK: return dict(RUNS[run_id])
    active = hypr('activewindow'); target = active.get('address')
    if is_overlay(active):
        target = json.loads((LOGS / 'overlay-target.json').read_text()).get('address')
    if not BUSY.acquire(blocking=False):
        raise RuntimeError('A desktop run is already active')
    new_run_id = str(uuid.uuid4())
    (LOGS / 'runs' / (new_run_id + '.log')).touch(mode=0o600)
    global BUSY_RUN_ID
    with STATE_LOCK:
        if len(RUNS) > 200: RUNS.pop(next(iter(RUNS)))
        RUNS[new_run_id] = {'run_id': new_run_id, 'status': 'planning', 'reply': 'Thinking…', 'plan': None, 'steps': [], 'prompt': seed}
        BUSY_RUN_ID = new_run_id
    journal_event(new_run_id, 'prompt', prompt=seed)
    threading.Thread(target=start_intake, args=(new_run_id, 'bug', seed, target, run_id), daemon=True).start()
    return {'run_id': new_run_id, 'status': 'planning', 'reply': 'Thinking…'}

def start_fixed_plan(run_id, plan, target):
    try:
        announce(run_id, 'Preparing…')
        commit_plan(run_id, plan, target)
    except Exception as e:
        fail_run(run_id, e)

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
        feedback_id = self.run_id_from('/feedback')
        if feedback_id:
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 256: raise ValueError('Invalid request size')
                if self.headers.get('Content-Type') != 'application/json': raise ValueError('Expected application/json')
                rating = json.loads(self.rfile.read(length)).get('rating')
            except (ValueError, AttributeError) as e: return self.reply(400, {'error': str(e)})
            try:
                result = handle_feedback(feedback_id, rating)
            except ValueError as e: return self.reply(400, {'error': str(e)})
            except RuntimeError as e: return self.reply(409, {'error': str(e)})
            if result is None: return self.reply(409, {'error': 'Run is not in a terminal state'})
            return self.reply(202 if 'run_id' in result and result['run_id'] != feedback_id else 200, result)
        answer_id = self.run_id_from('/answer')
        if answer_id:
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 2048: raise ValueError('Invalid request size')
                if self.headers.get('Content-Type') != 'application/json': raise ValueError('Expected application/json')
                body = json.loads(self.rfile.read(length)); text = body.get('text')
                if not isinstance(text,str) or not text.strip() or len(text)>600: raise ValueError('Answer must be 1–600 characters')
            except (ValueError,AttributeError) as e: return self.reply(400, {'error':str(e)})
            expire_stale()
            run = handle_answer(answer_id, text)
            return self.reply(202, run) if run else self.reply(409, {'error':'Run is not awaiting an answer'})
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
                RUNS[run_id] = {'run_id':run_id,'status':'planning','reply':'Thinking…','plan':None,'steps':[], 'prompt':prompt}
                BUSY_RUN_ID = run_id
            journal_event(run_id, 'prompt', prompt=prompt)
            prompt = prompt.strip()
            kind, seed = detect_intake(prompt)
            dispatch_match = DISPATCH_SLASH.match(prompt)
            if kind:
                thread_target, thread_args = start_intake, (run_id, kind, seed, target)
            elif BACKLOG_SLASH.match(prompt):
                thread_target, thread_args = start_fixed_plan, (run_id, {'actions':[{'tool':'list_backlog','arguments':{}}],'reply':'Listing open backlog items.'}, target)
            elif dispatch_match:
                issue, agent = int(dispatch_match[1]), dispatch_match[2].lower()
                thread_target, thread_args = start_fixed_plan, (run_id, {'actions':[{'tool':'prepare_handoff','arguments':{'issue':issue,'agent':agent}}],'reply':'Preparing a handoff prompt for issue #'+str(issue)+'.'}, target)
            else:
                thread_target, thread_args = (plan_tools_run if os.environ.get('JARVIS_PLANNER') == 'tools' else plan_and_maybe_run), (run_id, prompt, target)
            threading.Thread(target=thread_target,args=thread_args,daemon=True).start()
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
