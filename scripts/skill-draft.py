#!/usr/bin/env python3
"""M4 CLI stub: draft, review exact bytes, then explicitly approve that digest."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('mode',choices=['propose','review','install'])
p.add_argument('skill_id')
p.add_argument('--source',type=Path)
p.add_argument('--confirm',help='Digest shown by review, only after explicit user approval')
a=p.parse_args()
if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a.skill_id) or len(a.skill_id)>63: p.error('Invalid skill id')
draft=ROOT/'skills/drafts'/a.skill_id
files=['SKILL.md','run.sh']
def read_files(folder):
 result={}
 for name in files:
  path=folder/name
  if path.is_symlink() or not path.is_file(): raise ValueError('Expected ordinary '+name)
  data=path.read_bytes()
  if len(data)>100000: raise ValueError('Draft file too large')
  result[name]=data
 return result
try:
 if a.mode=='propose':
  if a.source is None: p.error('--source required')
  data=read_files(a.source)
  draft.mkdir(parents=True,exist_ok=False)
  for name,content in data.items(): (draft/name).write_bytes(content)
  print('Draft saved. Run review; no executable installation has occurred.')
 else:
  data=read_files(draft)
  digest=hashlib.sha256(b''.join(name.encode()+b'\0'+data[name]+b'\0' for name in files)).hexdigest()
  if a.mode=='review':
   for name in files:
    print('--- /dev/null\n+++ '+str(draft/name))
    for line in data[name].decode().splitlines(): print('+'+line)
   print('Approval digest: '+digest)
  else:
   if a.confirm!=digest: raise ValueError('Explicit matching --confirm digest required; review again if changed')
   target=ROOT/'skills/installed'/a.skill_id
   target.mkdir(parents=True,exist_ok=False)
   for name,content in data.items(): (target/name).write_bytes(content)
   (target/'run.sh').chmod(0o755)
   print(json.dumps({'installed':str(target),'sha256':digest,'command':str(target/'run.sh')}))
except (OSError,ValueError) as e:
 print(str(e),file=sys.stderr); sys.exit(1)
