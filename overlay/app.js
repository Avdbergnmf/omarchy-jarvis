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
const runIdBtn=document.querySelector('#run-id-btn');
const feedbackSection=document.querySelector('#feedback');
const feedbackPrompt=document.querySelector('#feedback-prompt');
const fbGood=document.querySelector('#fb-good');
const fbNeutral=document.querySelector('#fb-neutral');
const fbBad=document.querySelector('#fb-bad');
const meta=document.querySelector('#meta');
const session=fetch('/v1/session').then(r=>r.json());
let currentRunId=null;
let pollHandle=null;
let lastRenderKey=null;

const commandList=document.querySelector('#command-list');
let commandMatches=[],commandIndex=0;
function hideCommands(){
 commandList.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');
}
function suggestCommands(){
 const value=input.value;
 commandMatches=value.startsWith('/')&&!/\s/.test(value)?JarvisCommands.filter(c=>c.name.startsWith(value.toLowerCase())):[];
 commandIndex=0;renderCommands();
}
function renderCommands(){
 commandList.innerHTML='';
 if(!commandMatches.length){hideCommands();return;}
 commandMatches.forEach((command,index)=>{
  const li=document.createElement('li');li.id='command-'+index;li.setAttribute('role','option');
  li.setAttribute('aria-selected',String(index===commandIndex));
  li.textContent=command.name+' — '+command.description;
  li.addEventListener('mousedown',event=>{event.preventDefault();completeCommand(index);});
  commandList.appendChild(li);
 });
 commandList.hidden=false;input.setAttribute('aria-expanded','true');
 input.setAttribute('aria-activedescendant','command-'+commandIndex);
}
function completeCommand(index=commandIndex){
 if(commandList.hidden||!commandMatches[index])return false;
 input.value=commandMatches[index].usage;hideCommands();input.focus();return true;
}
input.addEventListener('input',suggestCommands);
input.addEventListener('keydown',event=>{
 if(commandList.hidden)return;
 if(event.key==='ArrowDown'||event.key==='ArrowUp'){
  event.preventDefault();commandIndex=(commandIndex+(event.key==='ArrowDown'?1:-1)+commandMatches.length)%commandMatches.length;renderCommands();
 }else if(event.key==='Tab'||event.key==='Enter'){
  event.preventDefault();completeCommand();
 }
});

function loadLastRun(){try{return localStorage.getItem('jarvis:lastRun');}catch(e){return null;}}
function saveLastRun(id){try{localStorage.setItem('jarvis:lastRun',id);}catch(e){}}
function setConsoleTarget(id){
 if(id!==currentRunId)lastRenderKey=null;  // a genuinely different run must always render fresh
 currentRunId=id;consoleBtn.disabled=!id;if(id)saveLastRun(id);
 // A-020: Jarvis never showed a human the run id it just asked them to attach as
 // "evidence" in Validate features — expose it right where they're already looking.
 runIdBtn.hidden=!id;
 if(id)runIdBtn.textContent='Run: '+id.slice(0,8)+'… (copy)';
}
runIdBtn.addEventListener('click',async()=>{
 if(!currentRunId)return;
 try{await navigator.clipboard.writeText(currentRunId);runIdBtn.textContent='Copied: '+currentRunId.slice(0,8)+'…';}
 catch(error){runIdBtn.textContent=currentRunId;}
});

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
 feedbackPrompt.textContent=result.prompt||'';
 feedbackSection.hidden=false;
 fbGood.disabled=fbNeutral.disabled=fbBad.disabled=false;
}

// A-010: poll() re-fetches and re-renders every 700ms while a run is in progress —
// that's what makes the live step list work — but render() used to unconditionally
// reset qaAnswer's value/focus and runBtn's focus on *every* tick, even when nothing
// about the question/plan had actually changed. That wiped out whatever the user had
// already typed into the Q&A box roughly once a second. Only reset those on a real
// transition (a new question, a newly-shown plan), tracked via a cheap signature of
// the parts of `result` that matter for that decision.
function render(result){
 status.className=result.status==='error'?'error':'';
 status.textContent=result.reply||result.status;
 const key=result.status+'|'+result.reply+'|'+JSON.stringify(result.plan)+'|'+JSON.stringify(result.draft);
 const isNewState=key!==lastRenderKey;
 lastRenderKey=key;
 if(result.status==='awaiting_answer'){
  planSection.hidden=true;stepsSection.hidden=true;feedbackSection.hidden=true;
  qaSection.hidden=false;
  if(isNewState){
   qaQuestion.textContent=result.reply;
   qaAnswer.value='';qaAnswer.focus();
  }
 }else if(result.status==='awaiting_approval'){
  qaSection.hidden=true;feedbackSection.hidden=true;
  stepsSection.hidden=true;
  if(isNewState){
   renderPlan(result.plan||{actions:[]},result.draft);
   runBtn.focus();
  }
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
 event.preventDefault();if(completeCommand())return;if(!input.value.trim()||input.disabled)return;
 const prompt=input.value.trim();
 if(prompt.toLowerCase()==='/train'){input.value='';enterTraining();return;}
 input.disabled=true;input.value='';status.className='';status.textContent='Thinking…';
 planSection.hidden=true;stepsSection.hidden=true;qaSection.hidden=true;feedbackSection.hidden=true;
 try{
  const {run_id}=await post('/v1/run',{prompt});
  setConsoleTarget(run_id);
  await poll(run_id);
 }catch(error){
  status.textContent=error.message;status.className='error';input.disabled=false;input.value=prompt;input.focus();
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
 event.preventDefault();const text=qaAnswer.value.trim();await answer(text||'skip');
});
qaSkip.addEventListener('click',()=>answer('skip'));

document.addEventListener('keydown',async event=>{
 if(event.key!=='Escape')return;
 event.preventDefault();
 if(!commandList.hidden){hideCommands();return;}
 if(typeof leaveTraining==='function'&&leaveTraining())return;
 const pending=!planSection.hidden||!qaSection.hidden;
 try{if(pending&&currentRunId)await post('/v1/runs/'+currentRunId+'/deny').catch(()=>{});}
 finally{await post('/v1/close');}
});

// A-010: reopening the overlay (hotkey/Escape then hotkey again) used to always start
// from a blank "Ready" screen, discarding the last run's reply/steps/feedback controls
// even though the server still had them — the console button was the only thing that
// remembered anything. Restore and re-render the last known run on load; if it's still
// in progress (dismissed mid-flight, e.g. the hotkey's close path doesn't deny a pending
// plan the way Escape does), resume polling it instead of leaving it to time out unseen.
(async()=>{
 const last=loadLastRun();
 if(last){
  setConsoleTarget(last);
  try{
   const result=await get('/v1/runs/'+last);
   render(result);
   if(result.status==='planning'||result.status==='awaiting_approval'||result.status==='awaiting_answer'||result.status==='running'){
    input.disabled=true;
    await poll(last);
   }
  }catch(error){/* unknown/expired run id (e.g. after a service restart) — start fresh */}
 }
 try{
  const health=await (await fetch('/health')).json();
  meta.textContent=health.model+' · ollama '+health.ollama+(health.approval_mode==='off'?' · ⚠ approval off':'');
  meta.className=health.ollama==='ok'&&health.approval_mode!=='off'?'':'warn';
 }catch(error){meta.textContent='health unavailable';meta.className='warn';}
})();
