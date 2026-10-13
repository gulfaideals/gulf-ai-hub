"""Arabic/English completion for new auto-published items (run by daily.sh after refresh.py).
- English-sourced items lacking title_ar/summary_ar, and Arabic-sourced items lacking English, are completed via an LLM
  IF an API key is present (XAI_API_KEY or OPENAI_API_KEY; optional LLM_MODEL). Style: native MSA Gulf business-press, glossary below.
- Without a key: items stay published with a visible 'translation pending' note and are listed in data/ar_pending.json for manual editing."""
import json,os,urllib.request,re
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P=f"{root}/data/deals.json"
GLOSSARY="HUMAIN=هيوماين; G42=جي42; MGX=إم جي إكس; PIF=صندوق الاستثمارات العامة; SDAIA=سدايا (الهيئة السعودية للبيانات والذكاء الاصطناعي); NEOM=نيوم; Oxagon=أوكساجون; Aramco=أرامكو; ADNOC=أدنوك; Mubadala=مبادلة; Khazna=خزنة; stc=stc; center3=سنتر3; DataVolt=داتافولت; AWS=أمازون ويب سيرفيسز; Microsoft=مايكروسوفت; Google=غوغل; Oracle=أوراكل; NVIDIA=إنفيديا; OpenAI=أوبن إيه آي; QIA=جهاز قطر للاستثمار; KIA=الهيئة العامة للاستثمار الكويتية; ALLaM=علّام; Stargate UAE=ستارغيت الإمارات"
SYS=("You are an editor at a Gulf business newspaper (Asharq Al-Awsat/Argaam style). Write native Modern Standard Arabic, not literal translation. "
     "Use correct Arabic entity names: "+GLOSSARY+". Western digits, amounts like '40 مليار دولار', '25 مليون درهم'. Put company names in «» when not widely Arabized. "
     "Never add facts or figures not in the input. Return JSON only.")
def llm(prompt):
    key=os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key: return None
    url,model=("https://api.x.ai/v1/chat/completions",os.environ.get("LLM_MODEL","grok-4")) if os.environ.get("XAI_API_KEY") else ("https://api.openai.com/v1/chat/completions",os.environ.get("LLM_MODEL","gpt-4.1"))
    body=json.dumps({"model":model,"messages":[{"role":"system","content":SYS},{"role":"user","content":prompt}],"temperature":0.2,"response_format":{"type":"json_object"}}).encode()
    try:
        r=json.load(urllib.request.urlopen(urllib.request.Request(url,body,{"Authorization":"Bearer "+key,"Content-Type":"application/json"}),timeout=60))
        return json.loads(r["choices"][0]["message"]["content"])
    except Exception as ex: print("  llm error:",ex); return None
def main():
    D=json.load(open(P)); pend=[]; done=0
    for d in D:
        if d.get("status","published")!="published": continue
        if not d.get("title_ar"):
            j=llm(f'Headline (English): {d["title"]}\nSummary: {d["summary"]}\nReturn {{"title_ar": "<= 90 chars headline", "summary_ar": "1-2 sentences"}}')
            if j and j.get("title_ar"): d["title_ar"]=j["title_ar"][:120]; d["summary_ar"]=j.get("summary_ar") or j["title_ar"]; d["ar_generated"]="llm"; done+=1
            else: pend.append({"id":d["id"],"need":"arabic","title":d["title"],"source_url":d["source_url"]})
        if d.get("title_pending"):
            j=llm(f'العنوان: {d["title_ar"]}\nالملخص: {d.get("summary_ar","")}\nTranslate to concise English news style. Return {{"title": "<= 90 chars", "summary": "1-2 sentences"}}')
            if j and j.get("title"): d["title"]=j["title"][:90]; d["summary"]=j.get("summary") or j["title"]; d.pop("title_pending"); done+=1
            else: pend.append({"id":d["id"],"need":"english","title_ar":d["title_ar"],"source_url":d["source_url"]})
    json.dump(D,open(P,"w"),indent=1,ensure_ascii=False); json.dump(pend,open(f"{root}/data/ar_pending.json","w"),indent=1,ensure_ascii=False)
    print(json.dumps({"translated":done,"translation_pending":len(pend),"llm":bool(os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY"))}))
main()
