import json
D=json.load(open('data/deals.json')); UC=json.load(open('data/use_cases.json')); TL=json.load(open('data/tools.json'))
T={ # id: title
"12992a670a":"Napster and HUMAIN partner on Arabic-native AI agents for the Middle East",
"8488f32cd1":"Abu Dhabi to refresh TAMM app in push for AI-native government",
"dbafc253c1":"Dubai launches Agentic AI for Government Services Accelerator",
"40a230fd1c":"Al Yamama wins infrastructure contract for HUMAIN's 6GW Riyadh AI campus",
"7d3fac77e9":"Synapse Analytics raises $13m Series A led by Partech",
"7c5a825ec3":"Sirdab raises $10m Series A co-led by Elm and BECO Capital",
"2bff6ef94a":"HUMAIN and DataVolt partner on ~100MW AI data center at NEOM's Oxagon",
"fd5d360986":"HUMAIN and AWS expand partnership: 50MW AI Zone, ALLaM on Amazon Bedrock",
"37e2fb3d37":"Stellaria closes AED 25m seed round at AED 420m valuation",
"bded877a74":"MGX, AIP and BlackRock's GIP close Aligned Data Centers acquisition",
"be4e6e6fdf":"CNTXT AI closes $60m Series A co-led by AI71 and BlueFive Capital",
"d01e088869":"KKR, Kuwait Investment Authority, NVIDIA and Vistra launch $10bn+ Helix",
"f920b35fc5":"AI startup 1001 raises $30m Series A led by Lux Capital, with Sanabil",
"e0c7e17c5b":"G42 and Cerebras to deploy 8-exaflop sovereign AI supercomputer in India",
"b16ea60a36":"HUMAIN invests $3bn in xAI's Series E round",
"dbc3e0d895":"UAE AI minister: Stargate UAE campus to cost more than $30bn",
"d37c428193":"Hassan Allam–Sterling & Wilson JV wins SAR750m HUMAIN data center contract",
"5679f27d52":"Signit raises $15m Series A led by Raed Ventures",
"08847b0fce":"stc's center3 and HUMAIN sign MoU for 1GW AI data center JV",
"5f7b322d5b":"Brookfield and Qatar's Qai form $20bn AI infrastructure JV",
"616fbffeaa":"Microsoft details $15.2bn UAE investment through 2029",
"032ccfc3a6":"HUMAIN and AWS expand strategic relationship (November 2025)",
"6470aeccbf":"HUMAIN and Blackstone-backed AirTrunk agree $3bn Saudi data center deal",
"baaf512e60":"MGX, AIP and BlackRock's GIP agree to buy Aligned Data Centers for ~$40bn",
"1a2cd2d6b0":"Cerebras aims to deploy AI infrastructure at Stargate UAE",
"4b28097c15":"HUMAIN and Qualcomm to deploy 200MW of AI200/AI250 inference racks",
"0e631cfa98":"HUMAIN and center3 sign connectivity agreement",
"118513d6b2":"US approves Microsoft export licences for Nvidia GB300 chips to UAE",
"4611b29f15":"G42, OpenAI, Oracle, NVIDIA, SoftBank and Cisco launch Stargate UAE",
"33616f1bb2":"UAE and US announce 5GW UAE–US AI Campus in Abu Dhabi",
"aa05b695e1":"AWS and HUMAIN plan $5bn+ 'AI Zone' in Saudi Arabia",
"d06eed371d":"Google Cloud and PIF advance $10bn AI hub in Saudi Arabia",
"eca84c69a4":"Oracle pledges $14bn Saudi investment over 10 years",
"99c8dd5ec8":"AMD and HUMAIN form $10bn, 500MW AI compute collaboration",
"7854308249":"Saudi DataVolt plans $20bn of AI data centers and energy in the US",
"60eacc85d6":"SDAIA signs AI and data center MoUs with AMD, DDN, WEKA and others",
"ca5475a0c2":"HUMAIN to build up to 500MW of NVIDIA-powered AI factories",
"298ea1898d":"SDAIA and NVIDIA to deploy up to 5,000 Blackwell GPUs for sovereign AI",
"66898ea779":"Aramco Digital and NVIDIA agree AI infrastructure collaboration",
"f265328c7a":"Saudi Crown Prince launches HUMAIN as PIF-owned AI company",
"b12a81df16":"Groq secures $1.5bn Saudi commitment to expand Dammam inference hub",
"5111fd3f73":"MGX joins US Stargate venture; reportedly to contribute ~$7bn",
}
FIX={
"12992a670a":dict(source_url="https://www.napster.com/news/napster-and-humain-partner-to-bring-arabic-native-ai-to-public-and-private-organizations-across-the-middle-east",parties=["Napster","HUMAIN"],summary="Napster and HUMAIN announced a partnership to deploy Arabic-native AI agents combining HUMAIN's ALLaM model and Arabic speech technology with Napster's voice and video agent infrastructure.",source_domain="napster.com"),
"7c5a825ec3":dict(source_url="https://www.wamda.com/en/2026/09/sirdab-raises-10-million-series-expand-gcc",date="2026-09-03",summary="Saudi logistics platform Sirdab raised a $10m (SAR 37.5m) Series A co-led by Elm and BECO Capital; funds support GCC expansion and AI that matches businesses to logistics capacity."),
"d01e088869":dict(source_url="https://www.helixdi.com/news-insights/kkr-launches-helix-digital-infrastructure-to-finance-and-deliver-the-next-generation-of-ai-infrastructure/",date="2026-06-11",category="partnership",summary="KKR launched Helix Digital Infrastructure with the Kuwait Investment Authority, NVIDIA and Vistra, backed by more than $10bn of capital commitments for AI data centers, power and connectivity."),
"eca84c69a4":dict(source_url="https://www.oracle.com/news/announcement/oracles-commitment-to-saudi-arabia-and-president-trumps-vision-for-global-prosperity-2025-05-13/"),
"99c8dd5ec8":dict(source_url="https://ir.amd.com/news-events/press-releases/detail/1250/amd-and-humain-form-strategic-10b-collaboration-to-advance-global-ai",summary="AMD and HUMAIN agreed to invest up to $10bn to deploy 500MW of AI compute capacity over five years across Saudi Arabia and the US."),
"7854308249":dict(source_url="https://www.reuters.com/world/middle-east/saudi-arabia-partners-with-nvidia-spur-ai-goals-trump-visits-2025-05-13/",summary="The White House said Saudi firm DataVolt will invest $20bn in AI data centers and energy infrastructure in the United States."),
"f265328c7a":dict(source_url="https://www.pif.gov.sa/en/news-and-insights/press-releases/2025/hrh-crown-prince-launches-humain-as-global-ai-powerhouse/",date="2025-05-12",date_precision="day",summary="Crown Prince Mohammed bin Salman launched HUMAIN, a PIF-owned company operating across the AI value chain: data centers, cloud, AI models and a multimodal Arabic LLM."),
"b12a81df16":dict(source_url="https://www.reuters.com/technology/artificial-intelligence/ai-chip-startup-groq-secures-15-billion-commitment-saudi-arabia-2025-02-10/",date="2025-02-10",date_precision="day",summary="AI chip startup Groq secured a $1.5bn commitment from Saudi Arabia at LEAP 2025 to expand its LPU inference infrastructure, including its Dammam data center."),
"4b28097c15":dict(source_url="https://www.qualcomm.com/news/releases/2025/10/humain-and-qualcomm-to-deploy-ai-infrastructure-in-saudi-arabia-",date="2025-10-27",date_precision="day"),
}
REMOVE_DEALS={"8b888ceb30"}  # Bahrain Sitra $400m: only aiinarabia.com, uncorroborated
n_t=n_s=0
out=[]
for d in D:
    if d["id"] in REMOVE_DEALS: continue
    if d["id"] in T and d["title"]!=T[d["id"]]: d["title"]=T[d["id"]]; n_t+=1
    if d["id"] in FIX: d.update(FIX[d["id"]]); n_s+=1
    if d.get("status")=="published" and d["id"] in FIX: d.pop("auto",None)
    out.append(d)
for d in out:
    if d.get("status")!="unreviewed": assert len(d["title"])<=90, d["title"]
json.dump(sorted(out,key=lambda x:x["date"],reverse=True),open('data/deals.json','w'),indent=1)
# use cases
RM_UC={"tawakkalna-ai-assistant-guides-citizens-through-services","absher-virtual-agent-for-passport-and-visa-queries","emirates-nbd-routes-inquiries-through-arabic-optimised-models","snb-moves-sme-underwriting-onto-an-arabic-llm","mashreq-sharia-audit-engine","arabic-triage-agents-in-seha-virtual-hospital"}
UFIX={
"al-rajhi-arabic-assistant-and-ai-fraud-detection":dict(title="Al Rajhi Bank deploys Mozn's FOCAL AI to fight fraud",tool="Mozn FOCAL",summary="Al Rajhi Bank partnered with Mozn (Oct 2025) to deploy FOCAL, an AI financial-crime prevention platform for real-time fraud detection and risk intelligence.",source_url="https://www.mozn.ai/blog/alrajhi-bank-partners-with-mozn-to-harness-ai-in-the-fight-against-fraud",how_to="1) Stream card and transfer events to a fraud-scoring engine. 2) Score in real time and hold high-risk payments. 3) Alert the customer for confirmation. 4) Route cases to investigators with model explanations."),
"e-rolls-arabic-copilot-to-50k-staff":dict(title="e& UAE deploys Microsoft 365 Copilot at scale",summary="e& UAE announced a large-scale Microsoft 365 Copilot deployment in March 2025 to drive AI-powered workplace transformation.",source_url="https://www.eand.com/en/news/14-march-25-eand-uae-deploys-m365-copilot-at-scale-to-drive-aI-powered-workplace-transformation.html"),
"arabic-voice-agents-live-at-e":dict(title="Arabic.AI and HeyBreez team up on enterprise Arabic voice agents",summary="Arabic.AI and HeyBreez partnered (Apr 2026) to run production Arabic voice AI for enterprises and governments, pairing dialect-aware models with low-latency telephony.",source_url="https://arabic.ai/arabic-ai-and-heybreez-join-forces-to-run-arabic-voice-ai-at-enterprise-scale/"),
"dp-world-cargoes-flow-visibility-at-jebel-ali":dict(title="DP World's CARGOES Flow gives end-to-end shipment visibility",summary="DP World made CARGOES Flow available as a global supply-chain visibility platform for tracking sea, air and land shipments end to end.",source_url="https://www.dpworld.com/en/news/dp-world-announces-availability-of-cargoes-flow"),
}
uo=[];n_ut=n_us=0
for u in UC:
    if u["slug"] in RM_UC: continue
    if u["slug"] in UFIX: u.update(UFIX[u["slug"]]); n_us+=1
    assert len(u["title"])<=90; uo.append(u)
json.dump(uo,open('data/use_cases.json','w'),indent=1)
TFIX={"heybreez":dict(source_url="https://arabic.ai/arabic-ai-and-heybreez-join-forces-to-run-arabic-voice-ai-at-enterprise-scale/",url="https://heybreez.com",description="Low-latency telephony and multi-agent voice infrastructure; partnered with Arabic.AI for enterprise Arabic voice agents."),
      "mozn-focal":dict(source_url="https://www.mozn.ai/blog/alrajhi-bank-partners-with-mozn-to-harness-ai-in-the-fight-against-fraud",url="https://www.mozn.ai")}
n_ts=0
for t in TL:
    if t["slug"] in TFIX: t.update(TFIX[t["slug"]]); n_ts+=1
json.dump(TL,open('data/tools.json','w'),indent=1)
print(f"deals: {n_t} titles rewritten, {n_s} source/summary fixes, {len(REMOVE_DEALS)} removed -> {sum(1 for d in out if d.get('status')!='unreviewed')} published")
print(f"use cases: {len(RM_UC)} removed, {n_us} re-sourced -> {len(uo)}; tools: {n_ts} re-sourced -> {len(TL)}")
