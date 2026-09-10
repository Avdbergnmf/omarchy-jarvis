const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function element(){return {value:'',hidden:true,checked:false,disabled:false,className:'',textContent:'',children:[],handlers:{},
 set innerHTML(value){this.children=[];},addEventListener(k,fn){this.handlers[k]=fn;},appendChild(child){this.children.push(child);},focus(){}};}
const els={},previews=[];const $=id=>els[id]||(els[id]=element());
const item={id:'feat-test',title:'A guided test',status:'unvalidated',definition_hash:'abc',
 steps:['Perform one step',{text:'Type: hello. Confirm a reply appears.',kind:'auto',prompt:'hello'}],
 expected:'Expected result',jarvis_version_shipped:'0.5.0',last_run:null};
let posted=null,target=null,getCalls=[];
const ctx={document:{querySelector:$,createElement:element},trainingData:{version:'0.5.1'},
 trainingLine(parent,text){const p=element();p.textContent=text;parent.children.push(p);return p;},trainMessage(){},
 previewTraining:async payload=>previews.push(payload),
 post:async(path,body)=>{posted={path,body};if(path==='/v1/run')return {run_id:'auto-run-1'};return {run_id:'bug-run'};},
 get:async path=>{getCalls.push(path);return {status:'done',reply:'Hello! How can I help?'};},
 leaveTraining(){},input:element(),setConsoleTarget(id){target=id;},poll:async()=>{},};
vm.runInNewContext(fs.readFileSync('overlay/validation.js','utf8'),ctx);
(async()=>{
 ctx.renderValidations([item]);ctx.startValidation(item);
 assert.equal($('#validation-verify').disabled,true);
 const stepWraps=$('#validation-steps').children;
 const checks=stepWraps.map(wrap=>wrap.children[0].children[0]);
 checks[0].checked=true;checks[0].handlers.change();assert.equal($('#validation-verify').disabled,true);
 checks[1].checked=true;checks[1].handlers.change();assert.equal($('#validation-verify').disabled,false);

 // Auto step: a "Run this step" button exists only for the auto step and calls the same
 // /v1/run a chat send uses, then polls /v1/runs/<id> and shows the reply + run id.
 assert.equal(stepWraps[0].children.length,1,'a human step has only its checkbox label, no Run button');
 const runButton=stepWraps[1].children[1],result=stepWraps[1].children[2];
 assert.equal(runButton.textContent,'Run this step');
 await runButton.handlers.click();
 assert.equal(posted.path,'/v1/run');assert.equal(posted.body.prompt,'hello');
 assert.equal(getCalls[0],'/v1/runs/auto-run-1');
 assert.match(result.textContent,/Hello! How can I help\?/);
 assert.equal($('#validation-run').value,'auto-run-1','the observed run id is captured automatically');
 assert.equal(runButton.disabled,false,'button re-enables once the run settles');

 $('#validation-notes').value='Worked';await $('#validation-verify').handlers.click();
 assert.equal(previews[0].outcome,'validated');assert.equal(previews[0].attempted,true);
 assert.equal(posted.path,'/v1/run','preview must not file or record the result, or touch training endpoints');

 // A confirmed result closes the guide back to the list, and the list itself (not just a
 // click-through) shows the report — so it's unmistakable the result actually recorded.
 ctx.validationSaved({outcome:'validated'});
 assert.equal($('#validation-guide').hidden,true,'guide collapses on a confirmed result');
 const validated={...item,status:'validated',last_run:{id:'r1',result:'validated',ts:'2026-09-10T00:00:00Z',jarvis_version:'0.5.1',notes:''}};
 $('#validation-show-all').checked=true;ctx.renderValidations([validated,{...item,definition_hash:'other',id:'feat-two',title:'Second'}]);
 assert.match($('#validation-list').children[0].children[1].textContent,/validated · 2026-09-10 · Jarvis 0.5.1/,'a validated item shows its report inline in the list, not only after a click');
 assert.equal($('#validation-list').children[1].children.length,1,'an item with no last_run has no report line');

 const failed={...item,status:'failed',last_run:{id:'record',result:'failed',ts:'today',jarvis_version:'0.5.1',notes:'Did not work'}};
 ctx.renderValidations([failed]);ctx.startValidation(failed);
 assert.equal($('#validation-report').hidden,false);
 await $('#validation-report').handlers.click();
 assert.equal(posted.path,'/v1/training/report');assert.equal(posted.body.record_id,'record');assert.equal(target,'bug-run');
 ctx.renderValidations([{...item,definition_hash:'changed'}]);
 assert.equal($('#validation-guide').hidden,true,'changed guide requires a fresh test');
 console.log('PASS: guided steps gate Verify; auto steps run+capture a run id; confirmed results close the guide with an inline list report; failed evidence opens report intake; changed guides reset');
})().catch(error=>{console.error(error);process.exitCode=1;});
