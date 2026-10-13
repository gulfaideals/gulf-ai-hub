"""Static site generator: data/deals.json -> dist/"""
import json,os,html,shutil,datetime
B=os.environ.get("SITE_URL","https://gulfaideals.com").rstrip("/")
NAME="DealDune"; TAG="The Gulf AI Hub: deals, agent use cases & Arabic AI tools"
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=[d for d in json.load(open(f"{root}/data/deals.json")) if d.get("status","published")!="unreviewed"]; D.sort(key=lambda x:x["date"],reverse=True)
out=f"{root}/dist"; shutil.rmtree(out,ignore_errors=True); os.makedirs(f"{out}/deals")
UC=json.load(open(f"{root}/data/use_cases.json")); TL=json.load(open(f"{root}/data/tools.json"))
e=html.escape
def val(d):
    if d["value"] is None: return "Undisclosed"
    v=d["value"]; s=f"{v/1e9:g}bn" if v>=1e9 else f"{v/1e6:g}m"
    return f'{d["currency"]} {s}'
CSS="""*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,sans-serif;background:#0b1020;color:#e6e9f2}a{color:#7cc4ff}
header,footer{padding:16px 24px;display:flex;gap:20px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #1d2540}footer{border:0;border-top:1px solid #1d2540;color:#8a93ad;font-size:14px}
.logo{font-weight:800;font-size:20px;color:#fff;text-decoration:none}.logo span{color:#f5b942}main{max-width:1000px;margin:auto;padding:24px}
.hero h1{font-size:34px;margin:.2em 0}.muted{color:#8a93ad}.f{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}select,input,button{padding:9px 12px;border-radius:8px;border:1px solid #2a3458;background:#121a33;color:#e6e9f2}
button{background:#f5b942;color:#111;border:0;font-weight:700;cursor:pointer}.card{background:#121a33;border:1px solid #1d2540;border-radius:12px;padding:16px;margin:12px 0}
.card h3{margin:.2em 0;font-size:18px}.tag{display:inline-block;font-size:12px;padding:2px 8px;border-radius:99px;background:#1d2a50;margin-right:6px}.v{color:#f5b942;font-weight:700}
.sp{border:1px dashed #f5b942;border-radius:12px;padding:14px;margin:16px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}"""
def page(path,title,desc,body,canon):
    nav=f'<header><a class="logo" href="/">Deal<span>Dune</span></a><a href="/">Deals</a><a href="/use-cases/">Agent Use Cases</a><a href="/tools/">Arabic AI Tools</a><a href="/sponsor/">Sponsor</a><a href="/about/">About</a><a href="/rss.xml">RSS</a></header>'
    h=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{B}{canon}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{B}{canon}"><meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="/rss.xml"><style>{CSS}</style></head><body>{nav}<main>{body}</main>
<footer>© {datetime.date.today().year} {NAME} — independent Gulf AI hub: deals, agent use cases and Arabic AI tools. Not investment advice. Every entry links to its source.</footer></body></html>'''
    p=f"{out}{path}"; os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w").write(h)
NL='''<div class="card"><h3>Weekly Gulf AI deal brief</h3><p class="muted">Every deal, tender and sovereign-AI move in KSA, UAE & GCC. One email, Mondays.</p>
<form class="f nl" method="post" action="/api/subscribe"><input name="email" type="email" required placeholder="you@company.com"><input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true"><button>Subscribe</button><span class="msg muted"></span></form>
<script>document.querySelectorAll('form.nl').forEach(f=>f.onsubmit=async ev=>{ev.preventDefault();const m=f.querySelector('.msg');m.textContent='…';try{const r=await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value,website:f.website.value,source:location.pathname})});const j=await r.json();if(j.ok){f.innerHTML='<b>'+j.message+'</b>'}else m.textContent=j.error}catch(e){m.textContent='Network error, please retry.'}});</script></div>'''
SP='<div class="sp"><b>Sponsor slot available</b> — reach Gulf AI decision makers. <a href="/sponsor/">Book this week →</a></div>'
cards="".join(f'''<div class="card" data-c="{e(d["country"])}" data-k="{e(d["category"])}"><span class="tag">{e(d["date"])}</span><span class="tag">{e(d["country"])}</span><span class="tag">{e(d["category"])}</span><span class="v">{val(d)}</span>
<h3><a href="/deals/{d["slug"]}/">{e(", ".join(d["parties"][:3]) or d["title"])}</a></h3><p>{e(d["summary"])}</p></div>''' for d in D)
opt=lambda k:"".join(f"<option>{e(x)}</option>" for x in sorted({d[k] for d in D}))
HUC="".join(f'<p><a href="/use-cases/{u["slug"]}/">{e(u["title"])}</a><br><span class="muted">{e(u["sector"])} · {e(u["country"])}</span></p>' for u in UC[:4])
HTL="".join(f'<p><a href="/tools/{t["slug"]}/">{e(t["name"])}</a> <span class="muted">— {e(t["category"])}</span></p>' for t in TL[:5])
home=f'''<section class="hero"><h1>The Gulf AI Hub</h1><p class="muted">{len(D)} sourced deals · {len(UC)} agent use cases · {len(TL)} Arabic AI tools — Saudi Arabia, UAE &amp; GCC. Updated daily.</p></section>
<div class="grid"><div class="card"><h3><a href="/use-cases/">Agent Use Cases →</a></h3>{HUC}</div><div class="card"><h3><a href="/tools/">Arabic AI Tools →</a></h3>{HTL}</div></div><h2>Latest deals</h2>
<div class="f"><select id="c"><option value="">All countries</option>{opt("country")}</select><select id="k"><option value="">All categories</option>{opt("category")}</select><input id="q" placeholder="Search parties…"></div>
{SP}<div id="list">{cards}</div>{NL}
<script>const f=()=>{{const c=document.getElementById('c').value,k=document.getElementById('k').value,q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#list .card').forEach(x=>{{x.style.display=(!c||x.dataset.c==c)&&(!k||x.dataset.k==k)&&(!q||x.textContent.toLowerCase().includes(q))?'':'none'}})}};['c','k','q'].forEach(i=>document.getElementById(i).addEventListener('input',f));</script>'''
page("/index.html",f"{NAME} — {TAG}","The Gulf AI hub: sourced AI deals, AI agent use cases and Arabic AI tools for Saudi Arabia, the UAE and the GCC.",home,"/")
for d in D:
    ld=json.dumps({"@context":"https://schema.org","@type":"NewsArticle","headline":d["title"],"datePublished":d["date"],"description":d["summary"],"isBasedOn":d["source_url"]})
    b=f'''<p><a href="/">← All deals</a></p><h1>{e(", ".join(d["parties"]) or d["title"])}</h1><p><span class="tag">{e(d["date"])}</span><span class="tag">{e(d["country"])}</span><span class="tag">{e(d["category"])}</span></p>
<div class="grid"><div class="card"><b>Value</b><br><span class="v">{val(d)}</span></div><div class="card"><b>Parties</b><br>{e(", ".join(d["parties"]) or "See source")}</div></div>
<p>{e(d["summary"])}</p><p>Source: <a rel="nofollow noopener" href="{e(d["source_url"])}">{e(d["source_url"])}</a></p>{SP}{NL}<script type="application/ld+json">{ld}</script>'''
    page(f"/deals/{d['slug']}/index.html",f"{d['title'][:80]} | {NAME}",d["summary"][:155],b,f"/deals/{d['slug']}/")
page("/sponsor/index.html",f"Sponsor — {NAME}","Sponsor the Gulf AI deals tracker and weekly brief.",'''<h1>Sponsor DealDune</h1><p class="muted">Reach founders, investors, operators and government-tech buyers following AI in the Gulf. Pricing below is introductory placeholder pricing.</p>
<div class="grid"><div class="card"><h3>Weekly site slot</h3><p class="v">$300 / week</p><p>Banner on homepage + all deal pages for 7 days.</p></div><div class="card"><h3>Newsletter sponsor</h3><p class="v">$400 / issue</p><p>Top-of-email placement in the Monday brief.</p></div><div class="card" id="featured"><h3>Featured tool listing</h3><p class="v">$150 / month</p><p>Top placement in the Arabic AI Tools directory + "Featured" badge. Tool submissions (free, editorially reviewed) open soon.</p></div><div class="card"><h3>Bundle</h3><p class="v">$600 / week</p><p>Site slot + newsletter + featured listing.</p></div></div>
<p><button disabled>Booking opens soon</button></p><p class="muted">Sponsored content is always labelled. Sponsors never influence deal coverage.</p>''',"/sponsor/")
page("/about/index.html",f"About — {NAME}","About DealDune.",f'''<h1>About {NAME}</h1><p>{NAME} is an independent Gulf AI hub covering publicly announced AI, sovereign-AI, data-center, tender, partnership and funding activity in Saudi Arabia, the UAE and the wider GCC, plus real AI agent use cases and a directory of Arabic AI tools.</p>
<p>Every entry is based on a public source, linked on its page. Values are shown only when disclosed; we never estimate undisclosed figures. Dates marked by month or year reflect source precision.</p><p>Spotted a deal or correction? A submission form is coming soon.</p>{NL}''',"/about/")
def listing(path,title,desc,items,keyf,cardf,intro):
    opts="".join(f"<option>{e(x)}</option>" for x in sorted({keyf(i) for i in items}))
    b=f'''<h1>{title}</h1><p class="muted">{intro}</p><div class="f"><select id="k"><option value="">All</option>{opts}</select><input id="q" placeholder="Search…"></div>{SP}<div id="list">{"".join(cardf(i) for i in items)}</div>{NL}
<script>const f=()=>{{const k=document.getElementById('k').value,q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#list .card').forEach(x=>{{x.style.display=(!k||x.dataset.k==k)&&(!q||x.textContent.toLowerCase().includes(q))?'':'none'}})}};['k','q'].forEach(i=>document.getElementById(i).addEventListener('input',f));</script>'''
    page(path+"index.html",f"{title} | {NAME}",desc,b,path)
listing("/use-cases/","AI Agent Use Cases in the Gulf","Real, sourced examples of AI agents and automation used by GCC governments and businesses, with how-to steps.",UC,lambda u:u["sector"],
 lambda u:f'<div class="card" data-k="{e(u["sector"])}"><span class="tag">{e(u["sector"])}</span><span class="tag">{e(u["country"])}</span><h3><a href="/use-cases/{u["slug"]}/">{e(u["title"])}</a></h3><p>{e(u["summary"])}</p></div>',
 f"{len(UC)} real, sourced examples of AI agents and automation in GCC government and business — each with a how-to.")
for u in UC:
    b=f'''<p><a href="/use-cases/">← All use cases</a></p><h1>{e(u["title"])}</h1><p><span class="tag">{e(u["sector"])}</span><span class="tag">{e(u["country"])}</span><span class="tag">{e(u["tool"])}</span></p><p>{e(u["summary"])}</p>
<div class="card"><h3>How to do it</h3><p>{e(u["how_to"])}</p><p class="muted">Generic implementation steps by the editors, not a description of the organisation's internal process.</p></div><p>Source: <a rel="nofollow noopener" href="{e(u["source_url"])}">{e(u["source_url"])}</a></p>{SP}{NL}'''
    page(f"/use-cases/{u['slug']}/index.html",f"{u['title'][:70]} | {NAME}",u["summary"][:155],b,f"/use-cases/{u['slug']}/")
CTA='<div class="sp"><b>Built an Arabic AI tool?</b> Submit it or get a featured listing ($150/month, placeholder). <a href="/sponsor/#featured">Submit / feature your tool →</a></div>'
listing("/tools/","Arabic AI Tools Directory","Directory of AI tools with notable Arabic support: LLMs, speech, dubbing, chatbots and OCR.",TL,lambda t:t["category"],
 lambda t:f'<div class="card" data-k="{e(t["category"])}"><span class="tag">{e(t["category"])}</span><span class="tag">{e(t["pricing"])}</span><h3><a href="/tools/{t["slug"]}/">{e(t["name"])}</a></h3><p>{e(t["description"])}</p><p class="muted">Arabic: {e(t["arabic_support"])}</p></div>',
 f"{len(TL)} AI tools with notable Arabic support. Dialect support is as stated by each source.</p>{CTA}<p>")
for t in TL:
    b=f'''<p><a href="/tools/">← All tools</a></p><h1>{e(t["name"])}</h1><p><span class="tag">{e(t["category"])}</span></p><p>{e(t["description"])}</p>
<div class="grid"><div class="card"><b>Arabic support</b><br>{e(t["arabic_support"])}</div><div class="card"><b>Pricing</b><br>{e(t["pricing"])}</div><div class="card"><b>Website</b><br><a rel="nofollow noopener" href="{e(t["url"])}">{e(t["url"])}</a></div></div>
<p>Source: <a rel="nofollow noopener" href="{e(t["source_url"])}">{e(t["source_url"])}</a></p>{CTA}{NL}'''
    page(f"/tools/{t['slug']}/index.html",f"{t['name']} — Arabic AI tool | {NAME}",t["description"][:155],b,f"/tools/{t['slug']}/")
urls=["/","/use-cases/","/tools/","/sponsor/","/about/"]+[f"/deals/{d['slug']}/" for d in D]+[f"/use-cases/{u['slug']}/" for u in UC]+[f"/tools/{t['slug']}/" for t in TL]
open(f"{out}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{B}{u}</loc></url>" for u in urls)+"</urlset>")
open(f"{out}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {B}/sitemap.xml\n")
def rfc(s):
    y,m,dd=(s.split("-")+["01","01"])[:3]; return datetime.datetime(int(y),int(m),int(dd)).strftime("%a, %d %b %Y 00:00:00 +0000")
items="".join(f"<item><title>{e(d['title'])}</title><link>{B}/deals/{d['slug']}/</link><guid>{B}/deals/{d['slug']}/</guid><pubDate>{rfc(d['date'])}</pubDate><description>{e(d['summary'])}</description></item>" for d in D[:50])+"".join(f"<item><title>Use case: {e(u['title'])}</title><link>{B}/use-cases/{u['slug']}/</link><guid>{B}/use-cases/{u['slug']}/</guid><description>{e(u['summary'])}</description></item>" for u in UC)+"".join(f"<item><title>Tool: {e(t['name'])}</title><link>{B}/tools/{t['slug']}/</link><guid>{B}/tools/{t['slug']}/</guid><description>{e(t['description'])}</description></item>" for t in TL)
open(f"{out}/rss.xml","w").write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAME} — {TAG}</title><link>{B}/</link><description>Gulf AI hub: deals, agent use cases, Arabic AI tools</description>{items}</channel></rss>')
shutil.copy(f"{root}/data/deals.json",f"{out}/deals.json")
print("built",len(D),"deals,",len(UC),"use cases,",len(TL),"tools ->",out)

import subprocess,sys
subprocess.run([sys.executable,f"{root}/scripts/agents.py"],check=True)
