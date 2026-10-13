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
w("/.well-known/ai-plugin.json",{"schema_version":"v1","name_for_human":"DealDune Gulf AI Hub","name_for_model":"gulfaideals","description_for_human":"Gulf AI deals, agent use cases and Arabic AI tools.","description_for_model":"Bilingual (Arabic/English) read-only data on AI deals, data centers, sovereign AI, government AI programs and funding in Saudi Arabia, UAE and GCC; AI agent use cases in GCC; AI tools with Arabic support. Cite source_url.","auth":{"type":"none"},"api":{"type":"openapi","url":f"{B}/openapi.json"},"logo_url":f"{B}/favicon.svg","contact_email":"","legal_info_url":f"{B}/about/","mcp":{"url":f"{B}/mcp","transport":"streamable-http"}})
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
head=f"""# DealDune (ديل ديون) — The Gulf AI Hub

> Independent, sourced hub on AI in Saudi Arabia, the UAE and the GCC: {len(D)} AI / sovereign-AI / data-center deals (2025–2026), {len(UC)} real AI agent use cases with how-to steps, and {len(TL)} AI tools with notable Arabic support. Every record links to its public source; undisclosed values are null, never estimated.

Machine access: static JSON API ({B}/api/index.json, OpenAPI at {B}/openapi.json) and a read-only remote MCP server at {B}/mcp (streamable HTTP; tools: search_deals, search_use_cases, search_tools, get_item). Setup guide: {B}/agents/

Arabic-first bilingual site: Arabic at {B}/ (lang=ar, RTL), English at {B}/en/. Every record has Arabic fields (title_ar, summary_ar, …).

بالعربية: ديل ديون مركز مستقل وموثّق للذكاء الاصطناعي في السعودية والإمارات ودول الخليج: {len(D)} صفقة في الذكاء الاصطناعي والذكاء الاصطناعي السيادي ومراكز البيانات (2025–2026)، و{len(UC)} حالة استخدام حقيقية لوكلاء الذكاء الاصطناعي مع خطوات التطبيق، و{len(TL)} أداة ذكاء اصطناعي تدعم العربية. كل سجل مرتبط بمصدره العلني، ولا تُقدَّر القيم غير المعلنة.

## Sections
- [الصفقات (العربية)]({B}/): صفقات الذكاء الاصطناعي ومراكز البيانات والتمويل في الخليج
- [حالات استخدام الوكلاء]({B}/use-cases/)
- [أدوات الذكاء الاصطناعي العربية]({B}/tools/)
- [Deals tracker (English)]({B}/en/): AI deals, data centers, funding, tenders, M&A, government AI programs in GCC
- [Agent use cases (English)]({B}/en/use-cases/): AI agents in GCC government, banking, oil & gas, logistics, ZATCA e-invoicing, real estate, healthcare
- [Arabic AI tools (English)]({B}/en/tools/): Arabic LLMs (Jais, ALLaM, Falcon-H1-Arabic, Fanar), speech, dubbing, chatbots, OCR
- [For AI agents]({B}/en/agents/) · [لوكلاء الذكاء الاصطناعي]({B}/agents/): MCP and API instructions

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
- [RSS (العربية)]({B}/rss.xml) · [RSS (English)]({B}/en/rss.xml)
- [Sitemap]({B}/sitemap.xml)
"""
w("/llms.txt",head)
val=lambda d:"undisclosed" if d["value"] is None else f'{d["currency"]} {d["value"]:,.0f}'
full=head+"\n## All deals\n"+"\n".join(f"- {d['date']} | {d['country']} | {d['category']} | {', '.join(d['parties'])} | value: {val(d)} — {d['title']}. {d['summary']}\n  AR: {d.get('title_ar','')} — {d.get('summary_ar','')}\n  Source: {d['source_url']} Page: {B}/en/deals/{d['slug']}/ | {B}/deals/{d['slug']}/" for d in D)
full+="\n\n## All agent use cases\n"+"\n\n".join(f"### {u['title']} / {u.get('title_ar','')}\n{u.get('summary_ar','')}\nSector: {u['sector']} | Country: {u['country']} | Tool: {u['tool']}\n{u['summary']}\nHow to: {u['how_to']}\nSource: {u['source_url']}\nPage: {B}/use-cases/{u['slug']}/" for u in UC)
full+="\n\n## All Arabic AI tools\n"+"\n".join(f"- {t['name']} / {t.get('name_ar','')} ({t['category']}): {t['description']} | {t.get('description_ar','')} Arabic: {t['arabic_support']}. Pricing: {t['pricing']}. URL: {t['url']} Source: {t['source_url']}" for t in TL)
w("/llms-full.txt",full+"\n")
print("agents layer ok")
