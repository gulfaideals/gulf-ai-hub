// Read-only remote MCP server (Streamable HTTP, JSON responses) over the site's static JSON.
const CORS = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET, POST, OPTIONS","Access-Control-Allow-Headers":"Content-Type, Accept, Mcp-Session-Id, MCP-Protocol-Version, Authorization","Access-Control-Expose-Headers":"Mcp-Session-Id"};
const SRC = {deal:"/api/deals.json", use_case:"/api/use-cases.json", tool:"/api/tools.json"};
const str = {type:"string"}, lim = {type:"integer",minimum:1,maximum:50,default:10,description:"Max results"};
const TOOLS = [
 {name:"search_deals",description:"Search sourced AI, sovereign-AI and data-center deals in Saudi Arabia, UAE and GCC (2025-2026). Returns date, country, parties, category, value (null if undisclosed), summary, source_url.",
  inputSchema:{type:"object",properties:{query:{...str,description:"Free text, e.g. 'HUMAIN Nvidia'"},country:{...str,description:"e.g. Saudi Arabia, UAE, Qatar, Kuwait, Bahrain"},category:{...str,description:"data center | partnership | funding | gov program | tender | M&A"},since:{...str,description:"ISO date lower bound, e.g. 2026-01-01"},limit:lim}}},
 {name:"search_use_cases",description:"Search real, sourced AI agent/automation use cases in GCC governments and businesses, with how-to steps.",
  inputSchema:{type:"object",properties:{query:str,sector:{...str,description:"e.g. Banking, Government services, ZATCA e-invoicing, Healthcare"},country:str,limit:lim}}},
 {name:"search_tools",description:"Search the directory of AI tools with notable Arabic support (LLMs, STT/TTS, dubbing, chatbots, OCR).",
  inputSchema:{type:"object",properties:{query:str,category:{...str,description:"e.g. Arabic LLM, OCR, Text-to-speech, Speech-to-text, Dubbing"},limit:lim}}},
 {name:"get_item",description:"Get one item by slug.",inputSchema:{type:"object",required:["type","slug"],properties:{type:{type:"string",enum:["deal","use_case","tool"]},slug:str}}},
];
const ok = (id, result) => ({jsonrpc:"2.0", id, result});
const err = (id, code, message) => ({jsonrpc:"2.0", id, error:{code, message}});
const has = (v, q) => !q || String(v ?? "").toLowerCase().includes(String(q).toLowerCase());
async function load(env, req, t){ const r = await env.ASSETS.fetch(new URL(SRC[t], req.url)); const j = await r.json(); return Array.isArray(j) ? j : j.items; }
const urlFor = (t,s) => `https://gulfaideals.com/${t==="deal"?"deals":t==="tool"?"tools":"use-cases"}/${s}/`;
async function callTool(env, req, name, a = {}){
  const n = Math.min(Math.max(parseInt(a.limit||10),1),50); let rows, t;
  if (name==="search_deals"){ t="deal"; rows=(await load(env,req,t)).filter(d=>has(JSON.stringify([d.title,d.summary,d.parties]),a.query)&&has(d.country,a.country)&&has(d.category,a.category)&&(!a.since||d.date>=a.since)); }
  else if (name==="search_use_cases"){ t="use_case"; rows=(await load(env,req,t)).filter(u=>has(JSON.stringify(u),a.query)&&has(u.sector,a.sector)&&has(u.country,a.country)); }
  else if (name==="search_tools"){ t="tool"; rows=(await load(env,req,t)).filter(x=>has(JSON.stringify(x),a.query)&&has(x.category,a.category)); }
  else if (name==="get_item"){ if(!SRC[a.type]) throw new Error("type must be deal, use_case or tool"); const it=(await load(env,req,a.type)).find(x=>x.slug===a.slug); if(!it) throw new Error("not found: "+a.slug); return {...it, page_url:urlFor(a.type,it.slug)}; }
  else throw new Error("unknown tool: "+name);
  return {total:rows.length, results:rows.slice(0,n).map(r=>({...r, page_url:urlFor(t,r.slug)}))};
}
async function handle(env, req, m){
  const id = m.id ?? null;
  switch(m.method){
    case "initialize": return ok(id,{protocolVersion:(m.params&&m.params.protocolVersion)||"2025-06-18",capabilities:{tools:{listChanged:false}},serverInfo:{name:"gulfaideals",title:"DealDune Gulf AI Hub",version:"1.0.0"},instructions:"Read-only data on Gulf (GCC) AI deals, AI agent use cases and Arabic AI tools. Always cite source_url."});
    case "ping": return ok(id,{});
    case "tools/list": return ok(id,{tools:TOOLS});
    case "resources/list": return ok(id,{resources:[]});
    case "prompts/list": return ok(id,{prompts:[]});
    case "tools/call": try { const r = await callTool(env, req, m.params?.name, m.params?.arguments); return ok(id,{content:[{type:"text",text:JSON.stringify(r)}],structuredContent:r,isError:false}); } catch(e){ return ok(id,{content:[{type:"text",text:String(e.message||e)}],isError:true}); }
    default: return err(id,-32601,"Method not found: "+m.method);
  }
}
export async function onRequest({request, env}){
  if (request.method==="OPTIONS") return new Response(null,{status:204,headers:CORS});
  if (request.method==="GET") return new Response(JSON.stringify({name:"gulfaideals MCP",transport:"streamable-http",endpoint:"https://gulfaideals.com/mcp",note:"POST JSON-RPC 2.0 here. SSE stream not offered (stateless)."}),{status:405,headers:{...CORS,"Content-Type":"application/json","Allow":"POST, OPTIONS"}});
  if (request.method==="DELETE") return new Response(null,{status:204,headers:CORS});
  let body; try { body = await request.json(); } catch { return new Response(JSON.stringify(err(null,-32700,"Parse error")),{status:400,headers:{...CORS,"Content-Type":"application/json"}}); }
  const msgs = Array.isArray(body)?body:[body];
  const out = (await Promise.all(msgs.map(m=>("id" in m)?handle(env,request,m):null))).filter(Boolean);
  if (!out.length) return new Response(null,{status:202,headers:CORS});
  return new Response(JSON.stringify(Array.isArray(body)?out:out[0]),{headers:{...CORS,"Content-Type":"application/json"}});
}
