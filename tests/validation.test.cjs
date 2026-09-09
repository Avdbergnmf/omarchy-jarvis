const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function element(){return {value:'',hidden:true,checked:false,disabled:false,children:[],handlers:{},
 addEventListener(k,fn){this.handlers[k]=fn;},appendChild(child){this.children.push(child);},focus(){}};}
const els={},previews=[];const $=id=>els[id]||(els[id]=element());
const item={id:'feat-test',title:'A guided test',status:'unvalidated',definition_hash:'abc',steps:['Perform one step','Check outcome'],expected:'Expected result',jarvis_version_shipped:'0.5.0',last_run:null};
let posted=null,target=null;
const ctx={document:{querySelector:$,createElement:element},trainingData:{version:'0.5.1'},trainingLine(){},trainMessage(){},
 previewTraining:async payload=>previews.push(payload),post:async(path,body)=>{posted={path,body};return {run_id:'bug-run'};},
 leaveTraining(){},input:element(),setConsoleTarget(id){target=id;},poll:async()=>{},};
vm.runInNewContext(fs.readFileSync('overlay/validation.js','utf8'),ctx);
(async()=>{
 ctx.renderValidations([item]);ctx.startValidation(item);
 assert.equal($('#validation-verify').disabled,true);
 const checks=$('#validation-steps').children.map(label=>label.children[0]);
 checks[0].checked=true;checks[0].handlers.change();assert.equal($('#validation-verify').disabled,true);
 checks[1].checked=true;checks[1].handlers.change();assert.equal($('#validation-verify').disabled,false);
 $('#validation-notes').value='Worked';await $('#validation-verify').handlers.click();
 assert.equal(previews[0].outcome,'validated');assert.equal(previews[0].attempted,true);
 assert.equal(posted,null,'preview must not file or record the result');
 const failed={...item,status:'failed',last_run:{id:'record',result:'failed',ts:'today',jarvis_version:'0.5.1',notes:'Did not work'}};
 ctx.renderValidations([failed]);ctx.startValidation(failed);
 assert.equal($('#validation-report').hidden,false);
 await $('#validation-report').handlers.click();
 assert.equal(posted.path,'/v1/training/report');assert.equal(posted.body.record_id,'record');assert.equal(target,'bug-run');
 ctx.renderValidations([{...item,definition_hash:'changed'}]);
 assert.equal($('#validation-guide').hidden,true,'changed guide requires a fresh test');
 console.log('PASS: guided steps gate Verify; failed evidence opens report intake; changed guides reset');
})().catch(error=>{console.error(error);process.exitCode=1;});
