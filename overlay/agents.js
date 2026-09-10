const agentEl=id=>document.querySelector('#agent-'+id);
let selectedAgent=null;
const effortLabels={low:'Low',medium:'Medium',high:'High',xhigh:'Ultra (xhigh)'};
function updateAgentControls(slot=null){
 const kind=slot?slot.kind:trainEl('kind').value,effort=trainEl('effort');
 effort.disabled=kind!=='cursor';
 effort.value=kind==='cursor'&&slot&&slot.reasoning_effort?slot.reasoning_effort:'';
 agentEl('effort-help').textContent=kind==='cursor'
  ?'Applied only when a new Codex window starts. Opening an existing window only focuses it; that session keeps its current depth.'
  :'This launcher does not control reasoning depth for this slot type.';
}
function updateDeliveryHelp(){
 agentEl('delivery-help').textContent=trainEl('mode').value==='queue'
  ?'Saves the assignment in local slot metadata. Jarvis will not open a window or send it later automatically.'
  :'After confirmation, opens or focuses a visible agent window and keeps the exact handoff ready to copy and paste.';
}
function renderAgents(data){
 const list=trainEl('agents');list.innerHTML='';
 for(const slot of data.agents){
  const row=document.createElement('button');row.type='button';row.className='assignment-row';
  const effort=slot.effective_reasoning_effort?' · depth '+(effortLabels[slot.effective_reasoning_effort]||slot.effective_reasoning_effort):'';
  row.textContent=slot.label+' · '+slot.kind+' · '+(slot.busy?'busy':'idle')+effort+(slot.current_assignment?' · working '+slot.current_assignment:'');
  row.setAttribute('aria-pressed',String(!!(selectedAgent&&selectedAgent.id===slot.id)));
  row.addEventListener('click',()=>selectAgent(slot.id));list.appendChild(row);
 }
 if(!data.agents.length)trainingLine(list,'No local slots yet. Preparing a handoff can create one.');
 const picker=trainEl('slot'),previous=picker.value;picker.innerHTML='';trainingOption(picker,'new','New agent slot');
 for(const slot of data.agents)trainingOption(picker,slot.id,slot.label+' ('+(slot.busy?'busy':'idle')+')');
 picker.value=data.agents.some(s=>s.id===previous)?previous:'new';
 if(selectedAgent){
  const fresh=data.agents.find(s=>s.id===selectedAgent.id);
  if(fresh)fillAgentDetail(fresh,false);else{selectedAgent=null;agentEl('detail').hidden=true;agentEl('hint').hidden=false;}
 }
 updateAgentControls(data.agents.find(s=>s.id===picker.value)||null);
 renderAgentBoard(data);
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
 agentEl('status').textContent=slot.kind+' · '+(slot.busy?'busy':'idle');
 agentEl('effort-summary').textContent=slot.kind==='cursor'
  ?'Reasoning depth: '+(slot.effective_reasoning_effort?(effortLabels[slot.effective_reasoning_effort]||slot.effective_reasoning_effort)+' · '+slot.reasoning_effort_source:'unknown — choose a launch setting below')
  :'Reasoning depth: unavailable for this launcher.';
 agentEl('current').textContent='Current assignment: '+(slot.current_assignment||'none');
 agentEl('queued').textContent='Queued: '+(slot.queued_assignment_ids.join(', ')||'none');
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
