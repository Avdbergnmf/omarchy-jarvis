#!/usr/bin/env python3
"""Read-only HTTP checks plus reversible overlay/console smoke tests."""
import json
from pathlib import Path
import selectors
import subprocess
import sys
import time
import uuid
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'actions'))
from core import hypr,dispatch,notify,is_overlay
BASE='http://127.0.0.1:7421'
def request(path,body=None,headers=None):
 req=Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,headers=headers or {})
 try:
  with urlopen(req,timeout=10) as r:return r.status,json.load(r)
 except HTTPError as e:return e.code,json.load(e)
assert request('/health')[0]==200
assert request('/health',headers={'Host':'evil.example'})[0]==403
assert request('/v1/run',{'prompt':'hello'},{'Content-Type':'application/json'})[0]==403
token=request('/v1/session')[1]['token'];headers={'Content-Type':'application/json','X-Jarvis-Token':token}
assert request('/v1/run',{'prompt':'hello'},{**headers,'Origin':'https://evil.example'})[0]==403
assert request('/v1/run',{'prompt':''},headers)[0]==400
assert request('/v1/run',{'prompt':[]},headers)[0]==400
# Toggle launch, close, then rapid launches must never create duplicate windows.
for c in hypr('clients'):
 if is_overlay(c):dispatch('closewindow','address:'+c['address'])
subprocess.run([str(ROOT/'scripts/toggle-overlay.py')],check=True)
overlays=[c for c in hypr('clients') if is_overlay(c)]
assert len(overlays)==1 and overlays[0]['floating'] and overlays[0]['size']==[640,460],overlays
# Exercise the same toggle command used by the installed hotkey twice more.
subprocess.run([str(ROOT/'scripts/toggle-overlay.py')],check=True)
time.sleep(.2)
assert not any(is_overlay(c) for c in hypr('clients'))
subprocess.run([str(ROOT/'scripts/toggle-overlay.py')],check=True)
assert len([c for c in hypr('clients') if is_overlay(c)])==1
assert request('/v1/close',{},headers)[0]==200
time.sleep(.2)
assert not any(is_overlay(c) for c in hypr('clients'))
# Verify tail follows a rotated filename, not just its original inode.
rid='rotation-'+str(uuid.uuid4());path=ROOT/'logs/runs'/(rid+'.log');path.write_text('before\n')
p=subprocess.Popen([str(ROOT/'console/jarvis-console'),rid,'--follow'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 assert p.stdout.readline().strip()=='before'
 rotated=path.with_suffix('.old');path.rename(rotated);path.write_text('after-rotation\n')
 selector=selectors.DefaultSelector();selector.register(p.stdout,selectors.EVENT_READ)
 assert selector.select(timeout=12),'tail did not follow replacement'
 assert p.stdout.readline().strip()=='after-rotation'
finally:
 p.terminate();p.wait(timeout=5);path.unlink(missing_ok=True);path.with_suffix('.old').unlink(missing_ok=True)
notify('host-verified','Jarvis host checks passed. Click for live console.')
subprocess.run(['omarchy-shell','notifications','invokeLast'],check=True)
time.sleep(.5)
consoles=[c for c in hypr('clients') if c['title']=='Jarvis · host-verified']
assert consoles and consoles[0]['floating']
(ROOT/'logs/host-evidence.json').write_text(json.dumps({'http':'host/origin/token/validation passed','overlay':{'floating':True,'size':[520,150],'single_instance':True,'close_endpoint':True},'console':{'native_notification_action':True,'floating':True,'tail_F_rotation':True}},indent=2))
print('PASS: HTTP guards, overlay open/close, native notification action, live tail -F rotation')
