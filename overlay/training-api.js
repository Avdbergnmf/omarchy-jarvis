const trainingSession=fetch('/v1/session').then(r=>r.json());
async function trainingRequest(path,body){
 const {token}=await trainingSession;
 const options={headers:{'X-Jarvis-Token':token}};
 if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
 const response=await fetch(path,options),result=await response.json();
 if(!response.ok)throw new Error(result.error||'Request failed');
 return result;
}
const get=path=>trainingRequest(path);
const post=(path,body)=>trainingRequest(path,body);
function trainingReportReady(result){
 localStorage.setItem('jarvis:lastRun',result.run_id);
 document.querySelector('#validation-open-chat').hidden=false;
 trainMessage('Draft prepared. Open the draft in chat to review it; Run is still required to file.');
}
window.addEventListener('DOMContentLoaded',()=>refreshTraining());
