// Tool-free, history-free LLM calls through Pi's supported authenticated runtime.
// Credentials stay inside Pi; only selected Mem0 prompts enter this process via stdin.
import {ModelRuntime} from '/Users/johansardar/.local/lib/node_modules/@earendil-works/pi-coding-agent/dist/index.js';
let input='';
try {
 for await (const chunk of process.stdin) {input+=chunk;if(input.length>500000)throw new Error('Input too large');}
 const request=JSON.parse(input);
 if(!Array.isArray(request.messages)||!request.messages.length)throw new Error('Messages required');
 const runtime=await ModelRuntime.create({allowModelNetwork:false,signal:AbortSignal.timeout(20000)});
 const model=runtime.getModel('openai-codex','gpt-5.6-luna');
 if(!model || model.thinkingLevelMap?.max!=='max')throw new Error('Exact Luna/max model unavailable');
 if(!runtime.hasConfiguredAuth('openai-codex'))throw new Error('Pi subscription authentication required');
 const system=[];const messages=[];
 for(const m of request.messages){
  if(typeof m.content!=='string')throw new Error('Only text messages supported');
  if(m.role==='system')system.push(m.content);
  else if(m.role==='user')messages.push({role:'user',content:m.content,timestamp:Date.now()});
  else throw new Error('Unsupported message role');
 }
 if(!messages.length)throw new Error('User message required');
 let sentMax=false;let responseStatus;
 const result=await runtime.completeSimple(model,{systemPrompt:system.join('\n\n'),messages},{
  reasoning:'max',maxTokens:8192,transport:'sse',maxRetries:0,timeoutMs:120000,
  signal:AbortSignal.timeout(150000),
  onPayload(payload){
   if(payload.model!=='gpt-5.6-luna'||payload.reasoning?.effort!=='max')throw new Error('Refusing model/reasoning downgrade');
   sentMax=true;
  },
  onResponse(response){responseStatus=response.status;},
 });
 if(!sentMax||result.stopReason!=='stop')throw new Error('LLM request did not complete normally');
 const text=result.content.filter(c=>c.type==='text').map(c=>c.text).join('');
 if(!text.trim())throw new Error('Empty LLM response');
 console.log(JSON.stringify({text,model:model.id,reasoning:'max',responseStatus,stopReason:result.stopReason,usage:result.usage}));
} catch(error){
 // No upstream payloads, credentials, reasoning traces or private text in diagnostics.
 console.error('Luna bridge failed ('+(error?.name||'Error')+'). Check Pi authentication, model access or request format.');
 process.exitCode=1;
}
