// Private: GET (JSON or ?format=csv) / DELETE ?email=  — requires header X-Export-Secret
const J=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:{"Content-Type":"application/json","Cache-Control":"no-store"}});
function authed(req,env){const k=req.headers.get("x-export-secret")||"";return env.EXPORT_SECRET&&k.length===env.EXPORT_SECRET.length&&k===env.EXPORT_SECRET;}
export async function onRequest({request,env}){
  if(!authed(request,env)) return J({error:"not found"},404);
  const u=new URL(request.url);
  if(request.method==="DELETE"){const e=(u.searchParams.get("email")||"").toLowerCase();await env.SUBS.delete("sub:"+e);return J({deleted:e});}
  let keys=[],cur; do{const r=await env.SUBS.list({prefix:"sub:",cursor:cur});keys.push(...r.keys);cur=r.list_complete?null:r.cursor;}while(cur);
  if(u.searchParams.get("count")) return J({count:keys.length});
  const rows=keys.map(k=>({email:k.name.slice(4),created_at:k.metadata?.created_at||null,source:k.metadata?.source||""}));
  if(u.searchParams.get("format")==="csv") return new Response("email,created_at,source\n"+rows.map(r=>[r.email,r.created_at,'"'+(r.source||"").replace(/"/g,'""')+'"'].join(",")).join("\n"),{headers:{"Content-Type":"text/csv","Cache-Control":"no-store"}});
  return J({count:rows.length,subscribers:rows});
}
