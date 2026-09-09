const input=document.querySelector('#prompt');
const status=document.querySelector('#status');
const planSection=document.querySelector('#plan');
const planActions=document.querySelector('#plan-actions');
const draftPreview=document.querySelector('#draft-preview');
const draftTitle=document.querySelector('#draft-title');
const draftBody=document.querySelector('#draft-body');
const runBtn=document.querySelector('#run-btn');
const cancelBtn=document.querySelector('#cancel-btn');
const stepsSection=document.querySelector('#steps');
const stepList=document.querySelector('#step-list');
const qaSection=document.querySelector('#qa');
const qaQuestion=document.querySelector('#qa-question');
const qaAnswer=document.querySelector('#qa-answer');
const qaSkip=document.querySelector('#qa-skip');
const consoleBtn=document.querySelector('#console-btn');
const feedbackSection=document.querySelector('#feedback');
const fbGood=document.querySelector('#fb-good');
const fbNeutral=document.querySelector('#fb-neutral');
const fbBad=document.querySelector('#fb-bad');
const meta=document.querySelector('#meta');
const session=fetch('/v1/session').then(r=>r.json());
let currentRunId=null;
let pollHandle=null;

function loadLastRun(){try{return localStorage.getItem('jarvis:lastRun');}catch(e){return null;}}
function saveLastRun(id){try{localStorage.setItem('jarvis:lastRun',id);}catch(e){}}
function setConsoleTarget(id){currentRunId=id;consoleBtn.disabled=!id;if(id)saveLastRun(id);}

async function post(path,body){
 const {token}=await session;
 const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Jarvis-Token':token},body:JSON.stringify(body||{})});
 const result=await response.json().catch(()=>({}));
 if(!response.ok)throw new Error(result.error||'Request failed');
 return result;
}
async function get(path){
 const {token}=await session;
 const response=await fetch(path,{headers:{'X-Jarvis-Token':token}});
 const result=await response.json();
 if(!response.ok)throw new Error(result.error||'Request failed');
 return result;
}

function describeAction(action){
 const label=((action.arguments&&action.arguments.skill)||action.tool).replace(/_/g,' ');
 const args=Object.entries(action.arguments||{}).filter(([k])=>k!=='skill').map(([k,v])=>k+'='+v).join(', ');
 return label+(args?' ('+args+')':'');
}

function renderPlan(plan,draft){
 planActions.innerHTML='';
 (plan.actions||[]).forEach(action=>{
  const li=document.createElement('li');
  li.textContent=describeAction(action);
  planActions.appendChild(li);
 });
 if(draft){
  draftTitle.textContent=draft.title;
  draftBody.textContent=draft.body;
  draftPreview.hidden=false;
 }else{
  draftPreview.hidden=true;
 }
 planSection.hidden=false;
}

function renderSteps(steps){
 stepList.innerHTML='';
 (steps||[]).forEach(step=>{
  const li=document.createElement('li');
  li.className='step-'+step.status;
  li.textContent=step.label+' — '+step.status+(step.summary?': '+step.summary:'');
  stepList.appendChild(li);
 });
 stepsSection.hidden=(steps||[]).length===0;
}

function renderFeedback(result){
 if(result.status!=='done'&&result.status!=='error'){feedbackSection.hidden=true;return;}
 if(result.feedback){feedbackSection.hidden=true;return;}
 feedbackSection.hidden=false;
 fbGood.disabled=fbNeutral.disabled=fbBad.disabled=false;
}

function render(result){
 status.className=result.status==='error'?'error':'';
 status.textContent=result.reply||result.status;
 if(result.status==='awaiting_answer'){
  planSection.hidden=true;stepsSection.hidden=true;feedbackSection.hidden=true;
  qaQuestion.textContent=result.reply;
  qaSection.hidden=false;
  qaAnswer.value='';qaAnswer.focus();
 }else if(result.status==='awaiting_approval'){
  qaSection.hidden=true;feedbackSection.hidden=true;
  renderPlan(result.plan||{actions:[]},result.draft);
  stepsSection.hidden=true;
  runBtn.focus();
 }else if(result.status==='running'){
  qaSection.hidden=true;planSection.hidden=true;feedbackSection.hidden=true;
  renderSteps(result.steps);
 }else{
  qaSection.hidden=true;planSection.hidden=true;
  renderSteps(result.steps);
  renderFeedback(result);
 }
}

async function poll(runId){
 if(pollHandle)clearTimeout(pollHandle);
 const step=async()=>{
  let result;
  try{result=await get('/v1/runs/'+runId);}
  catch(error){status.textContent=error.message;status.className='error';input.disabled=false;return;}
  render(result);
  if(result.status==='planning'||result.status==='awaiting_approval'||result.status==='awaiting_answer'||result.status==='running'){
   pollHandle=setTimeout(step,700);
  }else{
   input.disabled=false;input.focus();
  }
 };
 await step();
}

document.querySelector('#prompt-form').addEventListener('submit',async event=>{
 event.preventDefault();if(!input.value.trim()||input.disabled)return;
 input.disabled=true;status.className='';status.textContent='Thinking…';
 planSection.hidden=true;stepsSection.hidden=true;qaSection.hidden=true;feedbackSection.hidden=true;
 try{
  const {run_id}=await post('/v1/run',{prompt:input.value.trim()});
  setConsoleTarget(run_id);
  await poll(run_id);
 }catch(error){
  status.textContent=error.message;status.className='error';input.disabled=false;input.focus();
 }
});

runBtn.addEventListener('click',async()=>{
 if(!currentRunId)return;
 runBtn.disabled=true;cancelBtn.disabled=true;
 try{await post('/v1/runs/'+currentRunId+'/approve');await poll(currentRunId);}
 catch(error){status.textContent=error.message;status.className='error';}
 finally{runBtn.disabled=false;cancelBtn.disabled=false;}
});

cancelBtn.addEventListener('click',async()=>{
 if(!currentRunId)return;
 try{await post('/v1/runs/'+currentRunId+'/deny');await poll(currentRunId);}
 catch(error){status.textContent=error.message;status.className='error';}
});

consoleBtn.addEventListener('click',async()=>{
 const id=currentRunId||loadLastRun();
 if(!id)return;
 try{await post('/v1/runs/'+id+'/console');}
 catch(error){status.textContent=error.message;status.className='error';}
});

async function sendFeedback(rating){
 if(!currentRunId)return;
 fbGood.disabled=fbNeutral.disabled=fbBad.disabled=true;
 try{
  const result=await post('/v1/runs/'+currentRunId+'/feedback',{rating});
  if(rating==='bad'&&result.run_id){
   setConsoleTarget(result.run_id);
   await poll(result.run_id);
  }else{
   feedbackSection.hidden=true;
  }
 }catch(error){
  status.textContent=error.message;status.className='error';
  fbGood.disabled=fbNeutral.disabled=fbBad.disabled=false;
 }
}
fbGood.addEventListener('click',()=>sendFeedback('good'));
fbNeutral.addEventListener('click',()=>sendFeedback('neutral'));
fbBad.addEventListener('click',()=>sendFeedback('bad'));

async function answer(text){
 if(!currentRunId||!text)return;
 try{await post('/v1/runs/'+currentRunId+'/answer',{text});await poll(currentRunId);}
 catch(error){status.textContent=error.message;status.className='error';}
}
document.querySelector('#qa-form').addEventListener('submit',async event=>{
 event.preventDefault();await answer(qaAnswer.value.trim());
});
qaSkip.addEventListener('click',()=>answer('skip'));

document.addEventListener('keydown',async event=>{
 if(event.key!=='Escape')return;
 event.preventDefault();
 const pending=!planSection.hidden||!qaSection.hidden;
 try{if(pending&&currentRunId)await post('/v1/runs/'+currentRunId+'/deny').catch(()=>{});}
 finally{await post('/v1/close');}
});

(async()=>{
 const last=loadLastRun();
 if(last)setConsoleTarget(last);
 try{
  const health=await (await fetch('/health')).json();
  meta.textContent=health.model+' · ollama '+health.ollama+(health.approval_mode==='off'?' · ⚠ approval off':'');
  meta.className=health.ollama==='ok'&&health.approval_mode!=='off'?'':'warn';
 }catch(error){meta.textContent='health unavailable';meta.className='warn';}
})();
