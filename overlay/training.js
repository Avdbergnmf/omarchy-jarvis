const trainView=document.querySelector('#training-view');
const chatView=document.querySelector('#chat-view');
const trainEl=id=>document.querySelector('#train-'+id);
let trainingData=null,trainingPreview=null,trainingSource='Manual training observation';
let trainingLoad=0;
function trainMessage(text,error=false){trainEl('message').textContent=text;trainEl('message').className=error?'error':'';}
function leaveTraining(){
 if(trainView.hidden)return false;
 trainingLoad++;trainingPreview=null;trainEl('preview').hidden=true;
 trainView.hidden=true;chatView.hidden=false;input.focus();return true;
}
async function enterTraining(){
 hideCommands();chatView.hidden=true;trainView.hidden=false;
 trainEl('back').focus();await refreshTraining();
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
 const problems=trainEl('problems');problems.innerHTML='';
 if(!data.problems.length)trainingLine(problems,'No problems in the available evidence.');
 for(const problem of data.problems){
  const button=document.createElement('button');button.type='button';button.textContent=problem.source+' · '+problem.title;
  button.addEventListener('click',()=>{
   trainEl('title').value=problem.title.slice(0,140);
   trainingSource=[problem.id,problem.url||problem.path||'',problem.run_id?'run_id='+problem.run_id:'',problem.version?'jarvis_version='+problem.version:''].filter(Boolean).join(' ');
   trainEl('comments').focus();trainMessage('Selected '+problem.source+'. Add the expected outcome, then preview.');
  });problems.appendChild(button);
 }
 const assignmentList=trainEl('assignments');assignmentList.innerHTML='';const selection=trainEl('assignment');selection.innerHTML='';
 for(const item of data.assignments){
  trainingLine(assignmentList,item.id+' · '+item.status+' · '+item.title);
  if(['queued','in_progress','blocked'].includes(item.status))trainingOption(selection,item.id,item.id+' — '+item.title);
 }
 const agentList=trainEl('agents');agentList.innerHTML='';const picker=trainEl('slot');const previous=picker.value;picker.innerHTML='';trainingOption(picker,'new','New agent slot');
 for(const slot of data.agents){
  trainingOption(picker,slot.id,slot.label+' ('+(slot.busy?'busy':'idle')+')');
  const row=document.createElement('div');trainingLine(row,slot.label+' · '+(slot.busy?'busy':'idle')+' · current: '+(slot.current_assignment||'none')+' · queued: '+(slot.queued_assignment_ids.join(', ')||'none'));
  if(slot.last_handoff)trainingLine(row,'Last handoff: '+slot.last_handoff);
  const button=document.createElement('button');button.type='button';button.textContent='Preview marking '+(slot.status==='busy'?'idle':'busy');
  button.addEventListener('click',()=>previewTraining({operation:'slot',slot_id:slot.id,status:slot.status==='busy'?'idle':'busy'}));row.appendChild(button);agentList.appendChild(row);
 }
 if(!data.agents.length)trainingLine(agentList,'No local slots yet. Preparing a handoff can create one.');
 picker.value=data.agents.some(s=>s.id===previous)?previous:'new';
 if(typeof renderValidations==='function')renderValidations(data.validations||[]);
}
function trainingTarget(){return {slot_id:trainEl('slot').value,label:trainEl('agent-label').value,kind:trainEl('kind').value,mode:trainEl('mode').value,template:trainEl('template').value};}
async function previewTraining(payload){
 trainingPreview=null;trainEl('preview').hidden=true;trainEl('result').hidden=true;
 try{
  const result=await post('/v1/training/preview',payload);trainingPreview=result.preview_id;
  trainEl('preview-message').textContent=result.message;
  trainEl('preview-files').textContent=result.files.map(f=>'FILE: '+f.path+'\n'+f.content).join('\n\n');
  trainEl('preview').hidden=false;trainEl('confirm').focus();trainMessage('Review the exact file contents. Nothing has been written yet.');
 }catch(error){trainMessage(error.message,true);}
}
trainEl('btn').addEventListener('click',enterTraining);
trainEl('back').addEventListener('click',leaveTraining);
trainEl('refresh').addEventListener('click',refreshTraining);
document.querySelector('#assignment-form').addEventListener('submit',event=>{
 event.preventDefault();previewTraining({...trainingTarget(),operation:'assignment',title:trainEl('title').value,comments:trainEl('comments').value,area:trainEl('area').value,source:trainingSource});
});
document.querySelector('#work-form').addEventListener('submit',event=>{
 event.preventDefault();previewTraining({...trainingTarget(),operation:'work',assignment_id:trainEl('assignment').value});
});
trainEl('cancel').addEventListener('click',()=>{trainingPreview=null;trainEl('preview').hidden=true;trainMessage('Cancelled. No files written.');});
trainEl('confirm').addEventListener('click',async()=>{
 if(!trainingPreview)return;trainEl('confirm').disabled=true;
 const id=trainingPreview;trainingPreview=null;
 try{
  const result=await post('/v1/training/confirm',{preview_id:id});trainEl('preview').hidden=true;
  trainEl('result-message').textContent=result.message;trainEl('handoff').value=result.handoff;
  trainEl('paths').textContent=result.paths.join('\n');trainEl('result').hidden=false;
  trainEl('copy').hidden=!result.handoff;trainEl('handoff').hidden=!result.handoff;
  await refreshTraining();
  if(result.validation&&typeof validationSaved==='function')validationSaved(result.validation);
 }catch(error){trainMessage(error.message,true);}
 finally{trainEl('confirm').disabled=false;}
});
trainEl('copy').addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText(trainEl('handoff').value);trainMessage('Handoff copied. Paste it into your agent chat.');}
 catch(error){trainEl('handoff').focus();trainEl('handoff').select();trainMessage('Select and copy the handoff text manually.');}
});
