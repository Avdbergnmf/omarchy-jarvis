import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'actions')); sys.path.insert(0,str(ROOT/'brain'))
import core
import server

class ActionsTest(unittest.TestCase):
 def test_chord_modifier_order(self):
  self.assertEqual(core.chord('SUPER + ALT + S'),core.chord('ALT SUPER + S'))
 def test_workspace_ignores_special_and_fills_hole(self):
  with patch.object(core,'hypr',return_value=[{'id':1},{'id':3},{'id':-98}]):
   result=core.workspace_new(True)
  self.assertEqual(result['workspace'],2)
  self.assertIn('workspace = "2"',result['argv'][2])
 def test_unsafe_url_rejected_before_launch(self):
  for url in ['file:///etc/passwd','https://example.com/$(id)','https://example.com/;id','https://example.com/a b']:
   with self.subTest(url=url),self.assertRaises(ValueError): core.open_app('Outlook',url,dry=True)
 def test_unknown_skill_and_path_rejected(self):
  for name in ['../../bin/sh','draft','open-planning;id']:
   with self.assertRaises(ValueError): core.run_skill(name,True)
 def test_unsupported_binding_fails_closed(self):
  with patch.object(core,'catalog',return_value={'bindings':[{'chord':'SUPER W','description':'Close window'}]}):
   with self.assertRaisesRegex(ValueError,'no reviewed'): core.run_binding('SUPER + W')
 def test_live_chord_is_resolved_by_description(self):
  with patch.object(core,'catalog',return_value={'bindings':[{'chord':'SUPER Z','description':'Toggle scratchpad'}]}):
   result=core.run_binding('SUPER Z',True)
  self.assertIn('toggle_special',result['argv'][2])
 def test_notification_uses_discrete_argv(self):
  result=core.notify('test-run','$(touch /tmp/should-not-exist)',True)
  self.assertEqual(result['argv'][-2:], [str(ROOT/'console/jarvis-console'),'test-run'])
  self.assertIn('$(touch /tmp/should-not-exist)',result['argv'])
  with self.assertRaises(ValueError): core.notify('../bad','test',True)
 def test_app_matching_does_not_hijack_generic_browser_title(self):
  clients=[{'class':'brave-browser','title':'Outlook tutorial','address':'0x1'}, {'class':'brave-outlook.live.com__mail_-Default','address':'0x2','workspace':{'id':4}}]
  with patch.object(core,'hypr',return_value=clients),patch.object(core,'dispatch') as dsp:
   result=core.open_app('Outlook','https://outlook.live.com/mail/',workspace=4)
  self.assertEqual(result['address'],'0x2')
  dsp.assert_any_call('movetoworkspacesilent','4,address:0x2')
 def test_console_path_traversal_rejected(self):
  p=subprocess.run([str(ROOT/'console/jarvis-console'),'../bad','--dry-run'],capture_output=True)
  self.assertNotEqual(p.returncode,0)

class BrainTest(unittest.TestCase):
 def test_tool_validation(self):
  for name,args in [('exec',{}),('workspace_switch',{'workspace':True}),('workspace_switch',{'workspace':0}),('run_skill',{'skill':'../../evil'}),('open_webapp',{'name':'Outlook','url':'https://evil.example'})]:
   with self.subTest(name=name,args=args),self.assertRaises(ValueError): server.tool_argv(name,args)
 def test_known_skill_argv(self):
  self.assertEqual(server.tool_argv('run_skill',{'skill':'open-planning'}),[str(ROOT/'actions/run_skill'),'open-planning'])
 def test_original_target_disappearing_stops_actions(self):
  with patch.object(server,'hypr',return_value=[]),self.assertRaises(ValueError): server.restore_target('0x123')
 def test_redacts_common_credentials(self):
  self.assertNotIn('test-secret',server.redact('token=test-secret password=test-secret Bearer test-secret'))
 def test_run_failure_stops_before_later_action(self):
  class Response:
   def __enter__(self): return self
   def __exit__(self,*args): pass
   def read(self): return json.dumps({'message':{'role':'assistant','content':'','tool_calls':[{'function':{'name':'run_skill','arguments':{'skill':'open-planning'}}},{'function':{'name':'scratch_toggle','arguments':{}}}]}}).encode()
  rid='unit-test'; server.RUNS[rid]={};server.BUSY.acquire()
  with patch.object(server,'urlopen',return_value=Response()),patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'failure','')) as run:
   server.execute_run(rid,'planning',None)
  self.assertEqual(run.call_count,1); self.assertEqual(server.RUNS[rid]['status'],'error');self.assertFalse(server.BUSY.locked())


class JsonPlanTest(unittest.TestCase):
 def response(self,plan):
  class Response:
   def __enter__(self): return self
   def __exit__(self,*args): pass
   def read(self): return json.dumps({'message':{'content':json.dumps(plan)}}).encode()
  return Response()
 def test_valid_complete_recipe(self):
  plan={'actions':[{'tool':'run_skill','arguments':{'skill':'scratch-and-mail'}}],'reply':'Opening mail.'}
  with patch.object(server,'urlopen',return_value=self.response(plan)):
   self.assertEqual(server.json_plan('scratch and mail'),plan)
 def test_rejects_multiple_actions_before_execution(self):
  plan={'actions':[{'tool':'scratch_move_here','arguments':{}},{'tool':'run_skill','arguments':{'skill':'scratch-and-mail'}}],'reply':'Done'}
  with patch.object(server,'urlopen',return_value=self.response(plan)),self.assertRaises(ValueError):server.json_plan('scratch and mail')
 def test_rejects_wrong_argument_type(self):
  plan={'actions':[{'tool':'workspace_switch','arguments':{'workspace':'1'}}],'reply':'Done'}
  with patch.object(server,'urlopen',return_value=self.response(plan)),self.assertRaises(ValueError):server.json_plan('workspace one')
 def test_success_reply_comes_from_executed_tool(self):
  rid='json-unit';server.RUNS[rid]={};server.BUSY.acquire()
  plan={'actions':[{'tool':'run_skill','arguments':{'skill':'open-planning'}}],'reply':'Unverified claim'}
  with patch.object(server,'json_plan',return_value=plan),patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')):
   server.execute_json_run(rid,'planning',None)
  self.assertEqual(server.RUNS[rid]['reply'],'Completed: open-planning.')
  self.assertFalse(server.BUSY.locked())

if __name__=='__main__': unittest.main()
