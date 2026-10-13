# Executed inside build.py (shares its globals: D, UC, TL, T, P, page, e, B, out, ORG, val, dtitle, dsum, lc, COUNTRY, CAT, SECTOR, NL, SP, URLS)
# Adds: legal pages, 404, FII10 tracker, Gulf AI Index + widget, badges, company/country/sector hubs, FAQ/Dataset markup, A2A card.
import datetime as _dt
TODAY=_dt.date.today().isoformat()
FX={"USD":1.0,"AED":1/3.6725,"SAR":1/3.75,"QAR":1/3.64}
def usd(d): return (d.get("value") or 0)*FX.get(d.get("currency") or "USD",0) if d.get("value") else 0
def money(v,lang):
    if lang=="en": return f"${v/1e9:,.1f}bn" if v>=1e9 else f"${v/1e6:,.0f}m"
    return (f"{v/1e9:,.1f}".rstrip("0").rstrip(".")+" مليار دولار") if v>=1e9 else (f"{v/1e6:,.0f} مليون دولار")
def slugify(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
ALIAS={"G42 / Khazna":["G42","Khazna"],"stc / center3":["stc","center3"],"Qai (QIA)":["QIA"],"NEOM / Oxagon":["NEOM"]}
SKIP={"UAE Government","US Government","US Department of Commerce"}
ENT_AR={"HUMAIN":"هيوماين","NVIDIA":"إنفيديا","G42":"جي42","AWS":"أمازون ويب سيرفيسز","MGX":"إم جي إكس","Oracle":"أوراكل","DataVolt":"داتافولت","BlackRock GIP":"جي آي بي (بلاك روك)","Aligned Data Centers":"ألايند داتا سنترز","Cerebras":"سيريبراس","center3":"سنتر3","Microsoft":"مايكروسوفت","OpenAI":"أوبن إيه آي","SoftBank":"سوفت بنك","PIF":"صندوق الاستثمارات العامة","AMD":"إيه إم دي","SDAIA":"سدايا","Aramco Digital":"أرامكو الرقمية","Khazna":"خزنة","stc":"stc","QIA":"جهاز قطر للاستثمار","AI Infrastructure Partnership":"شراكة البنية التحتية للذكاء الاصطناعي","Qualcomm":"كوالكوم","xAI":"إكس إيه آي","Elm":"علم","NEOM":"نيوم","Kuwait Investment Authority":"الهيئة العامة للاستثمار الكويتية","Brookfield":"بروكفيلد","Blackstone":"بلاكستون","AirTrunk":"إير ترانك","Cisco":"سيسكو","Napster":"نابستر","Stargate UAE":"ستارغيت الإمارات"}
def ents(d):
    r=[]
    for p_ in d["parties"]:
        for x in ALIAS.get(p_,[p_]):
            if x not in SKIP and x not in r: r.append(x)
    return r
def ename(x,lang): return ENT_AR.get(x,x) if lang=="ar" else x
AR_DIGITS=lambda s:s
# ---------- index (dedupe: records flagged same_transaction_as count only additional_commitment)
def idx_value(d):
    if d.get("same_transaction_as"): return (d.get("additional_commitment") or 0)*FX.get(d.get("currency") or "USD",1)
    return usd(d)+((d.get("additional_commitment") or 0) if not d.get("same_transaction_as") else 0)
by_country={}; by_company={}
for d in D:
    v=idx_value(d); c=by_country.setdefault(d["country"],{"value":0,"deals":0,"disclosed":0})
    c["deals"]+=1; c["value"]+=v; c["disclosed"]+=1 if v else 0
    for x in ents(d):
        k=by_company.setdefault(x,{"value":0,"deals":0}); k["deals"]+=1; k["value"]+=v
IDX_C=sorted(by_country.items(),key=lambda kv:-kv[1]["value"]); IDX_K=sorted([kv for kv in by_company.items() if kv[1]["value"]>0],key=lambda kv:-kv[1]["value"])[:12]
TOTAL=sum(v["value"] for _,v in IDX_C)
def chart(rows,lang,name=lambda k,l:k):
    mx=max([r[1]["value"] for r in rows] or [1]) or 1; h=34*len(rows)+10; W=640; lab=200; rtl=lang=="ar"
    bars=[]
    for i,(k,v) in enumerate(rows):
        w=max(2,(W-lab-130)*v["value"]/mx); y=10+i*34
        if rtl:
            bars.append(f'<text x="{W-6}" y="{y+18}" text-anchor="end" fill="#e6e9f2" font-size="14">{e(name(k,lang))}</text><rect x="{W-lab-w}" y="{y+4}" width="{w:.0f}" height="20" rx="4" fill="#f5b942"/><text x="{W-lab-w-6}" y="{y+19}" text-anchor="end" fill="#e6e9f2" font-size="13">{e(money(v["value"],lang))}</text>')
        else:
            bars.append(f'<text x="6" y="{y+18}" fill="#e6e9f2" font-size="14">{e(name(k,lang))}</text><rect x="{lab}" y="{y+4}" width="{w:.0f}" height="20" rx="4" fill="#f5b942"/><text x="{lab+w+6}" y="{y+19}" fill="#e6e9f2" font-size="13">{e(money(v["value"],lang))}</text>')
    return f'<svg direction="ltr" role="img" viewBox="0 0 {W} {h}" width="100%" style="max-width:{W}px;font-family:\'IBM Plex Sans Arabic\',system-ui,sans-serif" xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>'
cname=lambda k,lang:lc(k,COUNTRY,lang)
L={"ar":dict(idx="مؤشر الذكاء الاصطناعي الخليجي",idx_sub="الإنفاق المُعلن على الذكاء الاصطناعي حسب الدولة والشركة — الإصدار 1",bycountry="حسب الدولة",bycompany="حسب الشركة (أكبر 12)",method="المنهجية",embed="تضمين المؤشر في موقعك",faq="أسئلة شائعة",
  meth=["يجمع المؤشر القيم المُعلنة فقط للصفقات المنشورة في قاعدة بياناتنا، وكل صفقة مرتبطة بمصدرها المنشور.","لا نقدّر القيم غير المُفصح عنها؛ تُحتسب هذه الصفقات في العدد دون القيمة.","تُحوَّل المبالغ إلى الدولار بأسعار الربط الرسمية (الدرهم 3.6725، الريال 3.75).","تُحتسب الصفقة الواحدة مرة واحدة: إتمام صفقة سبق الإعلان عنها لا يُضاف مجدداً، ويُضاف فقط أي التزام جديد معلن عند الإتمام.","في ترتيب الشركات تُنسب قيمة الصفقة كاملة لكل طرف مسمّى فيها، لذا لا يمكن جمع أرقام الشركات.","تُنسب كل صفقة إلى الدولة الخليجية المعنية بها، بما في ذلك استثمارات المستثمرين الخليجيين في الخارج (مثل استحواذ «ألايند» في الولايات المتحدة).","القيم المُعلنة تشمل تعهدات وخططاً متعددة السنوات وليست إنفاقاً فعلياً مؤكداً."],
  companies="الشركات",countries="الدول",sectors="القطاعات",records="سجلاً موثّقاً",deals_h="الصفقات",uc_h="حالات الاستخدام",badge_h="شارة «مُدرج في Gulf AI Deals»",badge_p="إن كانت شركتك مدرجة، يمكنك عرض الشارة على موقعك بنسخ الكود التالي:",
  hub_ans="حتى {d}، يرصد ديل ديون {n} {rec} عن {x}: {nd} صفقة ({nv} منها بقيمة مُعلنة إجماليها {tv}) و{nu} حالة استخدام. أحدث سجل: «{lt}» ({ld}).",
  q_total="ما إجمالي الإنفاق المُعلن على الذكاء الاصطناعي في الخليج؟",a_total="يبلغ إجمالي القيم المُعلنة في {n} صفقة نرصدها نحو {t}، منها {sa} في السعودية و{ae} في الإمارات (حتى {d}). القيم تعهدات مُعلنة وليست إنفاقاً فعلياً.",
  q_big="ما أكبر صفقة ذكاء اصطناعي مرصودة في الخليج؟",a_big="أكبر صفقة بقيمة مُعلنة في بياناتنا هي «{t}» بقيمة {v} ({d}).",
  q_x="ما أبرز صفقات {x} في الذكاء الاصطناعي؟",q_xn="كم عدد سجلات {x} لدى ديل ديون؟",a_xn="{n} سجلات موثّقة، لكل منها رابط للمصدر.",q_src="هل البيانات موثّقة؟",a_src="نعم، كل سجل مرتبط بمصدر منشور، ولا نقدّر القيم غير المُفصح عنها. البيانات متاحة عبر واجهة JSON وخادم MCP.",
  all_c="كل الشركات",all_k="كل الدول",all_s="كل القطاعات",nf="الصفحة غير موجودة",nf_p="عذراً، لم نعثر على هذه الصفحة. جرّب:",legal_upd="آخر تحديث: 13 أكتوبر 2026",
  fii="متتبع صفقات FII10 المباشر",fii_sub="صفقات الذكاء الاصطناعي ومراكز البيانات المُعلنة خلال مبادرة مستقبل الاستثمار، الرياض 26–29 أكتوبر 2026",fii_pre="ما قبل الحدث",fii_live="مباشر الآن",fii_post="انتهى الحدث",fii_ctx="خلفية قبل الحدث",fii_deals="الصفقات المُعلنة خلال FII10",fii_empty="لم تُرصد صفقات بعد. تُحدَّث الصفحة تلقائياً يومياً، وكل ساعة خلال أيام الحدث، ولا تُنشر إلا الصفقات ذات المصادر الموثوقة.",fii_prev="سياق: صفقات سعودية للذكاء الاصطناعي في أسبوع النسخة السابقة (أكتوبر 2025)",fii_sa="إجمالي ما نرصده من صفقات سعودية للذكاء الاصطناعي: {n} صفقة، بقيم مُعلنة تقارب {v}.",upd="آخر تحديث"),
 "en":dict(idx="Gulf AI Index",idx_sub="Announced AI spend by country and company — v1",bycountry="By country",bycompany="By company (top 12)",method="Methodology",embed="Embed the Index on your site",faq="FAQ",
  meth=["The Index sums only disclosed values of published deals in our dataset; every deal links to its published source.","We never estimate undisclosed values; such deals count toward deal counts, not value.","Amounts are converted to USD at official pegs (AED 3.6725, SAR 3.75).","Each transaction is counted once: the closing of a previously announced deal is not re-added; only any new commitment announced at closing is added.","In the company ranking the full deal value is attributed to every named party, so company figures are not additive.","Each deal is attributed to the Gulf country it concerns, including outbound investments by Gulf investors (e.g. the US Aligned acquisition).","Announced values include pledges and multi-year plans, not confirmed spend."],
  companies="Companies",countries="Countries",sectors="Sectors",records="sourced records",deals_h="Deals",uc_h="Use cases",badge_h="“Featured on Gulf AI Deals” badge",badge_p="If your company is listed, show the badge on your site with this code:",
  hub_ans="As of {d}, DealDune tracks {n} {rec} on {x}: {nd} deals ({nv} with disclosed value totalling {tv}) and {nu} use cases. Latest: “{lt}” ({ld}).",
  q_total="How much AI spending has been announced in the Gulf?",a_total="Disclosed values across the {n} deals we track total about {t}, including {sa} in Saudi Arabia and {ae} in the UAE (as of {d}). These are announced commitments, not confirmed spend.",
  q_big="What is the largest Gulf AI deal tracked?",a_big="The largest deal with a disclosed value in our data is “{t}” at {v} ({d}).",
  q_x="What are {x}'s main AI deals?",q_xn="How many {x} records does DealDune have?",a_xn="{n} sourced records, each linked to its source.",q_src="Is the data sourced?",a_src="Yes. Every record links to a published source and undisclosed values are never estimated. Data is available via JSON API and MCP.",
  all_c="All companies",all_k="All countries",all_s="All sectors",nf="Page not found",nf_p="Sorry, we couldn't find that page. Try:",legal_upd="Last updated: 13 October 2026",
  fii="FII10 Live Deal Tracker",fii_sub="AI and data-center deals announced at the Future Investment Initiative, Riyadh, 26–29 October 2026",fii_pre="Pre-event",fii_live="Live now",fii_post="Event ended",fii_ctx="Pre-event context",fii_deals="Deals announced at FII10",fii_empty="No deals recorded yet. This page updates automatically daily, and hourly during the event; only deals with credible sources are published.",fii_prev="Context: Saudi AI deals dated during last year's FII week (October 2025)",fii_sa="Saudi AI deals tracked to date: {n}, with disclosed values of about {v}.",upd="Updated")}
def faq_html(qa,lang): return f'<h2>{L[lang]["faq"]}</h2>'+"".join(f'<details class="card"><summary><b>{e(q)}</b></summary><p>{e(a)}</p></details>' for q,a in qa)
def faq_ld(qa,lang): return {"@context":"https://schema.org","@type":"FAQPage","inLanguage":lang,"mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa]}
def dataset_ld(name,desc,url,lang,kw=None): return {"@context":"https://schema.org","@type":"Dataset","name":name,"description":desc,"url":url,"inLanguage":lang,"creator":ORG,"license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":True,"dateModified":TODAY,"spatialCoverage":"Gulf Cooperation Council","keywords":kw or [],"distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":f"{B}/api/deals.json"}]}
def mini(d,lang,p): return f'<div class="card"><span class="tag" dir="ltr">{e(d["date"])}</span><span class="tag">{e(lc(d["country"],COUNTRY,lang))}</span><span class="v">{e(val(d,lang))}</span><h3><a href="{p}/deals/{d["slug"]}/">{e(dtitle(d,lang))}</a></h3></div>'
def umini(u,lang,p): return f'<div class="card"><span class="tag">{e(lc(u["sector"],SECTOR,lang))}</span><h3><a href="{p}/use-cases/{u["slug"]}/">{e(u.get("title_ar",u["title"]) if lang=="ar" else u["title"])}</a></h3></div>'
BADGE_EMBED=lambda lang,rel:f'<a href="{B}{"" if lang=="ar" else "/en"}{rel}"><img src="{B}/badge/featured-{lang}.svg" alt="{"مُدرج في Gulf AI Deals" if lang=="ar" else "Featured on Gulf AI Deals"}" width="240" height="56"></a>'
# hubs
COMP={}
for d in D:
    for x in ents(d): COMP.setdefault(x,{"d":[],"u":[]})["d"].append(d)
COUNT={}
for d in D: COUNT.setdefault(d["country"],{"d":[],"u":[]})["d"].append(d)
for u in UC: COUNT.setdefault(u["country"],{"d":[],"u":[]})["u"].append(u)
SECT={}
for d in D: SECT.setdefault(("cat",d["category"]),{"d":[],"u":[]})["d"].append(d)
for u in UC: SECT.setdefault(("sec",u["sector"]),{"d":[],"u":[]})["u"].append(u)
n_of=lambda r:len(r["d"])+len(r["u"])
COMP={k:v for k,v in COMP.items() if n_of(v)>=2}; COUNT={k:v for k,v in COUNT.items() if n_of(v)>=2}; SECT={k:v for k,v in SECT.items() if n_of(v)>=2}
sname=lambda k,lang:(lc(k[1],CAT,lang) if k[0]=="cat" else lc(k[1],SECTOR,lang))
HUBS={"companies":(COMP,lambda k,l:ename(k,l),lambda k:slugify(k)),"countries":(COUNT,cname,lambda k:slugify(k)),"sectors":(SECT,sname,lambda k:slugify(k[1]))}
HUB_INDEX=[]
for lang in ("ar","en"):
    t=T[lang]; l=L[lang]; p=P(lang)
    # ---- legal + support
    priv={"ar":["ديل ديون (gulfaideals.com) مركز معلومات مجاني للاطلاع فقط، ولا يتطلب إنشاء حسابات.","<b>النشرة البريدية:</b> إذا اشتركت فإننا نحفظ بريدك الإلكتروني وتاريخ الاشتراك وصفحة التسجيل ولغتها فقط، لإرسال النشرة إليك. لا نبيع البيانات ولا نشاركها. لإلغاء الاشتراك أو حذف بريدك راسلنا على العنوان أدناه.","<b>خادم MCP والواجهة البرمجية والإضافات</b> (/mcp و/openapi.json): تُعالج الاستعلامات فقط لإرجاع النتائج، ولا نخزّن محتواها مرتبطاً بأي شخص. قد يعالج مزوّد الاستضافة (Cloudflare) سجلات الطلبات القياسية (عنوان IP والتوقيت ونوع المتصفح) لأغراض الأمان والموثوقية وفق سياسته.","<b>ملفات تعريف الارتباط:</b> لا نستخدمها للتتبع أو الإعلانات.","<b>الأطراف الثالثة:</b> تحيل النتائج إلى مصادر خارجية منشورة، وتسري سياساتها عند زيارتها.","<b>الأطفال:</b> الموقع غير موجّه لمن هم دون 13 عاماً.","تُنشر أي تغييرات على هذه الصفحة. للتواصل: <a href=\"mailto:gulfaideals@mail.grokbot.com\">gulfaideals@mail.grokbot.com</a>"],
          "en":["Gulf AI Deals (gulfaideals.com) is a free, read-only information hub. No accounts are required.","<b>Newsletter:</b> if you subscribe, we store only your email address, signup date, signup page and language, to send you the newsletter. We do not sell or share it. To unsubscribe or have your email deleted, email us at the address below.","<b>MCP server, API and plugins</b> (/mcp, /openapi.json): search queries are processed only to return results. We do not store query content linked to any person. Our host (Cloudflare) may process standard request logs (IP address, timestamp, user agent) for security and reliability under its own privacy policy.","<b>Cookies:</b> none for tracking or advertising.","<b>Third parties:</b> results link to public external sources; their policies apply when you visit them.","<b>Children:</b> not directed at children under 13.","Changes will be posted on this page. Contact: <a href=\"mailto:gulfaideals@mail.grokbot.com\">gulfaideals@mail.grokbot.com</a>"]}
    terms={"ar":["<b>الخدمة:</b> يقدّم gulfaideals.com وواجهته البرمجية (/openapi.json) وخادم MCP (/mcp) معلومات مجانية للاطلاع فقط عن صفقات الذكاء الاصطناعي وحالات استخدامه وأدواته في دول الخليج.","<b>ليست نصيحة:</b> المحتوى للمعلومات فقط وليس نصيحة استثمارية أو قانونية أو مالية. تحقّق من المعلومات عبر المصادر المرفقة.","<b>الدقة:</b> نربط كل سجل بمصدر منشور ولا نقدّر القيم غير المُفصح عنها، لكننا لا نضمن اكتمال المعلومات أو دقتها.","<b>الترخيص:</b> البيانات مرخّصة بموجب CC BY 4.0 (مع الإشارة إلى «Gulf AI Deals, gulfaideals.com»)، والشيفرة البرمجية بموجب MIT. المحتوى الخارجي ملك لأصحابه.","<b>الاستخدام المقبول:</b> لا تُثقل الخدمة ولا تحاول الوصول غير المصرّح به ولا تحرّف بياناتنا. قد نحدّ من معدل الوصول الآلي.","<b>المحتوى الممول</b> يُوسَم دائماً بعبارة «ممول» ولا يغيّر البيانات.","<b>المسؤولية:</b> تُقدَّم الخدمة «كما هي» دون ضمانات، في الحدود التي يسمح بها القانون.","تُنشر أي تعديلات على هذه الشروط في هذه الصفحة. للتواصل: <a href=\"mailto:gulfaideals@mail.grokbot.com\">gulfaideals@mail.grokbot.com</a>"],
           "en":["<b>Service.</b> gulfaideals.com, its API (/openapi.json) and MCP server (/mcp) provide free, read-only information about AI deals, use cases and tools in the GCC.","<b>No advice.</b> Content is for information only and is not investment, legal or financial advice. Verify facts against the linked sources.","<b>Accuracy.</b> We link every record to a published source and do not estimate undisclosed values, but we cannot guarantee completeness or accuracy.","<b>License.</b> Data is licensed CC BY 4.0 (attribute “Gulf AI Deals, gulfaideals.com”). Code is MIT. Third-party content belongs to its owners.","<b>Acceptable use.</b> Do not overload the service, attempt unauthorized access, or misrepresent our data. We may rate-limit automated access.","<b>Sponsored content</b> is always labelled “Sponsored” and never changes the data.","<b>Liability.</b> The service is provided “as is”, without warranties, to the extent permitted by law.","Changes to these terms are posted on this page. Contact: <a href=\"mailto:gulfaideals@mail.grokbot.com\">gulfaideals@mail.grokbot.com</a>"]}
    sup={"ar":["<b>البريد الإلكتروني:</b> <a href=\"mailto:gulfaideals@mail.grokbot.com\">gulfaideals@mail.grokbot.com</a> (نرد خلال 3 أيام عمل)","<b>الإبلاغ عن خطأ أو إضافة صفقة:</b> راسلنا مع رابط المصدر.","<b>خادم MCP:</b> <code>https://gulfaideals.com/mcp</code> — أدلة الإعداد: <a href=\"https://github.com/gulfaideals/gulf-ai-hub-mcp\">github.com/gulfaideals/gulf-ai-hub-mcp</a>","<b>الأعطال وطلبات الميزات:</b> <a href=\"https://github.com/gulfaideals/gulf-ai-hub-mcp/issues\">GitHub Issues</a>"],
         "en":["<b>Email:</b> <a href=\"mailto:gulfaideals@mail.grokbot.com\">gulfaideals@mail.grokbot.com</a> (reply within 3 business days)","<b>Report a data error or submit a deal:</b> email us with the source link.","<b>MCP server:</b> <code>https://gulfaideals.com/mcp</code> — setup guides: <a href=\"https://github.com/gulfaideals/gulf-ai-hub-mcp\">github.com/gulfaideals/gulf-ai-hub-mcp</a>","<b>Bugs and feature requests:</b> <a href=\"https://github.com/gulfaideals/gulf-ai-hub-mcp/issues\">GitHub Issues</a>"]}
    for rel,h,items in [("/privacy/","سياسة الخصوصية" if lang=="ar" else "Privacy Policy",priv[lang]),("/terms/","شروط الاستخدام" if lang=="ar" else "Terms of Use",terms[lang]),("/support/","الدعم والتواصل" if lang=="ar" else "Support",sup[lang])]:
        page(lang,rel,f"{h} | {t['brand']}",re.sub("<[^>]+>","",items[0])[:155],f'<h1>{h}</h1><p class="muted">{l["legal_upd"]}</p>'+"".join(f"<p>{x}</p>" for x in items),[{"@context":"https://schema.org","@type":"WebPage","name":h,"inLanguage":lang,"publisher":ORG}])
    # ---- 404 (written directly; not in sitemap)
    nf=f'<!doctype html><html lang="{lang}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>404 — {l["nf"]}</title>{FONT}<style>{CSS}</style></head><body><main><h1>404 — {l["nf"]}</h1><p>{l["nf_p"]}</p><p><a href="{p}/">{t["deals"]}</a> · <a href="{p}/gulf-ai-index/">{l["idx"]}</a> · <a href="{p}/use-cases/">{t["uc"]}</a> · <a href="{p}/tools/">{t["tools"]}</a> · <a href="{P("en" if lang=="ar" else "ar")}/">{t["switch"]}</a></p></main></body></html>'
    open(f"{out}{p}/404.html","w").write(nf)
    # ---- Gulf AI Index
    sa=by_country.get("Saudi Arabia",{"value":0})["value"]; ae=by_country.get("UAE",{"value":0})["value"]
    big=max(D,key=idx_value)
    qa=[(l["q_total"],l["a_total"].format(n=len(D),t=money(TOTAL,lang),sa=money(sa,lang),ae=money(ae,lang),d=TODAY)),(l["q_big"],l["a_big"].format(t=dtitle(big,lang),v=val(big,lang),d=big["date"])),(l["q_src"],l["a_src"])]
    rows_c="".join(f'<tr><td>{(f'<a href="{p}/countries/{slugify(k)}/">'+e(cname(k,lang))+'</a>') if k in COUNT else e(cname(k,lang))}</td><td>{v["deals"]}</td><td>{v["disclosed"]}</td><td class="v">{e(money(v["value"],lang)) if v["value"] else "—"}</td></tr>' for k,v in IDX_C)
    th=("الدولة","الصفقات","بقيمة مُعلنة","القيمة المُعلنة") if lang=="ar" else ("Country","Deals","With disclosed value","Announced value")
    emb_iframe=f'<iframe src="{B}{p}/embed/gulf-ai-index/" width="100%" height="420" style="border:0;max-width:680px" loading="lazy" title="{l["idx"]}"></iframe>'
    emb_js=f'<div data-gulfaideals-index data-lang="{lang}"></div><script async src="{B}/widget.js"></script>'
    body=f'''<h1>{l["idx"]}</h1><p class="muted">{l["idx_sub"]} · {l["upd"]} {TODAY}</p>
<p class="card"><b>{e(qa[0][1])}</b></p>
<h2>{l["bycountry"]}</h2>{chart(IDX_C,lang,cname)}<table class="card" style="width:100%"><tr>{"".join(f"<th>{x}</th>" for x in th)}</tr>{rows_c}</table>
<h2>{l["bycompany"]}</h2>{chart(IDX_K,lang,ename)}
<h2>{l["method"]}</h2><ol>{"".join(f"<li>{x}</li>" for x in l["meth"])}</ol><p class="muted">JSON: <a href="/api/gulf-ai-index.json">/api/gulf-ai-index.json</a></p>
<h2>{l["embed"]}</h2><p>iframe:</p><pre>{e(emb_iframe)}</pre><p>JavaScript:</p><pre>{e(emb_js)}</pre>{faq_html(qa,lang)}{NL(lang)}'''
    page(lang,"/gulf-ai-index/",f"{l['idx']} — {l['idx_sub']} | {t['brand']}",qa[0][1][:155],body,[dataset_ld(l["idx"],l["idx_sub"]+". "+qa[0][1],f"{B}{p}/gulf-ai-index/",lang,["AI","GCC","data centers","sovereign AI"]),faq_ld(qa,lang)])
    os.makedirs(f"{out}{p}/embed/gulf-ai-index",exist_ok=True)
    open(f"{out}{p}/embed/gulf-ai-index/index.html","w").write(f'<!doctype html><html lang="{lang}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><link rel="canonical" href="{B}{p}/gulf-ai-index/"><title>{l["idx"]}</title>{FONT}<style>{CSS} body{{padding:12px}}</style></head><body><b>{l["idx"]}</b> <span class="muted">{l["bycountry"]} · {TODAY}</span>{chart(IDX_C,lang,cname)}<p class="muted" style="font-size:13px">{"المصدر" if lang=="ar" else "Source"}: <a target="_blank" rel="noopener" href="{B}{p}/gulf-ai-index/">{"ديل ديون — gulfaideals.com" if lang=="ar" else "DealDune — gulfaideals.com"}</a></p></body></html>')
    # ---- FII10
    F=json.load(open(f"{root}/data/fii10.json"))
    now=TODAY; status=l["fii_pre"] if now<F["start"] else (l["fii_live"] if now<=F["end"] else l["fii_post"])
    fd=[d for d in D if "fii10" in d.get("tags",[]) or d["id"] in F["manual_deal_ids"] or (d["country"]=="Saudi Arabia" and F["start"]<=d["date"]<=F["end"])]
    prev=[d for d in D if d["country"]=="Saudi Arabia" and "2025-10-27"<=d["date"]<="2025-10-30"]
    sad=[d for d in D if d["country"]=="Saudi Arabia"]; sav=sum(idx_value(d) for d in sad)
    days=(_dt.date.fromisoformat(F["start"])-_dt.date.today()).days
    cd=(f"يتبقى {days} يوماً على انطلاق الحدث." if lang=="ar" else f"{days} days to go.") if days>0 else ""
    body=f'''<h1>{l["fii"]}</h1><p class="muted">{l["fii_sub"]}</p><p><span class="tag">{status}</span> {cd} <span class="muted">{l["upd"]} {TODAY}</span></p>
<h2>{l["fii_deals"]} ({len(fd)})</h2>{"".join(mini(d,lang,p) for d in sorted(fd,key=lambda x:x["date"],reverse=True)) or f'<p class="card">{l["fii_empty"]}</p>'}
<h2>{l["fii_ctx"]}</h2><ul>{"".join(f'<li>{e(x[lang])} <a rel="nofollow noopener" href="{e(x["source_url"])}">[{"المصدر" if lang=="ar" else "source"}]</a></li>' for x in F["facts"])}<li>{e(l["fii_sa"].format(n=len(sad),v=money(sav,lang)))} <a href="{p}/countries/saudi-arabia/">→</a></li></ul>
<h3>{l["fii_prev"]}</h3>{"".join(mini(d,lang,p) for d in prev)}<p class="muted">JSON: <a href="/api/fii10.json">/api/fii10.json</a> · RSS: <a href="{p}/rss.xml">{p}/rss.xml</a></p>{NL(lang)}'''
    ev={"@context":"https://schema.org","@type":"Event","name":F["event_ar"] if lang=="ar" else F["event"],"startDate":F["start"],"endDate":F["end"],"eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode","location":{"@type":"Place","name":F["venue_ar"] if lang=="ar" else F["venue"],"address":{"@type":"PostalAddress","addressLocality":"Riyadh","addressCountry":"SA"}},"organizer":{"@type":"Organization","name":"FII Institute","url":"https://fii-institute.org/"},"url":F["source_url"]}
    page(lang,"/fii10/",f"{l['fii']} | {t['brand']}",l["fii_sub"],body,[ev,dataset_ld(l["fii"],l["fii_sub"],f"{B}{p}/fii10/",lang,["FII10","Riyadh","AI deals"])])
    if lang=="en":
        os.makedirs(f"{out}/api",exist_ok=True)
        json.dump({"event":F,"status":"pre-event" if now<F["start"] else ("live" if now<=F["end"] else "ended"),"updated":TODAY,"deals":fd,"context_previous_edition":prev},open(f"{out}/api/fii10.json","w"),ensure_ascii=False,indent=1)
        json.dump({"version":"1","updated":TODAY,"total_announced_usd":TOTAL,"by_country":[{"country":k,**v} for k,v in IDX_C],"by_company_top":[{"company":k,**v} for k,v in IDX_K],"methodology":L["en"]["meth"]},open(f"{out}/api/gulf-ai-index.json","w"),ensure_ascii=False,indent=1)
    # ---- hubs
    for hub,(M,nm,sl) in HUBS.items():
        hl=l[hub]; cards=[]
        for k,r in sorted(M.items(),key=lambda kv:-n_of(kv[1])):
            rel=f"/{hub}/{sl(k)}/"; x=nm(k,lang); ds=sorted(r["d"],key=lambda z:z["date"],reverse=True); us=r["u"]
            dv=[z for z in ds if idx_value(z)]; tv=sum(idx_value(z) for z in dv)
            latest=(ds[0] if ds else None)
            ans=l["hub_ans"].format(d=TODAY,n=n_of(r),rec=l["records"],x=x,nd=len(ds),nv=len(dv),tv=money(tv,lang) if tv else ("—"),nu=len(us),lt=dtitle(latest,lang) if latest else (us[0].get("title_ar",us[0]["title"]) if lang=="ar" else us[0]["title"]),ld=latest["date"] if latest else "")
            qa=[(l["q_xn"].format(x=x),l["a_xn"].format(n=n_of(r))),(l["q_src"],l["a_src"])]
            if ds: qa.insert(0,(l["q_x"].format(x=x),"؛ ".join(f"{dtitle(z,lang)} ({z['date']})" for z in ds[:3]) if lang=="ar" else "; ".join(f"{dtitle(z,lang)} ({z['date']})" for z in ds[:3])))
            badge=f'<h2>{l["badge_h"]}</h2><p>{BADGE_EMBED(lang,rel)}</p><p>{l["badge_p"]}</p><pre>{e(BADGE_EMBED(lang,rel))}</pre>' if hub=="companies" else ""
            body=f'''<p><a href="{p}/{hub}/">{hl}</a></p><h1>{e(x)}</h1><p class="card"><b>{e(ans)}</b></p>{f"<h2>{l['deals_h']} ({len(ds)})</h2>"+"".join(mini(z,lang,p) for z in ds) if ds else ""}{f"<h2>{l['uc_h']} ({len(us)})</h2>"+"".join(umini(u,lang,p) for u in us) if us else ""}{faq_html(qa,lang)}{badge}{NL(lang)}'''
            page(lang,rel,f"{x} — {'صفقات الذكاء الاصطناعي' if lang=='ar' else 'AI deals & use cases'} | {t['brand']}",ans[:155],body,[dataset_ld(f"{x} — {t['brand']}",ans,f"{B}{p}{rel}",lang,[x]),faq_ld(qa,lang)])
            cards.append(f'<div class="card"><h3><a href="{p}{rel}">{e(x)}</a></h3><span class="muted">{n_of(r)} {l["records"]}</span></div>')
            if lang=="ar": HUB_INDEX.append(rel)
        page(lang,f"/{hub}/",f"{hl} | {t['brand']}",hl,f'<h1>{hl}</h1><p class="muted">{"صفحات لكل كيان لديه سجلان موثّقان على الأقل." if lang=="ar" else "One page per entity with at least two sourced records."}</p><div class="grid">{"".join(cards)}</div>',[{"@context":"https://schema.org","@type":"CollectionPage","name":hl,"inLanguage":lang,"publisher":ORG}])
# badges, widget, A2A card
for lang,txt,sub in [("ar","مُدرج في","Gulf AI Deals"),("en","FEATURED ON","Gulf AI Deals")]:
    anchor,xx=("end",228) if lang=="ar" else ("start",56)
    open(f"{out}/badge/featured-{lang}.svg" if os.path.isdir(f"{out}/badge") else (os.makedirs(f"{out}/badge") or f"{out}/badge/featured-{lang}.svg"),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="240" height="56" viewBox="0 0 240 56" role="img" aria-label="{txt} {sub}"><title>{txt} {sub}</title><rect x="1" y="1" width="238" height="54" rx="10" fill="#0b1020" stroke="#f5b942" stroke-width="2"/><g transform="translate({"196" if lang=="ar" else "12"},12)"><rect width="32" height="32" rx="7" fill="#f5b942"/><text x="16" y="22" font-size="15" font-weight="700" text-anchor="middle" fill="#0b1020" font-family="Arial,sans-serif">GA</text></g><text x="{186 if lang=="ar" else 54}" y="24" text-anchor="{anchor}" font-size="11" fill="#8a93ad" font-family="IBM Plex Sans Arabic,Tahoma,Arial,sans-serif" {"direction=\"rtl\"" if lang=="ar" else "letter-spacing=\"1\""}>{txt}</text><text x="{186 if lang=="ar" else 54}" y="42" text-anchor="{anchor}" font-size="16" font-weight="700" fill="#ffffff" font-family="Arial,sans-serif">{sub}</text></svg>')
open(f"{out}/widget.js","w").write("""(function(){document.querySelectorAll('[data-gulfaideals-index]').forEach(function(el){if(el.dataset.gaiDone)return;el.dataset.gaiDone=1;var l=el.getAttribute('data-lang')==='en'?'/en':'';var f=document.createElement('iframe');f.src='%s'+l+'/embed/gulf-ai-index/';f.width='100%%';f.height=el.getAttribute('data-height')||'420';f.loading='lazy';f.title='Gulf AI Index';f.style.border='0';f.style.maxWidth='680px';el.appendChild(f);});})();""" % B)
os.makedirs(f"{out}/.well-known",exist_ok=True)
card={"protocolVersion":"0.3.0","name":"DealDune — Gulf AI Deals","description":"Sourced, bilingual (Arabic/English) data on AI, sovereign-AI and data-center deals in the GCC, AI agent use cases and Arabic AI tools. Read-only; every record links to its source.","url":f"{B}/a2a","preferredTransport":"JSONRPC","additionalInterfaces":[{"url":f"{B}/a2a","transport":"JSONRPC"}],"version":"1.0.0","documentationUrl":f"{B}/en/agents/","iconUrl":f"{B}/favicon.svg","provider":{"organization":"DealDune","url":B},"capabilities":{"streaming":False,"pushNotifications":False,"stateTransitionHistory":False},"defaultInputModes":["text/plain"],"defaultOutputModes":["text/plain","application/json"],
 "skills":[{"id":"search_deals","name":"Search Gulf AI deals","description":"Find AI / data-center deals in Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, Oman by company, country or keyword (Arabic or English).","tags":["deals","GCC","AI","data centers"],"examples":["HUMAIN deals","صفقات إم جي إكس","Saudi data center deals 2026"]},
  {"id":"search_use_cases","name":"Search AI agent use cases","description":"Find deployed AI agent use cases in Gulf government, banking, energy and more.","tags":["use cases","agents"],"examples":["bank AI agent UAE"]},
  {"id":"search_tools","name":"Search Arabic AI tools","description":"Find Arabic LLMs, speech, OCR and dubbing tools.","tags":["Arabic","tools"],"examples":["Arabic text to speech"]},
  {"id":"gulf_ai_index","name":"Gulf AI Index","description":"Announced AI spend by country and company, with methodology.","tags":["index","statistics"],"examples":["Gulf AI Index"]}],
 "supportsAuthenticatedExtendedCard":False,"x-mcp":f"{B}/mcp"}
for fn in ("agent.json","agent-card.json"): json.dump(card,open(f"{out}/.well-known/{fn}","w"),ensure_ascii=False,indent=1)
for r in ["/privacy/","/terms/","/support/","/gulf-ai-index/","/fii10/","/companies/","/countries/","/sectors/"]: pass
print("hub pages:",{h:len(M) for h,(M,_,_) in HUBS.items()},"| index total",round(TOTAL/1e9,1),"bn",flush=True)
