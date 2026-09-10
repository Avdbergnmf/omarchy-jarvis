const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function element(){return {value:'',hidden:true,children:[],handlers:{},textContent:'',disabled:false,
 set innerHTML(value){this.children=[];},addEventListener(event,fn){this.handlers[event]=fn;},appendChild(child){this.children.push(child);},setAttribute(){},focus(){this.focused=true;},select(){}};}
const els={},requests=[],previews=[];const $=id=>els[id]||(els[id]=element());
const problem={id:'bad:one',title:'Focus failed',notes:'Window should receive focus',area:'overlay',priority:'P1',revision:'p1'};
let detail={id:'A-020',path:'docs/assignments/active/A-020-training.md',status:'queued',area:'area:overlay',parallel:'NO',editable:true,revision:'a1',body:'Original context',fields:{title:'Fix focus',area:'overlay',priority:'P1',goal:'Stable focus',notes:'',checklist:'- [ ] Check focus',allowed_paths:'overlay/',forbidden_paths:'brain/',out_of_scope:'Other tasks'}};
let resolveGeneration=null;
const data={assignments:[detail],problems:[problem]};
let currentPanel=null;
const ctx={document:{querySelector:$,createElement:element},trainingData:data,trainEl:id=>$('#train-'+id),trainingPanel:name=>{currentPanel=name;},trainMessage(text){$('#message').textContent=text;},trainingLine(){},trainingOption(){},
 post:async(path,body)=>{requests.push({path,body});if(path.endsWith('/assignment'))return detail;if(path.endsWith('/generate'))return new Promise(resolve=>{resolveGeneration=resolve;});throw Error('unexpected request');},
 previewTraining:async payload=>previews.push(payload),navigator:{clipboard:{writeText:async()=>{}}}};
vm.runInNewContext(fs.readFileSync('overlay/assignments.js','utf8'),ctx);
(async()=>{
 ctx.renderAssignments(data);ctx.newAssignment(problem);
 assert.equal(currentPanel,'work');assert.equal($('#assign-title').value,'Focus failed');assert.equal($('#assign-priority').value,'P1');
 $('#assign-title').value='Edited draft';$('#assignment-form').handlers.input();
 ctx.renderAssignments(data);assert.equal($('#assign-title').value,'Edited draft','refresh must preserve edits');
 $('#assignment-form').handlers.submit({preventDefault(){}});
 assert.equal(previews[0].operation,'assignment_save');assert.equal(previews[0].problem_id,'bad:one');assert.equal(previews[0].fields.title,'Edited draft');
 assert.equal(requests.length,0,'save only previews, no writes or agent launch');
 await ctx.assignmentSaved('A-020');assert.equal($('#assign-heading').textContent,'A-020');assert.equal($('#assign-body').textContent,'Original context');
 $('#assign-handoff').handlers.click();assert.equal(currentPanel,'agents');assert.equal($('#train-assignment').value,'A-020');
 $('#assign-title').value='More edits';$('#assignment-form').handlers.input();
 $('#assign-handoff').handlers.click();assert.match($('#message').textContent,/Save the assignment/);
 await ctx.selectAssignment('A-020',true);detail={...detail,status:'in_progress',editable:false};
 await ctx.selectAssignment('A-020');assert.equal($('#assign-fields').disabled,true,'owned work must be read-only');
 ctx.newAssignment(null,true);$('#assign-title').value='Draft idea';$('#assign-generator').value='local';
 const pending=ctx.generateAssignment();await Promise.resolve();
 $('#assign-title').value='Typed while waiting';$('#assignment-form').handlers.input();
 resolveGeneration({draft:{title:'Late model answer',goal:'Goal',checklist:'- [ ] Verify',out_of_scope:'Other work'},message:'Ready'});await pending;
 assert.equal($('#assign-title').value,'Typed while waiting','late generation must not wipe newer edits');
 $('#assign-generator').value='agent';const agent=ctx.generateAssignment();await Promise.resolve();resolveGeneration({prompt:'Copy me',message:'No agent contacted'});await agent;
 assert.equal($('#assign-agent-import').hidden,false);assert.equal($('#assign-agent-prompt').value,'Copy me');
 $('#assign-import-json').value=JSON.stringify({title:'Imported',goal:'Expected result',checklist:'- [ ] Verify result',out_of_scope:'Other work'});
 $('#assign-import').handlers.click();assert.equal($('#assign-title').value,'Imported');
 $('#assign-import-json').value='{"title":123}';$('#assign-import').handlers.click();assert.equal($('#assign-title').value,'Imported','invalid import cannot overwrite form');
 console.log('PASS: assignment list/detail, linked drafts, confirmed save, owned read-only, handoff selection, manual import and late-generation guard');
})().catch(error=>{console.error(error);process.exitCode=1;});
