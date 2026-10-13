"""Daily refresh. Pulls Google News RSS (no keys), dedupes, and:
 - deals: AUTO-PUBLISHES only candidates passing strict checks (Gulf country + AI term + deal verb + whitelisted source domain);
   others are saved as status='unreviewed' (hidden from site).
 - use cases / tools: new candidates go to data/candidates_use_cases.json / data/candidates_tools.json for manual review (never auto-published).
Values only from explicit headline figures, else null. Writes data/last_refresh.json (new published URLs etc.).
Usage: python3 scripts/refresh.py [--dry-run]"""
import json,os,re,sys,hashlib,urllib.request,urllib.parse,xml.etree.ElementTree as ET,email.utils
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P=f"{root}/data/deals.json"
WL=["reuters.com","bloomberg.com","arabnews.com","thenationalnews.com","gulfnews.com","zawya.com","saudigazette.com.sa","wam.ae","spa.gov.sa","argaam.com","khaleejtimes.com","agbi.com","ft.com","cnbc.com","datacenterdynamics.com","techcrunch.com","wsj.com","apnews.com","mediaoffice.ae","mediaoffice.abudhabi","qna.org.qa","bna.bh","kuna.net.kw","omannews.gov.om",
    "humain.com","g42.ai","mgx.ae","aboutamazon.com","blogs.microsoft.com","news.microsoft.com","nvidianews.nvidia.com","blog.google","googlecloudpresscorner.com","oracle.com","openai.com","aramco.com","adnoc.ae","pif.gov.sa","sdaia.gov.sa","stc.com.sa","eand.com","mubadala.com","presight.ai","khazna.ae","qia.qa"]
DQ=["HUMAIN Saudi AI","G42 Abu Dhabi AI","MGX Abu Dhabi investment","Stargate UAE","SDAIA agreement","Saudi data center AI","UAE data centre AI","Saudi AI startup raises","UAE AI startup raises","Qatar AI investment","Kuwait AI data center","Bahrain AI data centre","Oman AI data center","NEOM AI"]
UQ=["Saudi AI agent launches","UAE government AI agent","Dubai AI agent service","bank Saudi generative AI deploys","UAE bank AI agent","ZATCA AI automation"]
TQ=["Arabic LLM launch","Arabic AI model released","Arabic speech recognition AI launch","Arabic text to speech AI","Arabic AI chatbot launch"]
CC={"Saudi Arabia":r"\bsaudi|\bksa\b|riyadh|jeddah|neom|humain|sdaia|\bpif\b|dammam","UAE":r"\buae\b|emirat|abu dhabi|dubai|\bg42\b|\bmgx\b|khazna","Qatar":r"qatar|doha|\bqia\b","Kuwait":r"kuwait","Bahrain":r"bahrain","Oman":r"\boman\b|muscat"}
AI=r"\bai\b|artificial intelligence|data ?cent|\bgpus?\b|compute|\bllm\b|machine learning|generative"
DV=r"\b(signs?|signed|invests?|investment|raises? \$|raised \$|acquires?|acquisition|partners?|partnership|mou|agreement|deal|awards?|awarded|contract|launch(es|ed)?|funding|joint venture|jv|builds?|to build|expands?)\b"
KK=[("funding",r"raise|series [a-e]|seed|funding round"),("M&A",r"acqui|merger|takeover"),("tender",r"tender|contract|award"),("data center",r"data ?cent|campus|\bmw\b|\bgw\b"),("gov program",r"ministry|government|authority|strategy|program"),("partnership",r"partner|mou|agreement|collaborat|joint venture")]
def fetch(q):
    u="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q+" when:2d","hl":"en-US","gl":"US","ceid":"US:en"})
    r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=20)
    for it in ET.fromstring(r.read()).iter("item"):
        s=it.find("source"); dom=urllib.parse.urlparse(s.get("url","") if s is not None else "").netloc.lower().removeprefix("www.")
        t=(it.findtext("title") or ""); h=t.rsplit(" - ",1)[0]
        yield dict(title=h,link=it.findtext("link") or "",domain=dom,source_name=(s.text if s is not None else ""),date=email.utils.parsedate_to_datetime(it.findtext("pubDate")).date().isoformat())
def norm(t): return re.sub(r"[^a-z0-9 ]","",t.lower())[:80]
def trusted(dom): return any(dom==w or dom.endswith("."+w) for w in WL)
def candidates(qs,seen_u,seen_t):
    for q in qs:
        try: items=list(fetch(q))
        except Exception as ex: print("  skip query:",q,ex); continue
        for it in items:
            if it["link"] in seen_u or norm(it["title"]) in seen_t: continue
            seen_u.add(it["link"]); seen_t.add(norm(it["title"])); yield it
def load(p,d): return json.load(open(p)) if os.path.exists(p) else d
def main():
    dry="--dry-run" in sys.argv
    D=load(P,[]); su={d["source_url"] for d in D}; st={norm(d["title"]) for d in D}; new=[]
    for it in candidates(DQ,su,st):
        low=it["title"].lower()
        c=next((k for k,v in CC.items() if re.search(v,low)),None)
        if not c or not re.search(AI,low): continue
        cat=next((k for k,v in KK if re.search(v,low)),None)
        strict=bool(cat) and bool(re.search(DV,low)) and trusted(it["domain"])
        m=re.search(r"\$\s?([\d.]+)\s?(billion|bn|million|m)\b",low); val=float(m.group(1))*(1e9 if m.group(2) in("billion","bn") else 1e6) if m else None
        rec=dict(id=hashlib.sha1(it["link"].encode()).hexdigest()[:10],slug=re.sub(r"[^a-z0-9]+","-",it["date"]+"-"+norm(it["title"])[:60]).strip("-"),date=it["date"],date_precision="day",country=c,parties=[],category=cat or "partnership",value=val,currency="USD" if val else None,
                 title=it["title"],summary=f'{it["title"]} (reported by {it["source_name"] or it["domain"]}).',source_url=it["link"],source_name=it["source_name"],source_domain=it["domain"],status="published" if strict else "unreviewed",auto=True)

        new.append(rec)
    slugs={d["slug"] for d in D}
    for n in new:
        while n["slug"] in slugs: n["slug"]+="-2"
        slugs.add(n["slug"])
    pub=[n for n in new if n["status"]=="published"]; pend=[n for n in new if n["status"]!="published"]
    res={"published":[f"https://gulfaideals.com/deals/{n['slug']}/" for n in pub],"published_titles":[n["title"] for n in pub],"pending_deals":len(pend)}
    for kind,qs in (("use_cases",UQ),("tools",TQ)):
        cp=f"{root}/data/candidates_{kind}.json"; C=load(cp,[]); cu={c["link"] for c in C}; ct={norm(c["title"]) for c in C}
        add=[dict(**it,status="unreviewed") for it in candidates(qs,cu,ct) if re.search(AI,it["title"].lower()) and (kind=="tools" and re.search(r"arabic",it["title"].lower()) or kind=="use_cases" and any(re.search(v,it["title"].lower()) for v in CC.values()))]
        res[f"pending_{kind}_new"]=len(add); res[f"pending_{kind}_total"]=len(C)+len(add)
        if not dry and add: json.dump(C+add,open(cp,"w"),indent=1)
    res["pending_deals_total"]=sum(1 for d in D+new if d.get("status")=="unreviewed")
    if not dry:
        if new: json.dump(sorted(D+new,key=lambda x:x["date"],reverse=True),open(P,"w"),indent=1)
        json.dump(res,open(f"{root}/data/last_refresh.json","w"),indent=1)
    print(json.dumps(res,indent=1))
main()
