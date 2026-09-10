const latencyEl=id=>document.querySelector('#latency-'+id);
let latencyTraces=[],latencyActiveId=null,latencyLoad=0;

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
  const data=await get('/v1/latency/traces');
  if(load!==latencyLoad)return;
  renderLatencyHistory(data.traces||[]);
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
  if(!keepList)renderLatencyHistory(latencyTraces);
 }catch(error){if(typeof trainMessage==='function')trainMessage(error.message,true);}
}

if(latencyEl('refresh'))latencyEl('refresh').addEventListener('click',refreshLatency);
