#!/usr/bin/env python3
"""A-031: repeated fresh-context, planner-only trials for the critical behaviors in
docs/evals/stochastic/cases.json.

Each trial runs in its own short-lived child process (`--worker`) that installs tripwires
over every execution, desktop and approval path in brain/server.py *before* calling one
planner surface, points LOGS at a directory it then proves stayed empty, and allows exactly
one outbound URL — the local Ollama daemon. So a trial can only ever observe a proposed
plan: nothing is approved, nothing is executed, and no state survives into the next trial.

  scripts/stochastic-evals.py --validate                 # registry + baseline check, no model
  scripts/stochastic-evals.py --surface router           # deterministic routers, no model
  scripts/stochastic-evals.py --trials 3                 # planner trials via local Ollama
  scripts/stochastic-evals.py --backend stub --stub F    # scripted planner (shape demos/tests)

Results are reported as successes/trials per case plus per-case consistency — never a single
promotional number, and never pass@k (see docs/evals/stochastic/README.md). Raw model text is
private: it is only written when you pass --private-out, and never to the repo, the summary or
the evidence bundle. The exit code reflects *runner* health (validation, tripwires, model
errors); how many trials passed only affects it under --gate, which in turn refuses to run
until a human has approved a baseline.
"""
import argparse
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
sys.path.insert(0, str(ROOT / 'brain'))
import evidence  # noqa: E402
import server  # noqa: E402  (safe to import: no socket bind outside __main__)

CASES = ROOT / 'docs/evals/stochastic/cases.json'
BASELINE = ROOT / 'docs/evals/stochastic/baseline.json'
SUMMARY_SCHEMA_VERSION = 1
DEFAULT_TRIALS = 3
DEVELOPMENT_TRIAL_BAND = 5   # the brief's small-N band; more is allowed, loudly
MAX_TRIALS = 20              # hard cost bound, not a statistical opinion
DEFAULT_TIMEOUT = 180        # matches brain/server.py's own Ollama request timeout
OLLAMA_TAGS = 'http://127.0.0.1:11434/api/tags'
OLLAMA_PREFIX = 'http://127.0.0.1:11434/'
ROUTER_PATTERN_NAMES = ('APP_CORRECTION_RE', 'BUG_SLASH', 'FEATURE_SLASH', 'BUG_NL', 'FEATURE_NL', 'BACKLOG_SLASH', 'DISPATCH_SLASH')

ID_RE = re.compile(r'^SEVAL-\d{3,}$')
REQUIRED = ('id', 'version', 'kind', 'title', 'surface', 'owner', 'protection_class', 'prompt', 'expect')
OPTIONAL = ('notes',)
ENUMS = {
    'kind': {'capability', 'regression'},
    'surface': {'planner-json', 'router'},
    'owner': {'control-plane'},
    'protection_class': {'protected-regression', 'candidate-capability'},
}
PLANNER_EXPECT = {'actions', 'arguments', 'forbidden_tools', 'planner_rejection', 'reply'}
ROUTER_EXPECT = {'route', 'detail'}
ROUTES = {'json_plan', 'tools_run', 'correction', 'intake', 'fixed_plan'}
DETAIL_KEYS = {'correction': {'query'}, 'intake': {'kind'}, 'fixed_plan': {'tool'}, 'json_plan': set(), 'tools_run': set()}


class ExecutionAttempted(RuntimeError):
    """A planner-only trial reached an execution, desktop or approval surface."""


# --- registry validation (no model, no trials) -----------------------------------------

def load_json(path):
    return json.loads(Path(path).read_text())


def validate(cases, baseline, schemas=None, excluded=None):
    """Every problem found in the case registry and the baseline, as strings. Tool and
    argument names are checked against the schemas that actually ship, so a case cannot
    quietly grade a tool the planner has no way to emit."""
    schemas = server.SCHEMAS if schemas is None else schemas
    excluded = server.LLM_EXCLUDED_TOOLS if excluded is None else excluded
    problems = []
    if not isinstance(cases, list):
        return ['cases.json: "cases" must be a list']
    seen = set()
    for index, case in enumerate(cases):
        label = case.get('id', '#' + str(index)) if isinstance(case, dict) else '#' + str(index)
        if not isinstance(case, dict):
            problems.append(label + ': case must be an object')
            continue
        missing = [key for key in REQUIRED if key not in case]
        if missing:
            problems.append(label + ': missing required field(s) ' + str(missing))
            continue
        extra = set(case) - set(REQUIRED) - set(OPTIONAL)
        if extra:
            problems.append(label + ': unknown field(s) ' + str(sorted(extra)))
        if not ID_RE.match(case['id']):
            problems.append(label + ': id must match SEVAL-NNN')
        if case['id'] in seen:
            problems.append('duplicate case id ' + case['id'])
        seen.add(case['id'])
        if not isinstance(case['version'], int) or case['version'] < 1:
            problems.append(case['id'] + ': version must be an integer >= 1')
        for field, allowed in ENUMS.items():
            if case.get(field) not in allowed:
                problems.append(case['id'] + ': ' + field + '=' + repr(case.get(field)) + ' not in ' + str(sorted(allowed)))
        if not isinstance(case['prompt'], str) or not case['prompt'].strip() or len(case['prompt']) > 200:
            problems.append(case['id'] + ': prompt must be a non-empty string of at most 200 characters')
        expect = case.get('expect')
        if not isinstance(expect, dict) or not expect:
            problems.append(case['id'] + ': expect must be a non-empty object')
            continue
        if case.get('surface') == 'router':
            problems += validate_router_expect(case['id'], expect)
        elif case.get('surface') == 'planner-json':
            problems += validate_planner_expect(case['id'], expect, schemas, excluded)
    problems += validate_baseline(baseline, cases if isinstance(cases, list) else [])
    return problems


def validate_planner_expect(cid, expect, schemas, excluded):
    problems = []
    unknown = set(expect) - PLANNER_EXPECT
    if unknown:
        problems.append(cid + ': planner-json expect has unknown key(s) ' + str(sorted(unknown)))
    wanted = expect.get('actions')
    if wanted is not None and wanted != 'none' and not (isinstance(wanted, list) and wanted and all(isinstance(t, str) for t in wanted)):
        problems.append(cid + ': expect.actions must be "none" or a non-empty list of tool names')
        wanted = None
    for tool in (wanted if isinstance(wanted, list) else []):
        if tool not in schemas:
            problems.append(cid + ': expect.actions names unknown tool ' + repr(tool))
        elif tool in excluded:
            problems.append(cid + ': ' + tool + ' is planner-excluded, so no plan may legitimately contain it')
    for tool in expect.get('forbidden_tools') or []:
        if tool not in schemas:
            problems.append(cid + ': forbidden_tools names unknown tool ' + repr(tool))
    arguments = expect.get('arguments') or {}
    if arguments and not (isinstance(wanted, list) and len(wanted) == 1):
        problems.append(cid + ': expect.arguments requires expect.actions to name exactly one tool')
    elif arguments:
        properties = schemas[wanted[0]]['properties'] if wanted[0] in schemas else {}
        for name, pattern in arguments.items():
            if name not in properties:
                problems.append(cid + ': ' + wanted[0] + ' has no argument ' + repr(name))
            try:
                re.compile(pattern)
            except re.error as error:
                problems.append(cid + ': argument ' + name + ' pattern does not compile (' + str(error) + ')')
    if expect.get('planner_rejection') not in (None, 'pass', 'fail'):
        problems.append(cid + ': planner_rejection must be "pass" or "fail"')
    if expect.get('reply') not in (None, 'must-not-claim-action', 'any'):
        problems.append(cid + ': reply must be "must-not-claim-action" or "any"')
    return problems


def validate_router_expect(cid, expect):
    problems = []
    unknown = set(expect) - ROUTER_EXPECT
    if unknown:
        problems.append(cid + ': router expect has unknown key(s) ' + str(sorted(unknown)))
    route = expect.get('route')
    if route not in ROUTES:
        problems.append(cid + ': expect.route=' + repr(route) + ' not in ' + str(sorted(ROUTES)))
        return problems
    detail = expect.get('detail') or {}
    if not isinstance(detail, dict):
        problems.append(cid + ': expect.detail must be an object')
        return problems
    unknown_detail = set(detail) - DETAIL_KEYS[route]
    if unknown_detail:
        problems.append(cid + ': ' + route + ' has no routing detail ' + str(sorted(unknown_detail)))
    return problems


def validate_baseline(baseline, cases):
    """A baseline may only gate promotion once a human has approved a specific summary and
    written a tolerance for every planner-json case."""
    problems = []
    if not isinstance(baseline, dict):
        return ['baseline.json: must be an object']
    status = baseline.get('status')
    if status not in ('unapproved', 'approved'):
        problems.append('baseline.json: status must be "unapproved" or "approved"')
    tolerance = baseline.get('tolerance')
    if not isinstance(tolerance, dict):
        return problems + ['baseline.json: tolerance must be an object']
    planner_ids = {c['id'] for c in cases if isinstance(c, dict) and c.get('surface') == 'planner-json' and 'id' in c}
    for cid, rule in tolerance.items():
        if cid not in planner_ids:
            problems.append('baseline.json: tolerance names unknown planner case ' + repr(cid))
            continue
        if not isinstance(rule, dict) or not isinstance(rule.get('min_successes'), int) or not isinstance(rule.get('of_trials'), int):
            problems.append('baseline.json: ' + cid + ' tolerance needs integer min_successes and of_trials')
        elif not 0 <= rule['min_successes'] <= rule['of_trials'] or rule['of_trials'] < 1:
            problems.append('baseline.json: ' + cid + ' tolerance is out of range')
    if status == 'approved':
        for field in ('approved_by', 'approved_at', 'approved_summary', 'trials'):
            if not baseline.get(field):
                problems.append('baseline.json: an approved baseline needs ' + field)
        for cid in sorted(planner_ids - set(tolerance)):
            problems.append('baseline.json: an approved baseline needs a tolerance for ' + cid)
    return problems


# --- deterministic oracles --------------------------------------------------------------

def grade_plan(case, plan, error=None):
    """One planner trial, graded in code. No model judges another model here, and no
    predicate is read as executable text out of the registry."""
    expect = case['expect']
    if error is not None:
        outcome = 'pass' if expect.get('planner_rejection', 'fail') == 'pass' else 'fail'
        return outcome, 'planner refused the model output: ' + str(error)[:120]
    actions = plan.get('actions') or []
    tools = [action.get('tool') for action in actions]
    forbidden = [tool for tool in tools if tool in (expect.get('forbidden_tools') or [])]
    if forbidden:
        return 'fail', 'planned forbidden tool(s) ' + ','.join(forbidden)
    wanted = expect.get('actions')
    if wanted == 'none' and actions:
        return 'fail', 'expected no action, planned ' + ','.join(tools)
    if isinstance(wanted, list):
        if len(actions) != 1:
            return 'fail', 'expected exactly one of ' + ','.join(wanted) + ', planned ' + (','.join(tools) or 'nothing')
        if tools[0] not in wanted:
            return 'fail', 'planned ' + str(tools[0]) + ', expected one of ' + ','.join(wanted)
        for name, pattern in (expect.get('arguments') or {}).items():
            value = (actions[0].get('arguments') or {}).get(name)
            if value is None:
                return 'fail', 'planned ' + tools[0] + ' without argument ' + name
            if not re.search(pattern, str(value), re.I):
                return 'fail', 'argument ' + name + ' did not match /' + pattern + '/'
    rule = expect.get('reply') or ('must-not-claim-action' if wanted == 'none' else 'any')
    if rule == 'must-not-claim-action' and server.FALSE_ACTION_CLAIM_RE.match((plan.get('reply') or '').strip()):
        return 'fail', 'reply claims an action happened'
    return 'pass', 'ok'


def route_detail(route):
    detail = {}
    if 'correction' in route:
        detail['query'] = (route['correction'] or {}).get('query')
    if route.get('kind'):
        detail['kind'] = route['kind']
    plan = route.get('plan')
    if plan:
        actions = plan.get('actions') or []
        detail['tool'] = actions[0]['tool'] if actions else None
    return detail


def grade_route(case, route, error=None):
    if error is not None:
        return 'error', 'router raised: ' + str(error)[:120]
    expect = case['expect']
    if route.get('mode') != expect['route']:
        return 'fail', 'routed to ' + str(route.get('mode')) + ', expected ' + expect['route']
    observed = route_detail(route)
    for key, want in (expect.get('detail') or {}).items():
        got = observed.get(key, '(absent)')
        if got != want:
            return 'fail', 'routing detail ' + key + '=' + repr(got) + ', expected ' + repr(want)
    return 'pass', 'ok'


def plan_digest(plan):
    return evidence.sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))


# --- the trial sandbox (child process) --------------------------------------------------

def tripwire(name, tripped):
    def guard(*args, **kwargs):
        tripped.append({'surface': name, 'first_argument': str(args[0])[:120] if args else ''})
        raise ExecutionAttempted(name + ' was reached during a planner-only trial')
    return guard


def local_only(original, tripped, seen):
    def guarded(request, *args, **kwargs):
        url = str(getattr(request, 'full_url', request))
        if not url.startswith(OLLAMA_PREFIX):
            tripped.append({'surface': 'urlopen', 'first_argument': url[:120]})
            raise ExecutionAttempted('planner trial attempted a non-local request')
        seen.append(url)
        return original(request, *args, **kwargs)
    return guarded


def install_tripwires(tripped, logs, model_calls):
    """Every path that could approve, execute, touch the desktop or write evidence is
    replaced with something that records the attempt and raises. This is the proof that a
    trial is planner-only: it does not rely on json_plan happening not to call them."""
    import core
    for module, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                          (os, ('system', 'posix_spawn', 'execv', 'execvp'))):
        for name in names:
            if hasattr(module, name):
                setattr(module, name, tripwire(module.__name__ + '.' + name, tripped))
    for name in ('commit_plan', 'execute_plan', 'execute_tools_plan', 'plan_and_maybe_run', 'plan_tools_run',
                 'run_pending', 'handle_approve', 'handle_deny', 'restore_target', 'dispatch', 'notify',
                 'announce', 'journal_event', 'start_intake', 'start_correction_plan', 'start_fixed_plan'):
        setattr(server, name, tripwire('server.' + name, tripped))
    for name in ('dispatch', 'hypr', 'notify', 'open_app', 'run_skill', 'correct_open'):
        if hasattr(core, name):
            setattr(core, name, tripwire('core.' + name, tripped))
    server.urlopen = local_only(server.urlopen, tripped, model_calls)
    server.LOGS = logs
    server.CONFIG['approval_mode'] = 'always'


def state_notes(logs):
    notes = []
    if server.RUNS:
        notes.append('RUNS left populated')
    if server.PENDING:
        notes.append('PENDING left populated')
    if server.BUSY.locked():
        notes.append('BUSY lock still held')
    if server.BUSY_RUN_ID:
        notes.append('BUSY_RUN_ID left set')
    if Path(logs).exists():
        notes.append('trial wrote under LOGS')
    return notes


def stub_chat(job, raw):
    replies = (job.get('stub') or {}).get(job['case']['prompt'])
    if not replies:
        raise RuntimeError('stub backend has no scripted reply for this prompt')
    reply = replies[job['index'] % len(replies)]

    def chat(payload):
        content = reply if isinstance(reply, str) else json.dumps(reply)
        raw['reply'] = content
        return {'content': content}
    return chat


def worker(job):
    """One trial in a throwaway process. Prints exactly one JSON result line; raw model
    text is included only when the job asked for it, and even then the parent writes it to
    a private file rather than the summary."""
    tripped, model_calls, raw = [], [], {}
    with tempfile.TemporaryDirectory() as temp:
        logs = Path(temp) / 'logs'
        install_tripwires(tripped, logs, model_calls)
        rewrites = []
        original_empty_reply = server.empty_plan_reply

        def watched_empty_reply(reply):
            result = original_empty_reply(reply)
            rewrites.append(result != (reply or '').strip()[:1000])
            return result
        server.empty_plan_reply = watched_empty_reply
        if job.get('backend') == 'stub':
            server.ollama_chat = stub_chat(job, raw)
        case = job['case']
        error = None
        try:
            if case['surface'] == 'router':
                observed = server.route_prompt(case['prompt'])
                outcome, reason = grade_route(case, observed)
                digest, shape = plan_digest(observed), {'route': observed.get('mode'), 'detail': route_detail(observed)}
            else:
                plan = server.json_plan(case['prompt'])
                outcome, reason = grade_plan(case, plan)
                digest = plan_digest(plan)
                shape = {'tools': [a.get('tool') for a in plan.get('actions') or []], 'reply_chars': len(plan.get('reply') or '')}
                raw['plan'] = plan
        except ExecutionAttempted as trip:
            outcome, reason, digest, shape = 'error', 'tripwire: ' + str(trip)[:160], None, {}
        except ValueError as rejected:
            error = type(rejected).__name__ + ': ' + str(rejected)
            outcome, reason = grade_plan(case, {}, error=error) if case['surface'] != 'router' else grade_route(case, {}, error=error)
            digest, shape = 'rejected:' + evidence.sha256_hex(error)[:16], {'rejected': True}
        except Exception as failure:   # unreachable daemon, timeout, anything else
            outcome, reason, digest, shape = 'error', type(failure).__name__ + ': ' + str(failure)[:160], None, {}
        result = {
            'index': job['index'],
            'outcome': outcome,
            'reason': server.redact(reason)[:200],
            'digest': digest,
            'shape': shape,
            'honesty_guard_rewrote_reply': any(rewrites),
            'tripwires': tripped,
            'model_calls': len(model_calls),
            'state_notes': state_notes(logs),
        }
    if job.get('include_raw'):
        result['private'] = raw
    return result


# --- parent: trials, aggregation, evidence ----------------------------------------------

def run_trial(case, index, options):
    job = {'case': case, 'index': index, 'backend': options.backend, 'include_raw': bool(options.private_out)}
    if options.backend == 'stub':
        job['stub'] = options.stub_data
    try:
        done = subprocess.run([sys.executable, str(SCRIPT), '--worker'], input=json.dumps(job),
                              capture_output=True, text=True, timeout=options.timeout)
    except subprocess.TimeoutExpired:
        return {'index': index, 'outcome': 'error', 'reason': 'trial timed out after ' + str(options.timeout) + 's',
                'digest': None, 'shape': {}, 'honesty_guard_rewrote_reply': False, 'tripwires': [], 'model_calls': 0, 'state_notes': []}
    line = (done.stdout or '').strip().splitlines()[-1] if (done.stdout or '').strip() else ''
    try:
        return json.loads(line)
    except ValueError:
        detail = (done.stderr or '').strip().splitlines()[-1:] or ['no output']
        return {'index': index, 'outcome': 'error', 'reason': 'trial process failed: ' + detail[0][:160],
                'digest': None, 'shape': {}, 'honesty_guard_rewrote_reply': False, 'tripwires': [], 'model_calls': 0, 'state_notes': []}


def run_case(case, options):
    """Independent trials of one case. Each is a fresh process, so nothing — not a cached
    plan, not a lock, not a log file — carries from one trial to the next."""
    trials = 1 if case['surface'] == 'router' else options.trials
    results, private = [], []
    for index in range(trials):
        result = run_trial(case, index, options)
        private.append(result.pop('private', None))
        results.append(result)
        if options.progress:
            print('  ' + case['id'] + ' trial ' + str(index + 1) + '/' + str(trials) + ': ' + result['outcome'], file=sys.stderr)
    outcomes = [r['outcome'] for r in results]
    digests = [r['digest'] for r in results]
    action_shapes = [json.dumps(r['shape'].get('tools', r['shape'].get('route')), sort_keys=True) for r in results]
    summary = {
        'id': case['id'],
        'version': case['version'],
        'surface': case['surface'],
        'kind': case['kind'],
        'protection_class': case['protection_class'],
        'title': case['title'],
        'trials': trials,
        'successes': outcomes.count('pass'),
        'failures': outcomes.count('fail'),
        'errors': outcomes.count('error'),
        'outcomes': outcomes,
        'reasons': sorted({r['reason'] for r in results if r['outcome'] != 'pass'}),
        'consistent_actions': len(set(action_shapes)) == 1,
        'consistent_output': len(set(digests)) == 1,
        'output_digests': [d[:16] if isinstance(d, str) else None for d in digests],
        'honesty_guard_rewrites': sum(1 for r in results if r['honesty_guard_rewrote_reply']),
        'tripwires': [t for r in results for t in r['tripwires']],
        'state_notes': sorted({note for r in results for note in r['state_notes']}),
    }
    return summary, results, private


def ollama_reachable():
    try:
        with urlopen(OLLAMA_TAGS, timeout=2):
            return True
    except Exception:
        return False


def host_facts(backend):
    """Bounded, non-secret facts that can change a planner result. Deliberately not the
    Hyprland instance signature or anything else identifying — only whether a desktop
    session and the model daemon were present at all."""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
        'python': platform.python_version(),
        'ollama': 'reachable' if (backend == 'ollama' and ollama_reachable()) else ('stub' if backend == 'stub' else 'unreachable'),
        'hyprland_session': bool(os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')),
    }


def router_signature():
    return {name: getattr(server, name).pattern for name in ROUTER_PATTERN_NAMES}


def case_fingerprint(case, backend, model_digest):
    system_prompt = ROOT / 'brain/system_prompt.md'
    if case['surface'] == 'router':
        return evidence.fingerprint(
            jarvis_version=server.VERSION, git_revision=server.REVISION, planner_mode='router',
            model='none (deterministic router)', model_digest=None, system_prompt_hash=None,
            schema_hash=evidence.sha256_hex(json.dumps(router_signature(), sort_keys=True)),
            options={}, case_id=case['id'], case_version=case['version'])
    return evidence.fingerprint(
        jarvis_version=server.VERSION, git_revision=server.REVISION, planner_mode='json_plan',
        model='stub' if backend == 'stub' else server.MODEL,
        model_digest=None if backend == 'stub' else model_digest,
        system_prompt_hash=evidence.sha256_hex(system_prompt.read_text()) if system_prompt.exists() else None,
        schema_hash=evidence.sha256_hex(json.dumps(server.PLAN_SCHEMA, sort_keys=True)),
        options={'temperature': 0, 'num_ctx': 8192}, case_id=case['id'], case_version=case['version'])


def planner_source_hash():
    """The literal planner, not just the system prompt: json_plan's instruction block and
    validation live in brain/server.py's source, so pinning system_prompt.md alone would
    miss a changed example or rule."""
    import inspect
    return evidence.sha256_hex(inspect.getsource(server.json_plan))


def write_case_evidence(case, result, fingerprint, host, dest):
    counts = {'total': result['trials'], 'passed': result['successes'], 'failed': result['failures'], 'errored': result['errors']}
    trials = [{'index': i, 'outcome': result['outcomes'][i], 'output_digest': result['output_digests'][i]} for i in range(result['trials'])]
    envelope = evidence.build_eval_envelope(fingerprint, counts, trials, source={
        'host': host,
        'case_prompt_hash': evidence.sha256_hex(case['prompt']),
        'planner_source_hash': None if case['surface'] == 'router' else planner_source_hash(),
        'consistent_actions': result['consistent_actions'],
        'consistent_output': result['consistent_output'],
    })
    path, created = evidence.write_bundle(dest, envelope)
    return evidence.content_id(envelope), path, created


def aggregate(results):
    planner = [r for r in results if r['surface'] == 'planner-json']
    return {
        'cases': len(results),
        'planner_cases': len(planner),
        'router_cases': len(results) - len(planner),
        'trials_total': sum(r['trials'] for r in results),
        'successes_total': sum(r['successes'] for r in results),
        'unanimous_pass': sum(1 for r in results if r['successes'] == r['trials']),
        'mixed': sum(1 for r in results if 0 < r['successes'] < r['trials']),
        'unanimous_fail': sum(1 for r in results if r['successes'] == 0 and r['failures'] == r['trials']),
        'cases_with_errors': sum(1 for r in results if r['errors']),
        'inconsistent_output_cases': sum(1 for r in results if not r['consistent_output']),
        'honesty_guard_rewrites': sum(r['honesty_guard_rewrites'] for r in results),
        'tripwires': sum(len(r['tripwires']) for r in results),
    }


RELIABILITY_NOTE = (
    'successes/trials per case estimates first-answer reliability: every trial is an independent '
    'first answer from a fresh context, and the number reported is the fraction that were correct. '
    'It is deliberately not pass@k — the product only ever shows the user one plan, so a behavior '
    'that needs a retry to be right is not a behavior that works. At this N no confidence interval, '
    'significance claim or promotional pass rate is supportable; the useful signals are per-case '
    'unanimity and consistency, and any case that changes between revisions.'
)


def build_summary(results, options, baseline, host, gate):
    return {
        'schema_version': SUMMARY_SCHEMA_VERSION,
        'assignment': 'A-031',
        'backend': options.backend,
        'trials_per_planner_case': options.trials,
        'jarvis_version': server.VERSION,
        'git_revision': server.REVISION,
        'model': 'stub' if options.backend == 'stub' else server.MODEL,
        'model_digest': options.model_digest,
        'system_prompt_hash': evidence.sha256_hex((ROOT / 'brain/system_prompt.md').read_text()),
        'plan_schema_hash': evidence.sha256_hex(json.dumps(server.PLAN_SCHEMA, sort_keys=True)),
        'planner_source_hash': planner_source_hash(),
        'router_signature_hash': evidence.sha256_hex(json.dumps(router_signature(), sort_keys=True)),
        'host': host,
        'baseline': {'status': baseline.get('status'), 'gated': gate, 'approved_summary': baseline.get('approved_summary')},
        'raw_model_output': 'written to a private directory' if options.private_out else 'not recorded',
        'aggregate': aggregate(results),
        'reliability_note': RELIABILITY_NOTE,
        'cases': results,
    }


def gate_report(results, baseline):
    """Only reachable with an approved baseline: which cases fell below the tolerance a
    human accepted, scaled to the trials actually run."""
    below = []
    for result in results:
        rule = (baseline.get('tolerance') or {}).get(result['id'])
        if not rule or result['surface'] != 'planner-json':
            continue
        required = rule['min_successes'] / rule['of_trials'] * result['trials']
        if result['successes'] < required:
            below.append(result['id'] + ': ' + str(result['successes']) + '/' + str(result['trials']) +
                         ' below tolerance ' + str(rule['min_successes']) + '/' + str(rule['of_trials']))
    return below


def print_report(summary):
    print('Stochastic planner evals (A-031) — backend=' + summary['backend'] +
          ', trials/planner case=' + str(summary['trials_per_planner_case']) +
          ', model=' + str(summary['model']) + ', revision=' + summary['git_revision'])
    for surface, label in (('planner-json', 'Planner (stochastic)'), ('router', 'Deterministic routers (reported separately, never averaged in)')):
        rows = [r for r in summary['cases'] if r['surface'] == surface]
        if not rows:
            continue
        print('\n' + label)
        for row in rows:
            flags = [] if row['consistent_output'] else ['output varies']
            if not row['consistent_actions']:
                flags.append('action varies')
            if row['honesty_guard_rewrites']:
                flags.append(str(row['honesty_guard_rewrites']) + 'x honesty guard fired')
            if row['tripwires']:
                flags.append('TRIPWIRE')
            if row['state_notes']:
                flags.append('state: ' + '; '.join(row['state_notes']))
            print('  ' + row['id'] + '  ' + str(row['successes']) + '/' + str(row['trials']) +
                  '  ' + row['protection_class'] + '  ' + row['title'] +
                  ('  [' + ', '.join(flags) + ']' if flags else ''))
            for reason in row['reasons']:
                print('      - ' + reason)
    counts = summary['aggregate']
    print('\nAggregate: ' + str(counts['cases']) + ' cases, ' + str(counts['trials_total']) + ' trials — ' +
          str(counts['unanimous_pass']) + ' unanimous pass, ' + str(counts['mixed']) + ' mixed, ' +
          str(counts['unanimous_fail']) + ' unanimous fail, ' + str(counts['cases_with_errors']) + ' with errors')
    print(RELIABILITY_NOTE)
    print('Baseline: ' + str(summary['baseline']['status']) +
          (' — gating' if summary['baseline']['gated'] else ' — informational only, nothing is gated'))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--validate', action='store_true', help='check the registry and baseline only; no trials, no model')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--surface', choices=('all', 'planner-json', 'router'), default='all')
    parser.add_argument('--case', action='append', default=[], help='run only these SEVAL ids (repeatable)')
    parser.add_argument('--trials', type=int, default=DEFAULT_TRIALS, help='trials per planner case (default %(default)s; router cases are deterministic and always run once)')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='seconds per trial')
    parser.add_argument('--backend', choices=('ollama', 'stub'), default='ollama')
    parser.add_argument('--stub', help='JSON file of {prompt: [reply, ...]} for --backend stub')
    parser.add_argument('--cases', default=str(CASES))
    parser.add_argument('--baseline', default=str(BASELINE))
    parser.add_argument('--summary-out', help='write the redacted, content-hashed summary here')
    parser.add_argument('--evidence-out', help='write A-038 eval bundles here instead of XDG state')
    parser.add_argument('--no-evidence', action='store_true', help='skip evidence bundles (validation/debugging runs)')
    parser.add_argument('--private-out', help='also write raw model output here (private, never the repo)')
    parser.add_argument('--gate', action='store_true', help='fail on results below an approved baseline tolerance')
    parser.add_argument('--quiet', action='store_true', help='no per-trial progress on stderr')
    return prepare(parser.parse_args(argv))


def prepare(options):
    """Derived options every caller needs, whether it came from a command line or a test."""
    options.stub_data = load_json(options.stub) if (options.backend == 'stub' and options.stub) else None
    options.progress = not options.quiet
    options.model_digest = None
    return options


def main(argv=None):
    options = parse_args(argv)
    if options.worker:
        print(json.dumps(worker(json.load(sys.stdin))))
        return 0
    cases = load_json(options.cases).get('cases')
    baseline = load_json(options.baseline)
    problems = validate(cases, baseline)
    for problem in problems:
        print('PROBLEM: ' + problem, file=sys.stderr)
    if problems:
        print(str(len(problems)) + ' problem(s) in the stochastic eval registry.', file=sys.stderr)
        return 1
    if options.validate:
        print(str(len(cases)) + ' stochastic case(s) valid; baseline status=' + str(baseline.get('status')) + '.')
        return 0
    if not 1 <= options.trials <= MAX_TRIALS:
        print('--trials must be between 1 and ' + str(MAX_TRIALS) + '.', file=sys.stderr)
        return 1
    if options.trials > DEVELOPMENT_TRIAL_BAND:
        print('Note: ' + str(options.trials) + ' trials exceeds the development band of ' + str(DEVELOPMENT_TRIAL_BAND) +
              '; a larger N here still does not make a small-sample result significant.', file=sys.stderr)
    if options.gate and baseline.get('status') != 'approved':
        print('Refusing to gate: docs/evals/stochastic/baseline.json is not human-approved.', file=sys.stderr)
        return 1
    selected = [c for c in cases if (options.surface in ('all', c['surface'])) and (not options.case or c['id'] in options.case)]
    if not selected:
        print('No case matched the selection.', file=sys.stderr)
        return 1
    if options.backend == 'stub' and not options.stub_data:
        print('--backend stub needs --stub FILE.', file=sys.stderr)
        return 1
    needs_model = any(c['surface'] == 'planner-json' for c in selected)
    if needs_model and options.backend == 'ollama' and not ollama_reachable():
        print('Ollama is unreachable at 127.0.0.1:11434, so planner trials cannot run. Use --surface router '
              'for the deterministic routers, or --backend stub for a scripted planner.', file=sys.stderr)
        return 1
    options.model_digest = evidence.ollama_model_digest(server.MODEL) if (needs_model and options.backend == 'ollama') else None
    host = host_facts(options.backend)

    results, raw_by_case = [], {}
    for case in selected:
        result, _trials, private = run_case(case, options)
        results.append(result)
        raw_by_case[case['id']] = private
    if not options.no_evidence:
        dest = Path(options.evidence_out).expanduser() if options.evidence_out else evidence.EVIDENCE_DIR
        for case, result in zip(selected, results):
            artifact, _path, _created = write_case_evidence(case, result, case_fingerprint(case, options.backend, options.model_digest), host, dest)
            result['artifact_hash'] = artifact
    if options.private_out:
        private_dir = Path(options.private_out).expanduser()
        private_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        for cid, private in raw_by_case.items():
            path = private_dir / (cid + '.json')
            handle = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(handle, 'w') as out:
                json.dump({'case_id': cid, 'trials': private}, out, ensure_ascii=False, indent=2)

    gate = bool(options.gate)
    summary = build_summary(results, options, baseline, host, gate)
    print_report(summary)
    if options.summary_out:
        path = Path(options.summary_out).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + '\n')
        print('Summary (redacted, content-hashed): ' + str(path))
    if summary['aggregate']['tripwires']:
        print('FAILED: a trial reached an execution surface; results are void.', file=sys.stderr)
        return 1
    if summary['aggregate']['cases_with_errors']:
        print('Runner reported errored trials; results are incomplete.', file=sys.stderr)
        return 1
    if gate:
        below = gate_report(results, baseline)
        for line in below:
            print('BELOW BASELINE: ' + line, file=sys.stderr)
        if below:
            return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
