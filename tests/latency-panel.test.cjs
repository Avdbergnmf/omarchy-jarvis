const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function element(){
 return {value:'',hidden:true,disabled:false,className:'',textContent:'',children:[],handlers:{},style:{},
  set innerHTML(value){this.children=[];},
  addEventListener(k,fn){this.handlers[k]=fn;},
  appendChild(child){this.children.push(child);return child;},
  setAttribute(k,v){this[k]=v;},
  focus(){}};
}
const els={};
const $=selector=>els[selector]||(els[selector]=element());
const traces=[{
 trace_id:'t-slow',run_id:'run-slow',status:'done',planner_mode:'json_plan',
 meaningful_response_latency_ns:80_000_000,ack_latency_ns:5_000_000,ttft_ns:20_000_000,
 jarvis_version:'0.5.10',git_revision:'abc',model:'qwen2.5:3b'
},{
 trace_id:'t-err',run_id:'run-err',status:'error',planner_mode:'json_plan',
 meaningful_response_latency_ns:null,ack_latency_ns:4_000_000,ttft_ns:null,
 jarvis_version:'0.5.10',git_revision:'abc',model:'qwen2.5:3b'
}];
const detail={
 trace_id:'t-slow',run_id:'run-slow',status:'done',planner_mode:'json_plan',
 started_ns:0,ended_ns:80_000_000,
 meaningful_response_latency_ns:80_000_000,ack_latency_ns:5_000_000,ttft_ns:20_000_000,
 jarvis_version:'0.5.10',git_revision:'abc',model:'qwen2.5:3b',
 spans:[
  {span_id:'root',parent_id:null,name:'interaction',start_ns:0,end_ns:80_000_000,duration_ns:80_000_000,status:'done',attrs:{}},
  {span_id:'plan',parent_id:'root',name:'plan',start_ns:5_000_000,end_ns:40_000_000,duration_ns:35_000_000,status:'ok',attrs:{}},
  {span_id:'chat',parent_id:'plan',name:'model.chat',start_ns:6_000_000,end_ns:26_000_000,duration_ns:20_000_000,status:'ok',attrs:{}},
  {span_id:'exe',parent_id:'root',name:'execute',start_ns:45_000_000,end_ns:70_000_000,duration_ns:25_000_000,status:'ok',attrs:{}},
  {span_id:'ta',parent_id:'exe',name:'tool',start_ns:46_000_000,end_ns:60_000_000,duration_ns:14_000_000,status:'ok',attrs:{tool:'scratch_toggle'}},
  {span_id:'tb',parent_id:'exe',name:'tool',start_ns:48_000_000,end_ns:62_000_000,duration_ns:14_000_000,status:'ok',attrs:{tool:'workspace_new'}},
  {span_id:'open',parent_id:'exe',name:'tool',start_ns:63_000_000,end_ns:70_000_000,duration_ns:7_000_000,status:'unfinished',attrs:{tool:'open_app_by_name'}}
 ]
};
const gets=[];
const ctx={
 document:{querySelector:$,createElement:element},
 trainMessage(){},
 get:async path=>{
  gets.push(path);
  if(path==='/v1/latency/traces')return {traces};
  if(path==='/v1/latency/traces/t-slow')return detail;
  throw new Error('unexpected '+path);
 }
};
['#latency-refresh','#latency-list','#latency-count','#latency-inspector','#latency-hint','#latency-meta','#latency-waterfall'].forEach($);
vm.runInNewContext(fs.readFileSync('overlay/latency.js','utf8'),ctx);
(async()=>{
 await ctx.refreshLatency();
 assert.equal(gets[0],'/v1/latency/traces');
 assert.equal($('#latency-list').children.length,2,'history lists recent traces');
 assert.match($('#latency-list').children[0].children[0].textContent,/run-slow · done · 80 ms/);
 assert.match($('#latency-list').children[1].children[0].textContent,/run-err · error · no MRL/,'incomplete/error traces stay visible');
 const slowBar=$('#latency-list').children[0].children[1].children[0];
 const errBar=$('#latency-list').children[1].children[1].children[0];
 assert.equal(slowBar.style.width,'100%');
 assert.equal(errBar.className.includes('unfinished')||errBar.className.includes('error'),true);
 assert.match($('#latency-count').textContent,/meaningful_response_latency/);

 await $('#latency-list').children[0].handlers.click();
 assert.equal(gets.includes('/v1/latency/traces/t-slow'),true);
 assert.equal($('#latency-inspector').hidden,false);
 assert.match($('#latency-meta').textContent,/MRL 80 ms/);
 assert.doesNotMatch($('#latency-meta').textContent,/open bitwarden|prompt/i);
 const water=$('#latency-waterfall').children;
 assert.equal(water.length,7);
 const names=water.map(row=>row.children[0].textContent);
 assert.ok(names.some(n=>n.startsWith('model.chat')),'nested model.chat is shown');
 assert.ok(names.filter(n=>n.includes('tool')).length>=2,'parallel tool spans both appear');
 const toolA=water.find(row=>row.children[0].textContent.includes('scratch_toggle'));
 const toolB=water.find(row=>row.children[0].textContent.includes('workspace_new'));
 const leftA=parseFloat(toolA.children[1].children[0].style.marginLeft);
 const leftB=parseFloat(toolB.children[1].children[0].style.marginLeft);
 assert.ok(leftA>0&&leftB>0,'waterfall offsets nested/parallel work from t0');
 const unfinished=water.find(row=>row.children[0].textContent.includes('unfinished'));
 assert.ok(unfinished,'incomplete spans remain inspectable');
 assert.equal(unfinished.className.includes('unfinished'),true);
 const dumped=JSON.stringify($('#latency-waterfall'));
 assert.doesNotMatch(dumped,/password|arguments/);
 console.log('PASS: Training latency history bars, waterfall inspector, parallel/nested spans, incomplete traces');
})().catch(error=>{console.error(error);process.exitCode=1;});
