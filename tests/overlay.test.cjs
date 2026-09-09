const fs=require('node:fs');const vm=require('node:vm');const assert=require('node:assert/strict');
const handlers={};const requests=[];
function makeElement(){
 return {hidden:true,disabled:false,className:'',textContent:'',innerHTML:'',children:[],focused:false,
  focus(){this.focused=true;},
  appendChild(child){this.children.push(child);},
  addEventListener(n,fn){this.handlers=this.handlers||{};this.handlers[n]=fn;}};
}
const elements={
 '#prompt':{value:'open my planning in a new workspace',disabled:false,focused:false,focus(){this.focused=true;}},
 '#status':makeElement(),
 '#plan':makeElement(),
 '#plan-actions':makeElement(),
 '#run-btn':makeElement(),
 '#cancel-btn':makeElement(),
 '#steps':makeElement(),
 '#step-list':makeElement(),
 '#console-btn':makeElement(),
 '#meta':makeElement(),
};
const store={};
let runState='awaiting_approval';
const context={
 document:{
  querySelector(selector){
   if(elements[selector])return elements[selector];
   if(selector==='#prompt-form')return {addEventListener(n,fn){handlers[n]=fn;}};
   throw new Error('unexpected selector '+selector);
  },
  createElement(){return makeElement();},
  addEventListener(n,fn){handlers[n]=fn;},
 },
 localStorage:{getItem(k){return store[k]||null;},setItem(k,v){store[k]=v;}},
 setTimeout(fn){fn();},
 clearTimeout(){},
 fetch:async(path,options)=>{
  requests.push({path,options});
  if(path==='/v1/session')return {ok:true,json:async()=>({token:'test'})};
  if(path==='/health')return {ok:true,json:async()=>({model:'qwen2.5:3b',ollama:'ok',approval_mode:'always'})};
  if(path==='/v1/run')return {ok:true,json:async()=>({run_id:'test-run',status:'planning',reply:'Thinking…'})};
  if(path==='/v1/runs/test-run')return {ok:true,json:async()=>{
   if(runState==='awaiting_approval')return {status:'awaiting_approval',reply:'Review the plan.',plan:{actions:[{tool:'run_skill',arguments:{skill:'open-planning'}}]},steps:[]};
   return {status:'done',reply:'Completed: open-planning.',plan:{actions:[{tool:'run_skill',arguments:{skill:'open-planning'}}]},steps:[{tool:'run_skill',label:'open-planning',status:'done',summary:'ok'}]};
  }};
  if(path==='/v1/runs/test-run/approve'){runState='done';return {ok:true,json:async()=>({status:'running'})};}
  if(path==='/v1/runs/test-run/deny')return {ok:true,json:async()=>({status:'denied'})};
  if(path==='/v1/close')return {ok:true,json:async()=>({ok:true})};
  return {ok:true,json:async()=>({ok:true})};
 },
};
vm.runInNewContext(fs.readFileSync('overlay/app.js','utf8'),context);
(async()=>{
 await handlers.submit({preventDefault(){}});
 assert.equal(JSON.parse(requests.find(r=>r.path==='/v1/run').options.body).prompt,elements['#prompt'].value);
 assert.equal(elements['#status'].textContent,'Review the plan.');
 assert.equal(elements['#plan'].hidden,false,'plan panel must be shown while awaiting approval');
 assert.equal(elements['#run-btn'].focused,true,'Run button must receive focus so Enter confirms');
 assert.equal(elements['#console-btn'].disabled,false,'Open console must be enabled for the current run');

 await elements['#run-btn'].handlers.click();
 assert(requests.some(r=>r.path==='/v1/runs/test-run/approve'),'Run must approve the pending plan');
 assert.equal(elements['#status'].textContent,'Completed: open-planning.');
 assert.equal(elements['#prompt'].disabled,false);

 await handlers.keydown({key:'Escape',preventDefault(){}});
 assert(requests.some(r=>r.path==='/v1/close'),'Escape must close the overlay');

 await elements['#console-btn'].handlers.click();
 assert(requests.some(r=>r.path==='/v1/runs/test-run/console'),'Open console must target the current/last run');

 console.log('PASS: overlay plan/approve, step completion, Escape, always-available Open console');
})();
