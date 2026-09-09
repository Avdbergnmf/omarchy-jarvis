#!/usr/bin/env python3
import json
from pathlib import Path
import shutil
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'actions'))
from core import catalog,chord
path=Path.home()/'.config/hypr/bindings.lua'
text=path.read_text(); marker='-- BEGIN OMARCHY JARVIS'; end='-- END OMARCHY JARVIS'
rows=catalog(refresh=True)['bindings']
conflicts=[r for r in rows if chord(r['chord'])==chord('SUPER SHIFT J') and r['description']!='Jarvis overlay']
if conflicts: raise SystemExit('Hotkey occupied: '+str(conflicts))
if marker in text:
 start=text.index(marker); finish=text.index(end,start)+len(end)
 text=text[:start]+text[finish:]
block=f'''{marker}
o.bind("SUPER + SHIFT + J", "Jarvis overlay", {json.dumps(str(ROOT/'scripts/toggle-overlay.py'))})
o.window("^(jarvis-overlay|chrome-127[.]0[.]0[.]1__jarvis-overlay-Default)$", {{ float = true, center = true, size = {{ 520, 150 }} }})
{end}
'''
shutil.copy2(path,str(path)+'.jarvis-backup-'+str(time.time_ns()))
path.write_text(text.rstrip()+'\n\n'+block)
print('Installed SUPER + SHIFT + J; previous bindings backed up')
