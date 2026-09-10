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
        self.assertIn('no agent was contacted',committed['message'])
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
        self.assertIn('Nothing is sent automatically',queued['message'])
        training.confirm(self.root,queued['preview_id'])
        self.assertIn(slot['current_assignment'],training.slots(self.root)['agents'][0]['queued_assignment_ids'])
        idle=training.preview(self.root,dict(operation='slot',slot_id=slot['id'],status='idle'))
        training.confirm(self.root,idle['preview_id'])
        payload['mode']='now'
        ready=training.preview(self.root,payload)
        training.confirm(self.root,ready['preview_id'])
        self.assertEqual(training.slots(self.root)['agents'][0]['queued_assignment_ids'],[])

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
