const validationEl=id=>document.querySelector('#validation-'+id);
let validationItems=[],validationActive=null,validationChecks=[],validationReport=null;
function stepText(step){return typeof step==='string'?step:step.text;}
function stepKind(step){return typeof step==='string'?'human':(step.kind||'human');}
function reportLine(item){
 const last=item.last_run;
 if(!last)return'';
 return last.result+' · '+last.ts.slice(0,10)+' · Jarvis '+last.jarvis_version+(last.notes?' · '+last.notes:'');
}
function renderValidations(items){
 validationItems=items;
 const pending=items.filter(item=>item.status!=='validated');
 validationEl('count').textContent=pending.length+' features need human review';
 const list=validationEl('list');list.innerHTML='';
 const visible=validationEl('show-all').checked?items:pending;
 if(!visible.length)trainingLine(list,'No pending human checks. Include validated features to repeat a test.');
 for(const item of visible){
  const row=document.createElement('div');row.className='validation-row';
  const button=document.createElement('button');button.type='button';button.textContent=item.title+' · '+item.status;
  button.addEventListener('click',()=>startValidation(item));row.appendChild(button);
  // A-020: the report (date/version/outcome/notes) is visible right in the list —
  // selecting an item is for retesting, not the only way to see what was last found.
  const report=reportLine(item);
  if(report)trainingLine(row,report);
  list.appendChild(row);
 }
 if(validationActive){
  const current=items.find(i=>i.id===validationActive.id);
  if(!current||current.definition_hash!==validationActive.definition_hash){
   validationActive=null;validationEl('guide').hidden=true;trainMessage('Validation definition changed; select it again and repeat the guided test.');
  }else{validationActive=current;showLastValidation(current);}
 }
}
function showLastValidation(item){
 if(typeof trainingReportReady==='function')validationEl('open-chat').hidden=true;
 const last=item.last_run;
 validationEl('last').textContent=last?'Last human result: '+last.result+' · '+last.ts+' · Jarvis '+last.jarvis_version+' · '+last.notes:'No human result recorded yet.';
 validationReport=item.status==='failed'&&last?{feature_id:item.id,record_id:last.id}:null;
 validationEl('report').hidden=!validationReport;
}
function startValidation(item){
 validationActive=item;validationChecks=[];
 validationEl('guide').hidden=false;validationEl('title').textContent=item.title;
 validationEl('version').textContent='Testing Jarvis '+(trainingData?trainingData.version:'current')+' · feature shipped '+item.jarvis_version_shipped;
 const steps=validationEl('steps');steps.innerHTML='';
 item.steps.forEach((step,index)=>{
  const wrap=document.createElement('div');wrap.className='validation-step';
  const label=document.createElement('label');
  const checkbox=document.createElement('input');checkbox.type='checkbox';
  checkbox.addEventListener('change',()=>{validationEl('verify').disabled=!validationChecks.every(c=>c.checked);});
  const span=document.createElement('span');span.textContent=(index+1)+'. '+stepText(step);
  label.appendChild(checkbox);label.appendChild(span);wrap.appendChild(label);validationChecks.push(checkbox);
  if(stepKind(step)==='auto'){
   const run=document.createElement('button');run.type='button';run.textContent='Run this step';
   const result=document.createElement('p');result.className='muted validation-step-result';
   run.addEventListener('click',()=>runAutoStep(step,run,result));
   wrap.appendChild(run);wrap.appendChild(result);
  }
  steps.appendChild(wrap);
 });
 validationEl('expected').textContent=item.expected;validationEl('notes').value='';validationEl('run').value='';
 validationEl('verify').disabled=true;showLastValidation(item);validationEl('notes').focus();
}
// A-020: Training performs only the mechanical part (typing the prompt, pressing Enter) of
// an "auto" step via the same /v1/run a chat send uses — never judgment, never Cancel/Run
// approval, which stay in the real chat overlay. The step's own checkbox still needs an
// explicit human tick after reading what came back.
async function runAutoStep(step,button,result){
 button.disabled=true;result.textContent='Running…';
 try{
  const {run_id}=await post('/v1/run',{prompt:step.prompt});
  validationEl('run').value=run_id;
  let state;
  for(;;){
   state=await get('/v1/runs/'+run_id);
   if(!['planning','running'].includes(state.status))break;
   await new Promise(resolve=>setTimeout(resolve,700));
  }
  if(state.status==='awaiting_approval')result.textContent='Prompt submitted — a plan is now awaiting your approval in chat. Review and decide there, then judge this step.';
  else if(state.status==='awaiting_answer')result.textContent='Prompt submitted — chat is asking a follow-up question there.';
  else result.textContent='Reply: '+(state.reply||'(no reply)');
 }catch(error){result.textContent='Could not run this step: '+error.message;}
 finally{button.disabled=false;}
}
function previewValidation(outcome){
 if(!validationActive)return;
 return previewTraining({operation:'validation',feature_id:validationActive.id,definition_hash:validationActive.definition_hash,
  outcome,attempted:validationChecks.every(c=>c.checked),notes:validationEl('notes').value,run_id:validationEl('run').value.trim()});
}
function validationSaved(result){
 // A-020: close the guide back to the list on success — the list itself now shows the
 // updated status/report line, so it's unmistakable that Verify/Fail actually recorded.
 validationActive=null;validationEl('guide').hidden=true;
 trainMessage(result.outcome==='failed'?'Failure recorded. Draft bug report opens chat intake; review and Run are still required to file.':'Human verification recorded with date, version and notes.');
}
validationEl('show-all').addEventListener('change',()=>renderValidations(validationItems));
validationEl('verify').addEventListener('click',()=>previewValidation('validated'));
validationEl('fail').addEventListener('click',()=>previewValidation('failed'));
validationEl('report').addEventListener('click',async()=>{
 if(!validationReport)return;validationEl('report').disabled=true;
 try{
  const result=await post('/v1/training/report',validationReport);
  if(typeof trainingReportReady==='function')trainingReportReady(result);
  else{leaveTraining();input.disabled=true;setConsoleTarget(result.run_id);await poll(result.run_id);}
 }catch(error){trainMessage(error.message,true);}
 finally{validationEl('report').disabled=false;}
});
