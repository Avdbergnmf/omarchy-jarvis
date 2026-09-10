from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class DraftTest(unittest.TestCase):
 def test_exact_reviewed_bytes_required_for_install(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'scripts').mkdir();source=root/'sample';source.mkdir()
   (source/'SKILL.md').write_text('---\nname: example\ndescription: Example\n---\n')
   (source/'run.sh').write_text('#!/bin/bash\nprintf "example\\n"\n')
   script=root/'scripts/skill-draft.py';shutil.copy2(ROOT/'scripts/skill-draft.py',script)
   def run(*args): return subprocess.run(['python3',str(script),*args],capture_output=True,text=True)
   self.assertEqual(run('propose','example','--source',str(source)).returncode,0)
   self.assertNotEqual(run('install','example').returncode,0)
   reviewed=run('review','example');digest=reviewed.stdout.split('Approval digest: ')[1].strip()
   (root/'skills/drafts/example/run.sh').write_text('#!/bin/bash\nprintf "changed\\n"\n')
   self.assertNotEqual(run('install','example','--confirm',digest).returncode,0)
   digest=run('review','example').stdout.split('Approval digest: ')[1].strip()
   self.assertEqual(run('install','example','--confirm',digest).returncode,0)
   installed=root/'skills/installed/example/run.sh'
   self.assertEqual(subprocess.check_output([str(installed)],text=True),'changed\n')
   self.assertNotEqual(run('install','example','--confirm',digest).returncode,0)
if __name__=='__main__':unittest.main()
