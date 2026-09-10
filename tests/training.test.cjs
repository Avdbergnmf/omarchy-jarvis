const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function element(){return {value:'',hidden:true,children:[],handlers:{},textContent:'',disabled:false,
 addEventListener(event,fn){this.handlers[event]=fn;},appendChild(child){this.children.push(child);},setAttribute(){},focus(){this.focused=true;},select(){}};}
const els={},requests=[];let previewCount=0,confirmCount=0;
const $=selector=>els[selector]||(els[selector]=element());
const data={version:'test',revision:'abc',metrics:{runs:4,good:2,neutral:1,bad:0,flags:1,executed:2,denied:1},period:'Today UTC',sampled:false,context:['START.md'],session:'A-008 active',warnings:[],problems:[{id:'run:test',source:'Journal eval',title:'Review focus'}],assignments:[{id:'A-008',title:'Training',status:'in_progress'}],agents:[]};
const ctx={document:{querySelector:$,createElement:element},input:element(),hideCommands(){},
 get:async path=>{requests.push(path);return data;},
 post:async(path,body)=>{requests.push(path);
 if(path.endsWith('/preview')){previewCount++;return {preview_id:'p',message:'Review',files:[{path:'docs/assignment.md',content:'Scope'}]};}
 if(path.endsWith('/confirm')){confirmCount++;return {message:'Prepared; no agent contacted',handoff:'Paste START',paths:['docs/assignment.md']};}
 throw Error('unexpected mutation');},navigator:{clipboard:{writeText:async()=>{}}},};
vm.runInNewContext(fs.readFileSync('overlay/training.js','utf8'),ctx);
(async()=>{
 await ctx.enterTraining();
 assert.equal($('#training-view').hidden,false);assert.equal($('#chat-view').hidden,true);
 assert.equal($('#train-version').textContent,'Jarvis test · abc');
 await ctx.previewTraining({operation:'assignment'});
 assert.equal(previewCount,1);assert.equal(confirmCount,0,'preview must not write');
 $('#train-cancel').handlers.click();assert.equal(confirmCount,0);
 await ctx.previewTraining({operation:'assignment'});
 await $('#train-confirm').handlers.click();
 assert.equal(confirmCount,1);assert.equal($('#train-handoff').value,'Paste START');
 await $('#train-confirm').handlers.click();assert.equal(confirmCount,1,'double confirm is ignored');
 assert.equal(ctx.leaveTraining(),true);assert.equal($('#training-view').hidden,true);
 assert.equal(ctx.leaveTraining(),false);
 console.log('PASS: Training open/back, metrics, preview/cancel/confirm and paste-ready result');
})().catch(error=>{console.error(error);process.exitCode=1;});
