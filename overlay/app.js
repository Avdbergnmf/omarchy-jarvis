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

// A-019: one friendly verb phrase per tool (using its most important argument) instead of
// a bare tool_name plus raw key=value soup. TITLE_ARGS lists which argument(s) each title
// already folds in, so actionChips() only surfaces genuinely extra ones as small chips.
const ACTION_TITLES={
 workspace_new:()=>'Create a new workspace',
 scratch_toggle:()=>'Toggle the scratchpad',
 scratch_move_here:()=>'Move this window to the scratchpad',
 list_backlog:()=>'List the open backlog',
 workspace_switch:a=>'Switch to workspace '+a.workspace,
 run_binding:a=>'Run keybinding: '+a.binding,
 catalog_bindings:a=>'Look up keybindings'+(a.query?': '+a.query:''),
 open_webapp:a=>'Open '+a.name,
 open_app_by_name:a=>'Open '+a.name,
 correct_app_open:a=>'Open the other matching app'+(a.query?': '+a.query:''),
 run_skill:a=>'Run skill: '+a.skill,
 report_bug:a=>'File a bug report: '+a.title,
 report_feature:a=>'File a feature request: '+a.title,
 prepare_handoff:a=>'Prepare a handoff for issue #'+a.issue+' → '+a.agent,
};
const TITLE_ARGS={
 workspace_switch:['workspace'],run_binding:['binding'],catalog_bindings:['query'],
 open_webapp:['name'],open_app_by_name:['name'],correct_app_open:['query'],run_skill:['skill'],
 report_bug:['title'],report_feature:['title'],prepare_handoff:['issue','agent'],
};
function actionTitle(action){
 const build=ACTION_TITLES[action.tool];
 return build?build(action.arguments||{}):action.tool.replace(/_/g,' ');
}
function actionChips(action){
 const used=new Set(TITLE_ARGS[action.tool]||[]);
 return Object.entries(action.arguments||{}).filter(([k])=>!used.has(k));
}
function actionCard(action,description){
 const li=document.createElement('li');li.className='action-card';
 const title=document.createElement('div');title.className='action-title';title.textContent=actionTitle(action);li.appendChild(title);
 if(description){const desc=document.createElement('p');desc.className='action-desc';desc.textContent=description;li.appendChild(desc);}
 const chips=actionChips(action);
 if(chips.length){
  const row=document.createElement('div');row.className='action-chips';
  for(const [key,value] of chips){
   const chip=document.createElement('span');chip.className='chip';chip.textContent=key+': '+value;chip.title=key+': '+value;
   row.appendChild(chip);
  }
  li.appendChild(row);
 }
 return li;
}

function renderPlan(plan,draft){
 planActions.innerHTML='';
 (plan.actions||[]).forEach(action=>{
  // run_skill's reply is a deterministic description of what the skill actually does
  // (brain/server.py, A-015) — surfacing it here, not just once in the now-retired
  // below-bubble status line, is the "important what" Alex asked to see in the bubble.
  const description=action.tool==='run_skill'?plan.reply:null;
  planActions.appendChild(actionCard(action,description));
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
 // A-019: the reply now lives inside the proposed-action bubble itself (see renderPlan) —
 // showing it again here too was the "separate hard-to-read text dump underneath" Alex
 // asked to retire, and this single-line output truncates long replies anyway.
 status.textContent=result.status==='awaiting_approval'?'Review the plan below.':(result.reply||result.status);
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
