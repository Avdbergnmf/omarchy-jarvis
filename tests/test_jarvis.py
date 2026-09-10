import json
from pathlib import Path
import shutil
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

def setUpModule():
 global _logs_tmp, _logs_patch
 _logs_tmp = tempfile.TemporaryDirectory()
 _logs_patch = patch.object(server, 'LOGS', Path(_logs_tmp.name))
 _logs_patch.start()
 (server.LOGS/'runs').mkdir()

def tearDownModule():
 _logs_patch.stop()
 _logs_tmp.cleanup()

class ActionsTest(unittest.TestCase):
 def test_chord_modifier_order(self):
  self.assertEqual(core.chord('SUPER + ALT + S'),core.chord('ALT SUPER + S'))
 def test_youtube_is_a_webapp_independent_of_any_installed_desktop_file(self):
  # A-012: open_webapp's launcher never checks for a .desktop file at all — it always
  # opens the URL directly via omarchy-launch-webapp — so adding YouTube here gives the
  # "webapp if installed [as a running window], else a browser tab" fallback the
  # assignment asked for regardless of whether a local .desktop shortcut exists.
  self.assertIn('YouTube',core.APPS)
  self.assertEqual(core.APPS['YouTube'],'https://www.youtube.com/')
 def test_youtube_launch_requires_observed_window(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(core,'LOGS',Path(tmp)),patch.object(core,'hypr',return_value=[]),patch.object(core.subprocess,'Popen') as launch,patch.object(core.time,'monotonic',side_effect=[0,31]),patch.object(core,'dispatch') as dispatch:
   with self.assertRaisesRegex(RuntimeError,'window was not found'):
    core.open_app('YouTube')
  self.assertEqual(launch.call_args.args[0],['omarchy-launch-webapp','https://www.youtube.com/','--class=jarvis-youtube'])
  dispatch.assert_not_called()
 def test_is_overlay_matches_known_and_unseen_chromium_variants(self):
  # A-010: Chromium has derived classes ADR-013 didn't anticipate before; the match
  # must survive a variant we haven't hardcoded, without matching unrelated windows.
  for cls in ('jarvis-overlay','chrome-127.0.0.1__jarvis-overlay-Default','chrome-127.0.0.1__jarvis-overlay-Profile-2'):
   self.assertTrue(core.is_overlay({'class':cls}),cls)
  for cls in ('brave-browser','code','',None):
   self.assertFalse(core.is_overlay({'class':cls}),cls)
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
 def test_restore_target_focuses_without_closing_overlay(self):
  # A-004: the overlay used to be closed here at the *start* of execution, before the
  # user could see any live step progress. It must now only focus the pre-overlay
  # window and leave every window (including the overlay) open.
  clients=[{'address':'0xabc','class':'jarvis-overlay'},{'address':'0x123'}]
  with patch.object(server,'hypr',return_value=clients),patch.object(server,'dispatch') as dsp:
   server.restore_target('0x123')
  dsp.assert_called_once_with('focuswindow','address:0x123')
 def test_restore_target_noop_without_a_target(self):
  clients=[{'address':'0xabc','class':'jarvis-overlay'}]
  with patch.object(server,'hypr',return_value=clients),patch.object(server,'dispatch') as dsp:
   server.restore_target(None)
  dsp.assert_not_called()
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
 def test_false_action_claim_with_no_actions_is_rewritten_honestly(self):
  # A-012: run fad6f832 shipped exactly {"actions": [], "reply": "Opening YouTube."} —
  # a zero-action plan skips approval entirely (commit_plan's zero-action branch), so
  # this false claim reached the user as already "done" with nothing to review first.
  plan={'actions':[],'reply':'Opening YouTube.'}
  with patch.object(server,'urlopen',return_value=self.response(plan)):
   result=server.json_plan('open youtube')
  self.assertEqual(result['actions'],[])
  self.assertNotIn('Opening YouTube',result['reply'])
  self.assertIn("No actions were run",result['reply'])
 def test_empty_plan_claim_variants_and_blank_replies(self):
  for reply in ('', '  ', 'Done.', 'Completed!', "I've opened Spotify.", 'Sure, opening YouTube.', 'I will launch Spotify.', 'Moved the window.'):
   with self.subTest(reply=reply):
    self.assertIn('No actions were run',server.empty_plan_reply(reply))
  for reply in ('Hello!', "I cannot open that app.", 'You can open Spotify yourself.'):
   self.assertEqual(server.empty_plan_reply(reply),reply)
 def test_tools_completion_uses_executed_labels(self):
  rid='tools-summary-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  messages=[{'role':'assistant','tool_calls':[{'function':{'name':'scratch_toggle','arguments':{}}}]}]
  with patch.object(server,'restore_target'),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')),patch.object(server,'ollama_chat',return_value={'content':'I opened Spotify and YouTube.'}):
   server.execute_tools_plan(rid,None,messages)
  self.assertEqual(server.RUNS[rid]['reply'],'Completed: scratch toggle.')
 def test_honest_empty_reply_is_left_alone(self):
  plan={'actions':[],'reply':'Hello! How can I help?'}
  with patch.object(server,'urlopen',return_value=self.response(plan)):
   result=server.json_plan('hello')
  self.assertEqual(result['reply'],'Hello! How can I help?')
 def test_false_action_claim_reply_only_checked_when_actions_empty(self):
  plan={'actions':[{'tool':'scratch_toggle','arguments':{}}],'reply':'Opening a thing.'}
  with patch.object(server,'urlopen',return_value=self.response(plan)):
   result=server.json_plan('toggle scratchpad')
  self.assertEqual(result['reply'],'Opening a thing.')  # a real action legitimately gets an "Opening …"-style reply
 def test_plan_tools_run_rewrites_false_action_claim_too(self):
  # Same fad6f832-shaped bug, opt-in JARVIS_PLANNER=tools loop path.
  rid='tools-false-claim-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  with patch.object(server,'ollama_chat',return_value={'role':'assistant','content':'Opening YouTube.'}),patch.object(server,'announce'),patch.object(server,'log'):
   server.plan_tools_run(rid,'open youtube',None)
  self.assertEqual(server.RUNS[rid]['status'],'done')
  self.assertNotIn('Opening YouTube',server.RUNS[rid]['reply'])
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
 def test_app_open_plans_are_reviewed_before_any_launch(self):
  for tool,name in [('open_app_by_name','Spotify'),('open_webapp','YouTube')]:
   with self.subTest(tool=tool):
    rid='review-'+tool; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
    plan={'actions':[{'tool':tool,'arguments':{'name':name}}],'reply':'Opening '+name+'.'}
    with patch.object(server,'ollama_chat',return_value={'content':json.dumps(plan)}),patch.object(server.subprocess,'run') as launch,patch.object(server,'restore_target') as restore,patch.object(server,'announce'),patch.object(server,'log'):
     server.plan_and_maybe_run(rid,'open '+name,None)
     self.assertEqual(server.RUNS[rid]['status'],'awaiting_approval')
     self.assertEqual(server.RUNS[rid]['plan'],plan)
     launch.assert_not_called(); restore.assert_not_called()
     server.handle_deny(rid)
    self.assertFalse(server.BUSY.locked())
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
 def test_expire_stale_covers_awaiting_answer(self):
  rid='stale-answer-unit'
  server.RUNS[rid]={'status':'awaiting_answer','awaiting_since':time.monotonic()-server.AWAIT_TIMEOUT-1,'steps':[]}
  server.BUSY.acquire()
  with patch.object(server,'BUSY_RUN_ID',rid),patch.object(server,'log'):
   server.expire_stale()
  self.assertEqual(server.RUNS[rid]['status'],'denied')
  self.assertFalse(server.BUSY.locked())


class BacklogActionsTest(unittest.TestCase):
 def test_redact_strips_token_shaped_secrets(self):
  text=core.redact('key sk-ant-abc123def456ghi789 and ghp_ABCDEFGHIJ1234567890 here')
  self.assertNotIn('sk-ant-abc123def456ghi789',text)
  self.assertNotIn('ghp_ABCDEFGHIJ1234567890',text)
 def test_slugify_basic(self):
  self.assertEqual(core.slugify("Bug: Window Won't Move!!"),'bug-window-won-t-move')
 def test_ensure_labels_is_idempotent_create_or_update(self):
  with patch.object(core.subprocess,'run') as run:
   core.ensure_labels(['bug','jarvis-reported'])
  self.assertEqual(run.call_count,2)
  for call in run.call_args_list: self.assertIn('--force',call.args[0])
 def test_report_record_dry_run_makes_no_gh_call(self):
  with patch.object(core,'command') as cmd:
   result=core.report_record('bug','Test title','body text','M',dry=True)
  cmd.assert_not_called()
  self.assertTrue(result['dry_run'])
  self.assertIn('bug',result['labels'])
 def test_report_record_rejects_bad_difficulty(self):
  with self.assertRaises(ValueError): core.report_record('bug','Title','body','X',dry=True)
 def test_report_record_writes_mirror_and_index(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   (root/'docs/templates').mkdir(parents=True)
   for name in ('ISSUE_BUG.md','ISSUE_FEATURE.md'): shutil.copy2(ROOT/'docs/templates'/name,root/'docs/templates'/name)
   (root/'docs/backlog/bugs').mkdir(parents=True)
   (root/'docs/backlog/INDEX.md').write_text('| id | type | title | difficulty | status | gh issue |\n|---|---|---|---|---|---|\n')
   fake=lambda *a,**k:{'argv':[],'stdout':'https://github.com/Avdbergnmf/omarchy-jarvis/issues/123\n','stderr':''}
   with patch.object(core,'ROOT',root),patch.object(core,'command',side_effect=fake),patch.object(core,'ensure_labels') as ensure:
    result=core.report_record('bug','Window fails to move','body & stuff','M')
   ensure.assert_called_once_with(['bug','jarvis-reported'])
   self.assertEqual(result['number'],123)
   self.assertTrue((root/'docs/backlog/bugs'/(result['slug']+'.md')).exists())
   self.assertIn('#123',(root/'docs/backlog/INDEX.md').read_text())
 def test_prepare_handoff_dry_run_and_bad_agent(self):
  result=core.prepare_handoff(7,'claude-code',dry=True)
  self.assertTrue(result['dry_run'])
  with self.assertRaises(ValueError): core.prepare_handoff(7,'not-an-agent',dry=True)
 def test_list_backlog_dry_run(self):
  self.assertTrue(core.list_backlog(dry=True)['dry_run'])


class SelfImproveServerTest(unittest.TestCase):
 def tearDown(self):
  server.CONFIG['approval_mode']='always'
 def test_detect_intake_slash_and_natural_language(self):
  self.assertEqual(server.detect_intake('/report the scratchpad binding is broken'),('bug','the scratchpad binding is broken'))
  self.assertEqual(server.detect_intake('/feature add dark mode'),('feature','add dark mode'))
  kind,_=server.detect_intake('you messed up, the window moved to the wrong workspace')
  self.assertEqual(kind,'bug')
  kind,_=server.detect_intake('I wish it could remember my last workspace')
  self.assertEqual(kind,'feature')
  self.assertEqual(server.detect_intake('hello there'),(None,None))
 def test_report_tools_excluded_from_model_facing_planner(self):
  names={t['function']['name'] for t in server.TOOLS_FOR_MODEL}
  self.assertNotIn('report_bug',names); self.assertNotIn('report_feature',names)
  self.assertIn('list_backlog',names); self.assertIn('prepare_handoff',names)
  self.assertNotIn('report_bug',json.dumps(server.PLAN_SCHEMA))
 def test_validate_call_respects_maxlength_override(self):
  server.validate_call('report_bug',{'title':'t','body':'x'*500,'difficulty':'M'})
  with self.assertRaises(ValueError): server.validate_call('report_bug',{'title':'t'*300,'body':'b','difficulty':'M'})
 def test_tool_argv_for_backlog_tools(self):
  argv=server.tool_argv('report_bug',{'title':'T','body':'B','difficulty':'M'})
  self.assertEqual(argv[-6:],['--title','T','--body','B','--difficulty','M'])
  argv=server.tool_argv('prepare_handoff',{'issue':9,'agent':'human'})
  self.assertEqual(argv[-4:],['--issue','9','--agent','human'])
 def test_execute_plan_skips_restore_for_backlog_tools(self):
  rid='backlog-exec-unit'; server.RUNS[rid]={'steps':[]}; server.BUSY.acquire()
  plan={'actions':[{'tool':'list_backlog','arguments':{}}],'reply':'Listing.'}
  with patch.object(server,'restore_target') as restore,patch.object(server,'announce'),patch.object(server,'log'),patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"ok":true}','')):
   server.execute_plan(rid,plan,'0xdead')
  restore.assert_not_called()
  self.assertEqual(server.RUNS[rid]['status'],'done')
 def test_intake_flow_reaches_draft_awaiting_approval(self):
  rid='intake-unit'
  server.RUNS[rid]={'run_id':rid,'status':'planning','reply':'Thinking…','plan':None,'steps':[]}
  server.BUSY.acquire()
  with patch.object(server,'announce'),patch.object(server,'log'),patch.object(server,'gather_host_facts',return_value='(skipped)'),patch.object(server,'gather_binding_hits',return_value='(skipped)'):
   server.start_intake(rid,'bug','the scratchpad toggle did nothing',None)
   self.assertEqual(server.RUNS[rid]['status'],'awaiting_answer')
   for answer in ('it should toggle the scratchpad','nothing happened','always reproduces'):
    server.handle_answer(rid,answer)
  run=server.RUNS[rid]
  self.assertEqual(run['status'],'awaiting_approval')
  self.assertEqual(run['plan']['actions'][0]['tool'],'report_bug')
  self.assertIn('nothing happened',run['plan']['actions'][0]['arguments']['body'])
  server.handle_deny(rid)
 def test_intake_skip_files_with_partial_context(self):
  rid='intake-skip-unit'
  server.RUNS[rid]={'run_id':rid,'status':'planning','reply':'Thinking…','plan':None,'steps':[]}
  server.BUSY.acquire()
  with patch.object(server,'announce'),patch.object(server,'log'),patch.object(server,'gather_host_facts',return_value='(skipped)'),patch.object(server,'gather_binding_hits',return_value='(skipped)'):
   server.start_intake(rid,'feature','add a dark mode toggle',None)
   server.handle_answer(rid,'skip')
  run=server.RUNS[rid]
  self.assertEqual(run['status'],'awaiting_approval')
  self.assertEqual(run['plan']['actions'][0]['tool'],'report_feature')
  self.assertIn('no answers',run['plan']['actions'][0]['arguments']['body'])
  server.handle_deny(rid)
 def test_handle_answer_rejects_wrong_status(self):
  rid='answer-wrong-status'; server.RUNS[rid]={'status':'done'}
  self.assertIsNone(server.handle_answer(rid,'text'))
 def test_backlog_and_dispatch_slash_commands_build_expected_plan(self):
  # list_backlog is read-only but still goes through Run/Cancel like any other
  # tool call, matching how catalog_bindings is gated (consistency over risk).
  rid='backlog-route-unit'
  server.RUNS[rid]={'run_id':rid,'status':'planning','reply':'Thinking…','plan':None,'steps':[]}
  server.BUSY.acquire()
  with patch.object(server,'announce'),patch.object(server,'log'):
   server.start_fixed_plan(rid,{'actions':[{'tool':'list_backlog','arguments':{}}],'reply':'Listing open backlog items.'},None)
  self.assertEqual(server.RUNS[rid]['status'],'awaiting_approval')
  self.assertEqual(server.RUNS[rid]['plan']['actions'][0]['tool'],'list_backlog')
  server.handle_deny(rid)

class FeedbackTest(unittest.TestCase):
 def test_good_feedback_is_cheap_and_terminal(self):
  rid='fb-good-unit'; server.RUNS[rid]={'run_id':rid,'status':'done','reply':'Completed: x.','prompt':'toggle scratchpad','steps':[]}
  with patch.object(server,'journal_event') as journal:
   result=server.handle_feedback(rid,'good')
  self.assertEqual(result['run_id'],rid)
  self.assertEqual(server.RUNS[rid]['feedback'],'good')
  journal.assert_called_once_with(rid,'feedback',feedback={'rating':'good'})
 def test_neutral_feedback_appends_needs_review_without_github(self):
  rid='fb-neutral-unit'; server.RUNS[rid]={'run_id':rid,'status':'error','reply':'Stopped: nope.','prompt':'move window','steps':[]}
  with patch.object(server,'journal_event'):
   server.handle_feedback(rid,'neutral')
  path=server.LOGS/'feedback'/'needs-review.jsonl'
  self.assertTrue(path.exists())
  record=json.loads(path.read_text().splitlines()[-1])
  self.assertEqual(record['run_id'],rid); self.assertEqual(record['prompt'],'move window')
 def test_feedback_rejects_run_not_in_terminal_state(self):
  rid='fb-pending-unit'; server.RUNS[rid]={'status':'awaiting_approval'}
  self.assertIsNone(server.handle_feedback(rid,'good'))
 def test_feedback_rejects_second_rating_for_same_run(self):
  rid='fb-twice-unit'; server.RUNS[rid]={'run_id':rid,'status':'done','reply':'Done.','prompt':'x','steps':[],'feedback':'good'}
  with self.assertRaises(ValueError): server.handle_feedback(rid,'neutral')
 def test_feedback_rejects_unknown_rating(self):
  rid='fb-badrating-unit'; server.RUNS[rid]={'run_id':rid,'status':'done','reply':'Done.','prompt':'x','steps':[]}
  with self.assertRaises(ValueError): server.handle_feedback(rid,'awful')
 def test_bad_feedback_starts_bug_intake_with_source_run_attached(self):
  rid='fb-bad-unit'; server.RUNS[rid]={'run_id':rid,'status':'error','reply':'Stopped: failed.','prompt':'the scratchpad toggle did nothing','steps':[]}
  active={'address':'0x123','class':'code'}
  with patch.object(server,'hypr',return_value=active),patch.object(server,'is_overlay',return_value=False),patch.object(server,'announce'),patch.object(server,'log'),patch.object(server,'gather_host_facts',return_value='(skipped)'),patch.object(server,'gather_binding_hits',return_value='(skipped)'):
   result=server.handle_feedback(rid,'bad')
   new_id=result['run_id']
   self.assertNotEqual(new_id,rid)
   self.assertEqual(server.RUNS[new_id]['status'],'awaiting_answer')
   context=server.RUNS[new_id]['intake']['context']
   self.assertEqual(context['last_run_id'],rid,'the bug report context must reference the rated run, not whatever ran most recently')
   server.handle_deny(new_id)
  self.assertEqual(server.RUNS[rid]['feedback'],'bad')
 def test_bad_feedback_refuses_when_a_run_is_already_busy(self):
  rid='fb-bad-busy-unit'; server.RUNS[rid]={'run_id':rid,'status':'done','reply':'Done.','prompt':'x','steps':[]}
  server.BUSY.acquire()
  try:
   with patch.object(server,'hypr',return_value={'address':None,'class':''}),patch.object(server,'is_overlay',return_value=False):
    with self.assertRaises(RuntimeError): server.handle_feedback(rid,'bad')
  finally:
   server.BUSY.release()

def write_desktop(path,name,exec_line,extra=''):
 path.write_text('[Desktop Entry]\nType=Application\nName='+name+'\nExec='+exec_line+'\n'+extra)

class OpenByNameTest(unittest.TestCase):
 def test_desktop_entries_skips_nodisplay_and_non_application(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp)
   write_desktop(d/'a.desktop','Alpha','alpha')
   write_desktop(d/'b.desktop','Beta','beta','NoDisplay=true\n')
   (d/'c.desktop').write_text('[Desktop Entry]\nType=Link\nName=Gamma\nExec=gamma\n')
   with patch.object(core,'DESKTOP_DIRS',(d,)):
    entries=core.desktop_entries()
  self.assertEqual({e['name'] for e in entries},{'Alpha'})
 def test_desktop_entries_prefers_first_dir_on_duplicate_stem(self):
  with tempfile.TemporaryDirectory() as tmp:
   d1=Path(tmp)/'d1'; d2=Path(tmp)/'d2'; d1.mkdir(); d2.mkdir()
   write_desktop(d1/'spotify.desktop','Spotify Local','spotify-local')
   write_desktop(d2/'spotify.desktop','Spotify System','spotify-system')
   with patch.object(core,'DESKTOP_DIRS',(d1,d2)):
    entries=core.desktop_entries()
  self.assertEqual(len(entries),1); self.assertEqual(entries[0]['name'],'Spotify Local')
 def test_resolve_app_exact_prefix_fuzzy_and_ambiguous(self):
  entries=[{'name':'Spotify','exec':'spotify','stem':'spotify','wmclass':'spotify'},
           {'name':'Spotify Beta','exec':'spotify-beta','stem':'spotify-beta','wmclass':'spotify-beta'},
           {'name':'Discord','exec':'discord','stem':'discord','wmclass':'discord'}]
  self.assertEqual(core.resolve_app('Spotify',entries)['name'],'Spotify')
  self.assertEqual(core.resolve_app('spotify',entries)['name'],'Spotify')  # case-insensitive exact
  self.assertEqual(core.resolve_app('Discor',entries)['name'],'Discord')  # unambiguous prefix
  self.assertEqual(core.resolve_app('Discrod',entries)['name'],'Discord')  # fuzzy typo
  with self.assertRaisesRegex(ValueError,'Multiple installed apps match'):
   core.resolve_app('ify',entries)  # substring of both "Spotify" and "Spotify Beta"
  with self.assertRaisesRegex(ValueError,'No installed app matches'):
   core.resolve_app('totally-unrelated-xyz',entries)
  with self.assertRaises(ValueError):
   core.resolve_app('',entries)
 def test_launch_command_drops_field_codes_not_just_the_token_value(self):
  entry={'name':'Spotify','exec':'spotify --uri=%u','stem':'spotify','wmclass':'spotify'}
  self.assertEqual(core.launch_command_for(entry),'spotify')
  entry2={'name':'Files','exec':'nautilus %U','stem':'nautilus','wmclass':'nautilus'}
  self.assertEqual(core.launch_command_for(entry2),'nautilus')
 def test_launch_command_rejects_empty_exec(self):
  with self.assertRaises(ValueError): core.launch_command_for({'name':'X','exec':'%u','stem':'x','wmclass':'x'})
 def test_open_by_name_dry_run_uses_omarchy_launch_or_focus(self):
  entries=[{'name':'Spotify','exec':'spotify --uri=%u','stem':'spotify','wmclass':'spotify'}]
  with patch.object(core,'desktop_entries',return_value=entries):
   result=core.open_by_name('spotify',dry=True)
  self.assertEqual(result['argv'],['omarchy-launch-or-focus','spotify','uwsm-app -- spotify'])
  self.assertTrue(result['dry_run'])
 def test_open_by_name_finds_the_resulting_window(self):
  entries=[{'name':'Spotify','exec':'spotify','stem':'spotify','wmclass':'spotify'}]
  clients=[{'address':'0xabc','class':'Spotify','title':'Spotify','workspace':{'id':3}}]
  with patch.object(core,'desktop_entries',return_value=entries),patch.object(core,'hypr',return_value=clients),patch.object(core.subprocess,'Popen') as popen:
   result=core.open_by_name('spotify')
  popen.assert_called_once()
  self.assertEqual(result,{'name':'Spotify','address':'0xabc','workspace':3,'class':'Spotify'})
 def test_open_by_name_times_out_if_no_window_appears(self):
  entries=[{'name':'Ghost','exec':'ghost-app','stem':'ghost-app','wmclass':'ghost-app'}]
  with patch.object(core,'desktop_entries',return_value=entries),patch.object(core,'hypr',return_value=[]),patch.object(core.subprocess,'Popen'),patch.object(core.time,'monotonic',side_effect=[0,100]):
   with self.assertRaisesRegex(RuntimeError,'no matching window appeared'):
    core.open_by_name('ghost')
 def test_tool_argv_and_action_label_for_open_app_by_name(self):
  argv=server.tool_argv('open_app_by_name',{'name':'Spotify'})
  self.assertEqual(argv[-2:],['--name','Spotify'])
  self.assertEqual(server.action_label('open_app_by_name',{'name':'Spotify'}),'Spotify')

if __name__=='__main__': unittest.main()
