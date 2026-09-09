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
 '#draft-preview':makeElement(),
 '#draft-title':makeElement(),
 '#draft-body':makeElement(),
 '#run-btn':makeElement(),
 '#cancel-btn':makeElement(),
 '#steps':makeElement(),
 '#step-list':makeElement(),
 '#qa':makeElement(),
 '#qa-question':makeElement(),
 '#qa-answer':{value:'',disabled:false,focused:false,focus(){this.focused=true;}},
 '#qa-skip':makeElement(),
 '#console-btn':makeElement(),
 '#meta':makeElement(),
 '#feedback':makeElement(),
 '#fb-good':makeElement(),
 '#fb-neutral':makeElement(),
 '#fb-bad':makeElement(),
};
const store={};
let runState='awaiting_approval';
let qaRunState='fresh'; // 'fresh' -> 'answered' -> 'finished'
const context={
 document:{
  querySelector(selector){
   if(elements[selector])return elements[selector];
   if(selector==='#prompt-form')return {addEventListener(n,fn){handlers[n]=fn;}};
   if(selector==='#qa-form')return {addEventListener(n,fn){handlers['qaForm'+n]=fn;}};
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
  if(path==='/v1/runs/test-run/feedback'){
   const rating=JSON.parse(options.body).rating;
   if(rating==='bad')return {ok:true,json:async()=>({run_id:'fb-bug-run',status:'planning',reply:'Thinking…'})};
   return {ok:true,json:async()=>({run_id:'test-run',status:'done',reply:'Completed: open-planning.',feedback:rating,plan:{actions:[{tool:'run_skill',arguments:{skill:'open-planning'}}]},steps:[{tool:'run_skill',label:'open-planning',status:'done',summary:'ok'}]})};
  }
  if(path==='/v1/runs/fb-bug-run')return {ok:true,json:async()=>({status:'awaiting_answer',reply:'What did you expect to happen?',plan:null,steps:[]})};
  if(path==='/v1/runs/qa-run')return {ok:true,json:async()=>{
   if(qaRunState==='fresh')return {status:'awaiting_answer',reply:'What actually happened instead?',plan:null,steps:[]};
   if(qaRunState==='finished')return {status:'done',reply:'Cancelled — no actions were run.',plan:null,steps:[]};
   return {status:'awaiting_approval',reply:'Draft ready — review before filing.',plan:{actions:[{tool:'report_bug',arguments:{title:'Bug: x',body:'y',difficulty:'M'}}]},draft:{title:'Bug: x',body:'y'},steps:[]};
  }};
  if(path==='/v1/runs/qa-run/answer'){qaRunState='answered';return {ok:true,json:async()=>({status:'awaiting_approval'})};}
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

 assert.equal(elements['#feedback'].hidden,false,'feedback controls must show once a run reaches a terminal status');
 await elements['#fb-good'].handlers.click();
 assert(requests.some(r=>r.path==='/v1/runs/test-run/feedback'&&JSON.parse(r.options.body).rating==='good'),'thumbs-up must post rating=good');
 assert.equal(elements['#feedback'].hidden,true,'feedback controls must hide once a rating is recorded');

 await handlers.keydown({key:'Escape',preventDefault(){}});
 assert(requests.some(r=>r.path==='/v1/close'),'Escape must close the overlay');

 await elements['#console-btn'].handlers.click();
 assert(requests.some(r=>r.path==='/v1/runs/test-run/console'),'Open console must target the current/last run');

 // Re-fetch a fresh done state (no feedback recorded yet) so the controls show again.
 context.render(await context.get('/v1/runs/test-run'));
 assert.equal(elements['#feedback'].hidden,false);
 // Exercise the thumbs-down -> bug-intake handoff directly via post/render (not the
 // real button click): fb-bug-run always answers 'awaiting_answer', and this mock's
 // synchronous setTimeout would otherwise recurse sendFeedback's own poll() forever
 // (same hazard the qa-run scenario below already avoids the same way).
 const fbBad=await context.post('/v1/runs/test-run/feedback',{rating:'bad'});
 assert(requests.some(r=>r.path==='/v1/runs/test-run/feedback'&&JSON.parse(r.options.body).rating==='bad'),'thumbs-down must post rating=bad');
 assert.equal(fbBad.run_id,'fb-bug-run','thumbs-down must hand off to the new intake run id the server returns');
 context.setConsoleTarget(fbBad.run_id);
 context.render(await context.get('/v1/runs/fb-bug-run'));
 assert.equal(elements['#qa'].hidden,false,'thumbs-down must enter the bug-intake Q&A flow on the new run it returns');
 assert.equal(elements['#qa-question'].textContent,'What did you expect to happen?');

 // Single get+render (not the auto-continuing poll loop) — this mock's setTimeout
 // fires synchronously/immediately rather than after a real delay, so letting
 // poll() self-schedule here would race an orphaned background chain against
 // the assertions below instead of just exercising one rendered state.
 context.setConsoleTarget('qa-run');
 context.render(await context.get('/v1/runs/qa-run'));
 assert.equal(elements['#qa'].hidden,false,'qa panel must show during intake Q&A');
 assert.equal(elements['#plan'].hidden,true,'plan panel must stay hidden during intake Q&A');
 assert.equal(elements['#qa-question'].textContent,'What actually happened instead?');

 elements['#qa-answer'].value='it crashed';
 await handlers['qaFormsubmit']({preventDefault(){}});
 const answerReq=requests.find(r=>r.path==='/v1/runs/qa-run/answer');
 assert(answerReq,'answer must post to /answer');
 assert.equal(JSON.parse(answerReq.options.body).text,'it crashed');
 assert.equal(elements['#qa'].hidden,true,'qa panel must hide once intake finalizes into a draft');
 assert.equal(elements['#plan'].hidden,false,'plan panel must show the filed draft for review');
 assert.equal(elements['#draft-preview'].hidden,false,'draft preview must show for report_bug plans');
 assert.equal(elements['#draft-title'].textContent,'Bug: x');
 qaRunState='finished'; // let any still-orphaned background poll settle to a terminal status

 console.log('PASS: overlay plan/approve, step completion, Escape, always-available Open console, intake Q&A + draft preview');
})();
