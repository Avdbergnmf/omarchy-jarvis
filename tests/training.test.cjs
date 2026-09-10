const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function element(){return {value:'',hidden:true,children:[],handlers:{},textContent:'',disabled:false,
 set innerHTML(value){this.children=[];},addEventListener(event,fn){this.handlers[event]=fn;},appendChild(child){this.children.push(child);},setAttribute(){},focus(){this.focused=true;},select(){}};}
const els={},requests=[];let previewCount=0,confirmCount=0,linked=null;
const $=selector=>els[selector]||(els[selector]=element());
let problem={id:'run:test',source:'Journal eval',title:'Review focus',priority:'P2',area:'brain',status:'open',notes:'',revision:'r1',evidence:{run_id:'test',version:'0.5.4'}};
const data={version:'test',revision:'abc',metrics:{runs:4,good:2,neutral:1,bad:0,flags:1,executed:2,denied:1},period:'Today UTC',sampled:false,context:['START.md'],session:'A-016 active',warnings:[],problems:[problem],assignments:[{id:'A-016',title:'Training',status:'in_progress'}],agents:[]};
let clipboardWrite=async()=>{},execCommandResult=true,execCommandCalls=0;
const ctx={newAssignment(p){linked=p;ctx.trainingPanel('work');},
 document:{querySelector:$,createElement:element,execCommand(){execCommandCalls++;return execCommandResult;}},
 get:async path=>{requests.push({path});return data;},
 post:async(path,body)=>{requests.push({path,body});
 if(path.endsWith('/preview')){previewCount++;return {preview_id:'p',message:'Review',files:[{path:'docs/assignment.md',content:'Scope'}]};}
 if(path.endsWith('/confirm')){confirmCount++;return {message:'Prepared; no agent contacted',handoff:'Paste START',paths:['docs/assignment.md']};}
 if(path.endsWith('/problem')){problem={...problem,...body,revision:'r2'};data.problems=[problem];return problem;}
 throw Error('unexpected mutation');},navigator:{clipboard:{writeText:(...args)=>clipboardWrite(...args)}}};
vm.runInNewContext(fs.readFileSync('overlay/training.js','utf8'),ctx);
(async()=>{
 await ctx.refreshTraining();
 assert.equal($('#train-version').textContent,'Jarvis test · abc');
 ctx.trainingPanel('validate');assert.equal($('#train-panel-validate').hidden,false);assert.equal($('#train-panel-problems').hidden,true);
 ctx.trainingPanel('problems');ctx.selectProblem(problem);
 assert.match($('#train-problem-context').textContent,/run_id/);
 $('#train-problem-title').value='Edited focus';$('#train-problem-priority').value='P0';$('#train-problem-notes').value='Expected stable focus';
 $('#problem-form').handlers.input();await ctx.refreshTraining();
 assert.equal($('#train-problem-title').value,'Edited focus','refresh preserves unsaved edits');
 await $('#train-generate').handlers.click();
 assert.equal(problem.title,'Edited focus');assert.equal(problem.priority,'P0');assert.equal($('#train-panel-work').hidden,false);
 assert.equal(linked.id,'run:test');assert.equal(linked.revision,'r2');assert.equal(linked.priority,'P0');
 $('#train-slot').value='slot-c1';$('#train-agent-label').value='Codex';$('#train-kind').value='cursor';$('#train-mode').value='now';$('#train-template').value='NEW_AGENT';
 $('#train-effort').disabled=false;$('#train-effort').value='high';$('#train-assignment').value='A-016';
 assert.equal(ctx.trainingTarget().reasoning_effort,'high','handoff preview carries the selected Codex launch effort');
 await ctx.previewTraining({operation:'assignment_save'});
 assert.equal(previewCount,1);assert.equal(confirmCount,0,'preview must not write');
 $('#train-cancel').handlers.click();assert.equal(confirmCount,0);
 await ctx.previewTraining({operation:'assignment'});await $('#train-confirm').handlers.click();
 assert.equal(confirmCount,1);assert.equal($('#train-handoff').value,'Paste START');
 await $('#train-confirm').handlers.click();assert.equal(confirmCount,1,'double confirm is ignored');

 // A-044: Copy handoff must actually work, degrade gracefully, and never claim
 // success it did not achieve.
 assert.equal($('#train-copy').hidden,false,'a confirmed handoff reveals Copy');
 assert.equal($('#train-copy').disabled,false);
 await $('#train-copy').handlers.click();
 assert.match($('#train-message').textContent,/Handoff copied/,'clipboard write succeeds');

 clipboardWrite=async()=>{throw new Error('denied')};execCommandResult=true;execCommandCalls=0;
 $('#train-handoff').focused=false;
 await $('#train-copy').handlers.click();
 assert.equal(execCommandCalls,1,'clipboard failure falls back to select+execCommand');
 assert.equal($('#train-handoff').focused,true);
 assert.match($('#train-message').textContent,/Handoff copied/,'fallback copy still reports success');

 execCommandResult=false;
 await $('#train-copy').handlers.click();
 assert.match($('#train-message').textContent,/Could not copy automatically/,'never claims success when every path fails');

 ctx.setHandoffText('');
 assert.equal($('#train-copy').hidden,true,'no handoff text hides Copy');
 assert.equal($('#train-copy').disabled,true);
 assert.equal($('#train-handoff').hidden,true);
 await $('#train-copy').handlers.click();
 assert.match($('#train-message').textContent,/No handoff text to copy yet/,'empty state is a clear message, not a silent no-op');
 $('#train-filter').value='done';ctx.renderProblems();assert.match($('#train-problem-count').textContent,/0 done/);
 $('#train-filter').value='open';ctx.renderProblems();
 const actions=$('#train-problems').children[0].children[2];
 await actions.children[0].handlers.click();assert.equal(problem.status,'done');
 $('#train-filter').value='done';ctx.renderProblems();
 await $('#train-problems').children[0].children[2].children[1].handlers.click();
 assert.equal(requests.at(-1).body.operation,'problem_delete');assert.equal(confirmCount,1,'delete only previews');
 console.log('PASS: Training panels, problem edits/priority/evidence, status filters, delete preview, confirmed handoff');
})().catch(error=>{console.error(error);process.exitCode=1;});
