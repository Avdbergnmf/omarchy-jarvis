#!/usr/bin/env python3
"""Live integration demos; launches/moves apps. Explicitly run on the Omarchy host."""
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'actions'))
from core import hypr,dispatch
BASE='http://127.0.0.1:7421'
def get(path):
 with urlopen(Request(BASE+path,headers={'X-Jarvis-Token':token}),timeout=10) as r: return json.load(r)
def post(path,body=None):
 request=Request(BASE+path,data=json.dumps(body or {}).encode(),headers={'Content-Type':'application/json','X-Jarvis-Token':token})
 with urlopen(request,timeout=10) as r: return json.load(r)
def run(prompt,approve=True):
 result=post('/v1/run',{'prompt':prompt}); run_id=result['run_id']
 print(json.dumps(result),flush=True)
 approved=False
 for _ in range(300):
  result=get('/v1/runs/'+run_id)
  if result['status']=='awaiting_approval':
   print(json.dumps(result),flush=True)
   if approved: raise RuntimeError('Plan still awaiting approval after decision')
   approved=True
   result=post('/v1/runs/'+run_id+('/approve' if approve else '/deny'))
   continue
  if result['status'] not in ('planning','running'):
   print(json.dumps(result),flush=True)
   if approve and result['status']!='done': raise RuntimeError(result)
   if not approve and result['status']!='denied': raise RuntimeError(result)
   return result
  time.sleep(1)
 raise RuntimeError('Demo exceeded 5 minutes')
with urlopen(BASE+'/v1/session') as r: token=json.load(r)['token']
# First exercise the Ollama loop with no desktop mutation; chitchat skips approval entirely.
results=[run('Say hello in one short sentence. Do not use tools.')]
assert results[-1]['status']=='done'
assert not (results[-1].get('plan') or {}).get('actions'), 'Chitchat must skip approval and run no actions'
# Existing overlay is closed by the brain only when running a desktop action.
before_workspaces={w['id'] for w in hypr('workspaces')}
# Deny the plan first: nothing should happen (acceptance test 3).
denied=run('open my planning in a new workspace',approve=False)
assert not any(host in c['class'] for c in hypr('clients') for host in ['app.todoist.com','calendar.google.com'] if c['workspace']['id'] not in before_workspaces)
assert {w['id'] for w in hypr('workspaces')}==before_workspaces, 'Deny must not create a workspace'
results.append(denied)
results.append(run('open my planning in a new workspace'))
apps=hypr('clients'); expected=['app.todoist.com','calendar.google.com','outlook.live.com','web.whatsapp.com']
selected=[next(c for c in apps if host in c['class']) for host in expected]
assert len({c['workspace']['id'] for c in selected})==1, selected
assert selected[0]['workspace']['id'] not in before_workspaces
assert '"skill": "open-planning"' in (ROOT/'logs/runs'/(results[-1]['run_id']+'.log')).read_text()
# Use a disposable terminal so the demo never hides the user's working window.
demo_class='jarvis-demo-'+str(uuid.uuid4())
subprocess.Popen(['foot','--app-id='+demo_class,'--title=Jarvis disposable demo','sleep','1800'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
for _ in range(50):
 test=next((c for c in hypr('clients') if c['class']==demo_class),None)
 if test: break
 time.sleep(.1)
assert test
dispatch('focuswindow','address:'+test['address'])
subprocess.run([str(ROOT/'scripts/toggle-overlay.py')],check=True)
results.append(run('move this window to scratchpad and open email'))
moved=next(c for c in hypr('clients') if c['address']==test['address'])
assert moved['workspace']['name']=='special:scratchpad',moved
assert '"skill": "scratch-and-mail"' in (ROOT/'logs/runs'/(results[-1]['run_id']+'.log')).read_text()
assert any('outlook.live.com' in c['class'] and c['mapped'] for c in hypr('clients'))
(ROOT/'logs/demo-evidence.json').write_text(json.dumps({'runs':results,'planning':[{'class':c['class'],'workspace':c['workspace']['id']} for c in selected],'scratch_address':test['address'],'scratch_workspace':moved['workspace']['name']},indent=2))
dispatch('closewindow','address:'+test['address'])
print('PASS: Ollama hello (no approval), denied plan (no side effects), approved planning placement, scratch-and-mail with overlay focus restoration',flush=True)
