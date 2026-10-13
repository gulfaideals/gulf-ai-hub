// Minimal A2A (JSON-RPC) endpoint: message/send -> keyword search over deals, use cases, tools (Arabic or English). Read-only, stateless.
const J=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:{"Content-Type":"application/json; charset=utf-8","Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"Content-Type"}});
const SRC={deal:"/api/deals.json",use_case:"/api/use-cases.json",tool:"/api/tools.json"};
async function load(env,req,t){const r=await env.ASSETS.fetch(new URL(SRC[t],req.url));const j=await r.json();return j.items||j;}
const norm=s=>String(s||"").toLowerCase();
export async function onRequestOptions(){return J({},204);}
export async function onRequestGet(){return J({info:"A2A JSON-RPC endpoint. POST {jsonrpc:'2.0',method:'message/send',params:{message:{role:'user',parts:[{kind:'text',text:'HUMAIN deals'}]}}}. Agent card: /.well-known/agent.json"});}
export async function onRequestPost({request,env}){
  let b; try{b=await request.json();}catch{return J({jsonrpc:"2.0",id:null,error:{code:-32700,message:"Parse error"}});}
  const id=b.id??null;
  if(b.method!=="message/send") return J({jsonrpc:"2.0",id,error:{code:-32601,message:"Method not found (supported: message/send)"}});
  const msg=b.params?.message||{}; const text=(msg.parts||[]).filter(p=>p.kind==="text"||p.type==="text").map(p=>p.text).join(" ").trim();
  if(!text) return J({jsonrpc:"2.0",id,error:{code:-32602,message:"Send a text part with your question"}});
  if(/index|مؤشر/i.test(text)){const r=await env.ASSETS.fetch(new URL("/api/gulf-ai-index.json",request.url));const idx=await r.json();
    return J({jsonrpc:"2.0",id,result:{kind:"message",role:"agent",messageId:crypto.randomUUID(),contextId:msg.contextId||crypto.randomUUID(),parts:[{kind:"text",text:`Gulf AI Index v1 (updated ${idx.updated}): `+idx.by_country.map(c=>`${c.country} $${(c.value/1e9).toFixed(1)}bn across ${c.deals} deals`).join("; ")+". Methodology: https://gulfaideals.com/en/gulf-ai-index/"},{kind:"data",data:idx}]}});}
  const terms=norm(text).replace(/\b(deals?|show|me|find|list|about|the|in|for|صفقات|صفقة)\b/g," ").split(/\s+/).filter(w=>w.length>1);
  const out=[];
  for(const t of Object.keys(SRC)){for(const x of await load(env,request,t)){const h=norm(JSON.stringify([x.title,x.title_ar,x.name,x.name_ar,x.summary,x.summary_ar,x.description,x.parties,x.country,x.sector,x.category]));const s=terms.filter(w=>h.includes(w)).length+(h.includes(norm(text))?5:0);if(s)out.push({s,t,x});}}
  out.sort((a,b)=>b.s-a.s||String(b.x.date||"").localeCompare(String(a.x.date||"")));
  const top=out.slice(0,8).map(({t,x})=>({type:t,title:x.title||x.name,title_ar:x.title_ar||x.name_ar,date:x.date,value:x.value,currency:x.currency,source_url:x.source_url,page_url:`https://gulfaideals.com/${t==="deal"?"deals":t==="tool"?"tools":"use-cases"}/${x.slug}/`}));
  const txt=top.length?top.map(r=>`- ${r.title}${r.date?` (${r.date})`:""} — ${r.page_url}`).join("\n"):"No matching records. Try a company (HUMAIN, G42, MGX) or country.";
  return J({jsonrpc:"2.0",id,result:{kind:"message",role:"agent",messageId:crypto.randomUUID(),contextId:msg.contextId||crypto.randomUUID(),parts:[{kind:"text",text:txt},{kind:"data",data:{results:top}}]}});
}
