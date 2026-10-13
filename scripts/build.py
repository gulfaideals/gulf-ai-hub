"""Bilingual static site generator (Arabic-first at /, English at /en/). data/*.json -> dist/"""
import json,os,html,shutil,datetime,re,subprocess,sys
B=os.environ.get("SITE_URL","https://gulfaideals.com").rstrip("/")
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out=f"{root}/dist"; e=html.escape
D=[d for d in json.load(open(f"{root}/data/deals.json")) if d.get("status","published")!="unreviewed"]; D.sort(key=lambda x:x["date"],reverse=True)
UC=json.load(open(f"{root}/data/use_cases.json")); TL=json.load(open(f"{root}/data/tools.json"))
shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
YEAR=datetime.date.today().year
COUNTRY={"Saudi Arabia":"السعودية","UAE":"الإمارات","Qatar":"قطر","Kuwait":"الكويت","Bahrain":"البحرين","Oman":"عُمان"}
CAT={"data center":"مراكز البيانات","partnership":"شراكات","funding":"تمويل","gov program":"برامج حكومية","tender":"مناقصات وعقود","M&A":"استحواذ واندماج"}
SECTOR={"Government services":"الخدمات الحكومية","Arabic customer service":"خدمة العملاء بالعربية","Banking":"البنوك","Oil & gas":"النفط والغاز","Logistics & postal":"الخدمات اللوجستية والبريد","ZATCA e-invoicing":"الفوترة الإلكترونية (زاتكا)","Real estate":"العقارات","Healthcare":"الرعاية الصحية","Travel & aviation":"السفر والطيران","Telecom":"الاتصالات","Utilities":"المرافق"}
TCAT={"Arabic LLM":"نماذج لغوية عربية","Arabic NLP":"معالجة اللغة العربية","OCR":"التعرف الضوئي على النصوص","Speech-to-text":"تحويل الكلام إلى نص","Text-to-speech":"تحويل النص إلى كلام","Dubbing":"الدبلجة","Dubbing & lip-sync":"الدبلجة ومزامنة الشفاه","Enterprise AI platform":"منصات مؤسسية","Chatbot / voice agent":"روبوتات المحادثة والوكلاء الصوتيون","CX & social listening":"تجربة العملاء والرصد الاجتماعي","Voice agent":"وكلاء صوتيون","Fraud & AML AI":"مكافحة الاحتيال وغسل الأموال"}
PRICE={"Open weights":"أوزان مفتوحة","Free access / research":"وصول مجاني / بحثي","Via cloud providers":"عبر مزودي السحابة","Open weights (non-commercial) + paid API":"أوزان مفتوحة (غير تجارية) وواجهة مدفوعة","See source":"راجع المصدر","Paid API":"واجهة برمجية مدفوعة","See vendor site":"راجع موقع المورّد","Freemium":"مجاني مع خطط مدفوعة","Freemium / subscription":"مجاني مع اشتراكات","Pay-as-you-go":"الدفع حسب الاستخدام","Enterprise":"للمؤسسات","Subscription":"اشتراك"}
CUR_AR={"USD":"دولار","AED":"درهم","SAR":"ريال"}
T={"ar":dict(dir="rtl",brand="ديل ديون",tag="مركز الذكاء الاصطناعي في الخليج: الصفقات وحالات استخدام الوكلاء والأدوات العربية",deals="الصفقات",uc="حالات استخدام الوكلاء",tools="أدوات الذكاء الاصطناعي العربية",agents="لوكلاء الذكاء الاصطناعي",sponsor="رعاية",about="من نحن",rss="RSS",switch="English",
  hero="مركز الذكاء الاصطناعي في الخليج",herosub="{d} صفقة موثّقة · {u} حالة استخدام للوكلاء · {t} أداة ذكاء اصطناعي عربية — السعودية والإمارات ودول الخليج. تحديث يومي.",
  latest="أحدث الصفقات",allc="كل الدول",allk="كل الفئات",all="الكل",search="ابحث…",undisc="غير مُفصح عنها",value="القيمة",parties="الأطراف",source="المصدر",seesrc="راجع المصدر",back_d="→ كل الصفقات",back_u="→ كل حالات الاستخدام",back_t="→ كل الأدوات",
  howto="كيف تطبّقها",howto_note="خطوات تنفيذ عامة من إعداد المحرر، وليست وصفاً للإجراءات الداخلية للجهة المعنية.",arsup="دعم العربية",pricing="التسعير",website="الموقع",
  nl_h="النشرة البريدية الأسبوعية",nl_p="كل صفقة ومناقصة وخطوة في الذكاء الاصطناعي السيادي بالسعودية والإمارات والخليج. رسالة واحدة كل اثنين.",nl_btn="اشترك",nl_ph="بريدك الإلكتروني",nl_err="تعذّر الاتصال، يرجى المحاولة مجدداً.",
  sp_banner="<b>مساحة رعاية متاحة</b> — صِل إلى صنّاع القرار في قطاع الذكاء الاصطناعي الخليجي. <a href=\"/sponsor/\">احجز هذا الأسبوع ←</a>",
  cta_tool="<b>طوّرت أداة ذكاء اصطناعي تدعم العربية؟</b> أضفها أو احصل على إدراج مميّز (150 دولاراً شهرياً، سعر مبدئي). <a href=\"/sponsor/#featured\">أضف أداتك ←</a>",
  uc_h="حالات استخدام وكلاء الذكاء الاصطناعي في الخليج",uc_intro="{n} مثالاً حقيقياً موثّقاً لوكلاء الذكاء الاصطناعي والأتمتة في الجهات الحكومية والشركات الخليجية، مع خطوات التطبيق.",
  t_h="دليل أدوات الذكاء الاصطناعي العربية",t_intro="{n} أداة ذكاء اصطناعي تدعم العربية بشكل لافت. دعم اللهجات كما يذكره كل مصدر.",
  footer="ديل ديون — مركز مستقل للذكاء الاصطناعي في الخليج. ليس نصيحة استثمارية. كل خبر مرتبط بمصدره.",pending_ar="(العنوان بالإنجليزية — الترجمة قيد الإعداد)",
  sponsor_h="رعاية ديل ديون",sponsor_p="صِل إلى المؤسسين والمستثمرين والمشغلين ومشتري التقنية الحكومية المهتمين بالذكاء الاصطناعي في الخليج. الأسعار أدناه مبدئية.",
  sp1=("مساحة أسبوعية في الموقع","300 دولار / أسبوع","إعلان في الصفحة الرئيسية وجميع صفحات الصفقات لمدة 7 أيام."),sp2=("رعاية النشرة البريدية","400 دولار / عدد","أعلى الرسالة في نشرة الاثنين."),sp3=("إدراج مميّز لأداة","150 دولاراً / شهر","صدارة دليل الأدوات العربية مع شارة «مميّز». تقديم الأدوات مجاناً (بمراجعة تحريرية) قريباً."),sp4=("الباقة الكاملة","600 دولار / أسبوع","مساحة الموقع + النشرة + إدراج مميّز."),
  soon="الحجز متاح قريباً",sp_note="المحتوى المموّل يُوسم دائماً، ولا يؤثر الرعاة في التغطية.",
  about_p1="ديل ديون مركز مستقل يرصد الإعلانات العلنية عن صفقات الذكاء الاصطناعي والذكاء الاصطناعي السيادي ومراكز البيانات والمناقصات والشراكات والتمويل في السعودية والإمارات ودول الخليج، إلى جانب حالات استخدام حقيقية للوكلاء الذكيين ودليل لأدوات الذكاء الاصطناعي العربية.",
  about_p2="كل إدخال يستند إلى مصدر علني مرتبط بصفحته. لا نعرض القيم إلا إذا أُفصح عنها، ولا نقدّر الأرقام غير المعلنة. التواريخ المحددة بالشهر أو السنة تعكس دقة المصدر.",about_p3="لديك صفقة أو تصحيح؟ نموذج الإرسال قريباً.",
  ag_h="لوكلاء ومساعدي الذكاء الاصطناعي",ag_p="صُمّم ديل ديون ليُستخدم من قبل وكلاء الذكاء الاصطناعي. كل شيء للقراءة فقط ومجاني ودون مفتاح. يرجى الإشارة إلى <code>source_url</code> لكل سجل."),
"en":dict(dir="ltr",brand="DealDune",tag="The Gulf AI Hub: deals, agent use cases & Arabic AI tools",deals="Deals",uc="Agent Use Cases",tools="Arabic AI Tools",agents="For AI agents",sponsor="Sponsor",about="About",rss="RSS",switch="العربية",
  hero="The Gulf AI Hub",herosub="{d} sourced deals · {u} agent use cases · {t} Arabic AI tools — Saudi Arabia, UAE &amp; GCC. Updated daily.",
  latest="Latest deals",allc="All countries",allk="All categories",all="All",search="Search…",undisc="Undisclosed",value="Value",parties="Parties",source="Source",seesrc="See source",back_d="← All deals",back_u="← All use cases",back_t="← All tools",
  howto="How to do it",howto_note="Generic implementation steps by the editors, not a description of the organisation's internal process.",arsup="Arabic support",pricing="Pricing",website="Website",
  nl_h="Weekly Gulf AI brief",nl_p="Every deal, tender and sovereign-AI move in KSA, UAE &amp; GCC. One email, Mondays.",nl_btn="Subscribe",nl_ph="you@company.com",nl_err="Network error, please retry.",
  sp_banner="<b>Sponsor slot available</b> — reach Gulf AI decision makers. <a href=\"/en/sponsor/\">Book this week →</a>",
  cta_tool="<b>Built an Arabic AI tool?</b> Submit it or get a featured listing ($150/month, placeholder). <a href=\"/en/sponsor/#featured\">Submit / feature your tool →</a>",
  uc_h="AI Agent Use Cases in the Gulf",uc_intro="{n} real, sourced examples of AI agents and automation in GCC government and business — each with a how-to.",
  t_h="Arabic AI Tools Directory",t_intro="{n} AI tools with notable Arabic support. Dialect support is as stated by each source.",
  footer="DealDune — independent Gulf AI hub. Not investment advice. Every entry links to its source.",pending_ar="",
  sponsor_h="Sponsor DealDune",sponsor_p="Reach founders, investors, operators and government-tech buyers following AI in the Gulf. Introductory placeholder pricing.",
  sp1=("Weekly site slot","$300 / week","Banner on homepage + all deal pages for 7 days."),sp2=("Newsletter sponsor","$400 / issue","Top-of-email placement in the Monday brief."),sp3=("Featured tool listing","$150 / month","Top placement in the Arabic AI Tools directory + \"Featured\" badge. Free, editorially reviewed submissions open soon."),sp4=("Bundle","$600 / week","Site slot + newsletter + featured listing."),
  soon="Booking opens soon",sp_note="Sponsored content is always labelled. Sponsors never influence coverage.",
  about_p1="DealDune is an independent Gulf AI hub covering publicly announced AI, sovereign-AI, data-center, tender, partnership and funding activity in Saudi Arabia, the UAE and the wider GCC, plus real AI agent use cases and a directory of Arabic AI tools.",
  about_p2="Every entry is based on a public source, linked on its page. Values are shown only when disclosed; we never estimate undisclosed figures. Dates marked by month or year reflect source precision.",about_p3="Spotted a deal or correction? A submission form is coming soon.",
  ag_h="For AI agents &amp; assistants",ag_p="DealDune is built to be used by AI agents. Everything is read-only, free and needs no key. Please cite each record's <code>source_url</code>.")}
def P(lang): return "" if lang=="ar" else "/en"
def fmt_num(v):
    s=f"{v:,.2f}".rstrip("0").rstrip("."); return s
def val(d,lang):
    v=d.get("value")
    if v is None: return T[lang]["undisc"]
    cur=d.get("currency") or "USD"
    if lang=="en": return f'{cur} {v/1e9:g}bn' if v>=1e9 else f'{cur} {v/1e6:g}m'
    unit,n=("مليار",v/1e9) if v>=1e9 else ("مليون",v/1e6)
    if unit=="مليون" and n>=3 and n<=10 and n==int(n): unit="ملايين"
    return f"{n:g} {unit} {CUR_AR.get(cur,cur)}"
def dtitle(d,lang):
    if lang=="ar": return d.get("title_ar") or d["title"]
    return d["title"] if not d.get("title_pending") else (d.get("title_ar") or d["title"])
def dsum(d,lang): return (d.get("summary_ar") or d["summary"]) if lang=="ar" else d["summary"]
CSS="""*{box-sizing:border-box}body{margin:0;font:16px/1.7 'IBM Plex Sans Arabic',system-ui,sans-serif;background:#0b1020;color:#e6e9f2}html[lang=en] body{line-height:1.55}a{color:#7cc4ff}
header,footer{padding:14px 24px;display:flex;gap:18px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #1d2540}footer{border:0;border-top:1px solid #1d2540;color:#8a93ad;font-size:14px}
.logo{font-weight:700;font-size:21px;color:#fff;text-decoration:none}.logo span{color:#f5b942}.sw{margin-inline-start:auto;border:1px solid #2a3458;padding:3px 10px;border-radius:8px;text-decoration:none}main{max-width:1000px;margin:auto;padding:24px}
.hero h1{font-size:34px;margin:.2em 0}.muted{color:#8a93ad}.f{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}select,input,button{font:inherit;padding:8px 12px;border-radius:8px;border:1px solid #2a3458;background:#121a33;color:#e6e9f2}
button{background:#f5b942;color:#111;border:0;font-weight:700;cursor:pointer}.card{background:#121a33;border:1px solid #1d2540;border-radius:12px;padding:16px;margin:12px 0}
.card h3{margin:.2em 0;font-size:18px}.tag{display:inline-block;font-size:12px;padding:2px 8px;border-radius:99px;background:#1d2a50;margin-inline-end:6px}.v{color:#f5b942;font-weight:700}
.sp{border:1px dashed #f5b942;border-radius:12px;padding:14px;margin:16px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}pre{white-space:pre-wrap;direction:ltr;text-align:left;background:#0e1530;padding:10px;border-radius:8px}code{direction:ltr;unicode-bidi:embed}"""
FONT='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;600;700&display=swap" rel="stylesheet">'
ORG={"@type":"Organization","@id":f"{B}/#org","name":"DealDune","alternateName":"ديل ديون","url":B+"/","logo":f"{B}/favicon.svg"}
URLS=[]
def page(lang,rel,title,desc,body,ld=None):
    t=T[lang]; p=P(lang); other="en" if lang=="ar" else "ar"; orel=rel
    nav=f'<header><a class="logo" href="{p}/">{"ديل <span>ديون</span>" if lang=="ar" else "Deal<span>Dune</span>"}</a><a href="{p}/">{t["deals"]}</a><a href="{p}/use-cases/">{t["uc"]}</a><a href="{p}/tools/">{t["tools"]}</a><a href="{p}/gulf-ai-index/">{"المؤشر" if lang=="ar" else "Index"}</a><a href="{p}/fii10/">FII10</a><a href="{p}/companies/">{"الشركات" if lang=="ar" else "Companies"}</a><a href="{p}/agents/">{t["agents"]}</a><a href="{p}/sponsor/">{t["sponsor"]}</a><a href="{p}/about/">{t["about"]}</a><a href="{p}/rss.xml">{t["rss"]}</a><a class="sw" hreflang="{other}" lang="{other}" href="{P(other)}{orel}">{t["switch"]}</a></header>'
    lds="".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in (ld or []))
    h=f'''<!doctype html><html lang="{lang}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{B}{p}{rel}">
<link rel="alternate" hreflang="ar" href="{B}{rel}"><link rel="alternate" hreflang="en" href="{B}/en{rel}"><link rel="alternate" hreflang="x-default" href="{B}{rel}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{B}{p}{rel}"><meta property="og:locale" content="{"ar_AR" if lang=="ar" else "en_US"}"><meta name="twitter:card" content="summary">
<link rel="icon" href="/favicon.svg"><link rel="alternate" type="application/rss+xml" title="DealDune" href="{p}/rss.xml"><link rel="alternate" type="text/plain" title="llms.txt" href="/llms.txt">{FONT}<style>{CSS}</style></head><body>{nav}<main>{body}</main>
<footer>© {YEAR} {t["footer"]} · <a href="{p}/privacy/">{"الخصوصية" if lang=="ar" else "Privacy"}</a> · <a href="{p}/terms/">{"الشروط" if lang=="ar" else "Terms"}</a> · <a href="{p}/support/">{"الدعم" if lang=="ar" else "Support"}</a> · <a href="{p}/countries/">{"الدول" if lang=="ar" else "Countries"}</a> · <a href="{p}/sectors/">{"القطاعات" if lang=="ar" else "Sectors"}</a></footer>{lds}</body></html>'''
    fp=f"{out}{p}{rel}index.html"; os.makedirs(os.path.dirname(fp),exist_ok=True); open(fp,"w").write(h)
    if lang=="ar": URLS.append(rel)
def NL(lang):
    t=T[lang]
    return f'''<div class="card"><h3>{t["nl_h"]}</h3><p class="muted">{t["nl_p"]}</p>
<form class="f nl" method="post" action="/api/subscribe"><input name="email" type="email" required placeholder="{t["nl_ph"]}" dir="ltr"><input name="website" tabindex="-1" autocomplete="off" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);opacity:0" aria-hidden="true"><button>{t["nl_btn"]}</button><span class="msg muted"></span></form></div>
<script>document.querySelectorAll('form.nl').forEach(f=>f.onsubmit=async ev=>{{ev.preventDefault();const m=f.querySelector('.msg');m.textContent='…';try{{const r=await fetch('/api/subscribe',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:f.email.value,website:f.website.value,source:location.pathname,lang:document.documentElement.lang}})}});const j=await r.json();if(j.ok){{f.innerHTML='<b>'+(document.documentElement.lang==='ar'?(j.message_ar||'شكراً لاشتراكك.'):j.message)+'</b>'}}else m.textContent=(document.documentElement.lang==='ar'?(j.error_ar||j.error):j.error)}}catch(e){{m.textContent='{t["nl_err"]}'}}}});</script>'''
def SP(lang): return f'<div class="sp">{T[lang]["sp_banner"]}</div>'
FILTER_JS="""<script>const f=()=>{const g=i=>(document.getElementById(i)||{}).value||'';const c=g('c'),k=g('k'),q=g('q').toLowerCase();document.querySelectorAll('#list .card').forEach(x=>{x.style.display=(!c||x.dataset.c==c)&&(!k||x.dataset.k==k)&&(!q||x.textContent.toLowerCase().includes(q))?'':'none'})};['c','k','q'].forEach(i=>{const el=document.getElementById(i);if(el)el.addEventListener('input',f)});const _q=new URLSearchParams(location.search).get('q');if(_q){document.getElementById('q').value=_q;f()}</script>"""
def lc(x,m,lang): return m.get(x,x) if lang=="ar" else x
for lang in ("ar","en"):
    t=T[lang]; p=P(lang)
    def dcard(d):
        return f'''<div class="card" data-c="{e(d["country"])}" data-k="{e(d["category"])}"><span class="tag" dir="ltr">{e(d["date"])}</span><span class="tag">{e(lc(d["country"],COUNTRY,lang))}</span><span class="tag">{e(lc(d["category"],CAT,lang))}</span><span class="v">{e(val(d,lang))}</span>
<h3><a href="{p}/deals/{d["slug"]}/">{e(dtitle(d,lang))}</a></h3><p>{e(dsum(d,lang))}</p></div>'''
    opt=lambda vals,m:"".join(f'<option value="{e(x)}">{e(lc(x,m,lang))}</option>' for x in sorted(vals))
    huc="".join(f'<p><a href="{p}/use-cases/{u["slug"]}/">{e(u.get("title_ar",u["title"]) if lang=="ar" else u["title"])}</a><br><span class="muted">{e(lc(u["sector"],SECTOR,lang))} · {e(lc(u["country"],COUNTRY,lang))}</span></p>' for u in UC[:4])
    htl="".join(f'<p><a href="{p}/tools/{x["slug"]}/">{e(x.get("name_ar",x["name"]) if lang=="ar" else x["name"])}</a> <span class="muted">— {e(lc(x["category"],TCAT,lang))}</span></p>' for x in TL[:5])
    home=f'''<section class="hero"><h1>{t["hero"]}</h1><p class="muted">{t["herosub"].format(d=len(D),u=len(UC),t=len(TL))}</p></section>
<div class="grid"><div class="card"><h3><a href="{p}/use-cases/">{t["uc"]} {"←" if lang=="ar" else "→"}</a></h3>{huc}</div><div class="card"><h3><a href="{p}/tools/">{t["tools"]} {"←" if lang=="ar" else "→"}</a></h3>{htl}</div></div><h2>{t["latest"]}</h2>
<div class="f"><select id="c"><option value="">{t["allc"]}</option>{opt({d["country"] for d in D},COUNTRY)}</select><select id="k"><option value="">{t["allk"]}</option>{opt({d["category"] for d in D},CAT)}</select><input id="q" placeholder="{t["search"]}"></div>
{SP(lang)}<div id="list">{"".join(dcard(d) for d in D)}</div>{NL(lang)}{FILTER_JS}'''
    ld_home=[{"@context":"https://schema.org","@type":"WebSite","@id":f"{B}/#site","name":"DealDune — "+T["en"]["tag"],"alternateName":"ديل ديون","url":B+"/","inLanguage":["ar","en"],"publisher":ORG,"potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":f"{B}{p}/?q={{search_term_string}}"},"query-input":"required name=search_term_string"}},
        {"@context":"https://schema.org","@type":"Dataset","name":"صفقات الذكاء الاصطناعي في الخليج 2025-2026" if lang=="ar" else "Gulf AI deals 2025-2026","description":t["tag"],"url":B+p+"/","creator":ORG,"inLanguage":lang,"spatialCoverage":"Gulf Cooperation Council","temporalCoverage":"2025/2026","license":f"{B}/about/","distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":f"{B}/api/deals.json"}]}]
    page(lang,"/",f"{t['brand']} — {t['tag']}",t["tag"],home,ld_home)
    for d in D:
        pend=f' <span class="muted">{t["pending_ar"]}</span>' if lang=="ar" and not d.get("title_ar") else (' <span class="muted">(Arabic source — English translation pending)</span>' if lang=="en" and d.get("title_pending") else "")
        su=d.get("source_url_ar") if lang=="ar" and d.get("source_url_ar") else d["source_url"]
        extra=f'<p>{t["source"]} (EN): <a rel="nofollow noopener" href="{e(d["source_url"])}" dir="ltr">{e(d["source_url"])}</a></p>' if lang=="ar" and d.get("source_url_ar") else ""
        b=f'''<p><a href="{p}/">{t["back_d"]}</a></p><h1>{e(dtitle(d,lang))}{pend}</h1><p><span class="tag" dir="ltr">{e(d["date"])}</span><span class="tag">{e(lc(d["country"],COUNTRY,lang))}</span><span class="tag">{e(lc(d["category"],CAT,lang))}</span></p>
<div class="grid"><div class="card"><b>{t["value"]}</b><br><span class="v">{e(val(d,lang))}</span></div><div class="card"><b>{t["parties"]}</b><br>{e(", ".join(d["parties"]) or t["seesrc"])}</div></div>
<p>{e(dsum(d,lang))}</p><p>{t["source"]}: <a rel="nofollow noopener" href="{e(su)}" dir="ltr">{e(su)}</a></p>{extra}{SP(lang)}{NL(lang)}'''
        ld=[{"@context":"https://schema.org","@type":"NewsArticle","headline":dtitle(d,lang)[:110],"inLanguage":lang,"datePublished":d["date"],"description":dsum(d,lang),"isBasedOn":d["source_url"],"publisher":ORG,"mainEntityOfPage":f"{B}{p}/deals/{d['slug']}/"},
            {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":t["deals"],"item":B+p+"/"},{"@type":"ListItem","position":2,"name":dtitle(d,lang)[:80],"item":f"{B}{p}/deals/{d['slug']}/"}]}]
        page(lang,f"/deals/{d['slug']}/",f"{dtitle(d,lang)} | {t['brand']}",dsum(d,lang)[:155],b,ld)
    # use cases
    utitle=lambda u:u.get("title_ar",u["title"]) if lang=="ar" else u["title"]
    usum=lambda u:u.get("summary_ar",u["summary"]) if lang=="ar" else u["summary"]
    cards="".join(f'<div class="card" data-k="{e(u["sector"])}"><span class="tag">{e(lc(u["sector"],SECTOR,lang))}</span><span class="tag">{e(lc(u["country"],COUNTRY,lang))}</span><h3><a href="{p}/use-cases/{u["slug"]}/">{e(utitle(u))}</a></h3><p>{e(usum(u))}</p></div>' for u in UC)
    b=f'<h1>{t["uc_h"]}</h1><p class="muted">{t["uc_intro"].format(n=len(UC))}</p><div class="f"><select id="k"><option value="">{t["all"]}</option>{opt({u["sector"] for u in UC},SECTOR)}</select><input id="q" placeholder="{t["search"]}"></div>{SP(lang)}<div id="list">{cards}</div>{NL(lang)}{FILTER_JS}'
    page(lang,"/use-cases/",f"{t['uc_h']} | {t['brand']}",t["uc_intro"].format(n=len(UC)),b,[{"@context":"https://schema.org","@type":"Dataset","name":t["uc_h"],"description":t["uc_intro"].format(n=len(UC)),"url":f"{B}{p}/use-cases/","inLanguage":lang,"creator":ORG,"license":f"{B}/about/","distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":f"{B}/api/use-cases.json"}]}])
    for u in UC:
        how=u.get("how_to_ar",u["how_to"]) if lang=="ar" else u["how_to"]
        steps=[x.strip() for x in re.split(r"\d\)\s*",how) if x.strip()]
        b=f'''<p><a href="{p}/use-cases/">{t["back_u"]}</a></p><h1>{e(utitle(u))}</h1><p><span class="tag">{e(lc(u["sector"],SECTOR,lang))}</span><span class="tag">{e(lc(u["country"],COUNTRY,lang))}</span><span class="tag">{e(u["tool"])}</span></p><p>{e(usum(u))}</p>
<div class="card"><h3>{t["howto"]}</h3><ol>{"".join(f"<li>{e(s)}</li>" for s in steps)}</ol><p class="muted">{t["howto_note"]}</p></div><p>{t["source"]}: <a rel="nofollow noopener" href="{e(u["source_url"])}" dir="ltr">{e(u["source_url"])}</a></p>{SP(lang)}{NL(lang)}'''
        ld=[{"@context":"https://schema.org","@type":"HowTo","name":utitle(u),"inLanguage":lang,"description":usum(u),"step":[{"@type":"HowToStep","position":i+1,"text":s} for i,s in enumerate(steps)],"isBasedOn":u["source_url"],"publisher":ORG}]
        page(lang,f"/use-cases/{u['slug']}/",f"{utitle(u)} | {t['brand']}",usum(u)[:155],b,ld)
    # tools
    tname=lambda x:x.get("name_ar",x["name"]) if lang=="ar" else x["name"]
    tdesc=lambda x:x.get("description_ar",x["description"]) if lang=="ar" else x["description"]
    tsup=lambda x:x.get("arabic_support_ar",x["arabic_support"]) if lang=="ar" else x["arabic_support"]
    CTA=f'<div class="sp">{t["cta_tool"]}</div>'
    cards="".join(f'<div class="card" data-k="{e(x["category"])}"><span class="tag">{e(lc(x["category"],TCAT,lang))}</span><span class="tag">{e(lc(x["pricing"],PRICE,lang))}</span><h3><a href="{p}/tools/{x["slug"]}/">{e(tname(x))}</a>{f" <span class=muted dir=ltr>({e(x["name"])})</span>" if lang=="ar" and tname(x)!=x["name"] else ""}</h3><p>{e(tdesc(x))}</p><p class="muted">{t["arsup"]}: {e(tsup(x))}</p></div>' for x in TL)
    b=f'<h1>{t["t_h"]}</h1><p class="muted">{t["t_intro"].format(n=len(TL))}</p>{CTA}<div class="f"><select id="k"><option value="">{t["all"]}</option>{opt({x["category"] for x in TL},TCAT)}</select><input id="q" placeholder="{t["search"]}"></div><div id="list">{cards}</div>{NL(lang)}{FILTER_JS}'
    page(lang,"/tools/",f"{t['t_h']} | {t['brand']}",t["t_intro"].format(n=len(TL)),b,[{"@context":"https://schema.org","@type":"Dataset","name":t["t_h"],"description":t["t_intro"].format(n=len(TL)),"url":f"{B}{p}/tools/","inLanguage":lang,"creator":ORG,"license":f"{B}/about/","distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":f"{B}/api/tools.json"}]}])
    for x in TL:
        b=f'''<p><a href="{p}/tools/">{t["back_t"]}</a></p><h1>{e(tname(x))}</h1>{f'<p class="muted" dir="ltr">{e(x["name"])}</p>' if lang=="ar" and tname(x)!=x["name"] else ""}<p><span class="tag">{e(lc(x["category"],TCAT,lang))}</span></p><p>{e(tdesc(x))}</p>
<div class="grid"><div class="card"><b>{t["arsup"]}</b><br>{e(tsup(x))}</div><div class="card"><b>{t["pricing"]}</b><br>{e(lc(x["pricing"],PRICE,lang))}</div><div class="card"><b>{t["website"]}</b><br><a rel="nofollow noopener" href="{e(x["url"])}" dir="ltr">{e(x["url"])}</a></div></div>
<p>{t["source"]}: <a rel="nofollow noopener" href="{e(x["source_url"])}" dir="ltr">{e(x["source_url"])}</a></p>{CTA}{NL(lang)}'''
        ld=[{"@context":"https://schema.org","@type":"SoftwareApplication","name":x["name"],"alternateName":x.get("name_ar"),"applicationCategory":x["category"],"description":tdesc(x),"url":x["url"],"inLanguage":"ar","isBasedOn":x["source_url"],"offers":{"@type":"Offer","description":x["pricing"]}}]
        page(lang,f"/tools/{x['slug']}/",f"{tname(x)} | {t['tools']} | {t['brand']}",tdesc(x)[:155],b,ld)
    # sponsor / about / agents
    sp="".join(f'<div class="card"{" id=featured" if i==2 else ""}><h3>{a}</h3><p class="v">{b_}</p><p>{c}</p></div>' for i,(a,b_,c) in enumerate([t["sp1"],t["sp2"],t["sp3"],t["sp4"]]))
    page(lang,"/sponsor/",f"{t['sponsor_h']}",t["sponsor_p"],f'<h1>{t["sponsor_h"]}</h1><p class="muted">{t["sponsor_p"]}</p><div class="grid">{sp}</div><p><button disabled>{t["soon"]}</button></p><p class="muted">{t["sp_note"]}</p>',[{"@context":"https://schema.org","@type":"WebPage","name":t["sponsor_h"],"inLanguage":lang,"publisher":ORG}])
    page(lang,"/about/",f"{t['about']} — {t['brand']}",t["about_p1"][:155],f'<h1>{t["about"]}</h1><p>{t["about_p1"]}</p><p>{t["about_p2"]}</p><p>{t["about_p3"]}</p>{NL(lang)}',[{"@context":"https://schema.org","@type":"AboutPage","name":t["about"],"inLanguage":lang,"publisher":ORG}])
    MCPJ=json.dumps({"mcpServers":{"gulfaideals":{"url":f"{B}/mcp"}}},indent=2)
    if lang=="ar":
        ag=f"""<h1>{t["ag_h"]}</h1><p>{t["ag_p"]}</p>
<div class="card"><h3>خادم MCP عن بُعد</h3><p>العنوان: <code>{B}/mcp</code> (Streamable HTTP، دون مصادقة). الأدوات: <code>search_deals</code> و<code>search_use_cases</code> و<code>search_tools</code> و<code>get_item</code>، وتعيد النتائج بالعربية والإنجليزية. الملف التعريفي: <a href="/.well-known/mcp.json">/.well-known/mcp.json</a></p></div>
<div class="card"><h3>Claude</h3><p>الإعدادات ← Connectors ← إضافة موصل مخصص ← الاسم <code>DealDune</code> والعنوان <code>{B}/mcp</code>. في Claude Code: <code>claude mcp add --transport http gulfaideals {B}/mcp</code></p></div>
<div class="card"><h3>ChatGPT</h3><p>الإعدادات ← Apps &amp; Connectors ← Advanced ← تفعيل Developer mode ← إنشاء موصل بعنوان خادم MCP <code>{B}/mcp</code> ودون مصادقة، ثم تفعيله في المحادثة.</p></div>
<div class="card"><h3>Cursor وWindsurf وVS Code وغيرها</h3><p>أضف إلى ملف إعدادات MCP:</p><pre>{e(MCPJ)}</pre><p>للعملاء الذين يدعمون stdio فقط: <code>npx mcp-remote {B}/mcp</code></p></div>
<div class="card"><h3>Gemini وGrok وPerplexity</h3><p>وجّه المساعد إلى <a href="/llms.txt">/llms.txt</a> أو <a href="/llms-full.txt">/llms-full.txt</a> أو استخدم واجهة JSON. جميع زواحف الذكاء الاصطناعي الرئيسية مسموح لها في robots.txt.</p></div>
<div class="card"><h3>واجهة JSON</h3><p dir="ltr"><a href="/api/deals.json">/api/deals.json</a> · <a href="/api/use-cases.json">/api/use-cases.json</a> · <a href="/api/tools.json">/api/tools.json</a> · <code>/api/{{deals|use-cases|tools}}/{{slug}}.json</code> · <a href="/openapi.json">OpenAPI</a></p></div>
<div class="card"><h3>اختبار عبر curl</h3><pre>curl -s {B}/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \\
  -d '{{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{{"name":"search_deals","arguments":{{"query":"هيوماين","limit":3}}}}}}'</pre></div>"""
    else:
        ag=f"""<h1>{t["ag_h"]}</h1><p>{t["ag_p"]}</p>
<div class="card"><h3>Remote MCP server</h3><p>Endpoint: <code>{B}/mcp</code> (Streamable HTTP, no auth). Tools: <code>search_deals</code>, <code>search_use_cases</code>, <code>search_tools</code>, <code>get_item</code> — results include Arabic and English fields. Manifest: <a href="/.well-known/mcp.json">/.well-known/mcp.json</a></p></div>
<div class="card"><h3>Claude (claude.ai / Desktop)</h3><p>Settings → Connectors → Add custom connector → Name <code>DealDune</code>, URL <code>{B}/mcp</code>. Claude Code: <code>claude mcp add --transport http gulfaideals {B}/mcp</code></p></div>
<div class="card"><h3>ChatGPT</h3><p>Settings → Apps &amp; Connectors → Advanced → enable Developer mode → Create connector → MCP server URL <code>{B}/mcp</code>, Authentication: none. Then enable it in a chat.</p></div>
<div class="card"><h3>Cursor / Windsurf / VS Code / other MCP clients</h3><p>Add to your client's MCP config (e.g. <code>~/.cursor/mcp.json</code>):</p><pre>{e(MCPJ)}</pre><p>For stdio-only clients: <code>npx mcp-remote {B}/mcp</code></p></div>
<div class="card"><h3>Gemini, Grok, Perplexity &amp; others</h3><p>Point the assistant at <a href="/llms.txt">/llms.txt</a> or <a href="/llms-full.txt">/llms-full.txt</a>, or use the JSON API. All major AI crawlers are allowed in robots.txt.</p></div>
<div class="card"><h3>JSON API</h3><p><a href="/api/deals.json">/api/deals.json</a> · <a href="/api/use-cases.json">/api/use-cases.json</a> · <a href="/api/tools.json">/api/tools.json</a> · per item: <code>/api/{{deals|use-cases|tools}}/{{slug}}.json</code> · <a href="/openapi.json">OpenAPI</a> · CORS enabled.</p></div>
<div class="card"><h3>Test with curl</h3><pre>curl -s {B}/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \\
  -d '{{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{{"name":"search_deals","arguments":{{"query":"HUMAIN","limit":3}}}}}}'</pre></div>"""
    page(lang,"/agents/",f"{t['agents']} — MCP & API | {t['brand']}",t["ag_p"][:155].replace("<code>","").replace("</code>",""),ag,[{"@context":"https://schema.org","@type":"TechArticle","name":t["ag_h"],"inLanguage":lang,"publisher":ORG}])
    # RSS
    def rfc(s):
        y,m,dd=(s.split("-")+["01","01"])[:3]; return datetime.datetime(int(y),int(m),int(dd)).strftime("%a, %d %b %Y 00:00:00 +0000")
    items="".join(f"<item><title>{e(dtitle(d,lang))}</title><link>{B}{p}/deals/{d['slug']}/</link><guid>{B}{p}/deals/{d['slug']}/</guid><pubDate>{rfc(d['date'])}</pubDate><description>{e(dsum(d,lang))}</description></item>" for d in D[:60])
    items+="".join(f"<item><title>{e(('حالة استخدام: ' if lang=='ar' else 'Use case: ')+utitle(u))}</title><link>{B}{p}/use-cases/{u['slug']}/</link><guid>{B}{p}/use-cases/{u['slug']}/</guid><description>{e(usum(u))}</description></item>" for u in UC)
    items+="".join(f"<item><title>{e(('أداة: ' if lang=='ar' else 'Tool: ')+tname(x))}</title><link>{B}{p}/tools/{x['slug']}/</link><guid>{B}{p}/tools/{x['slug']}/</guid><description>{e(tdesc(x))}</description></item>" for x in TL)
    os.makedirs(f"{out}{p}",exist_ok=True)
    open(f"{out}{p}/rss.xml","w").write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{e(t["brand"])} — {e(t["tag"])}</title><link>{B}{p}/</link><language>{lang}</language><description>{e(t["tag"])}</description>{items}</channel></rss>')
exec(open(f"{root}/scripts/hub_pages.py").read())
sm=''.join(f'<url><loc>{B}{p}{u}</loc><xhtml:link rel="alternate" hreflang="ar" href="{B}{u}"/><xhtml:link rel="alternate" hreflang="en" href="{B}/en{u}"/><xhtml:link rel="alternate" hreflang="x-default" href="{B}{u}"/></url>' for u in URLS for p in ("","/en"))
open(f"{out}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+sm+"</urlset>")
print("built",len(D),"deals,",len(UC),"use cases,",len(TL),"tools x2 languages ->",out,flush=True)
subprocess.run([sys.executable,f"{root}/scripts/agents.py"],check=True)
