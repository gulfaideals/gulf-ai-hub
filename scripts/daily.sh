#!/usr/bin/env bash
# Daily pipeline: refresh -> build -> deploy -> IndexNow -> summary.   cron: 0 7 * * * /workspace/gulf-ai-deals/scripts/daily.sh >> /workspace/gulf-ai-deals/daily.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f "$HOME/.profile" ] && source "$HOME/.profile" >/dev/null 2>&1 || true
[ -f "$HOME/.bashrc" ] && source "$HOME/.bashrc" >/dev/null 2>&1 || true
set -a; source ./.secrets; set +a   # .secrets provides EXPORT_SECRET, CLOUDFLARE_ACCOUNT_ID (+ optional XAI_API_KEY/OPENAI_API_KEY for Arabic generation)
export SITE_URL=https://gulfaideals.com WRANGLER_SEND_METRICS=false
python3 scripts/refresh.py > /tmp/gad_refresh.json
python3 scripts/ar_auto.py
python3 scripts/build.py > /dev/null
/workspace/cftools/node_modules/.bin/node /workspace/cftools/node_modules/wrangler/bin/wrangler.js pages deploy dist --project-name gulfaideals --branch main --commit-dirty=true 2>&1 | grep -E "Deployment complete|ERROR" | sed 's/Take a peek.*//' || true
python3 - <<'PY'
import json,urllib.request
r=json.load(open("data/last_refresh.json"))
urls=r["published"]+(["https://gulfaideals.com/","https://gulfaideals.com/sitemap.xml","https://gulfaideals.com/rss.xml","https://gulfaideals.com/llms-full.txt"] if r["published"] else [])
st="no new URLs"
if urls:
    b=json.dumps({"host":"gulfaideals.com","key":"7f3c9a1e5b2d4c6a8e0f1a2b3c4d5e6f","keyLocation":"https://gulfaideals.com/7f3c9a1e5b2d4c6a8e0f1a2b3c4d5e6f.txt","urlList":urls}).encode()
    try: st=f"{urllib.request.urlopen(urllib.request.Request('https://api.indexnow.org/indexnow',b,{'Content-Type':'application/json'}),timeout=20).status} for {len(urls)} URLs"
    except Exception as e: st=f"error {e}"
print("IndexNow:",st)
PY
SUBS=$(curl -s -H "X-Export-Secret: $EXPORT_SECRET" "https://gulfaideals.com/api/subscribers/export?count=1" | python3 -c "import sys,json;print(json.load(sys.stdin).get('count','?'))" 2>/dev/null || echo "?")
python3 - "$SUBS" <<'PY'
import json,sys
r=json.load(open("data/last_refresh.json"))
print("=== DealDune daily summary ===")
print(f"New deals auto-published: {len(r['published'])}"); [print("  +",t) for t in r["published_titles"]]
print(f"Pending review — deals: {r['pending_deals_total']} | use-case candidates: {r['pending_use_cases_total']} (+{r['pending_use_cases_new']}) | tool candidates: {r['pending_tools_total']} (+{r['pending_tools_new']})")
print(f"Subscribers: {sys.argv[1]}")
PY
