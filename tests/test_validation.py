import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'brain'))
import server
import training
import validation


class ValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/'docs/validation').mkdir(parents=True)
        for path in (validation.CATALOG,validation.FEATURES):
            (self.root/path).write_text((ROOT/path).read_text())
        # Fixtures must not depend on Alex's real human-validation history.
        catalog = json.loads((self.root/validation.CATALOG).read_text())
        for feature in catalog['features']:
            feature.update(status='unvalidated', last_run=None, jarvis_version=None)
        (self.root/validation.CATALOG).write_text(json.dumps(catalog))
        self.item=validation.list_features(self.root)[0]
        self.payload=dict(operation='validation',feature_id=self.item['id'],definition_hash=self.item['definition_hash'],outcome='validated',attempted=True,notes='Observed expected behavior',run_id='evidence-run')

    def tearDown(self):
        training.PREVIEWS.clear()
        self.temp.cleanup()

    def test_schema_seed_and_missing_attestation(self):
        self.assertGreaterEqual(len(validation.load(self.root)['features']),9)
        self.assertTrue(all(i['status']=='unvalidated' for i in validation.list_features(self.root)))
        with self.assertRaisesRegex(ValueError,'guided steps'):
            training.preview(self.root,dict(self.payload,attempted=False),'0.5.1','abc')
        with self.assertRaisesRegex(ValueError,'actual-outcome'):
            training.preview(self.root,dict(self.payload,outcome='failed',notes=''),'0.5.1','abc')

    def test_result_requires_confirm_and_records_version(self):
        original=(self.root/validation.CATALOG).read_text()
        result=training.preview(self.root,self.payload,'0.5.1','abc')
        self.assertEqual((self.root/validation.CATALOG).read_text(),original)
        saved=training.confirm(self.root,result['preview_id'])
        item=validation.load(self.root)['features'][0]
        self.assertEqual(item['status'],'validated')
        self.assertEqual(item['last_run']['jarvis_version'],'0.5.1')
        self.assertEqual(item['last_run']['git_describe'],'abc')
        self.assertEqual(item['last_run']['run_id'],'evidence-run')
        self.assertEqual(saved['validation']['outcome'],'validated')
        self.assertIn('| validated | 0.5.1 |',(self.root/validation.FEATURES).read_text())

    def test_changed_definition_requires_retest(self):
        result=training.preview(self.root,self.payload,'0.5.1','abc')
        training.confirm(self.root,result['preview_id'])
        catalog=validation.load(self.root)
        catalog['features'][0]['expected']='A new behavior'
        (self.root/validation.CATALOG).write_text(json.dumps(catalog))
        self.assertEqual(validation.list_features(self.root)[0]['status'],'unvalidated')
        with self.assertRaisesRegex(ValueError,'steps changed'):
            training.preview(self.root,self.payload,'0.5.1','abc')

    def test_failed_result_enters_reviewed_intake_with_correct_context(self):
        preview=training.preview(self.root,dict(self.payload,outcome='failed',notes='The cancel button did not work'),'0.5.1','abc')
        saved=training.confirm(self.root,preview['preview_id'])['validation']
        server.RUNS['unrelated-later-run']={'status':'done','prompt':'unrelated'}
        server.RUNS['evidence-run']={'status':'done','prompt':'the real test','plan':{'actions':[]},'journal':[]}
        class ImmediateThread:
            def __init__(self,target,args,**kwargs): self.target,self.args=target,args
            def start(self): self.target(*self.args)
        try:
            with patch.object(server,'ROOT',self.root),patch.object(server,'LOGS',self.root/'logs'),patch.object(server.threading,'Thread',ImmediateThread),patch.dict(server.CONFIG,approval_mode='always',show_notifications=False):
                started=server.start_validation_report(saved['feature_id'],saved['record_id'])
                rid=started['run_id']
                self.assertEqual(server.RUNS[rid]['status'],'awaiting_answer')
                self.assertEqual(server.RUNS[rid]['intake']['context']['last_run_id'],'evidence-run')
                server.handle_answer(rid,'skip')
                self.assertEqual(server.RUNS[rid]['status'],'awaiting_approval')
                body=server.RUNS[rid]['draft']['body']
                self.assertIn('The cancel button did not work',body)
                self.assertIn(self.item['expected'],body)
                self.assertIn('0.5.1',body)
                self.assertNotIn('unrelated-later-run',body)
                server.handle_deny(rid)
                server.RUNS.pop(rid)
        finally:
            server.RUNS.pop('evidence-run',None);server.RUNS.pop('unrelated-later-run',None)
            if server.BUSY.locked(): server.BUSY.release()
            server.BUSY_RUN_ID=None

    def test_catalog_duplicates_and_stale_report_rejected(self):
        catalog=validation.load(self.root)
        catalog['features'].append(catalog['features'][0])
        (self.root/validation.CATALOG).write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError,'duplicate'): validation.load(self.root)
        (self.root/validation.CATALOG).write_text((ROOT/validation.CATALOG).read_text())
        with self.assertRaisesRegex(ValueError,'missing'):
            validation.report_evidence(self.root,self.item['id'],'unknown')

    def test_auto_steps_carry_a_literal_prompt_but_stay_optional(self):
        # A-020: a guided step may be a plain string (human) or {text,kind,prompt}
        # (auto) — Training submits only an auto step's own prompt on the human's
        # behalf; it never judges the result or approves/denies anything.
        catalog=validation.load(self.root)
        item=catalog['features'][0]
        item['steps']=['Open Jarvis.',{'text':'Type: hello. Confirm a reply.','kind':'auto','prompt':'hello'}]
        (self.root/validation.CATALOG).write_text(json.dumps(catalog))
        loaded=validation.list_features(self.root)[0]
        self.assertEqual(validation.step_kind(loaded['steps'][0]),'human')
        self.assertEqual(validation.step_kind(loaded['steps'][1]),'auto')
        self.assertEqual(validation.step_text(loaded['steps'][1]),'Type: hello. Confirm a reply.')

    def test_auto_step_without_a_prompt_is_rejected(self):
        catalog=validation.load(self.root)
        catalog['features'][0]['steps']=[{'text':'Type: hello.','kind':'auto'}]
        (self.root/validation.CATALOG).write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError,'literal chat prompt'):
            validation.load(self.root)

    def test_report_evidence_seed_joins_mixed_step_shapes(self):
        catalog=validation.load(self.root)
        item=catalog['features'][0]
        item['steps']=['Open Jarvis.',{'text':'Type: hello.','kind':'auto','prompt':'hello'}]
        item['status']='failed'
        item['last_run']=dict(id='rec1',result='failed',jarvis_version='0.5.1',git_describe='abc',notes='Did not reply',definition_hash=validation.definition_hash(item))
        (self.root/validation.CATALOG).write_text(json.dumps(catalog))
        found,last,seed=validation.report_evidence(self.root,item['id'],'rec1')
        self.assertIn('Open Jarvis.; Type: hello.',seed)
