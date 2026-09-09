const input=document.querySelector('#prompt');
const status=document.querySelector('#status');
const planSection=document.querySelector('#plan');
const planActions=document.querySelector('#plan-actions');
const runBtn=document.querySelector('#run-btn');
const cancelBtn=document.querySelector('#cancel-btn');
const stepsSection=document.querySelector('#steps');
const stepList=document.querySelector('#step-list');
const consoleBtn=document.querySelector('#console-btn');
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

function renderPlan(plan){
 planActions.innerHTML='';
 (plan.actions||[]).forEach(action=>{
  const li=document.createElement('li');
  li.textContent=describeAction(action);
  planActions.appendChild(li);
 });
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

function render(result){
 status.className=result.status==='error'?'error':'';
 status.textContent=result.reply||result.status;
 if(result.status==='awaiting_approval'){
  renderPlan(result.plan||{actions:[]});
  stepsSection.hidden=true;
  runBtn.focus();
 }else if(result.status==='running'){
  planSection.hidden=true;
  renderSteps(result.steps);
 }else{
  planSection.hidden=true;
  renderSteps(result.steps);
 }
}

async function poll(runId){
 if(pollHandle)clearTimeout(pollHandle);
 const step=async()=>{
  let result;
  try{result=await get('/v1/runs/'+runId);}
  catch(error){status.textContent=error.message;status.className='error';input.disabled=false;return;}
  render(result);
  if(result.status==='planning'||result.status==='awaiting_approval'||result.status==='running'){
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
 planSection.hidden=true;stepsSection.hidden=true;
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

document.addEventListener('keydown',async event=>{
 if(event.key!=='Escape')return;
 event.preventDefault();
 const awaitingApproval=!planSection.hidden;
 try{if(awaitingApproval&&currentRunId)await post('/v1/runs/'+currentRunId+'/deny').catch(()=>{});}
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
