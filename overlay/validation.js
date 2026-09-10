const validationEl=id=>document.querySelector('#validation-'+id);
let validationItems=[],validationActive=null,validationChecks=[],validationReport=null;
function renderValidations(items){
 validationItems=items;
 const pending=items.filter(item=>item.status!=='validated');
 validationEl('count').textContent=pending.length+' features need human review';
 const list=validationEl('list');list.innerHTML='';
 const visible=validationEl('show-all').checked?items:pending;
 if(!visible.length)trainingLine(list,'No pending human checks. Include validated features to repeat a test.');
 for(const item of visible){
  const button=document.createElement('button');button.type='button';button.textContent=item.title+' · '+item.status;
  button.addEventListener('click',()=>startValidation(item));list.appendChild(button);
 }
 if(validationActive){
  const current=items.find(i=>i.id===validationActive.id);
  if(!current||current.definition_hash!==validationActive.definition_hash){
   validationActive=null;validationEl('guide').hidden=true;trainMessage('Validation definition changed; select it again and repeat the guided test.');
  }else{validationActive=current;showLastValidation(current);}
 }
}
function showLastValidation(item){
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
 item.steps.forEach((text,index)=>{
  const label=document.createElement('label');label.className='validation-step';
  const checkbox=document.createElement('input');checkbox.type='checkbox';
  checkbox.addEventListener('change',()=>{validationEl('verify').disabled=!validationChecks.every(c=>c.checked);});
  const span=document.createElement('span');span.textContent=(index+1)+'. '+text;
  label.appendChild(checkbox);label.appendChild(span);steps.appendChild(label);validationChecks.push(checkbox);
 });
 validationEl('expected').textContent=item.expected;validationEl('notes').value='';validationEl('run').value='';
 validationEl('verify').disabled=true;showLastValidation(item);validationEl('notes').focus();
}
function previewValidation(outcome){
 if(!validationActive)return;
 return previewTraining({operation:'validation',feature_id:validationActive.id,definition_hash:validationActive.definition_hash,
  outcome,attempted:validationChecks.every(c=>c.checked),notes:validationEl('notes').value,run_id:validationEl('run').value.trim()});
}
function validationSaved(result){
 const item=validationItems.find(i=>i.id===result.feature_id);
 if(item){validationActive=item;showLastValidation(item);}
 trainMessage(result.outcome==='failed'?'Failure recorded. Draft bug report opens chat intake; review and Run are still required to file.':'Human verification recorded with date, version and notes.');
}
validationEl('show-all').addEventListener('change',()=>renderValidations(validationItems));
validationEl('verify').addEventListener('click',()=>previewValidation('validated'));
validationEl('fail').addEventListener('click',()=>previewValidation('failed'));
validationEl('report').addEventListener('click',async()=>{
 if(!validationReport)return;validationEl('report').disabled=true;
 try{
  const result=await post('/v1/training/report',validationReport);
  leaveTraining();input.disabled=true;setConsoleTarget(result.run_id);await poll(result.run_id);
 }catch(error){trainMessage(error.message,true);}
 finally{validationEl('report').disabled=false;}
});
