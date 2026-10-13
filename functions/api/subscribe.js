const J=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:{"Content-Type":"application/json","Cache-Control":"no-store"}});
const RE=/^[^\s@<>()",;:]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,24}$/;
async function sha(s){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");}
export async function onRequestPost({request,env}){
  if(!env.SUBS) return J({ok:false,error:"Signup temporarily unavailable",error_ar:"التسجيل غير متاح مؤقتاً"},503);
  let d={}; const ct=request.headers.get("content-type")||"";
  try{ d = ct.includes("json") ? await request.json() : Object.fromEntries(await request.formData()); }catch{ return J({ok:false,error:"Bad request",error_ar:"طلب غير صالح"},400); }
  if((d.website||"").trim()) return J({ok:true,message:"Thanks — you're subscribed.",message_ar:"شكراً، تم اشتراكك بنجاح."}); // honeypot: silently accept
  const email=String(d.email||"").trim().toLowerCase();
  if(!RE.test(email)||email.length>254) return J({ok:false,error:"Please enter a valid email.",error_ar:"يرجى إدخال بريد إلكتروني صحيح."},400);
  const ip=request.headers.get("cf-connecting-ip")||"";
  const rk="rl:"+(await sha(ip)).slice(0,16); const n=parseInt(await env.SUBS.get(rk)||"0");
  if(n>=10) return J({ok:false,error:"Too many attempts, try later.",error_ar:"محاولات كثيرة، يرجى المحاولة لاحقاً."},429);
  await env.SUBS.put(rk,String(n+1),{expirationTtl:3600});
  const key="sub:"+email; const ex=await env.SUBS.get(key);
  if(ex) return J({ok:true,message:"You're already on the list.",message_ar:"أنت مشترك بالفعل."});
  const src=String(d.source||request.headers.get("referer")||"").slice(0,300);
  const rec={email,created_at:new Date().toISOString(),source:src,country:request.cf?.country||null,ua:(request.headers.get("user-agent")||"").slice(0,200)};
  await env.SUBS.put(key,JSON.stringify(rec),{metadata:{created_at:rec.created_at,source:src.slice(0,200)}});
  return J({ok:true,message:"Thanks — you're subscribed.",message_ar:"شكراً، تم اشتراكك بنجاح."});
}
export const onRequest=()=>J({ok:false,error:"POST only",error_ar:"يُقبل POST فقط"},405);
