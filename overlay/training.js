const trainEl=id=>document.querySelector('#train-'+id);
let trainingData=null,trainingPreview=null,lastPreviewPayload=null;
let previewLoad=0,trainingLoad=0,activeProblem=null,problemDirty=false;
function trainMessage(text,error=false){trainEl('message').textContent=text;trainEl('message').className=error?'error':'';}
function trainingPanel(name){
 for(const panel of ['problems','validate','work','agents','latency']){
  trainEl('panel-'+panel).hidden=panel!==name;
  trainEl('nav-'+panel).setAttribute('aria-pressed',String(panel===name));
 }
 if(name==='latency'&&typeof refreshLatency==='function')refreshLatency();
}
function trainingLine(parent,text){const p=document.createElement('p');p.textContent=text;parent.appendChild(p);return p;}
function trainingOption(parent,value,label){const option=document.createElement('option');option.value=value;option.textContent=label;parent.appendChild(option);}
async function refreshTraining(){
 const load=++trainingLoad;trainMessage('Loading local evidence…');trainEl('refresh').disabled=true;
 try{
  const data=await get('/v1/training');if(load!==trainingLoad)return;
  trainingData=data;renderTraining(data);trainMessage(data.warnings.join(' '));
 }catch(error){if(load===trainingLoad)trainMessage(error.message,true);}
 finally{trainEl('refresh').disabled=false;}
}
function renderTraining(data){
 trainEl('version').textContent='Jarvis '+data.version+' · '+data.revision;
 const metrics=trainEl('metrics');metrics.innerHTML='';
 const labels={runs:'Runs',good:'Good',neutral:'Review later',bad:'Bad',flags:'Eval flags',executed:'Executed',denied:'Denied'};
 const max=Math.max(1,...Object.values(data.metrics));
 for(const [key,value] of Object.entries(data.metrics)){
  const card=document.createElement('div');card.className='metric-card';
  trainingLine(card,String(value));trainingLine(card,labels[key]);
  const bar=document.createElement('meter');bar.min=0;bar.max=max;bar.value=value;bar.setAttribute('aria-label',labels[key]);card.appendChild(bar);metrics.appendChild(card);
 }
 trainEl('period').textContent=data.period+(data.sampled?' · bounded recent sample, not complete totals':'');
 trainEl('context').textContent=data.context.join(' · ');trainEl('session').textContent=data.session;
 renderProblems();
 if(typeof renderAssignments==='function')renderAssignments(data);
 const selection=trainEl('assignment'),previousAssignment=selection.value;selection.innerHTML='';
 for(const item of data.assignments){
  if(['queued','in_progress','blocked'].includes(item.status))trainingOption(selection,item.id,item.id+' — '+item.title);
 }
 if(data.assignments.some(a=>a.id===previousAssignment))selection.value=previousAssignment;
 if(typeof renderAgents==='function')renderAgents(data);
 if(typeof renderValidations==='function')renderValidations(data.validations||[]);
}
function trainingTarget(){return {slot_id:trainEl('slot').value,label:trainEl('agent-label').value,kind:trainEl('kind').value,mode:trainEl('mode').value,template:trainEl('template').value,reasoning_effort:trainEl('effort').disabled?'':trainEl('effort').value};}
async function previewTraining(payload){
 const load=++previewLoad;
 trainingPreview=null;lastPreviewPayload=payload;trainEl('preview').hidden=true;trainEl('result').hidden=true;
 try{
  const result=await post('/v1/training/preview',payload);if(load!==previewLoad)return;trainingPreview=result.preview_id;
  trainEl('preview-message').textContent=result.message;
  trainEl('preview-files').textContent=result.files.map(f=>'FILE: '+f.path+'\n'+f.content).join('\n\n');
  trainEl('preview').hidden=false;trainEl('confirm').focus();trainMessage('Review the exact file contents. Nothing has been written yet.');
 }catch(error){trainMessage(error.message,true);}
}
for(const name of ['problems','validate','work','agents','latency'])trainEl('nav-'+name).addEventListener('click',()=>trainingPanel(name));
trainEl('filter').addEventListener('change',renderProblems);
trainEl('new').addEventListener('click',()=>newAssignment());
trainEl('refresh').addEventListener('click',refreshTraining);
document.querySelector('#work-form').addEventListener('submit',event=>{
 event.preventDefault();previewTraining({...trainingTarget(),operation:'work',assignment_id:trainEl('assignment').value});
});
trainEl('cancel').addEventListener('click',()=>{previewLoad++;trainingPreview=null;trainEl('preview').hidden=true;trainMessage('Cancelled. No files written.');});
trainEl('confirm').addEventListener('click',async()=>{
 if(!trainingPreview)return;trainEl('confirm').disabled=true;
 const id=trainingPreview;trainingPreview=null;
 try{
  const result=await post('/v1/training/confirm',{preview_id:id});trainEl('preview').hidden=true;
  trainEl('result-message').textContent=result.message;trainEl('handoff').value=result.handoff;
  trainEl('paths').textContent=result.paths.join('\n');trainEl('result').hidden=false;
  trainEl('copy').hidden=!result.handoff;trainEl('handoff').hidden=!result.handoff;
  await refreshTraining();
  if(result.assignment&&typeof assignmentSaved==='function')await assignmentSaved(result.assignment);
  if(result.validation&&typeof validationSaved==='function')validationSaved(result.validation);
  // A-018: a confirmed "prepare now" handoff always yields a visible window, not a
  // hidden background job — the slot id may be freshly minted, so look it up by the
  // assignment it now holds rather than trusting a client-side "new" placeholder.
  if(lastPreviewPayload&&lastPreviewPayload.operation==='work'&&lastPreviewPayload.mode==='now'&&typeof openAgentWindow==='function'){
   const slot=trainingData.agents.find(s=>s.current_assignment===lastPreviewPayload.assignment_id);
   if(slot&&slot.kind!=='human')await openAgentWindow(slot.id);
  }
  lastPreviewPayload=null;
 }catch(error){trainMessage(error.message,true);}
 finally{trainEl('confirm').disabled=false;}
});
trainEl('copy').addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText(trainEl('handoff').value);trainMessage('Handoff copied. Paste it into your agent chat.');}
 catch(error){trainEl('handoff').focus();trainEl('handoff').select();trainMessage('Select and copy the handoff text manually.');}
});

function sourceClass(problem){
 if(problem.id.startsWith('bad:'))return 'bad';
 if(problem.id.startsWith('validation:'))return 'validation';
 if(problem.id.startsWith('run:'))return 'eval';
 if(problem.id.startsWith('backlog:')||problem.id.startsWith('issue:'))return 'backlog';
 return 'feedback';
}
function renderProblems(){
 const list=trainEl('problems');list.innerHTML='';
 const filter=trainEl('filter').value||'open';
 const visible=trainingData.problems.filter(p=>filter==='all'||p.status===filter);
 trainEl('problem-count').textContent=visible.length+' '+(filter==='all'?'retained':filter)+' problems · priority P0 → P3';
 if(!visible.length)trainingLine(list,'No '+(filter==='all'?'retained':filter)+' problems. Refresh for new evidence or add an observation.');
 for(const problem of visible){
  const row=document.createElement('div');row.className='problem-row source-'+sourceClass(problem)+(activeProblem&&activeProblem.id===problem.id?' selected':'');
  const badges=document.createElement('div');badges.className='problem-badges';
  for(const label of [problem.source,problem.priority,problem.area,problem.status]){
   const badge=document.createElement('span');badge.className='problem-badge';badge.textContent=label;badges.appendChild(badge);
  }
  row.appendChild(badges);
  const title=document.createElement('button');title.type='button';title.className='problem-title';title.textContent=problem.title;
  title.addEventListener('click',()=>selectProblem(problem));row.appendChild(title);
  const actions=document.createElement('div');actions.className='problem-actions';
  for(const [label,status] of problem.status==='open'?[['✓ Done','done'],['Dismiss','dismissed']]:[['Reopen','open']]){
   const button=document.createElement('button');button.type='button';button.textContent=label;button.setAttribute('aria-label',label+': '+problem.title);
   button.addEventListener('click',async()=>{
    if(problemDirty&&activeProblem&&activeProblem.id===problem.id){trainMessage('Save or discard the current edits before changing status.',true);return;}
    button.disabled=true;
    try{await post('/v1/training/problem',{id:problem.id,revision:problem.revision,status});await refreshTraining();}
    catch(error){trainMessage(error.message,true);}finally{button.disabled=false;}
   });actions.appendChild(button);
  }
  const remove=document.createElement('button');remove.type='button';remove.className='danger';remove.textContent='Delete…';remove.setAttribute('aria-label','Delete: '+problem.title);
  remove.addEventListener('click',()=>previewTraining({operation:'problem_delete',id:problem.id,revision:problem.revision}));actions.appendChild(remove);
  row.appendChild(actions);list.appendChild(row);
 }
 if(activeProblem&&!trainingData.problems.some(p=>p.id===activeProblem.id)){
  activeProblem=null;problemDirty=false;document.querySelector('#problem-form').hidden=true;trainEl('detail-hint').hidden=false;
 }else if(activeProblem&&!problemDirty){
  fillProblem(trainingData.problems.find(p=>p.id===activeProblem.id));
 }
}
function fillProblem(problem){
 activeProblem=problem;
 for(const field of ['title','notes','priority','area','status'])trainEl('problem-'+field).value=problem[field];
 trainEl('problem-context').textContent=JSON.stringify(problem.evidence,null,2);
 document.querySelector('#problem-form').hidden=false;trainEl('detail-hint').hidden=true;
}
function selectProblem(problem){
 if(problemDirty){trainMessage('Save the current edits before selecting another problem.',true);return;}
 fillProblem(problem);renderProblems();trainEl('problem-title').focus();
}
async function saveProblem(){
 if(!activeProblem)return null;
 trainEl('save').disabled=true;trainEl('generate').disabled=true;
 try{
  const payload={id:activeProblem.id,revision:activeProblem.revision};
  for(const field of ['title','notes','priority','area','status'])payload[field]=trainEl('problem-'+field).value;
  const saved=await post('/v1/training/problem',payload);activeProblem=saved;problemDirty=false;
  trainingData.problems=trainingData.problems.map(p=>p.id===saved.id?saved:p).sort((a,b)=>a.priority.localeCompare(b.priority)||a.title.localeCompare(b.title));
  renderProblems();trainMessage('Problem saved locally.');return saved;
 }catch(error){trainMessage(error.message,true);return null;}
 finally{trainEl('save').disabled=false;trainEl('generate').disabled=false;}
}
document.querySelector('#problem-form').addEventListener('input',()=>{problemDirty=true;});
document.querySelector('#problem-form').addEventListener('submit',event=>{event.preventDefault();saveProblem();});
trainEl('generate').addEventListener('click',async()=>{
 const problem=await saveProblem();if(!problem)return;
 newAssignment(problem);
});

trainEl('discard').addEventListener('click',async()=>{problemDirty=false;await refreshTraining();});
