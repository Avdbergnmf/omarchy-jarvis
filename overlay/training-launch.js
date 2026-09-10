async function enterTraining(){
 hideCommands();
 const button=document.querySelector('#train-btn');button.disabled=true;
 try{await post('/v1/training/open',{});status.textContent='Training opened in its own window.';}
 catch(error){status.textContent=error.message;status.className='error';}
 finally{button.disabled=false;}
}
document.querySelector('#train-btn').addEventListener('click',enterTraining);
