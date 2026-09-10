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
},{
 trace_id:'t-new',run_id:'run-new',status:'done',planner_mode:'tools',
 meaningful_response_latency_ns:40_000_000,ack_latency_ns:3_000_000,ttft_ns:10_000_000,
 jarvis_version:'0.5.11',git_revision:'def',model:'qwen2.5:3b'
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
const summary={
 count:3,with_mrl:2,
 p50_ns:40_000_000,p90_ns:80_000_000,p95_ns:80_000_000,p99_ns:80_000_000,
 slow_tail:[{trace_id:'t-slow',run_id:'run-slow',meaningful_response_latency_ns:80_000_000,jarvis_version:'0.5.10',status:'done'}],
 options:{planner_mode:['json_plan','tools'],status:['done','error'],jarvis_version:['0.5.10','0.5.11'],git_revision:['abc','def']},
 compare:null,
 budgets:{p50_ms:null,p90_ms:null,enforced:false},
 flags:{over_p50:false,over_p90:false},
 ledger_note:'- 2026-09-10 — PERF: n=3 · with_mrl=2 · p50=40ms · p90=80ms · p95=80ms · p99=80ms · budgets unset (placeholders only; not a merge gate)'
};
const filteredSummary={
 ...summary,count:1,with_mrl:1,p50_ns:40_000_000,p90_ns:40_000_000,p95_ns:40_000_000,p99_ns:40_000_000,
 slow_tail:[],
 ledger_note:'- 2026-09-10 — PERF: n=1 · with_mrl=1 · p50=40ms · p90=40ms · p95=40ms · p99=40ms · budgets unset (placeholders only; not a merge gate)'
};
const compareSummary={
 ...summary,
 compare:{
  left:{label:'0.5.10',key:'jarvis_version',count:2,with_mrl:1,p50_ns:80_000_000,p90_ns:80_000_000},
  right:{label:'0.5.11',key:'jarvis_version',count:1,with_mrl:1,p50_ns:40_000_000,p90_ns:40_000_000}
 },
 ledger_note:'- 2026-09-10 — PERF: n=3 · with_mrl=2 · p50=40ms · p90=80ms · compare 0.5.10 (n=2 p50=80ms p90=80ms) vs 0.5.11 (n=1 p50=40ms p90=40ms) · budgets unset (placeholders only; not a merge gate)'
};
const gets=[];
let copied='';
const ctx={
 document:{querySelector:$,createElement:element},
 trainMessage(){},
 navigator:{clipboard:{writeText:async text=>{copied=text;}}},
 get:async path=>{
  gets.push(path);
  if(path.startsWith('/v1/latency/summary')){
   if(path.includes('planner_mode=tools'))return filteredSummary;
   if(path.includes('left=0.5.10'))return compareSummary;
   return summary;
  }
  if(path.startsWith('/v1/latency/traces?')||path==='/v1/latency/traces'){
   if(path.includes('planner_mode=tools'))return {traces:traces.filter(t=>t.planner_mode==='tools')};
   return {traces};
  }
  if(path==='/v1/latency/traces/t-slow')return detail;
  throw new Error('unexpected '+path);
 }
};
['#latency-refresh','#latency-list','#latency-count','#latency-inspector','#latency-hint','#latency-meta','#latency-waterfall',
 '#latency-stats','#latency-window','#latency-planner','#latency-status','#latency-version','#latency-revision',
 '#latency-left','#latency-right','#latency-compare-out','#latency-copy-note','#latency-note','#latency-tail','#latency-tail-count'
].forEach($);
$('#latency-window').value='20';
vm.runInNewContext(fs.readFileSync('overlay/latency.js','utf8'),ctx);
(async()=>{
 await ctx.refreshLatency();
 assert.ok(gets[0].startsWith('/v1/latency/traces'),'history fetch');
 assert.ok(gets.some(p=>p.startsWith('/v1/latency/summary')),'summary fetch');
 assert.equal($('#latency-list').children.length,3,'history lists recent traces');
 assert.match($('#latency-list').children[0].children[0].textContent,/run-slow · done · 80 ms/);
 assert.match($('#latency-list').children[1].children[0].textContent,/run-err · error · no MRL/,'incomplete/error traces stay visible');
 const slowBar=$('#latency-list').children[0].children[1].children[0];
 const errBar=$('#latency-list').children[1].children[1].children[0];
 assert.equal(slowBar.style.width,'100%');
 assert.equal(errBar.className.includes('unfinished')||errBar.className.includes('error'),true);
 assert.match($('#latency-count').textContent,/meaningful_response_latency/);

 const stats=$('#latency-stats').children.map(box=>box.children[0].textContent+' '+box.children[1].textContent).join(' | ');
 assert.match(stats,/p50 40 ms/);
 assert.match(stats,/p90 80 ms/);
 assert.match(stats,/p95 80 ms/);
 assert.match(stats,/p99 80 ms/);
 assert.match($('#latency-note').value,/PERF/);
 assert.doesNotMatch($('#latency-note').value,/open bitwarden|prompt/i);
 assert.equal($('#latency-tail').children.length,1,'slow tail lists p90 traces');
 assert.match($('#latency-tail').children[0].children[0].textContent,/run-slow/);

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

 gets.length=0;
 $('#latency-planner').value='tools';
 await ctx.refreshLatency();
 assert.ok(gets.some(p=>p.includes('planner_mode=tools')),'planner filter is sent');
 assert.equal($('#latency-list').children.length,1,'filtered history');
 assert.match($('#latency-list').children[0].children[0].textContent,/run-new/);

 gets.length=0;
 $('#latency-planner').value='';
 $('#latency-left').value='jarvis_version:0.5.10';
 $('#latency-right').value='jarvis_version:0.5.11';
 await ctx.refreshLatency();
 assert.ok(gets.some(p=>p.includes('left=0.5.10')&&p.includes('right=0.5.11')),'version compare query');
 assert.match($('#latency-compare-out').textContent,/0\.5\.10.*vs.*0\.5\.11/);
 assert.match($('#latency-note').value,/compare 0\.5\.10/);

 copied='';
 await $('#latency-copy-note').handlers.click();
 assert.match(copied,/PERF/);
 assert.doesNotMatch(copied,/prompt|open bitwarden/i);

 gets.length=0;
 await $('#latency-tail').children[0].handlers.click();
 assert.equal(gets.includes('/v1/latency/traces/t-slow'),true,'slow-tail click jumps to inspector');

 console.log('PASS: Training latency history bars, waterfall inspector, percentiles, filters, compare, PERF copy, slow-tail jump');
})().catch(error=>{console.error(error);process.exitCode=1;});
