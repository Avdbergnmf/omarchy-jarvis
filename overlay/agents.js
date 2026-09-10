const agentEl=id=>document.querySelector('#agent-'+id);
let selectedAgent=null;
function renderAgents(data){
 const list=trainEl('agents');list.innerHTML='';
 for(const slot of data.agents){
  const row=document.createElement('button');row.type='button';row.className='assignment-row';
  row.textContent=slot.label+' · '+slot.kind+' · '+(slot.busy?'busy':'idle')+(slot.current_assignment?' · working '+slot.current_assignment:'');
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
 renderAgentBoard(data);
}
function renderAgentBoard(data){
 const board=agentEl('board');board.innerHTML='';
 for(const item of data.assignments){
  const worker=data.agents.find(s=>s.current_assignment===item.id);
  trainingLine(board,item.id+' · '+item.status+' · '+item.area+' · parallel '+item.parallel+(worker?' · '+worker.label:''));
 }
 if(!data.assignments.length)trainingLine(board,'Queue is empty.');
}
function fillAgentDetail(slot,setPreparedFor=true){
 selectedAgent=slot;agentEl('hint').hidden=true;agentEl('detail').hidden=false;
 agentEl('heading').textContent=slot.label+' ('+slot.id+')';
 agentEl('status').textContent=slot.kind+' · '+(slot.busy?'busy':'idle');
 agentEl('current').textContent='Current assignment: '+(slot.current_assignment||'none');
 agentEl('queued').textContent='Queued: '+(slot.queued_assignment_ids.join(', ')||'none');
 agentEl('handoff').textContent=slot.last_handoff?'Last handoff: '+slot.last_handoff:'No handoff prepared yet.';
 agentEl('open-window').hidden=slot.kind==='human';
 agentEl('toggle-status').textContent='Preview marking '+(slot.status==='busy'?'idle':'busy');
 if(setPreparedFor)trainEl('slot').value=slot.id;
}
function selectAgent(id){
 const slot=trainingData.agents.find(s=>s.id===id);if(!slot)return;
 fillAgentDetail(slot);renderAgents(trainingData);
}
async function openAgentWindow(slotId){
 agentEl('open-window').disabled=true;
 try{await post('/v1/training/agent-window',{slot_id:slotId});trainMessage('Opening the agent window…');}
 catch(error){trainMessage(error.message,true);}
 finally{agentEl('open-window').disabled=false;}
}
agentEl('open-window').addEventListener('click',()=>{if(selectedAgent)openAgentWindow(selectedAgent.id);});
agentEl('toggle-status').addEventListener('click',()=>{
 if(!selectedAgent)return;
 previewTraining({operation:'slot',slot_id:selectedAgent.id,status:selectedAgent.status==='busy'?'idle':'busy'});
});
