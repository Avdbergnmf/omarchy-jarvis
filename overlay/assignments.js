const assignEl=id=>document.querySelector('#assign-'+id);
const assignmentFields=['title','area','priority','goal','notes','checklist','allowed_paths','forbidden_paths','out_of_scope'];
let selectedAssignment=null,linkedProblem=null,assignmentDirty=false,assignmentEpoch=0,assignmentSaveEpoch=null;
const assignmentDefaults=()=>({title:'',area:'overlay',priority:'P2',goal:'',notes:'',checklist:'- [ ] Reproduce the problem and record expected vs actual behavior\n- [ ] Implement the scoped improvement\n- [ ] Verify tests and update the human validation guide',allowed_paths:'overlay/, tests/, docs/assignments/, docs/SESSION.md, docs/PROGRESS.md, docs/DECISIONS.md',forbidden_paths:'brain/, actions/, skills/; approval bypass; automatic agent dispatch',out_of_scope:'Unrelated queue work, unreviewed skills and silent cloud spending.'});
function assignmentValues(){return Object.fromEntries(assignmentFields.map(key=>[key,assignEl(key).value]));}
function fillAssignment(fields){for(const key of assignmentFields)assignEl(key).value=fields[key]||'';}
function renderAssignments(data){
 const list=trainEl('assignments');list.innerHTML='';const filter=assignEl('filter').value||'all';
 const visible=data.assignments.filter(a=>filter==='all'||a.status===filter);
 assignEl('count').textContent=visible.length+' assignments · queue order';
 if(!visible.length)trainingLine(list,'No assignments in this view. Start a new draft or choose another status.');
 for(const item of visible){
  const row=document.createElement('button');row.type='button';row.className='assignment-row';
  row.textContent=item.id+' · '+item.title+'\n'+item.status+' · '+item.area+' · '+(item.priority||'priority not set')+' · parallel '+item.parallel;
  row.setAttribute('aria-pressed',String(selectedAssignment&&selectedAssignment.id===item.id));
  row.addEventListener('click',()=>selectAssignment(item.id));list.appendChild(row);
 }
 const picker=assignEl('problem'),prior=picker.value;picker.innerHTML='';trainingOption(picker,'','No linked problem');
 for(const problem of data.problems)trainingOption(picker,problem.id,problem.priority+' · '+problem.title);
 picker.value=data.problems.some(p=>p.id===prior)?prior:'';
 // Refresh never overwrites the editor or its revision; Save detects stale data.
}
function showAssignmentEditor(){
 assignEl('hint').hidden=true;document.querySelector('#assignment-form').hidden=false;trainingPanel('work');
 assignEl('agent-import').hidden=true;assignEl('agent-prompt').value='';assignEl('import-json').value='';
}
function newAssignment(problem=null,discard=false){
 if(assignmentDirty&&!discard){trainMessage('Save or discard the current assignment edits before starting another draft.',true);return;}
 assignmentEpoch++;selectedAssignment=null;linkedProblem=problem;assignmentDirty=false;showAssignmentEditor();
 assignEl('fields').disabled=false;assignEl('problem').disabled=false;assignEl('generation').hidden=false;
 assignEl('heading').textContent='New assignment';assignEl('status').textContent='New drafts are saved as queued, serial work.';
 assignEl('handoff').disabled=true;assignEl('body').textContent='No file saved yet.';
 const fields=assignmentDefaults();
 if(problem){fields.title=problem.title;fields.goal=problem.notes||problem.title;fields.notes=problem.notes;fields.priority=problem.priority;fields.area=problem.area;setDefaultScope(fields);}
 fillAssignment(fields);assignEl('problem').value=problem?problem.id:'';
 assignEl('source').textContent=problem?'Linked to '+problem.id+'; original evidence is preserved on Save/Add.':'No linked problem.';
 assignEl('title').focus();renderAssignments(trainingData);
}
function setDefaultScope(fields){
 fields.allowed_paths=fields.area+'/, tests/, docs/assignments/, docs/SESSION.md, docs/PROGRESS.md, docs/DECISIONS.md';
 fields.forbidden_paths=['overlay','brain','actions','skills'].filter(a=>a!==fields.area).map(a=>a+'/').join(', ')+'; approval bypass; automatic agent dispatch';
}
async function selectAssignment(id,discard=false){
 if(assignmentDirty&&!discard){trainMessage('Save or discard assignment edits before selecting another brief.',true);return;}
 const epoch=++assignmentEpoch;trainMessage('Loading assignment…');
 try{
  const detail=await post('/v1/training/assignment',{assignment_id:id});if(epoch!==assignmentEpoch)return;
  selectedAssignment=detail;linkedProblem=null;assignmentDirty=false;showAssignmentEditor();fillAssignment(detail.fields);
  assignEl('heading').textContent=detail.id;assignEl('status').textContent=detail.status+' · parallel '+detail.parallel+(detail.editable?' · edits require confirmation':' · read-only while owned or closed');
  assignEl('fields').disabled=!detail.editable;assignEl('problem').disabled=true;assignEl('generation').hidden=true;
  assignEl('source').textContent=detail.path;assignEl('body').textContent=detail.body;assignEl('handoff').disabled=false;
  renderAssignments(trainingData);trainMessage('Loaded '+id+'.');
 }catch(error){if(epoch===assignmentEpoch)trainMessage(error.message,true);}
}
async function assignmentSaved(id){
 if(assignmentSaveEpoch!==assignmentEpoch){trainMessage(id+' saved; newer editor changes have been kept. Reload before saving again.');return;}
 assignmentDirty=false;await selectAssignment(id,true);trainMessage(id+' saved. Hand off to agent when ready.');
}
function assignmentProblemPayload(){return linkedProblem?{problem_id:linkedProblem.id,problem_revision:linkedProblem.revision}:{};}
async function generateAssignment(){
 const epoch=assignmentEpoch;assignEl('generate').disabled=true;trainMessage('Preparing assignment draft…');
 try{
  const result=await post('/v1/training/generate',{mode:assignEl('generator').value,instructions:assignEl('goal').value||assignEl('title').value,area:assignEl('area').value,allowed_paths:assignEl('allowed_paths').value,forbidden_paths:assignEl('forbidden_paths').value,...assignmentProblemPayload()});
  if(epoch!==assignmentEpoch){trainMessage('Draft returned after the editor changed; it was not applied. Generate again if needed.');return;}
  if(result.prompt){assignEl('agent-prompt').value=result.prompt;assignEl('agent-import').hidden=false;assignEl('agent-prompt').focus();}
  else applyGeneratedDraft(result.draft);
  trainMessage(result.message);
 }catch(error){trainMessage(error.message,true);}
 finally{assignEl('generate').disabled=false;}
}
function applyGeneratedDraft(draft){
 const limits={title:140,goal:1400,checklist:1400,out_of_scope:1200};
 if(!draft||typeof draft!=='object'||Object.keys(draft).sort().join(',')!==Object.keys(limits).sort().join(','))throw Error('Import title, goal, checklist and out_of_scope as a JSON object.');
 for(const [key,limit] of Object.entries(limits))if(typeof draft[key]!=='string'||!draft[key].trim()||draft[key].length>limit)throw Error('Invalid or oversized '+key+' in draft.');
 if(!draft.checklist.split('\n').every(line=>/^- \[[ xX]\] .+/.test(line)))throw Error('Checklist needs one - [ ] verification step per line.');
 for(const key of Object.keys(limits))assignEl(key).value=draft[key];
 assignmentDirty=true;assignmentEpoch++;
}
document.querySelector('#assignment-form').addEventListener('input',()=>{assignmentDirty=true;assignmentEpoch++;});
document.querySelector('#assignment-form').addEventListener('submit',event=>{
 event.preventDefault();assignmentSaveEpoch=assignmentEpoch;
 previewTraining({operation:'assignment_save',fields:assignmentValues(),...(selectedAssignment?{assignment_id:selectedAssignment.id,revision:selectedAssignment.revision}:assignmentProblemPayload())});
});
assignEl('new').addEventListener('click',()=>newAssignment());
assignEl('filter').addEventListener('change',()=>renderAssignments(trainingData));
assignEl('reload').addEventListener('click',()=>selectedAssignment?selectAssignment(selectedAssignment.id,true):newAssignment(null,true));
assignEl('problem').addEventListener('change',()=>{
 const id=assignEl('problem').value;
 linkedProblem=trainingData.problems.find(p=>p.id===id)||null;assignmentEpoch++;assignmentDirty=true;
 if(linkedProblem){
  const fields=assignmentValues();fields.area=linkedProblem.area;fields.priority=linkedProblem.priority;fields.title=linkedProblem.title;fields.goal=linkedProblem.notes||linkedProblem.title;fields.notes=linkedProblem.notes;setDefaultScope(fields);fillAssignment(fields);
 }
 assignEl('source').textContent=linkedProblem?'Linked to '+linkedProblem.id+'; original evidence is preserved on Save/Add.':'No linked problem.';
});
assignEl('area').addEventListener('change',()=>{if(!selectedAssignment){const fields=assignmentValues();setDefaultScope(fields);fillAssignment(fields);}});
assignEl('generator').addEventListener('change',()=>{
 assignEl('generation-note').textContent=assignEl('generator').value==='agent'?'Prepare a prompt to paste yourself. Your chosen agent may use paid services. Jarvis will not launch or contact it.':'Generate uses the configured downloaded local model. Review its draft before saving.';
 assignEl('generate').textContent=assignEl('generator').value==='agent'?'Prepare agent prompt':'Generate draft';
});
assignEl('generate').addEventListener('click',generateAssignment);
assignEl('copy-prompt').addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText(assignEl('agent-prompt').value);trainMessage('Prompt copied. Paste it into your chosen agent.');}
 catch(error){assignEl('agent-prompt').focus();assignEl('agent-prompt').select();trainMessage('Select and copy the prompt manually.');}
});
assignEl('import').addEventListener('click',()=>{
 try{applyGeneratedDraft(JSON.parse(assignEl('import-json').value));trainMessage('Draft imported into the form. Review it, then preview Save/Add.');}
 catch(error){trainMessage(error.message,true);}
});
assignEl('handoff').addEventListener('click',()=>{
 if(!selectedAssignment||assignmentDirty){trainMessage('Save the assignment before preparing its handoff.',true);return;}
 trainEl('assignment').value=selectedAssignment.id;trainingPanel('agents');trainEl('slot').focus();trainMessage('Choose an agent slot and preview the handoff for '+selectedAssignment.id+'. Nothing has been sent.');
});
