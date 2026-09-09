#!/usr/bin/env python3
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'actions'))
from core import hypr, dispatch, is_overlay
(ROOT/'logs').mkdir(exist_ok=True,mode=0o700)
with (ROOT/'logs/overlay.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 clients=hypr('clients'); active=hypr('activewindow')
 existing=next((c for c in clients if is_overlay(c)),None)
 if existing:
  if active.get('address')==existing['address']: dispatch('closewindow','address:'+existing['address'])
  else:
   (ROOT/'logs/overlay-target.json').write_text(json.dumps({'address':active.get('address')}))
   dispatch('focuswindow','address:'+existing['address'])
  sys.exit(0)
 (ROOT/'logs/overlay-target.json').write_text(json.dumps({'address':active.get('address')}))
 subprocess.run([str(ROOT/'scripts/start.sh')],check=True,stdout=subprocess.DEVNULL)
 with (ROOT/'logs/overlay.log').open('a') as out:
  subprocess.Popen(['chromium','--user-data-dir='+str(ROOT/'logs/overlay-profile'),'--class=jarvis-overlay','--no-first-run','--disable-extensions','--disable-background-networking','--no-default-browser-check','--disable-background-mode','--app=http://127.0.0.1:7421/jarvis-overlay','--window-size=520,150'],stdout=out,stderr=out,start_new_session=True)
 for _ in range(75):
  if any(is_overlay(c) for c in hypr('clients')): break
  time.sleep(.1)
 else: raise RuntimeError('Overlay window did not appear; inspect logs/overlay.log')
