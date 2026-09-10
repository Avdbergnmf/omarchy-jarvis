const latencyEl=id=>document.querySelector('#latency-'+id);
let latencyTraces=[],latencyActiveId=null,latencyLoad=0,latencySummary=null;

function latencyMs(ns){
 if(ns==null||ns==='')return null;
 const value=Number(ns);
 return Number.isFinite(value)?value/1e6:null;
}
function latencyFormat(ns){
 const ms=latencyMs(ns);
 if(ms==null)return '—';
 if(ms<10)return ms.toFixed(1)+' ms';
 return Math.round(ms)+' ms';
}
function latencyDepth(span,byId){
 let depth=0,id=span.parent_id,guard=0;
 while(id&&byId[id]&&guard++<32){depth+=1;id=byId[id].parent_id;}
 return depth;
}
function latencyRange(trace){
 const started=Number(trace.started_ns)||0;
 let end=Number(trace.ended_ns)||started;
 for(const span of trace.spans||[]){
  if(span.end_ns!=null)end=Math.max(end,Number(span.end_ns));
  if(span.start_ns!=null)end=Math.max(end,Number(span.start_ns));
 }
 return Math.max(end-started,1);
}
function latencyVal(id){
 const el=latencyEl(id);
 return el&&el.value?el.value:'';
}
function latencyQueryString(){
 const params=[];
 const window=latencyVal('window')||'20';
 params.push('limit='+encodeURIComponent(window));
 const planner=latencyVal('planner'); if(planner)params.push('planner_mode='+encodeURIComponent(planner));
 const status=latencyVal('status'); if(status)params.push('status='+encodeURIComponent(status));
 const version=latencyVal('version'); if(version)params.push('jarvis_version='+encodeURIComponent(version));
 const revision=latencyVal('revision'); if(revision)params.push('git_revision='+encodeURIComponent(revision));
 const left=latencyVal('left');
 const right=latencyVal('right');
 if(left&&right){
  const [lk,lv]=left.split(':');
  const [rk,rv]=right.split(':');
  if(lv&&rv){
   params.push('left='+encodeURIComponent(lv));
   params.push('left_key='+encodeURIComponent(lk||'jarvis_version'));
   params.push('right='+encodeURIComponent(rv));
   params.push('right_key='+encodeURIComponent(rk||'jarvis_version'));
  }
 }
 return '?'+params.join('&');
}
function latencyFillSelect(id,values,blank){
 const el=latencyEl(id); if(!el)return;
 const current=el.value;
 el.innerHTML='';
 const all=document.createElement('option'); all.value=''; all.textContent=blank; el.appendChild(all);
 for(const value of values||[]){
  const option=document.createElement('option'); option.value=value; option.textContent=value; el.appendChild(option);
 }
 if([...el.children].some(opt=>opt.value===current))el.value=current;
}
function latencyFillCompare(id,options){
 const el=latencyEl(id); if(!el)return;
 const current=el.value;
 el.innerHTML='';
 const blank=document.createElement('option'); blank.value=''; blank.textContent='—'; el.appendChild(blank);
 for(const [key,label,values] of [['jarvis_version','Version',options&&options.jarvis_version],['git_revision','Revision',options&&options.git_revision]]){
  if(!values||!values.length)continue;
  const group=document.createElement('optgroup'); group.label=label;
  for(const value of values){
   const option=document.createElement('option'); option.value=key+':'+value; option.textContent=label+' '+value; group.appendChild(option);
  }
  el.appendChild(group);
 }
 function hasValue(node,value){
  if(!node)return false;
  if(node.value===value)return true;
  for(const child of node.children||[]){if(hasValue(child,value))return true;}
  return false;
 }
 if(current&&hasValue(el,current))el.value=current;
}
function latencyStat(label,value,over){
 const box=document.createElement('div');
 box.className='latency-stat'+(over?' over':'');
 const name=document.createElement('span'); name.className='latency-stat-label'; name.textContent=label;
 const num=document.createElement('span'); num.className='latency-stat-value'; num.textContent=value;
 box.appendChild(name); box.appendChild(num);
 return box;
}
function renderLatencyStats(summary){
 const root=latencyEl('stats'); if(!root)return;
 root.innerHTML='';
 latencySummary=summary||{};
 const flags=latencySummary.flags||{};
 const budgets=latencySummary.budgets||{};
 root.appendChild(latencyStat('n',String(latencySummary.count||0)));
 root.appendChild(latencyStat('with MRL',String(latencySummary.with_mrl||0)));
 root.appendChild(latencyStat('p50',latencyFormat(latencySummary.p50_ns),flags.over_p50));
 root.appendChild(latencyStat('p90',latencyFormat(latencySummary.p90_ns),flags.over_p90));
 root.appendChild(latencyStat('p95',latencyFormat(latencySummary.p95_ns)));
 root.appendChild(latencyStat('p99',latencyFormat(latencySummary.p99_ns)));
 if(budgets.p50_ms||budgets.p90_ms){
  root.appendChild(latencyStat('budget p50',(budgets.p50_ms||'unset')+' ms'));
  root.appendChild(latencyStat('budget p90',(budgets.p90_ms||'unset')+' ms'));
 }
 const note=latencyEl('note');
 if(note)note.value=latencySummary.ledger_note||'';
 const compare=latencyEl('compare-out');
 if(compare){
  const pair=latencySummary.compare;
  if(pair&&pair.left&&pair.right){
   compare.textContent=pair.left.label+' n='+pair.left.count+' p50 '+latencyFormat(pair.left.p50_ns)+' p90 '+latencyFormat(pair.left.p90_ns)+'  vs  '+pair.right.label+' n='+pair.right.count+' p50 '+latencyFormat(pair.right.p50_ns)+' p90 '+latencyFormat(pair.right.p90_ns);
  }else compare.textContent='Pick two versions or revisions to compare sample counts.';
 }
}
function renderLatencyTail(summary){
 const list=latencyEl('tail'); if(!list)return;
 list.innerHTML='';
 const rows=(summary&&summary.slow_tail)||[];
 const count=latencyEl('tail-count');
 if(count)count.textContent=rows.length?rows.length+' traces at or above p90 — click to inspect':'No slow-tail traces in this window.';
 for(const trace of rows){
  const row=document.createElement('button');
  row.type='button';
  row.className='latency-row'+(latencyActiveId===trace.trace_id?' selected':'');
  const label=document.createElement('span');
  label.className='latency-row-label';
  label.textContent=(trace.run_id||trace.trace_id)+' · '+latencyFormat(trace.meaningful_response_latency_ns)+' · '+(trace.jarvis_version||'');
  row.appendChild(label);
  row.addEventListener('click',()=>selectLatencyTrace(trace));
  list.appendChild(row);
 }
}

function renderLatencyHistory(traces){
 latencyTraces=traces||[];
 const list=latencyEl('list');list.innerHTML='';
 const withMetric=latencyTraces.map(t=>latencyMs(t.meaningful_response_latency_ns)).filter(v=>v!=null&&v>0);
 const max=Math.max(1,...withMetric);
 latencyEl('count').textContent=latencyTraces.length?latencyTraces.length+' recent traces · bar length is meaningful_response_latency, not TTFT':'No traces yet. Submit a chat turn with latency_profiler enabled.';
 if(!latencyTraces.length)return;
 for(const trace of latencyTraces){
  const row=document.createElement('button');
  row.type='button';
  row.className='latency-row'+(latencyActiveId===trace.trace_id?' selected':'');
  row.setAttribute('aria-pressed',String(latencyActiveId===trace.trace_id));
  const ms=latencyMs(trace.meaningful_response_latency_ns);
  const label=document.createElement('span');
  label.className='latency-row-label';
  label.textContent=(trace.run_id||trace.trace_id)+' · '+(trace.status||'ok')+' · '+(ms==null?'no MRL':latencyFormat(trace.meaningful_response_latency_ns));
  const track=document.createElement('span');track.className='latency-track';
  const bar=document.createElement('span');
  bar.className='latency-bar'+(trace.status==='error'?' error':(trace.status==='unfinished'||ms==null)?' unfinished':'');
  bar.style.width=Math.max(2,Math.round(((ms||0)/max)*100))+'%';
  track.appendChild(bar);
  row.appendChild(label);row.appendChild(track);
  row.addEventListener('click',()=>selectLatencyTrace(trace));
  list.appendChild(row);
 }
}

function renderLatencyInspector(trace){
 latencyActiveId=trace.trace_id;
 const inspector=latencyEl('inspector');inspector.hidden=false;
 latencyEl('hint').hidden=true;
 const mrl=latencyFormat(trace.meaningful_response_latency_ns);
 const ack=latencyFormat(trace.ack_latency_ns);
 const ttft=latencyFormat(trace.ttft_ns);
 latencyEl('meta').textContent='run '+trace.run_id+' · '+trace.status+' · MRL '+mrl+' · ack '+ack+' · TTFT '+ttft+' · '+(trace.planner_mode||'')+' · '+(trace.model||'')+' · Jarvis '+(trace.jarvis_version||'')+' · '+(trace.git_revision||'');
 const water=latencyEl('waterfall');water.innerHTML='';
 const spans=trace.spans||[];
 if(!spans.length){
  const empty=document.createElement('p');empty.className='muted';empty.textContent='No spans recorded for this trace.';water.appendChild(empty);return;
 }
 const byId={};
 for(const span of spans)byId[span.span_id]=span;
 const started=Number(trace.started_ns)||0;
 const range=latencyRange(trace);
 const sorted=spans.slice().sort((a,b)=>(a.start_ns||0)-(b.start_ns||0));
 for(const span of sorted){
  const row=document.createElement('div');
  row.className='latency-span'+(span.status==='error'?' error':'')+(span.status==='unfinished'?' unfinished':'');
  const name=document.createElement('span');
  name.className='latency-span-name';
  name.style.paddingLeft=(8+latencyDepth(span,byId)*14)+'px';
  const tool=span.attrs&&span.attrs.tool?(' '+span.attrs.tool):'';
  name.textContent=span.name+tool+' · '+latencyFormat(span.duration_ns)+' · '+span.status;
  const track=document.createElement('span');track.className='latency-track';
  const bar=document.createElement('span');bar.className='latency-span-bar';
  const left=Math.max(0,((Number(span.start_ns)||started)-started)/range*100);
  const width=Math.max(0.8,((span.duration_ns!=null?Number(span.duration_ns):0)/range)*100);
  bar.style.marginLeft=left+'%';
  bar.style.width=Math.min(100-left,width)+'%';
  track.appendChild(bar);
  row.appendChild(name);row.appendChild(track);water.appendChild(row);
 }
}

async function refreshLatency(){
 const load=++latencyLoad;
 try{
  const q=latencyQueryString();
  const [hist,sum]=await Promise.all([
   get('/v1/latency/traces'+q),
   get('/v1/latency/summary'+q)
  ]);
  if(load!==latencyLoad)return;
  latencyFillSelect('planner',sum.options&&sum.options.planner_mode,'all');
  latencyFillSelect('status',sum.options&&sum.options.status,'all');
  latencyFillSelect('version',sum.options&&sum.options.jarvis_version,'all');
  latencyFillSelect('revision',sum.options&&sum.options.git_revision,'all');
  latencyFillCompare('left',sum.options||{});
  latencyFillCompare('right',sum.options||{});
  renderLatencyStats(sum);
  renderLatencyTail(sum);
  renderLatencyHistory(hist.traces||[]);
  if(latencyActiveId){
   const still=latencyTraces.find(t=>t.trace_id===latencyActiveId);
   if(still)await selectLatencyTrace(still,true);
  }
 }catch(error){if(typeof trainMessage==='function')trainMessage(error.message,true);}
}

async function selectLatencyTrace(summary,keepList){
 try{
  const trace=await get('/v1/latency/traces/'+summary.trace_id);
  renderLatencyInspector(trace);
  if(!keepList){
   renderLatencyHistory(latencyTraces);
   renderLatencyTail(latencySummary||{});
  }
 }catch(error){if(typeof trainMessage==='function')trainMessage(error.message,true);}
}

async function copyLatencyNote(){
 const note=latencyEl('note');
 const text=note&&note.value?note.value:'';
 if(!text){if(typeof trainMessage==='function')trainMessage('No PERF note yet.',true);return;}
 try{
  const clip=typeof navigator!=='undefined'?navigator.clipboard:null;
  if(clip&&clip.writeText)await clip.writeText(text);
  if(typeof trainMessage==='function')trainMessage('PERF note copied. Paste it into an IMP Events line — do not write docs/ledger/ from Training.');
 }catch(error){if(typeof trainMessage==='function')trainMessage(error.message,true);}
}

if(latencyEl('refresh'))latencyEl('refresh').addEventListener('click',refreshLatency);
for(const id of ['window','planner','status','version','revision','left','right']){
 const el=latencyEl(id);
 if(el)el.addEventListener('change',refreshLatency);
}
if(latencyEl('copy-note'))latencyEl('copy-note').addEventListener('click',copyLatencyNote);
