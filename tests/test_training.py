import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'brain'))
import training
import server


class TrainingTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in (training.QUEUE, training.INDEX, 'docs/SESSION.md', 'docs/assignments/prompts/NEW_AGENT.txt', 'docs/assignments/prompts/CONTINUE.txt', 'docs/backlog/handoffs/INDEX.md'):
            target = self.root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT/path).read_text())
        training.PREVIEWS.clear()
        self.payload = dict(operation='assignment', title='Fix focus', comments='Expected: focus stays stable', area='overlay', source='run_id=test', slot_id='new', label='Tester', kind='human', mode='now')

    def tearDown(self):
        self.temp.cleanup()
        training.PREVIEWS.clear()

    def test_preview_confirm_and_replay(self):
        old = (self.root/training.QUEUE).read_text()
        result = training.preview(self.root, self.payload)
        self.assertEqual((self.root/training.QUEUE).read_text(), old)
        self.assertFalse((self.root/training.SLOTS).exists())
        expected = {f['path']:f['content'] for f in result['files']}
        brief=next(content for path,content in expected.items() if path.startswith('docs/assignments/active/'))
        forbidden=next(line for line in brief.splitlines() if '**Forbidden paths:**' in line)
        self.assertNotIn('docs/',forbidden,'metadata docs are explicitly allowed, so must not be forbidden')
        committed = training.confirm(self.root,result['preview_id'])
        for path, content in expected.items(): self.assertEqual((self.root/path).read_text(),content)
        self.assertIn('exact prompt remains ready',committed['message'])
        self.assertTrue(any(a['title']=='Fix focus' for a in training.assignments(self.root)))
        with self.assertRaises(ValueError): training.confirm(self.root,result['preview_id'])

    def test_stale_preview_no_partial_writes(self):
        result = training.preview(self.root,self.payload)
        (self.root/'docs/SESSION.md').write_text('Another agent claimed overlay')
        with self.assertRaisesRegex(ValueError,'ownership changed'):
            training.confirm(self.root,result['preview_id'])
        self.assertFalse((self.root/training.SLOTS).exists())
        self.assertFalse((self.root/'docs/assignments/active').exists())

    def test_busy_slot_queue_then_manual_prepare(self):
        result = training.preview(self.root,self.payload)
        training.confirm(self.root,result['preview_id'])
        slot = training.slots(self.root)['agents'][0]
        result = training.preview(self.root,dict(operation='slot',slot_id=slot['id'],status='busy'))
        training.confirm(self.root,result['preview_id'])
        payload = dict(operation='work',slot_id=slot['id'],assignment_id=slot['current_assignment'],mode='now')
        with self.assertRaisesRegex(ValueError,'busy'): training.preview(self.root,payload)
        payload['mode']='queue'
        queued=training.preview(self.root,payload)
        self.assertIn('will not open a window or send it automatically',queued['message'])
        training.confirm(self.root,queued['preview_id'])
        self.assertIn(slot['current_assignment'],training.slots(self.root)['agents'][0]['queued_assignment_ids'])
        idle=training.preview(self.root,dict(operation='slot',slot_id=slot['id'],status='idle'))
        training.confirm(self.root,idle['preview_id'])
        payload['mode']='now'
        ready=training.preview(self.root,payload)
        training.confirm(self.root,ready['preview_id'])
        self.assertEqual(training.slots(self.root)['agents'][0]['queued_assignment_ids'],[])

    def test_codex_handoff_persists_launch_effort(self):
        payload = dict(self.payload, kind='cursor', reasoning_effort='xhigh')
        result = training.preview(self.root, payload)
        training.confirm(self.root, result['preview_id'])
        slot = training.slots(self.root)['agents'][0]
        self.assertEqual(slot['reasoning_effort'], 'xhigh')
        with self.assertRaisesRegex(ValueError, 'only for Cursor / Codex'):
            training.preview(self.root, dict(self.payload, reasoning_effort='high'))

    def test_dashboard_offline_and_metrics(self):
        with patch.object(training.subprocess,'run',side_effect=OSError('offline')):
            data=training.dashboard(self.root,'test','abc')
        self.assertTrue(data['warnings'])
        self.assertEqual(data['metrics']['runs'],0)
        self.assertEqual(data['version'],'test')
        self.assertFalse((self.root/training.SLOTS).exists(),'read-only dashboard must not create files')

    def test_input_and_symlink_rejected(self):
        for key,value in [('title',''),('area','../../tmp'),('kind','cloud-auto'),('mode','send')]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                training.preview(self.root,dict(self.payload,**{key:value}))
        (self.root/training.QUEUE).unlink()
        (self.root/training.QUEUE).symlink_to(ROOT/training.QUEUE)
        with self.assertRaisesRegex(ValueError,'Symlinked'):
            training.preview(self.root,self.payload)

    def test_malformed_slot_cannot_supply_a_handoff_path(self):
        path=self.root/training.SLOTS
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'version':1,'agents':[{'id':'../../escape'}]}))
        with self.assertRaisesRegex(ValueError,'slot id'):
            training.preview(self.root,self.payload)

    def test_http_auth_and_confirmation_boundary(self):
        handler=object.__new__(server.Handler)
        handler.path='/v1/training/preview'
        handler.headers={'Host':'127.0.0.1:7421','Content-Type':'application/json','Content-Length':'2'}
        handler.rfile=io.BytesIO(b'{}')
        handler.reply=lambda status,body: (status,body)
        with patch.object(training,'preview') as preview:
            self.assertEqual(handler.do_POST()[0],403)
            preview.assert_not_called()
        handler.headers['X-Jarvis-Token']=server.TOKEN
        with patch.object(training,'preview',return_value={'preview_id':'test'}) as preview,patch.object(training,'confirm') as confirm:
            self.assertEqual(handler.do_POST()[0],200)
            preview.assert_called_once()
            confirm.assert_not_called()


class ProblemsTest(unittest.TestCase):
    setUp = TrainingTest.setUp
    tearDown = TrainingTest.tearDown

    def seed(self):
        return training.reconcile_problems(self.root, [dict(id='run:one', title='Original problem', source='Journal eval', run_id='one', version='0.5.4', context='Original evidence')])[0]

    def test_edits_survive_refresh_and_lost_source(self):
        problem = self.seed()
        saved = training.update_problem(self.root, dict(id=problem['id'], revision=problem['revision'], title='Edited', notes='Expected result', priority='P0', area='overlay', status='dismissed'))
        self.seed()
        result = training.reconcile_problems(self.root, [])[0]
        self.assertEqual(result, saved)
        self.assertEqual(result['evidence']['title'], 'Original problem')
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            training.update_problem(self.root, dict(id=problem['id'], revision=problem['revision'], status='done'))
        reopened = training.update_problem(self.root, dict(id=saved['id'], revision=saved['revision'], status='open'))
        self.assertEqual(reopened['status'], 'open')

    def test_delete_confirm_tombstone_and_stale_preview(self):
        problem = self.seed()
        payload = dict(operation='problem_delete', id=problem['id'], revision=problem['revision'])
        proposal = training.preview(self.root, payload)
        self.assertEqual(len(training.reconcile_problems(self.root, [])), 1)
        training.update_problem(self.root, dict(payload, priority='P1'))
        with self.assertRaisesRegex(ValueError, 'changed'):
            training.confirm(self.root, proposal['preview_id'])
        current = training.reconcile_problems(self.root, [])[0]
        proposal = training.preview(self.root, dict(payload, revision=current['revision']))
        training.confirm(self.root, proposal['preview_id'])
        self.assertEqual(training.reconcile_problems(self.root, []), [])
        self.assertEqual(training.reconcile_problems(self.root, [dict(id='run:one', title='Reimport', source='Journal eval')]), [])

    def test_assignment_uses_saved_problem_and_rejects_stale_evidence(self):
        problem = self.seed()
        saved = training.update_problem(self.root, dict(id=problem['id'], revision=problem['revision'], title='Edited title', notes='Expected stable focus', area='overlay', priority='P0'))
        payload = dict(self.payload, problem_id=saved['id'], problem_revision=saved['revision'])
        proposal = training.preview(self.root, payload)
        brief = next(f['content'] for f in proposal['files'] if '/assignments/active/' in f['path'])
        for text in ('Edited title', 'Expected stable focus', '**Priority:** P0', 'Original evidence', 'run:one'):
            self.assertIn(text, brief)
        training.update_problem(self.root, dict(id=saved['id'], revision=saved['revision'], priority='P1'))
        with self.assertRaisesRegex(ValueError, 'changed'):
            training.confirm(self.root, proposal['preview_id'])
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            training.preview(self.root, payload)

    def test_bad_feedback_and_failed_validation_sources(self):
        target = self.root/'logs/journal/CURRENT.jsonl'
        target.parent.mkdir(parents=True)
        ts = training.datetime.datetime.now(training.datetime.timezone.utc).isoformat()
        target.write_text(json.dumps(dict(ts=ts, phase='feedback', run_id='bad1', jarvis_version='test', feedback=dict(rating='bad', note='Bad focus'))) + '\n')
        with patch.object(training.subprocess, 'run', side_effect=OSError('offline')), patch.object(training.validation, 'list_features', return_value=[dict(id='feat-x', title='Failed check', status='failed', area='overlay', expected='Focus', last_run=dict(notes='Lost focus'))]):
            data = training.dashboard(self.root, 'test', 'abc')
        self.assertEqual(data['metrics']['bad'], 1)
        self.assertEqual({p['source'] for p in data['problems']}, {'Bad feedback', 'Failed human test'})
        target.unlink()
        self.assertEqual(len(training.reconcile_problems(self.root, [])), 2)

    def test_invalid_updates_and_problem_http_auth(self):
        problem = self.seed()
        for values in (dict(priority='urgent'), dict(status='deleted'), dict(area='../'), dict(title='')):
            with self.assertRaises(ValueError):
                training.update_problem(self.root, dict(id=problem['id'], revision=problem['revision'], **values))
        handler = object.__new__(server.Handler)
        handler.path = '/v1/training/problem'
        handler.headers = {'Host':'127.0.0.1:7421'}
        handler.reply = lambda status, body: (status, body)
        with patch.object(training, 'update_problem') as update:
            self.assertEqual(handler.do_POST()[0], 403)
            update.assert_not_called()
        handler.headers.update({'X-Jarvis-Token':server.TOKEN, 'Content-Type':'application/json', 'Content-Length':'2'})
        handler.rfile = io.BytesIO(b'{}')
        with patch.object(training, 'update_problem', return_value={'status':'open'}) as update:
            self.assertEqual(handler.do_POST()[0], 200)
            update.assert_called_once()
