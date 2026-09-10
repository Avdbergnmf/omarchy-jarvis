const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function element(){return {value:'',hidden:true,disabled:false,className:'',textContent:'',children:[],handlers:{},
 set innerHTML(value){this.children=[];},addEventListener(event,fn){this.handlers[event]=fn;},appendChild(child){this.children.push(child);},setAttribute(name,value){this[name]=value;},focus(){this.focused=true;},select(){}};}
const els={},requests=[];const $=id=>els[id]||(els[id]=element());
const claudeSlot={id:'slot-a1',label:'My coding agent',kind:'claude-code',status:'idle',computed_status:'waiting',current_assignment:null,queued_assignment_ids:['A-021'],personal_queue:[{id:'A-021',title:'Other',queue_status:'ready-next'}],busy:false,last_handoff:null,reasoning_effort:'max',effective_reasoning_effort:'max',reasoning_effort_source:'slot launch setting'};
const codexSlot={id:'slot-c1',label:'Codex deep',kind:'cursor',status:'idle',current_assignment:null,queued_assignment_ids:[],busy:false,last_handoff:null,reasoning_effort:'xhigh',effective_reasoning_effort:'xhigh',reasoning_effort_source:'slot launch setting'};
const humanSlot={id:'slot-h1',label:'Alex himself',kind:'human',status:'idle',current_assignment:'A-020',queued_assignment_ids:[],busy:true,last_handoff:'docs/backlog/handoffs/active/x.md'};
const data={agents:[claudeSlot,codexSlot,humanSlot],available_assignments:[{id:'A-021',title:'Other',status:'queued',area:'skills'}],assignments:[{id:'A-020',title:'Fix focus',status:'in_progress',area:'overlay',parallel:'NO'},{id:'A-021',title:'Other',status:'queued',area:'skills',parallel:'YES'},{id:'A-022',title:'Waiting',status:'blocked',area:'docs',parallel:'NO'}]};
const ctx={document:{querySelector:$,createElement:element},trainingData:data,trainEl:id=>$('#train-'+id),
 trainMessage(text){$('#message').textContent=text;},
 trainingLine(parent,text){const p=element();p.textContent=text;parent.children.push(p);return p;},
 trainingOption(parent,value,label){const o=element();o.value=value;o.textContent=label;parent.children.push(o);},
 post:async(path,body)=>{requests.push({path,body});return {ok:true};},
 previewTraining:async payload=>{ctx.lastPreview=payload;}};
vm.runInNewContext(fs.readFileSync('overlay/agents.js','utf8'),ctx);
(async()=>{
 ctx.renderAgents(data);
 assert.equal($('#train-agents').children.length,3,'one tile per slot');
 assert.equal($('#train-agents').children[0].className,'agent-tile status-waiting');
 assert.match($('#train-agents').children[0].children.map(c=>c.textContent).join(' '),/My coding agent.*waiting.*A-021.*queued-to-this-agent.*ready-next/);
 assert.equal($('#train-slot').children.length,4,'new + three known slots');
 assert.match($('#agent-available').children[0].textContent,/A-021[\s\S]*Other[\s\S]*ready/);
 $('#agent-available').children[0].handlers.click();assert.equal($('#train-assignment').value,'A-021');

 ctx.selectAgent('slot-a1');
 assert.equal($('#agent-detail').hidden,false);assert.equal($('#agent-hint').hidden,true);
 assert.equal($('#agent-heading').textContent,'My coding agent (slot-a1)');
 assert.equal($('#agent-open-window').hidden,false,'claude-code slots can be launched');
 assert.equal($('#agent-toggle-status').textContent,'Mark slot busy');
 assert.match($('#agent-status-note').textContent,/Local status only/);
 assert.equal($('#train-slot').value,'slot-a1','selecting a tile prepares that slot');
 assert.equal($('#train-effort').disabled,false,'Claude Code slots can choose depth');
 assert.equal($('#train-effort').value,'max');
 assert.ok($('#train-effort').children.some(option=>option.value==='max'),'Claude Code lists Max');
 assert.match($('#agent-effort-summary').textContent,/Max.*slot launch setting/);
 assert.match($('#agent-effort-help').textContent,/claude --effort.*new window/);

 ctx.selectAgent('slot-h1');
 assert.equal($('#agent-open-window').hidden,true,'human slots have nothing for Jarvis to open');
 assert.match($('#agent-current').textContent,/A-020/);
 assert.equal($('#train-effort').disabled,true,'human slots cannot choose depth');
 assert.match($('#agent-effort-help').textContent,/does not control reasoning depth/);
 assert.match($('#agent-effort-summary').textContent,/unavailable/);

 $('#agent-toggle-status').handlers.click();
 assert.equal(ctx.lastPreview.operation,'slot');assert.equal(ctx.lastPreview.slot_id,'slot-h1');
 assert.equal(ctx.lastPreview.status,'busy','idle status toggles to busy regardless of the separately computed busy flag');

 ctx.selectAgent('slot-c1');
 assert.match($('#agent-effort-summary').textContent,/Ultra \(xhigh\).*slot launch setting/);
 assert.equal($('#train-effort').value,'xhigh');assert.equal($('#train-effort').disabled,false);
 assert.ok(!$('#train-effort').children.some(option=>option.value==='max'),'Codex does not list Max');
 assert.match($('#agent-effort-help').textContent,/new Codex window/);

 ctx.selectAgent('slot-a1');
 $('#agent-open-window').handlers.click();await new Promise(resolve=>setTimeout(resolve,0));
 assert.equal(requests[0].path,'/v1/training/agent-window');assert.equal(requests[0].body.slot_id,'slot-a1');
 assert.equal($('#agent-open-window').disabled,false,'button re-enables after the request settles');

 $('#agent-board').innerHTML='';ctx.renderAgents(data);
 const active=$('#agent-active').children.map(c=>c.textContent).join('\n');
 assert.match(active,/A-020.*Fix focus.*Alex himself.*busy/,'persistent active-work strip names owner and status');
 const board=$('#agent-board').children.map(c=>c.textContent).join('\n');
 assert.match(board,/A-020.*in_progress.*Alex himself/,'queue board names the current worker');
 assert.match(board,/A-021.*queued/,'unworked assignments show with no worker suffix');
 assert.match(board,/A-022.*blocked.*waiting/,'blocked assignments have a simple waiting hint');

 $('#train-mode').value='queue';$('#train-mode').handlers.change();
 assert.match($('#agent-delivery-help').textContent,/ordered queue.*never.*paste|ordered queue/);

 $('#train-kind').value='cursor';$('#train-kind').handlers.change();
 assert.equal($('#train-effort').disabled,false);
 assert.ok(!$('#train-effort').children.some(option=>option.value==='max'),'new Codex slot omits Max');
 $('#train-kind').value='claude-code';$('#train-kind').handlers.change();
 assert.equal($('#train-effort').disabled,false);
 assert.ok($('#train-effort').children.some(option=>option.value==='max'),'new Claude slot lists Max');

 console.log('PASS: agent depth, clear delivery/status controls, visible window launch, active-work strip, queue board');
})().catch(error=>{console.error(error);process.exitCode=1;});
