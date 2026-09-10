import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'brain'))
import training
import server


class AssignmentTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        for name in [training.QUEUE,training.INDEX,'docs/SESSION.md']:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('# Queue\n\n| id | title | status | area | parallel-ok | path |\n|----|-------|--------|------|-------------|------|\n' if name!='docs/SESSION.md' else '# Session\n## Active goal\n- Assignment: A-017\n- Owner: Another worker\n\n## Next action\n- Continue A-017.\n')
        self.fields=dict(title='Fix focus',area='overlay',priority='P1',goal='The window gets focus',notes='Expected stable focus',checklist='- [ ] Reproduce the bug\n- [ ] Verify stable focus',allowed_paths='overlay/, tests/',forbidden_paths='brain/, actions/',blocked_by='',gate='',improvement='',out_of_scope='Unrelated work')
        training.PREVIEWS.clear()

    def tearDown(self):
        training.PREVIEWS.clear();self.temp.cleanup()

    def create(self,**kwargs):
        result=training.preview(self.root,dict(operation='assignment_save',fields=self.fields,**kwargs))
        return training.confirm(self.root,result['preview_id'])['assignment']

    def test_create_edit_real_files_and_preserve_ownership(self):
        old=(self.root/'docs/SESSION.md').read_text()
        proposal=training.preview(self.root,dict(operation='assignment_save',fields=self.fields))
        self.assertFalse((self.root/'docs/assignments/active').exists())
        aid=training.confirm(self.root,proposal['preview_id'])['assignment']
        self.assertIn(old.strip(),(self.root/'docs/SESSION.md').read_text())
        self.assertFalse((self.root/training.SLOTS).exists(),'creating a brief must not create a slot')
        detail=training.assignment_detail(self.root,aid)
        self.assertEqual(detail['priority'],'P1');self.assertEqual(detail['fields'],self.fields)
        path=self.root/detail['path'];path.write_text(path.read_text()+'\n## Custom evidence\nKeep this exact context.\n')
        detail=training.assignment_detail(self.root,aid)
        changed=dict(self.fields,title='Edited title',priority='P0',goal='Edited goal')
        proposal=training.preview(self.root,dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=changed))
        self.assertNotIn('Edited title',path.read_text())
        training.confirm(self.root,proposal['preview_id'])
        self.assertIn('## Custom evidence\nKeep this exact context.\n',path.read_text())
        for name in [training.QUEUE,training.INDEX]: self.assertIn(f'| {aid} | Edited title | queued |',(self.root/name).read_text())
        self.assertEqual(training.assignment_detail(self.root,aid)['fields'],changed)

    def test_allowed_and_forbidden_paths_are_optional(self):
        # A-023/ADR-034: paths are a soft hint, not a hard gate — isolation is area + worktree.
        fields=dict(self.fields,allowed_paths='',forbidden_paths='')
        proposal=training.preview(self.root,dict(operation='assignment_save',fields=fields))
        aid=training.confirm(self.root,proposal['preview_id'])['assignment']
        detail=training.assignment_detail(self.root,aid)
        self.assertEqual(detail['fields']['allowed_paths'],'')
        self.assertEqual(detail['fields']['forbidden_paths'],'')

    def test_blocked_by_and_gate_are_structured_optional_hints(self):
        # A-037: Blocked-by/Gate are parsed for claimability, not free prose — invalid shapes
        # are rejected up front so assignment-status.sh can trust the format later.
        for bad in (dict(blocked_by='not an id'), dict(gate='Not Lowercase')):
            with self.assertRaises(ValueError):
                training.preview(self.root,dict(operation='assignment_save',fields=dict(self.fields,**bad)))
        fields=dict(self.fields,blocked_by='A-038, A-030',gate='control-plane')
        aid=training.confirm(self.root,training.preview(self.root,dict(operation='assignment_save',fields=fields))['preview_id'])['assignment']
        detail=training.assignment_detail(self.root,aid)
        self.assertEqual(detail['fields']['blocked_by'],'A-038, A-030')
        self.assertEqual(detail['fields']['gate'],'control-plane')
        item=next(a for a in training.assignments(self.root) if a['id']==aid)
        self.assertEqual(item['blocked_by'],['A-038','A-030'])
        self.assertEqual(item['gate'],'control-plane')
        self.assertEqual(item['unmet_blocked_by'],['A-038','A-030'],'neither blocker is done yet')
        # Add a synthetic A-038 row marked done so unmet_blocked_by narrows to the remaining id.
        p=self.root/training.QUEUE
        p.write_text(p.read_text()+'| A-038 | Prereq | done | area:brain | NO | [done/A-038-x.md](done/A-038-x.md) |\n')
        item=next(a for a in training.assignments(self.root) if a['id']==aid)
        self.assertEqual(item['unmet_blocked_by'],['A-030'],'a done blocker drops out of unmet_blocked_by')

    def test_improvement_link_is_a_structured_optional_hint(self):
        # A-026: Improvement is a back-link into docs/ledger/ — same optional-hint validation
        # pattern as Blocked-by/Gate (A-037): shape-checked, not existence-checked.
        with self.assertRaises(ValueError):
            training.preview(self.root,dict(operation='assignment_save',fields=dict(self.fields,improvement='not an id')))
        fields=dict(self.fields,improvement='IMP-001')
        aid=training.confirm(self.root,training.preview(self.root,dict(operation='assignment_save',fields=fields))['preview_id'])['assignment']
        detail=training.assignment_detail(self.root,aid)
        self.assertEqual(detail['fields']['improvement'],'IMP-001')
        # Editing unrelated fields must preserve the Improvement link untouched.
        changed=dict(fields,title='Edited title')
        training.confirm(self.root,training.preview(self.root,dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=changed))['preview_id'])
        self.assertEqual(training.assignment_detail(self.root,aid)['fields']['improvement'],'IMP-001')

    def test_blocked_by_parser_strips_prose_and_dedupes(self):
        # A-037 hardening: parentheticals, em-dashes, and duplicates must not pollute the parsed id list.
        # This tests the parser robustness for briefs that may have prose (e.g. from manual edits or pre-validation).
        # The validation correctly rejects prose at save time, but the parser must handle it when reading.
        
        # Create a base assignment that we'll manually edit
        aid=self.create()
        detail=training.assignment_detail(self.root,aid)
        path=self.root/detail['path']
        
        # Test case 1: parenthetical prose like A-031 originally had
        # Manually edit the brief to add prose (bypassing validation)
        original_text=path.read_text()
        text1=original_text.replace('- **Blocked-by:**','- **Blocked-by:** A-028, A-030 (transitively also needs A-038, via A-028)')
        path.write_text(text1)
        item1=next(a for a in training.assignments(self.root) if a['id']==aid)
        self.assertEqual(item1['blocked_by'],['A-028','A-030'],'parenthetical prose must not add extra ids')
        
        # Test case 2: em-dash prose like A-027 originally had
        text2=original_text.replace('- **Blocked-by:**','- **Blocked-by:** none — blocked on a human decision, not an assignment id')
        path.write_text(text2)
        item2=next(a for a in training.assignments(self.root) if a['id']==aid)
        self.assertEqual(item2['blocked_by'],[],'none with em-dash prose yields empty blocked_by')
        
        # Test case 3: duplicates must collapse
        text3=original_text.replace('- **Blocked-by:**','- **Blocked-by:** A-028, A-030, A-028')
        path.write_text(text3)
        item3=next(a for a in training.assignments(self.root) if a['id']==aid)
        self.assertEqual(item3['blocked_by'],['A-028','A-030'],'duplicates must collapse to unique list')


    def test_stale_preview_and_claimed_assignment_rejected(self):
        aid=self.create();detail=training.assignment_detail(self.root,aid)
        payload=dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=self.fields)
        proposal=training.preview(self.root,payload)
        p=self.root/training.QUEUE;p.write_text(p.read_text().replace('| queued |','| in_progress |'))
        with self.assertRaisesRegex(ValueError,'changed'): training.confirm(self.root,proposal['preview_id'])
        with self.assertRaisesRegex(ValueError,'unclaimed'): training.preview(self.root,payload)
        self.assertFalse(training.assignment_detail(self.root,aid)['editable'])

    def test_stale_editor_and_symlink_or_untrusted_paths(self):
        aid=self.create();detail=training.assignment_detail(self.root,aid)
        (self.root/'docs/SESSION.md').write_text('New owner')
        with self.assertRaisesRegex(RuntimeError,'changed'):
            training.preview(self.root,dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=self.fields))
        p=self.root/detail['path'];p.unlink();p.symlink_to(ROOT/'START.md')
        with self.assertRaisesRegex(ValueError,'Symlinked'): training.assignment_detail(self.root,aid)
        p=self.root/training.QUEUE;p.write_text(p.read_text().replace('active/A-001-training.md','../../outside.md'))
        with self.assertRaises(ValueError): training.assignment_detail(self.root,aid)

    def test_problem_link_priority_and_stale_source(self):
        problem=training.reconcile_problems(self.root,[dict(id='run:one',title='Evidence',source='Journal eval',run_id='one')])[0]
        payload=dict(operation='assignment_save',fields=self.fields,problem_id=problem['id'],problem_revision=problem['revision'])
        proposal=training.preview(self.root,payload)
        brief=next(f['content'] for f in proposal['files'] if '/active/' in f['path'])
        self.assertIn('"run_id": "one"',brief);self.assertIn('**Priority:** P1',brief)
        training.update_problem(self.root,dict(id=problem['id'],revision=problem['revision'],priority='P0'))
        with self.assertRaisesRegex(ValueError,'changed'): training.confirm(self.root,proposal['preview_id'])

    def test_new_ids_consider_orphan_briefs_and_index_shape(self):
        path=self.root/'docs/assignments/done/A-030-orphan.md';path.parent.mkdir(parents=True);path.write_text('old')
        aid=self.create();self.assertEqual(aid,'A-031')
        index=self.root/training.INDEX;index.write_text('| A-031 | queued | Fix focus |\n')
        detail=training.assignment_detail(self.root,aid)
        proposal=training.preview(self.root,dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=dict(self.fields,title='Updated')))
        training.confirm(self.root,proposal['preview_id'])
        self.assertEqual(index.read_text(),'| A-031 | queued | Updated |\n')

    def test_validation_and_duplicate_rows(self):
        for key,value in [('title','Bad | table'),('goal','## Status\nhijack'),('checklist','no checklist'),('area','../'),('priority','urgent')]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                training.preview(self.root,dict(operation='assignment_save',fields=dict(self.fields,**{key:value})))
        aid=self.create();p=self.root/training.INDEX;p.write_text(p.read_text()+p.read_text())
        detail=training.assignment_detail(self.root,aid)
        with self.assertRaisesRegex(ValueError,'duplicated'):
            training.preview(self.root,dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=self.fields))

    def test_local_generation_never_writes_and_blocks_remote_models(self):
        draft={k:self.fields[k] for k in ('title','goal','checklist','out_of_scope')}
        before=(self.root/training.QUEUE).read_text()
        with patch.object(training,'ollama_request',side_effect=[{'model_info':{'general.architecture':'qwen2'}},{'message':{'content':json.dumps(draft)}}]) as request:
            result=training.generate_assignment(self.root,dict(mode='local',instructions='Fix focus'),'qwen2.5:3b')
        self.assertEqual(result['draft'],draft);self.assertEqual(request.call_args_list[0].args[0],'show')
        self.assertEqual(request.call_args_list[1].args[1]['stream'],False)
        self.assertNotIn('tools',request.call_args_list[1].args[1])
        self.assertEqual((self.root/training.QUEUE).read_text(),before)
        for info in [{'remote_host':'https://ollama.com','model_info':{'x':1}},{}]:
            with patch.object(training,'ollama_request',return_value=info) as request,self.assertRaisesRegex(ValueError,'local model'):
                training.generate_assignment(self.root,dict(mode='local',instructions='Fix focus'),'qwen2.5:3b')
            self.assertEqual(request.call_count,1,'reject remote before sending prompt')

    def test_manual_agent_prompt_and_generation_failures(self):
        with patch.object(training,'ollama_request') as request:
            result=training.generate_assignment(self.root,dict(mode='agent',instructions='Fix focus'),'unused')
            request.assert_not_called();self.assertIn('Return only JSON',result['prompt'])
        for response in [{'message':{'content':'invalid'}},{'message':{'content':'[]'}}]:
            with patch.object(training,'ollama_request',side_effect=[{'model_info':{'x':1}},response]),self.assertRaises(ValueError):
                training.generate_assignment(self.root,dict(mode='local',instructions='Fix focus'),'local')
            self.assertFalse(training.GENERATING.locked())
        with patch.object(training,'ollama_request',side_effect=TimeoutError('timeout')),self.assertRaises(TimeoutError):
            training.generate_assignment(self.root,dict(mode='local',instructions='Fix focus'),'local')
        self.assertFalse(training.GENERATING.locked())

    def test_endpoints_require_auth_and_generation_is_explicit(self):
        for endpoint,fn in [('assignment','assignment_detail'),('generate','generate_assignment')]:
            handler=object.__new__(server.Handler);handler.path='/v1/training/'+endpoint
            handler.headers={'Host':'127.0.0.1:7421','Content-Type':'application/json','Content-Length':'2'}
            handler.rfile=io.BytesIO(b'{}');handler.reply=lambda status,body:(status,body)
            with patch.object(training,fn) as call:
                self.assertEqual(handler.do_POST()[0],403);call.assert_not_called()
            handler.headers['X-Jarvis-Token']=server.TOKEN
            with patch.object(training,fn,return_value={}) as call:
                self.assertEqual(handler.do_POST()[0],200);call.assert_called_once()

    def test_write_failure_rolls_back_confirmed_assignment_files(self):
        aid=self.create();detail=training.assignment_detail(self.root,aid)
        proposal=training.preview(self.root,dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=dict(self.fields,title='Changed')))
        before={f['path']:(self.root/f['path']).read_text() for f in proposal['files']}
        original=Path.replace
        def fail_index(path,target):
            if str(target).endswith(training.INDEX): raise OSError('simulated write failure')
            return original(path,target)
        with patch.object(Path,'replace',fail_index),self.assertRaises(OSError):
            training.confirm(self.root,proposal['preview_id'])
        for path,body in before.items(): self.assertEqual((self.root/path).read_text(),body)

    def test_edit_records_default_priority_when_old_brief_has_none(self):
        aid=self.create();detail=training.assignment_detail(self.root,aid)
        p=self.root/detail['path'];p.write_text(p.read_text().replace('- **Priority:** P1\n',''))
        detail=training.assignment_detail(self.root,aid);fields=detail['fields']
        proposal=training.preview(self.root,dict(operation='assignment_save',assignment_id=aid,revision=detail['revision'],fields=fields))
        training.confirm(self.root,proposal['preview_id'])
        self.assertEqual(training.assignment_detail(self.root,aid)['priority'],'P2')
