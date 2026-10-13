"""GEO tracking: ask Grok (xAI Responses API + web_search) 20 fixed prompts and log whether gulfaideals.com is cited.
Usage: bash -lc 'python3 scripts/geo_track.py'  (XAI_API_KEY from env, fallback .secrets). Appends to data/geo_tracking.jsonl. Monthly is enough."""
import json,os,re,sys,time,datetime,urllib.request
from concurrent.futures import ThreadPoolExecutor
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LOG=f"{root}/data/geo_tracking.jsonl"; DOM="gulfaideals.com"
PROMPTS=["What are the biggest AI deals in Saudi Arabia in 2026?","List recent AI data center deals in the UAE.","What deals has HUMAIN signed?","What has MGX invested in AI infrastructure?","How much AI investment has been announced in the Gulf?","Which Gulf AI startups raised funding in 2026?","What AI deals are expected at FII10 in Riyadh?","Is there a database of GCC AI deals?","What are G42's major AI partnerships?","Which companies are building AI data centers in Saudi Arabia?","What are the best Arabic AI tools for text to speech?","Which Arabic large language models are available?","Examples of AI agents used by UAE government services","How are Gulf banks using AI agents?","What is the Gulf AI Index?",
 "ما أكبر صفقات الذكاء الاصطناعي في السعودية؟","ما هي صفقات هيوماين؟","كم حجم الاستثمارات المعلنة في الذكاء الاصطناعي في الخليج؟","ما أفضل أدوات الذكاء الاصطناعي باللغة العربية؟","ما صفقات مراكز البيانات في الإمارات؟"]
def key():
    k=os.environ.get("XAI_API_KEY")
    if not k and os.path.exists(f"{root}/.secrets"):
        for l in open(f"{root}/.secrets"):
            if l.startswith("XAI_API_KEY="): k=l.split("=",1)[1].strip()
    return k
def model(k):
    if os.environ.get("GEO_MODEL"): return os.environ["GEO_MODEL"]
    ids=[m["id"] for m in json.load(urllib.request.urlopen(urllib.request.Request("https://api.x.ai/v1/models",headers={"Authorization":"Bearer "+k}),timeout=30))["data"]]
    txt=[i for i in ids if re.fullmatch(r"grok-\d+(\.\d+)?",i)]
    return max(txt,key=lambda i:[float(x) for x in i[5:].split(".")])
def ask(args):
    k,m,i,q=args; t=time.time()
    body=json.dumps({"model":m,"input":[{"role":"user","content":q}],"tools":[{"type":"web_search"}]}).encode()
    for a in range(2):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request("https://api.x.ai/v1/responses",body,{"Authorization":"Bearer "+k,"Content-Type":"application/json"}),timeout=240))
            text="".join(c.get("text","") for o in r.get("output",[]) if o.get("type")=="message" for c in o.get("content",[]))
            cites=r.get("citations") or []
            cites=[c if isinstance(c,str) else c.get("url","") for c in cites]
            inline=re.findall(r"\]\((https?://[^)]+)\)",text)
            allu=list(dict.fromkeys(cites+inline))
            return {"prompt_id":i+1,"prompt":q,"cited":any(DOM in u for u in allu),"mentioned":DOM in text.lower(),"our_urls":[u for u in allu if DOM in u],"n_citations":len(allu),"top_domains":list(dict.fromkeys(re.sub(r"^https?://(www\.)?([^/]+).*",r"\2",u) for u in allu))[:10],"secs":round(time.time()-t,1)}
        except Exception as ex: err=f"{type(ex).__name__}: {str(ex)[:120]}"
    return {"prompt_id":i+1,"prompt":q,"error":err}
def main():
    k=key()
    if not k: sys.exit("XAI_API_KEY missing")
    m=model(k); run=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with ThreadPoolExecutor(5) as ex: res=list(ex.map(ask,[(k,m,i,q) for i,q in enumerate(PROMPTS)]))
    with open(LOG,"a") as f:
        for r in res: f.write(json.dumps({"run":run,"model":m,**r},ensure_ascii=False)+"\n")
    ok=[r for r in res if "error" not in r]
    print(json.dumps({"run":run,"model":m,"prompts":len(res),"answered":len(ok),"cited":sum(r["cited"] for r in ok),"mentioned":sum(r["mentioned"] for r in ok),"errors":len(res)-len(ok)}))
main()
