"""Weekly issue generator (no sending). Writes issues/<date>.html and .txt.
Usage: python3 scripts/newsletter.py [--days 7] [--date YYYY-MM-DD]"""
import json,os,sys,html,datetime
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); B="https://gulfaideals.com"; e=html.escape
a=sys.argv; days=int(a[a.index("--days")+1]) if "--days" in a else 7
today=datetime.date.fromisoformat(a[a.index("--date")+1]) if "--date" in a else datetime.date.today(); since=(today-datetime.timedelta(days=days)).isoformat()
D=[d for d in json.load(open(f"{root}/data/deals.json")) if d.get("status","published")=="published"]
UC=json.load(open(f"{root}/data/use_cases.json")); TL=json.load(open(f"{root}/data/tools.json"))
week=[d for d in D if d["date"]>=since]
if len(week)<3: week=sorted(D,key=lambda x:x["date"],reverse=True)[:5]
week=sorted(week,key=lambda d:(d["value"] is not None and d.get("currency")=="USD" and d["value"] or 0,d["date"]),reverse=True)[:7]
n=today.isocalendar()[1]; uc=UC[n%len(UC):n%len(UC)+3] or UC[:3]; tl=TL[n%len(TL):n%len(TL)+3] or TL[:3]
def val(d): return "Undisclosed" if d["value"] is None else (f'{d["currency"]} {d["value"]/1e9:g}bn' if d["value"]>=1e9 else f'{d["currency"]} {d["value"]/1e6:g}m')
title=f"Gulf AI Brief — week of {today:%d %b %Y}"
SP="[SPONSOR SLOT — available: gulfaideals.com/sponsor]"
txt=[title,"="*len(title),"",SP,"","TOP DEALS"]+[f"- {d['date']} | {d['country']} | {', '.join(d['parties'][:3]) or d['title']} — {val(d)}\n  {d['summary']}\n  {B}/deals/{d['slug']}/ (source: {d['source_url']})" for d in week]
txt+=["","AGENT USE CASES"]+[f"- {u['title']} ({u['sector']}, {u['country']})\n  {u['summary']}\n  {B}/use-cases/{u['slug']}/" for u in uc]
txt+=["","ARABIC AI TOOLS"]+[f"- {t['name']} — {t['category']}: {t['description']}\n  {B}/tools/{t['slug']}/" for t in tl]
txt+=["","—","DealDune · The Gulf AI Hub · gulfaideals.com","You received this because you subscribed at gulfaideals.com. Unsubscribe: {{UNSUBSCRIBE_URL}}"]
row=lambda h,b,l:f'<tr><td style="padding:10px 0;border-bottom:1px solid #eee"><a href="{l}" style="color:#0b5cad;font-weight:bold;text-decoration:none">{h}</a><br><span style="color:#333">{b}</span></td></tr>'
sec=lambda name,rows:f'<h2 style="font-size:18px;margin:24px 0 4px;color:#0b1020">{name}</h2><table width="100%" cellpadding="0" cellspacing="0">{"".join(rows)}</table>'
H=f'''<!doctype html><html><body style="margin:0;background:#f4f5f8;font-family:Arial,sans-serif"><table width="100%"><tr><td align="center"><table width="600" style="background:#fff;padding:24px;max-width:600px">
<tr><td><div style="font-size:22px;font-weight:800">Deal<span style="color:#d99a1e">Dune</span></div><h1 style="font-size:20px">{e(title)}</h1>
<div style="border:1px dashed #d99a1e;padding:12px;margin:12px 0">Sponsor slot available — <a href="{B}/sponsor/">book this week</a></div>
{sec("Top deals",[row(e(", ".join(d["parties"][:3]) or d["title"])+f' — {val(d)}',f'{e(d["date"])} · {e(d["country"])} · {e(d["summary"])} <a href="{e(d["source_url"])}">Source</a>',f'{B}/deals/{d["slug"]}/') for d in week])}
{sec("Agent use cases",[row(e(u["title"]),f'{e(u["sector"])} · {e(u["country"])} — {e(u["summary"])}',f'{B}/use-cases/{u["slug"]}/') for u in uc])}
{sec("Arabic AI tools",[row(e(t["name"]),f'{e(t["category"])} — {e(t["description"])}',f'{B}/tools/{t["slug"]}/') for t in tl])}
<p style="color:#888;font-size:12px;margin-top:24px">DealDune · The Gulf AI Hub · <a href="{B}">gulfaideals.com</a><br>You received this because you subscribed. <a href="{{{{UNSUBSCRIBE_URL}}}}">Unsubscribe</a></p></td></tr></table></td></tr></table></body></html>'''
os.makedirs(f"{root}/issues",exist_ok=True); base=f"{root}/issues/{today.isoformat()}"
open(base+".html","w").write(H); open(base+".txt","w").write("\n".join(txt)+"\n")
print("issue:",base+".html",base+".txt",f"({len(week)} deals, {len(uc)} use cases, {len(tl)} tools)")
