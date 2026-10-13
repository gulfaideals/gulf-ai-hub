"""Daily refresh. Pulls Google News RSS (no keys), dedupes, and:
 - deals: AUTO-PUBLISHES only candidates passing strict checks (Gulf country + AI term + deal verb + whitelisted source domain);
   others are saved as status='unreviewed' (hidden from site).
 - use cases / tools: new candidates go to data/candidates_use_cases.json / data/candidates_tools.json for manual review (never auto-published).
Values only from explicit headline figures, else null. Writes data/last_refresh.json (new published URLs etc.).
Usage: python3 scripts/refresh.py [--dry-run]"""
import json,os,re,sys,hashlib,urllib.request,urllib.parse,xml.etree.ElementTree as ET,email.utils
def headline(t,limit=90):
    """Complete headline: never cut mid-word; trims at a word boundary and drops trailing filler."""
    t=" ".join(str(t).split()).rstrip(" .")
    if len(t)<=limit: return t
    cut=t[:limit+1].rsplit(" ",1)[0]
    cut=re.sub(r"[\s,;:–-]+(and|or|of|to|the|a|an|in|for|with|at|by|on)$","",cut,flags=re.I).rstrip(" ,;:–-")
    return cut
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
def fetch(q,ar=False):
    u="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q+" when:2d","hl":"ar" if ar else "en-US","gl":"SA" if ar else "US","ceid":"SA:ar" if ar else "US:en"})
    r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=20)
    for it in ET.fromstring(r.read()).iter("item"):
        s=it.find("source"); dom=urllib.parse.urlparse(s.get("url","") if s is not None else "").netloc.lower().removeprefix("www.")
        t=(it.findtext("title") or ""); h=t.rsplit(" - ",1)[0]
        yield dict(title=h,link=it.findtext("link") or "",domain=dom,source_name=(s.text if s is not None else ""),date=email.utils.parsedate_to_datetime(it.findtext("pubDate")).date().isoformat())
def norm(t): return re.sub(r"[^\w ]","",t.lower())[:80]
def trusted(dom): return any(dom==w or dom.endswith("."+w) for w in WL)
def candidates(qs,seen_u,seen_t,ar=False):
    for q in qs:
        try: items=list(fetch(q,ar))
        except Exception as ex: print("  skip query:",q,ex); continue
        for it in items:
            if it["link"] in seen_u or norm(it["title"]) in seen_t: continue
            seen_u.add(it["link"]); seen_t.add(norm(it["title"])); yield it
WL_AR=["spa.gov.sa","wam.ae","argaam.com","aawsat.com","asharqbusiness.com","asharq.com","alarabiya.net","aleqt.com","alkhaleej.ae","albayan.ae","alittihad.ae","okaz.com.sa","sabq.org","alriyadh.com","aljazeera.net","cnbcarabia.com","skynewsarabia.com","maaal.com","qna.org.qa","bna.bh","kuna.net.kw","omannews.gov.om"]+WL
AQ=["هيوماين","جي42 الذكاء الاصطناعي","إم جي إكس استثمار","سدايا اتفاقية","مركز بيانات الذكاء الاصطناعي السعودية","مركز بيانات الذكاء الاصطناعي الإمارات","شركة ناشئة ذكاء اصطناعي تمويل السعودية","ستارغيت الإمارات"]
CC_AR={"Saudi Arabia":r"السعود|المملكة|الرياض|جدة|نيوم|هيوماين|سدايا|صندوق الاستثمارات","UAE":r"الإمارات|أبوظبي|دبي|جي42|إم جي إكس|خزنة","Qatar":r"قطر|الدوحة","Kuwait":r"الكويت","Bahrain":r"البحرين","Oman":r"عُمان|عمان|مسقط"}
AI_AR=r"الذكاء الاصطناعي|مراكز? البيانات|حوسبة|رقائق|نموذج لغوي"
DV_AR=r"(توقع|توقيع|توقّع)\s|اتفاقية|مذكرة تفاهم|تستحوذ|استحواذ على|تجمع .*(مليون|مليار)|جولة تمويل|ترسية|مشروع مشترك|تستثمر .*(مليون|مليار)"
NOT_AR=r"تقود|طفرة|تقرير|توقعات|رؤية|مستقبل|كيف|لماذا|هل "
KK_AR=[("funding",r"جولة تمويل|تجمع"),("M&A",r"استحواذ|تستحوذ|اندماج"),("tender",r"عقد|ترسية|مناقصة"),("data center",r"مركز بيانات|مراكز البيانات|ميغاواط|غيغاواط"),("gov program",r"وزارة|حكومة|هيئة|استراتيجية"),("partnership",r"شراكة|مذكرة تفاهم|اتفاقية|مشروع مشترك")]
def arabic_candidates(D,su,st,ids,slugs):
    new=[]
    for it in candidates(AQ,su,st,ar=True):
        h=it["title"]
        c=next((k for k,v in CC_AR.items() if re.search(v,h)),None)
        if not c or not re.search(AI_AR,h): continue
        cat=next((k for k,v in KK_AR if re.search(v,h)),None)
        strict=bool(cat) and bool(re.search(DV_AR,h)) and not re.search(NOT_AR,h) and any(it["domain"]==w or it["domain"].endswith("."+w) for w in WL_AR)
        i=hashlib.sha1(it["link"].encode()).hexdigest()[:10]
        if i in ids: continue
        ids.add(i); slug=f'{it["date"]}-ar-{i}'
        new.append(dict(id=i,slug=slug,date=it["date"],date_precision="day",country=c,parties=[],category=cat or "partnership",value=None,currency=None,
            title=h,title_pending=True,title_ar=headline(h),summary=h,summary_ar=f'{h}، بحسب {it["source_name"] or it["domain"]}.',source_url=it["link"],source_url_ar=it["link"],source_name=it["source_name"],source_domain=it["domain"],status="published" if strict else "unreviewed",auto=True,lang_source="ar"))
    return new

def load(p,d): return json.load(open(p)) if os.path.exists(p) else d
def main():
    dry="--dry-run" in sys.argv
    D=load(P,[]); su={d["source_url"] for d in D}|{u for d in D for u in d.get("alt_urls",[])}; ids={d["id"] for d in D}; st={norm(d["title"]) for d in D}; new=[]
    for it in candidates(DQ,su,st):
        low=it["title"].lower()
        c=next((k for k,v in CC.items() if re.search(v,low)),None)
        if not c or not re.search(AI,low): continue
        cat=next((k for k,v in KK if re.search(v,low)),None)
        strict=bool(cat) and bool(re.search(DV,low)) and trusted(it["domain"])
        m=re.search(r"\$\s?([\d.]+)\s?(billion|bn|million|m)\b",low); val=float(m.group(1))*(1e9 if m.group(2) in("billion","bn") else 1e6) if m else None
        rec=dict(id=hashlib.sha1(it["link"].encode()).hexdigest()[:10],slug=re.sub(r"[^a-z0-9]+","-",it["date"]+"-"+norm(it["title"])[:60]).strip("-"),date=it["date"],date_precision="day",country=c,parties=[],category=cat or "partnership",value=val,currency="USD" if val else None,
                 title=headline(it["title"]),summary=f'{it["title"]} (reported by {it["source_name"] or it["domain"]}).',source_url=it["link"],source_name=it["source_name"],source_domain=it["domain"],status="published" if strict else "unreviewed",auto=True)

        if rec["id"] in ids: continue
        ids.add(rec["id"]); new.append(rec)
    slugs={d["slug"] for d in D}
    new+=arabic_candidates(D,su,st,ids,slugs)
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
