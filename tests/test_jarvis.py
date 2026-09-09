import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
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
  messages=[{'role':'assistant','content':'','tool_calls':[{'function':{'name':'run_skill','arguments':{'skill':'open-planning'}}},{'function':{'name':'scratch_toggle','arguments':{}}}]}]
  rid='unit-test'; server.RUNS[rid]={'steps':[]};server.BUSY.acquire()
  with patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'failure','')) as run:
   server.execute_tools_plan(rid,None,messages)
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
  rid='json-unit';server.RUNS[rid]={'steps':[]};server.BUSY.acquire()
  plan={'actions':[{'tool':'run_skill','arguments':{'skill':'open-planning'}}],'reply':'Unverified claim'}
  with patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')):
   server.execute_plan(rid,plan,None)
  self.assertEqual(server.RUNS[rid]['reply'],'Completed: open-planning.')
  self.assertFalse(server.BUSY.locked())


class ApprovalFlowTest(unittest.TestCase):
 def tearDown(self):
  server.CONFIG['approval_mode']='always'
 def test_chitchat_skips_approval(self):
  rid='chitchat-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  plan={'actions':[],'reply':'Hello!'}
  with patch.object(server,'json_plan',return_value=plan),patch.object(server,'announce'),patch.object(server,'log'):
   server.plan_and_maybe_run(rid,'hello',None)
  self.assertEqual(server.RUNS[rid]['status'],'done')
  self.assertEqual(server.RUNS[rid]['reply'],'Hello!')
  self.assertFalse(server.BUSY.locked())
 def test_action_plan_awaits_approval_by_default(self):
  rid='awaiting-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  plan={'actions':[{'tool':'scratch_toggle','arguments':{}}],'reply':'Toggling scratchpad.'}
  with patch.object(server,'json_plan',return_value=plan),patch.object(server.subprocess,'run') as run,patch.object(server,'announce'),patch.object(server,'log'):
   server.plan_and_maybe_run(rid,'toggle scratchpad',None)
  run.assert_not_called()
  self.assertEqual(server.RUNS[rid]['status'],'awaiting_approval')
  self.assertIn(rid,server.PENDING)
  self.assertTrue(server.BUSY.locked())
  server.handle_deny(rid)  # release the busy lock this test acquired
 def test_deny_runs_nothing_and_releases_busy(self):
  rid='deny-unit'; server.RUNS[rid]={'status':'awaiting_approval','steps':[]}
  server.PENDING[rid]={'target':None,'planner':'json'}; server.BUSY.acquire()
  with patch.object(server.subprocess,'run') as run,patch.object(server,'log'):
   result=server.handle_deny(rid)
  run.assert_not_called()
  self.assertEqual(result['status'],'denied')
  self.assertNotIn(rid,server.PENDING)
  self.assertFalse(server.BUSY.locked())
 def test_deny_rejects_run_not_awaiting_approval(self):
  rid='deny-unit-2'; server.RUNS[rid]={'status':'done'}
  self.assertIsNone(server.handle_deny(rid))
 def test_approve_flips_status_and_dispatches_execution(self):
  rid='approve-unit'; server.RUNS[rid]={'status':'awaiting_approval','steps':[]}
  server.PENDING[rid]={'target':None,'planner':'json'}
  with patch.object(server,'run_pending'):
   result=server.handle_approve(rid)
  self.assertEqual(result['status'],'running')
 def test_approve_rejects_run_not_awaiting_approval(self):
  rid='approve-unit-2'; server.RUNS[rid]={'status':'done'}
  self.assertIsNone(server.handle_approve(rid))
 def test_run_pending_executes_stored_json_plan(self):
  rid='pending-unit'; server.BUSY.acquire()
  server.RUNS[rid]={'status':'running','plan':{'actions':[{'tool':'scratch_toggle','arguments':{}}],'reply':'Toggling.'},'steps':[]}
  server.PENDING[rid]={'target':None,'planner':'json'}
  with patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')):
   server.run_pending(rid)
  self.assertEqual(server.RUNS[rid]['status'],'done')
  self.assertNotIn(rid,server.PENDING)
  self.assertFalse(server.BUSY.locked())
 def test_run_pending_releases_busy_when_nothing_pending(self):
  server.BUSY.acquire()
  server.run_pending('missing-unit')
  self.assertFalse(server.BUSY.locked())
 def test_approval_mode_off_auto_runs_without_waiting(self):
  server.CONFIG['approval_mode']='off'
  rid='off-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  plan={'actions':[{'tool':'scratch_toggle','arguments':{}}],'reply':'Toggling.'}
  with patch.object(server,'json_plan',return_value=plan),patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')):
   server.plan_and_maybe_run(rid,'toggle scratchpad',None)
  self.assertEqual(server.RUNS[rid]['status'],'done')
  self.assertFalse(server.BUSY.locked())
 def test_skills_trusted_auto_runs_recipes_only(self):
  server.CONFIG['approval_mode']='skills_trusted'
  rid='trusted-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  plan={'actions':[{'tool':'run_skill','arguments':{'skill':'open-planning'}}],'reply':'Opening.'}
  with patch.object(server,'json_plan',return_value=plan),patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')):
   server.plan_and_maybe_run(rid,'open my planning in a new workspace',None)
  self.assertEqual(server.RUNS[rid]['status'],'done')
  self.assertFalse(server.BUSY.locked())
 def test_skills_trusted_still_gates_non_skill_actions(self):
  server.CONFIG['approval_mode']='skills_trusted'
  rid='trusted-gate-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  plan={'actions':[{'tool':'scratch_toggle','arguments':{}}],'reply':'Toggling.'}
  with patch.object(server,'json_plan',return_value=plan),patch.object(server.subprocess,'run') as run,patch.object(server,'announce'),patch.object(server,'log'):
   server.plan_and_maybe_run(rid,'toggle scratchpad',None)
  run.assert_not_called()
  self.assertEqual(server.RUNS[rid]['status'],'awaiting_approval')
  server.handle_deny(rid)
 def test_expire_stale_auto_denies_after_timeout(self):
  rid='stale-unit'
  server.RUNS[rid]={'status':'awaiting_approval','awaiting_since':time.monotonic()-server.AWAIT_TIMEOUT-1,'steps':[]}
  server.PENDING[rid]={'target':None,'planner':'json'}
  server.BUSY.acquire()
  with patch.object(server,'BUSY_RUN_ID',rid),patch.object(server,'log'):
   server.expire_stale()
  self.assertEqual(server.RUNS[rid]['status'],'denied')
  self.assertNotIn(rid,server.PENDING)
  self.assertFalse(server.BUSY.locked())

if __name__=='__main__': unittest.main()
