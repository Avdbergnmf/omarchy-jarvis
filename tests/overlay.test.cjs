const fs=require('node:fs');const vm=require('node:vm');const assert=require('node:assert/strict');
const handlers={};const requests=[];
const input={value:'open my planning in a new workspace',disabled:false,focus(){this.focused=true;}};
const status={textContent:'',className:''};
const context={document:{querySelector(selector){return selector==='#prompt'?input:selector==='#status'?status:{addEventListener(n,fn){handlers[n]=fn;}};},addEventListener(n,fn){handlers[n]=fn;}},setTimeout(fn){fn();},fetch:async(path,options)=>{requests.push({path,options});return {ok:true,json:async()=>path==='/v1/session'?{token:'test'}:path==='/v1/run'?{run_id:'test-run'}:path.startsWith('/v1/runs/')?{status:'done',reply:'Completed: open-planning.'}:{ok:true}};}};
vm.runInNewContext(fs.readFileSync('overlay/app.js','utf8'),context);
(async()=>{await handlers.submit({preventDefault(){}});assert.equal(status.textContent,'Completed: open-planning.');assert.equal(input.disabled,false);assert.equal(JSON.parse(requests.find(r=>r.path==='/v1/run').options.body).prompt,input.value);await handlers.keydown({key:'Escape',preventDefault(){}});assert(requests.some(r=>r.path==='/v1/close'));console.log('PASS: overlay submit, completion, Escape');})();
