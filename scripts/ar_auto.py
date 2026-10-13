"""Arabic/English completion for new auto-published items (run by daily.sh after refresh.py).
- English-sourced items lacking title_ar/summary_ar, and Arabic-sourced items lacking English, are completed via an LLM
  IF an API key is present (XAI_API_KEY or OPENAI_API_KEY; optional LLM_MODEL). Style: native MSA Gulf business-press, glossary below.
- Without a key: items stay published with a visible 'translation pending' note and are listed in data/ar_pending.json for manual editing."""
import json,os,sys,urllib.request,re
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P=f"{root}/data/deals.json"
GLOSSARY="HUMAIN=هيوماين; G42=جي42; MGX=إم جي إكس; PIF=صندوق الاستثمارات العامة; SDAIA=سدايا (الهيئة السعودية للبيانات والذكاء الاصطناعي); NEOM=نيوم; Oxagon=أوكساجون; Aramco=أرامكو; ADNOC=أدنوك; Mubadala=مبادلة; Khazna=خزنة; stc=stc; center3=سنتر3; DataVolt=داتافولت; AWS=أمازون ويب سيرفيسز; Microsoft=مايكروسوفت; Google=غوغل; Oracle=أوراكل; NVIDIA=إنفيديا; OpenAI=أوبن إيه آي; QIA=جهاز قطر للاستثمار; KIA=الهيئة العامة للاستثمار الكويتية; ALLaM=علّام; Stargate UAE=ستارغيت الإمارات; NOTE: NVIDIA MGX (server platform) is NOT the Abu Dhabi fund — write «MGX» من إنفيديا; WAM=وكالة أنباء الإمارات (وام); SPA=وكالة الأنباء السعودية (واس). Cite non-Arabic outlets by an Arabic rendering in «», never a URL."
SYS=("You are a senior editor at a Gulf business newspaper (Asharq Al-Awsat / Argaam / Al Eqtisadiah style). Rewrite the item as native Modern Standard Arabic business-press copy: Arabic word order (verb-first headlines like «توقّع»، «تستحوذ»، «تجمع»), idiomatic financial vocabulary, no calques, no literal translation. "
     "Use correct Arabic entity names: "+GLOSSARY+". Western digits, amounts like '40 مليار دولار', '25 مليون درهم'. Put company names in «» when not widely Arabized. "
     "Keep every number, date and party exactly as given; never add facts, figures or context not in the input. Headline <= 90 characters. Ensure verb-subject agreement (a verb preceding a plural/dual subject stays singular). Return JSON only.")
def _key():
    k=os.environ.get("XAI_API_KEY")
    if not k and os.path.exists(f"{root}/.secrets"):
        for l in open(f"{root}/.secrets"):
            if l.startswith("XAI_API_KEY="): k=l.split("=",1)[1].strip()
    return k
_M=None
def model(key):
    global _M
    if _M: return _M
    if os.environ.get("LLM_MODEL"): _M=os.environ["LLM_MODEL"]; return _M
    ids=[m["id"] for m in json.load(urllib.request.urlopen(urllib.request.Request("https://api.x.ai/v1/models",headers={"Authorization":"Bearer "+key}),timeout=30))["data"]]
    txt=[i for i in ids if re.fullmatch(r"grok-\d+(\.\d+)?",i)]
    _M=max(txt,key=lambda i:[float(x) for x in i[5:].split(".")]) if txt else next(i for i in ids if "non-reasoning" in i)
    return _M
SYS_EN=("You are a wire-service business editor (Reuters style). Write concise English only, never Arabic. Use standard English entity names (HUMAIN, G42, MGX, PIF, SDAIA). Keep every number, date and party exactly as given; add nothing. Return JSON only.")
def llm(prompt,sys_prompt=None):
    key=_key()
    if not key: return None
    body=json.dumps({"model":model(key),"messages":[{"role":"system","content":sys_prompt or SYS},{"role":"user","content":prompt}],"temperature":0.2,"response_format":{"type":"json_object"}}).encode()
    for attempt in range(3):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request("https://api.x.ai/v1/chat/completions",body,{"Authorization":"Bearer "+key,"Content-Type":"application/json"}),timeout=150))
            return json.loads(r["choices"][0]["message"]["content"])
        except Exception as ex: print("  llm retry",attempt+1,type(ex).__name__,str(ex)[:100])
    return None
def work(d):
    out={}
    if not d.get("title_ar"):
        j=llm(f'Headline (English): {d["title"]}\nSummary: {d["summary"]}\nReturn {{"title_ar": "<= 90 chars headline", "summary_ar": "1-2 sentences"}}')
        out["ar"]=j if j and j.get("title_ar") else None
    if d.get("title_pending"):
        j=llm(f'العنوان: {d["title_ar"]}\nالملخص: {d.get("summary_ar","")}\nWrite concise English news-wire copy. Return {{"title": "<= 90 chars, English", "summary": "1-2 sentences, English"}}',SYS_EN)
        out["en"]=j if j and j.get("title") else None
    return d,out
def main():
    from concurrent.futures import ThreadPoolExecutor
    D=json.load(open(P)); pend=[]; done=0
    todo=[d for d in D if (d.get("status","published")=="published" or "--all" in sys.argv) and (not d.get("title_ar") or d.get("title_pending"))]
    if _key() and todo: model(_key())
    with ThreadPoolExecutor(8) as ex:
        for d,o in ex.map(work,todo):
            if "ar" in o:
                if o["ar"]: d["title_ar"]=o["ar"]["title_ar"][:120]; d["summary_ar"]=o["ar"].get("summary_ar") or d["title_ar"]; d["ar_generated"]=_M; done+=1
                else: pend.append({"id":d["id"],"need":"arabic","title":d["title"],"source_url":d["source_url"]})
            if "en" in o:
                if o["en"] and not re.search(r"[\u0600-\u06FF]",o["en"]["title"]): d["title"]=o["en"]["title"][:90]; d["summary"]=o["en"].get("summary") or d["title"]; d.pop("title_pending"); done+=1
                else: pend.append({"id":d["id"],"need":"english","title_ar":d["title_ar"],"source_url":d["source_url"]})
    json.dump(D,open(P,"w"),indent=1,ensure_ascii=False); json.dump(pend,open(f"{root}/data/ar_pending.json","w"),indent=1,ensure_ascii=False)
    print(json.dumps({"candidates":len(todo),"filled":done,"translation_pending":len(pend),"llm":bool(_key()),"model":_M}))
main()
