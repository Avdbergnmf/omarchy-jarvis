const input=document.querySelector('#prompt');
const status=document.querySelector('#status');
const session=fetch('/v1/session').then(r=>r.json());
async function post(path,body={}){
 const {token}=await session;
 const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Jarvis-Token':token},body:JSON.stringify(body)});
 const result=await response.json(); if(!response.ok)throw new Error(result.error); return result;
}
document.addEventListener('keydown',async event=>{if(event.key==='Escape'){event.preventDefault();await post('/v1/close');}});
document.querySelector('#prompt-form').addEventListener('submit',async event=>{
 event.preventDefault(); if(!input.value.trim()||input.disabled)return;
 input.disabled=true;status.className='';status.textContent='Thinking…';
 try{
  const {run_id}=await post('/v1/run',{prompt:input.value.trim()});
  const {token}=await session;
  while(true){
   await new Promise(resolve=>setTimeout(resolve,700));
   const r=await fetch('/v1/runs/'+run_id,{headers:{'X-Jarvis-Token':token}});const result=await r.json();
   if(!r.ok)throw new Error(result.error);
   status.textContent=result.reply;
   if(result.status!=='running'){if(result.status==='error')status.className='error';break;}
  }
 }catch(error){status.textContent=error.message;status.className='error';}
 finally{input.disabled=false;input.focus();}
});
