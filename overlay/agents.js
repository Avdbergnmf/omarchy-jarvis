const agentEl=id=>document.querySelector('#agent-'+id);
let selectedAgent=null;
const effortLabels={low:'Low',medium:'Medium',high:'High',xhigh:'Ultra (xhigh)',max:'Max'};
const cursorEffortOptions=[['','Use Codex config'],['low','Low'],['medium','Medium'],['high','High'],['xhigh','Ultra (xhigh)']];
const claudeEffortOptions=[['','Use Claude settings'],['low','Low'],['medium','Medium'],['high','High'],['xhigh','Ultra (xhigh)'],['max','Max']];
function fillEffortOptions(kind,selected){
 const effort=trainEl('effort');
 const rows=kind==='cursor'?cursorEffortOptions:kind==='claude-code'?claudeEffortOptions:[['','Not used']];
 effort.innerHTML='';
 for(const [value,label] of rows){
  const option=document.createElement('option');option.value=value;option.textContent=label;effort.appendChild(option);
 }
 const allowed=new Set(rows.map(row=>row[0]));
 effort.value=allowed.has(selected||'')?selected:'';
}
function updateAgentControls(slot=null){
 const kind=slot?slot.kind:trainEl('kind').value,effort=trainEl('effort');
 const supports=kind==='cursor'||kind==='claude-code';
 effort.disabled=!supports;
 fillEffortOptions(kind,supports&&slot&&slot.reasoning_effort?slot.reasoning_effort:'');
 agentEl('effort-help').textContent=kind==='cursor'
  ?'Applied only when a new Codex window starts. Opening an existing window only focuses it; that session keeps its current depth.'
  :kind==='claude-code'
  ?'Applied as claude --effort on a new window start. Opening an existing window only focuses it; that session keeps its current depth.'
  :'This launcher does not control reasoning depth for this slot type.';
}
function updateDeliveryHelp(){
 agentEl('delivery-help').textContent=trainEl('mode').value==='queue'
  ?'Adds work to this agent’s ordered queue. When it becomes claimable, Jarvis opens/focuses the visible window and prepares the prompt; you still paste it.'
  :'After confirmation, opens or focuses the visible agent window and keeps the exact handoff ready for you to paste.';
}
function personalQueue(slot,data){
 if(slot.personal_queue)return slot.personal_queue;
 return slot.queued_assignment_ids.map(id=>{const item=data.assignments.find(a=>a.id===id);return {id,title:item?item.title:'Unknown assignment',queue_status:item&&item.status==='queued'?'ready-next':'blocked-waiting'};});
}
function renderAgents(data){
 const list=trainEl('agents');list.innerHTML='';
 for(const slot of data.agents){
  const row=document.createElement('button');row.type='button';
  const state=slot.computed_status||(slot.busy?'working':'idle');row.className='agent-tile status-'+state;
  const effort=slot.effective_reasoning_effort?' · depth '+(effortLabels[slot.effective_reasoning_effort]||slot.effective_reasoning_effort):'';
  const title=document.createElement('strong');title.textContent=slot.label;row.appendChild(title);
  const status=document.createElement('span');status.className='agent-state';status.textContent=state+' · '+slot.kind+effort;row.appendChild(status);
  const current=document.createElement('span');current.textContent=slot.current_assignment?'Working: '+slot.current_assignment:'No current assignment';row.appendChild(current);
  const queue=document.createElement('span');queue.className='agent-personal-queue';
  const items=personalQueue(slot,data);queue.textContent=items.length?items.map(item=>item.id+' · queued-to-this-agent · '+item.queue_status).join('\n'):'Queue empty';row.appendChild(queue);
  row.setAttribute('aria-pressed',String(!!(selectedAgent&&selectedAgent.id===slot.id)));
  row.addEventListener('click',()=>selectAgent(slot.id));list.appendChild(row);
 }
 if(!data.agents.length)trainingLine(list,'No local slots yet. Preparing a handoff can create one.');
 const picker=trainEl('slot'),previous=picker.value;picker.innerHTML='';trainingOption(picker,'new','+ New agent');
 for(const slot of data.agents)trainingOption(picker,slot.id,slot.label+' ('+(slot.busy?'busy':'idle')+')');
 picker.value=data.agents.some(s=>s.id===previous)?previous:'new';
 if(selectedAgent){
  const fresh=data.agents.find(s=>s.id===selectedAgent.id);
  if(fresh)fillAgentDetail(fresh,false);else{selectedAgent=null;agentEl('detail').hidden=true;agentEl('hint').hidden=false;}
 }
 updateAgentControls(data.agents.find(s=>s.id===picker.value)||null);
 renderAgentBoard(data);
 renderAvailableWork(data);
}
function renderAvailableWork(data){
 const list=agentEl('available');list.innerHTML='';
 const available=data.available_assignments||data.assignments.filter(item=>item.status==='queued'&&!(item.unmet_blocked_by||[]).length);
 for(const item of available){
  const row=document.createElement('button');row.type='button';row.className='assignment-row';row.textContent=item.id+' — '+item.title+'\n'+item.area+' · ready';
  row.addEventListener('click',()=>{trainEl('assignment').value=item.id;trainMessage(item.id+' selected. Choose an agent tile or + New agent.');});list.appendChild(row);
 }
 if(!available.length)trainingLine(list,'No work is claimable against the current queue and active areas.');
}
function renderAgentBoard(data){
 const active=agentEl('active');active.innerHTML='';
 const working=data.assignments.filter(item=>item.status==='in_progress');
 for(const item of working){
  const worker=data.agents.find(s=>s.current_assignment===item.id);
  trainingLine(active,item.id+' — '+item.title+' · '+(worker?worker.label+' · '+(worker.busy?'busy':'idle'):'no local slot assigned'));
 }
 if(!working.length)trainingLine(active,'No assignment is currently in progress.');
 const board=agentEl('board');board.innerHTML='';
 for(const item of data.assignments){
  const worker=data.agents.find(s=>s.current_assignment===item.id);
  const unmet=item.unmet_blocked_by&&item.unmet_blocked_by.length?item.unmet_blocked_by.join(', '):null;
  const waiting=item.status==='blocked'?(unmet?' · waiting on '+unmet:' · waiting — see assignment brief'):'';
  const gate=item.gate?' · gate '+item.gate:'';
  trainingLine(board,item.id+' · '+item.status+' · '+item.area+' · parallel '+item.parallel+gate+waiting+(worker?' · '+worker.label:''));
 }
 if(!data.assignments.length)trainingLine(board,'Queue is empty.');
}
function fillAgentDetail(slot,setPreparedFor=true){
 selectedAgent=slot;agentEl('hint').hidden=true;agentEl('detail').hidden=false;
 agentEl('heading').textContent=slot.label+' ('+slot.id+')';
 agentEl('status').textContent=slot.kind+' · '+(slot.computed_status||(slot.busy?'working':'idle'));
 agentEl('effort-summary').textContent=slot.kind==='human'
  ?'Reasoning depth: unavailable for this launcher.'
  :'Reasoning depth: '+(slot.effective_reasoning_effort?(effortLabels[slot.effective_reasoning_effort]||slot.effective_reasoning_effort)+' · '+slot.reasoning_effort_source:'unknown — choose a launch setting below');
 agentEl('current').textContent='Current assignment: '+(slot.current_assignment||'none');
 agentEl('queued').textContent='Personal queue: '+(personalQueue(slot,trainingData).map(item=>item.id+' (queued-to-this-agent · '+item.queue_status+')').join(', ')||'empty');
 agentEl('handoff').textContent=slot.last_handoff?'Last handoff: '+slot.last_handoff:'No handoff prepared yet.';
 agentEl('open-window').hidden=slot.kind==='human';
 agentEl('toggle-status').textContent='Mark slot '+(slot.status==='busy'?'idle':'busy');
 agentEl('status-note').textContent='Local status only. Jarvis does not inspect running Codex or Claude sessions.';
 if(setPreparedFor)trainEl('slot').value=slot.id;
 updateAgentControls(slot);
}
function selectAgent(id){
 const slot=trainingData.agents.find(s=>s.id===id);if(!slot)return;
 fillAgentDetail(slot);renderAgents(trainingData);
}
async function openAgentWindow(slotId){
 agentEl('open-window').disabled=true;
 try{await post('/v1/training/agent-window',{slot_id:slotId});trainMessage('Agent window opened or focused. An existing session keeps its current reasoning depth.');}
 catch(error){trainMessage(error.message,true);}
 finally{agentEl('open-window').disabled=false;}
}
agentEl('open-window').addEventListener('click',()=>{if(selectedAgent)openAgentWindow(selectedAgent.id);});
agentEl('toggle-status').addEventListener('click',()=>{
 if(!selectedAgent)return;
 previewTraining({operation:'slot',slot_id:selectedAgent.id,status:selectedAgent.status==='busy'?'idle':'busy'});
});
trainEl('slot').addEventListener('change',()=>updateAgentControls(trainingData.agents.find(s=>s.id===trainEl('slot').value)||null));
trainEl('kind').addEventListener('change',()=>updateAgentControls());
trainEl('mode').addEventListener('change',updateDeliveryHelp);
updateDeliveryHelp();
async function pollAgentAdvance(){
 if(document.querySelector('#train-panel-agents').hidden)return;
 try{
  const result=await post('/v1/training/agent-advance',{});
  if(result.advanced&&result.advanced.length){
   const first=result.advanced.find(item=>item.handoff_text);
   if(first){
    if(typeof setHandoffText==='function')setHandoffText(first.handoff_text);else trainEl('handoff').value=first.handoff_text;
    trainEl('result').hidden=false;
   }
   trainMessage(result.advanced.map(item=>item.launch_error?item.assignment_id+' window error: '+item.launch_error:item.assignment_id+' prepared for visible '+item.slot_id).join(' · ')+' — prompt not submitted.');
   if(typeof refreshTraining==='function')await refreshTraining();
  }
 }catch(error){trainMessage('Agent auto-advance paused: '+error.message,true);}
}
if(typeof setInterval==='function')setInterval(pollAgentAdvance,15000);
