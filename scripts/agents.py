"""Post-build: AI-agent discoverability (llms.txt, API, OpenAPI, manifests, JSON-LD, /agents, robots, _headers)."""
import json,os,re,glob,html
B=os.environ.get("SITE_URL","https://gulfaideals.com").rstrip("/")
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out=f"{root}/dist"; e=html.escape
D=[d for d in json.load(open(f"{root}/data/deals.json")) if d.get("status","published")!="unreviewed"]
UC=json.load(open(f"{root}/data/use_cases.json")); TL=json.load(open(f"{root}/data/tools.json"))
INDEXNOW_KEY="7f3c9a1e5b2d4c6a8e0f1a2b3c4d5e6f"
def w(p,s):
    p=f"{out}{p}"; os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w").write(s if isinstance(s,str) else json.dumps(s,indent=1,ensure_ascii=False))
# API
for name,items,t in [("deals",D,"deals"),("use-cases",UC,"use-cases"),("tools",TL,"tools")]:
    w(f"/api/{name}.json",{"count":len(items),"source":B,"license":"Facts with source links; cite source_url","items":items})
    for i in items: w(f"/api/{t}/{i['slug']}.json",{**i,"page_url":f"{B}/{t}/{i['slug']}/"})
w("/api/index.json",{"deals":f"{B}/api/deals.json","use_cases":f"{B}/api/use-cases.json","tools":f"{B}/api/tools.json","item":f"{B}/api/{{deals|use-cases|tools}}/{{slug}}.json","mcp":f"{B}/mcp","openapi":f"{B}/openapi.json"})
item={"type":"object","additionalProperties":True}
def op(summary,schema): return {"get":{"summary":summary,"operationId":summary.lower().replace(" ","_"),"responses":{"200":{"description":"OK","content":{"application/json":{"schema":schema}}}}}}
lst={"type":"object","properties":{"count":{"type":"integer"},"items":{"type":"array","items":item}}}
paths={"/api/deals.json":op("List deals",lst),"/api/use-cases.json":op("List use cases",lst),"/api/tools.json":op("List tools",lst)}
for t,n in [("deals","deal"),("use-cases","use case"),("tools","tool")]:
    paths[f"/api/{t}/{{slug}}.json"]={"get":{"summary":f"Get {n}","operationId":f"get_{n.replace(' ','_')}","parameters":[{"name":"slug","in":"path","required":True,"schema":{"type":"string"}}],"responses":{"200":{"description":"OK","content":{"application/json":{"schema":item}}},"404":{"description":"Not found"}}}}
w("/openapi.json",{"openapi":"3.1.0","info":{"title":"DealDune Gulf AI Hub API","version":"1.0.0","description":"Read-only static JSON: Gulf AI deals, AI agent use cases, Arabic AI tools. Every record has source_url."},"servers":[{"url":B}],"paths":paths})
w("/.well-known/ai-plugin.json",{"schema_version":"v1","name_for_human":"DealDune Gulf AI Hub","name_for_model":"gulfaideals","description_for_human":"Gulf AI deals, agent use cases and Arabic AI tools.","description_for_model":"Read-only data on AI deals, data centers, sovereign AI, government AI programs and funding in Saudi Arabia, UAE and GCC; AI agent use cases in GCC; AI tools with Arabic support. Cite source_url.","auth":{"type":"none"},"api":{"type":"openapi","url":f"{B}/openapi.json"},"logo_url":f"{B}/favicon.svg","contact_email":"","legal_info_url":f"{B}/about/","mcp":{"url":f"{B}/mcp","transport":"streamable-http"}})
TOOLS=["search_deals","search_use_cases","search_tools","get_item"]
w("/.well-known/mcp.json",{"name":"gulfaideals","title":"DealDune Gulf AI Hub","description":"Read-only MCP server: Gulf AI deals, AI agent use cases, Arabic AI tools.","version":"1.0.0","endpoint":f"{B}/mcp","transport":"streamable-http","authentication":"none","tools":TOOLS,"docs":f"{B}/agents/"})
w("/favicon.svg",'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#0b1020"/><text x="16" y="22" font-size="16" text-anchor="middle" fill="#f5b942" font-family="sans-serif" font-weight="bold">DD</text></svg>')
# robots + headers + indexnow
bots=["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","Claude-User","Claude-SearchBot","anthropic-ai","PerplexityBot","Perplexity-User","Google-Extended","Googlebot","Bingbot","Applebot","Applebot-Extended","xAI-Bot","GrokBot","Grok","CCBot","Meta-ExternalAgent","DuckAssistBot","Amazonbot","cohere-ai","*"]
w("/robots.txt","".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)+f"Sitemap: {B}/sitemap.xml\n# LLM guide: {B}/llms.txt\n")
w("/_headers","""/api/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, OPTIONS
  Content-Type: application/json; charset=utf-8
  Cache-Control: public, max-age=3600
/openapi.json
  Access-Control-Allow-Origin: *
/.well-known/*
  Access-Control-Allow-Origin: *
  Content-Type: application/json; charset=utf-8
/llms*.txt
  Access-Control-Allow-Origin: *
  Content-Type: text/plain; charset=utf-8
/*
  X-Content-Type-Options: nosniff
""")
w(f"/{INDEXNOW_KEY}.txt",INDEXNOW_KEY)
# llms.txt
def L(items,t,label,f): return "\n".join(f"- [{label(i)}]({B}/{t}/{i['slug']}/): {f(i)}" for i in items)
head=f"""# DealDune — The Gulf AI Hub

> Independent, sourced hub on AI in Saudi Arabia, the UAE and the GCC: {len(D)} AI / sovereign-AI / data-center deals (2025–2026), {len(UC)} real AI agent use cases with how-to steps, and {len(TL)} AI tools with notable Arabic support. Every record links to its public source; undisclosed values are null, never estimated.

Machine access: static JSON API ({B}/api/index.json, OpenAPI at {B}/openapi.json) and a read-only remote MCP server at {B}/mcp (streamable HTTP; tools: search_deals, search_use_cases, search_tools, get_item). Setup guide: {B}/agents/

## Sections
- [Deals tracker]({B}/): AI deals, data centers, funding, tenders, M&A, government AI programs in GCC
- [Agent use cases]({B}/use-cases/): AI agents in GCC government, banking, oil & gas, logistics, ZATCA e-invoicing, real estate, healthcare
- [Arabic AI tools]({B}/tools/): Arabic LLMs (Jais, ALLaM, Falcon-H1-Arabic, Fanar), speech, dubbing, chatbots, OCR
- [For AI agents]({B}/agents/): MCP and API instructions

## Data
- [Deals JSON]({B}/api/deals.json)
- [Use cases JSON]({B}/api/use-cases.json)
- [Tools JSON]({B}/api/tools.json)
- [OpenAPI]({B}/openapi.json)
- [MCP manifest]({B}/.well-known/mcp.json)
- [Full text for LLMs]({B}/llms-full.txt)

## Optional
- [Sponsor]({B}/sponsor/)
- [About]({B}/about/)
- [RSS]({B}/rss.xml)
- [Sitemap]({B}/sitemap.xml)
"""
w("/llms.txt",head)
val=lambda d:"undisclosed" if d["value"] is None else f'{d["currency"]} {d["value"]:,.0f}'
full=head+"\n## All deals\n"+"\n".join(f"- {d['date']} | {d['country']} | {d['category']} | {', '.join(d['parties'])} | value: {val(d)} — {d['summary']} Source: {d['source_url']} Page: {B}/deals/{d['slug']}/" for d in D)
full+="\n\n## All agent use cases\n"+"\n\n".join(f"### {u['title']}\nSector: {u['sector']} | Country: {u['country']} | Tool: {u['tool']}\n{u['summary']}\nHow to: {u['how_to']}\nSource: {u['source_url']}\nPage: {B}/use-cases/{u['slug']}/" for u in UC)
full+="\n\n## All Arabic AI tools\n"+"\n".join(f"- {t['name']} ({t['category']}): {t['description']} Arabic: {t['arabic_support']}. Pricing: {t['pricing']}. URL: {t['url']} Source: {t['source_url']}" for t in TL)
w("/llms-full.txt",full+"\n")
# /agents page from about template
tpl=open(f"{out}/about/index.html").read()
MCPJ=json.dumps({"mcpServers":{"gulfaideals":{"url":f"{B}/mcp"}}},indent=2)
body=f"""<h1>For AI agents &amp; assistants</h1><p>DealDune is built to be used by AI agents. Everything is read-only, free and needs no key. Please cite each record's <code>source_url</code>.</p>
<div class="card"><h3>Remote MCP server</h3><p>Endpoint: <code>{B}/mcp</code> (Streamable HTTP, no auth). Tools: <code>search_deals</code>, <code>search_use_cases</code>, <code>search_tools</code>, <code>get_item</code>. Manifest: <a href="/.well-known/mcp.json">/.well-known/mcp.json</a></p></div>
<div class="card"><h3>Claude (claude.ai / Desktop)</h3><p>Settings → Connectors → Add custom connector → Name <code>DealDune</code>, URL <code>{B}/mcp</code>. Claude Code: <code>claude mcp add --transport http gulfaideals {B}/mcp</code></p></div>
<div class="card"><h3>ChatGPT</h3><p>Settings → Apps &amp; Connectors → Advanced → enable Developer mode → Create connector → MCP server URL <code>{B}/mcp</code>, Authentication: none. Then enable it in a chat.</p></div>
<div class="card"><h3>Cursor / Windsurf / VS Code / other MCP clients</h3><p>Add to <code>~/.cursor/mcp.json</code> (or your client's MCP config):</p><pre>{e(MCPJ)}</pre><p>For stdio-only clients: <code>npx mcp-remote {B}/mcp</code></p></div>
<div class="card"><h3>Gemini, Grok, Perplexity &amp; others</h3><p>Point the assistant at <a href="/llms.txt">/llms.txt</a> or <a href="/llms-full.txt">/llms-full.txt</a>, or use the JSON API below. All major AI crawlers are allowed in robots.txt.</p></div>
<div class="card"><h3>JSON API</h3><p><a href="/api/deals.json">/api/deals.json</a> · <a href="/api/use-cases.json">/api/use-cases.json</a> · <a href="/api/tools.json">/api/tools.json</a> · per item: <code>/api/{{deals|use-cases|tools}}/{{slug}}.json</code> · <a href="/openapi.json">OpenAPI</a> · CORS enabled.</p></div>
<div class="card"><h3>Test with curl</h3><pre>curl -s {B}/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \\
  -d '{{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{{"name":"search_deals","arguments":{{"query":"HUMAIN","limit":3}}}}}}'</pre></div>"""
pg=re.sub(r"<main>.*</main>",lambda m:f"<main>{body}</main>",tpl,flags=re.S)
pg=re.sub(r"<title>.*?</title>","<title>For AI agents — MCP server &amp; API | DealDune</title>",pg).replace(f'href="{B}/about/"',f'href="{B}/agents/"').replace('content="About DealDune."','content="Connect AI agents to Gulf AI data via MCP, JSON API and llms.txt."')
w("/agents/index.html",pg)
# JSON-LD + nav + favicon on every page
ORG={"@type":"Organization","@id":f"{B}/#org","name":"DealDune","url":B,"logo":f"{B}/favicon.svg"}
def ld_for(rel):
    parts=rel.strip("/").split("/")
    if rel=="/": return [{"@context":"https://schema.org","@type":"WebSite","@id":f"{B}/#site","name":"DealDune — The Gulf AI Hub","url":B+"/","publisher":ORG,"potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":f"{B}/?q={{search_term_string}}"},"query-input":"required name=search_term_string"}},
        {"@context":"https://schema.org","@type":"Dataset","name":"Gulf AI deals 2025-2026","description":"Sourced AI, sovereign-AI and data-center deals in Saudi Arabia, UAE and GCC.","url":B+"/","license":f"{B}/about/","creator":ORG,"spatialCoverage":"Gulf Cooperation Council","temporalCoverage":"2025/2026","distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":f"{B}/api/deals.json"}]}]
    if rel in("/use-cases/","/tools/"):
        n="use-cases" if "use" in rel else "tools"
        return [{"@context":"https://schema.org","@type":"Dataset","name":"Gulf AI agent use cases" if n=="use-cases" else "Arabic AI tools directory","description":"Sourced AI agent use cases in GCC" if n=="use-cases" else "AI tools with notable Arabic support","url":B+rel,"creator":ORG,"license":f"{B}/about/","distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":f"{B}/api/{n}.json"}]}]
    if len(parts)==2 and parts[0]=="use-cases":
        u=next((x for x in UC if x["slug"]==parts[1]),None)
        if u: return [{"@context":"https://schema.org","@type":"HowTo","name":u["title"],"description":u["summary"],"step":[{"@type":"HowToStep","position":i+1,"text":s.strip()} for i,s in enumerate([x for x in re.split(r"\d\)\s*",u["how_to"]) if x.strip()])],"isBasedOn":u["source_url"],"publisher":ORG}]
    if len(parts)==2 and parts[0]=="tools":
        t=next((x for x in TL if x["slug"]==parts[1]),None)
        if t: return [{"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"applicationCategory":t["category"],"description":t["description"],"url":t["url"],"inLanguage":"ar","isBasedOn":t["source_url"],"offers":{"@type":"Offer","description":t["pricing"]}}]
    if len(parts)==2 and parts[0]=="deals": return [{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Deals","item":B+"/"},{"@type":"ListItem","position":2,"name":parts[1],"item":B+rel}]}]
    return [{"@context":"https://schema.org","@type":"WebPage","name":rel.strip("/") or "home","url":B+rel,"publisher":ORG}]
for f in glob.glob(f"{out}/**/index.html",recursive=True):
    rel="/"+os.path.relpath(os.path.dirname(f),out).replace(".","").strip("/")+"/"; rel="/" if rel=="//" else rel
    s=open(f).read()
    s=s.replace('<a href="/sponsor/">Sponsor</a>','<a href="/agents/">For AI agents</a><a href="/sponsor/">Sponsor</a>',1) if "/agents/" not in s.split("</header>")[0] else s
    s=s.replace("<style>",f'<link rel="icon" href="/favicon.svg"><link rel="alternate" type="text/plain" title="llms.txt" href="/llms.txt"><style>',1)
    s=s.replace("</body>","".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in ld_for(rel))+("<script>const _q=new URLSearchParams(location.search).get('q');if(_q&&document.getElementById('q')){const i=document.getElementById('q');i.value=_q;i.dispatchEvent(new Event('input'))}</script>" if rel=="/" else "")+"</body>")
    open(f,"w").write(s)
sm=open(f"{out}/sitemap.xml").read()
if "/agents/" not in sm: open(f"{out}/sitemap.xml","w").write(sm.replace("</urlset>",f"<url><loc>{B}/agents/</loc></url></urlset>"))
print("agents layer ok")
