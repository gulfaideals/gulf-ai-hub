# Gulf AI Hub — gulfaideals.com

An anonymous, sourced hub for **AI in Saudi Arabia, the UAE and the GCC**:
- **Deals**: sovereign AI, data centers, partnerships, funding, tenders (2025–2026), each with a source link.
- **AI agent use cases**: real deployments in GCC governments and businesses, with how-to steps.
- **Arabic AI tools**: LLMs, STT/TTS, dubbing, chatbots and OCR with strong Arabic support.

Site: https://gulfaideals.com · Machine-readable: [`/llms.txt`](https://gulfaideals.com/llms.txt) · [`/openapi.json`](https://gulfaideals.com/openapi.json)

## MCP server (read-only, no auth)
`https://gulfaideals.com/mcp` (streamable HTTP). Tools: `search_deals`, `search_use_cases`, `search_tools`, `get_item`.

- Cursor: [one-click install](https://github.com/gulfaideals/gulf-ai-hub-mcp/blob/main/INSTALL.md)
- VS Code: `code --add-mcp '{"name":"gulf-ai-deals","type":"http","url":"https://gulfaideals.com/mcp"}'`
- Claude Code: `claude mcp add --transport http gulf-ai-deals https://gulfaideals.com/mcp`
- Gemini CLI: `gemini extensions install https://github.com/gulfaideals/gulf-ai-hub-mcp`
- Claude Desktop: `.mcpb` from [releases](https://github.com/gulfaideals/gulf-ai-hub-mcp/releases)

More: [gulfaideals/gulf-ai-hub-mcp](https://github.com/gulfaideals/gulf-ai-hub-mcp)

## Repo layout
`data/` JSON datasets · `scripts/` build/refresh (Python) · `functions/` Cloudflare Pages Functions (MCP, API).

## License
Code: MIT. Data (`data/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), attribute "Gulf AI Deals (gulfaideals.com)". Underlying facts belong to their linked sources.

## Bilingual (Arabic-first)
- Arabic at `/` (RTL, IBM Plex Sans Arabic); English at `/en/`, linked with hreflang plus a language switcher. RSS feeds: `/rss.xml` (Arabic) and `/en/rss.xml` (English).
- Records carry `title_ar` / `summary_ar` (deals and use cases) and `name_ar` / `description_ar` (tools). `source_url_ar` is set where an Arabic source exists. MCP search matches Arabic queries and returns both languages.
- `scripts/daily.sh` runs the steps refresh → `ar_auto.py` → build → deploy → IndexNow. `refresh.py` also ingests Arabic-language news from a whitelist of Gulf outlets. `ar_auto.py` fills in the missing language through an LLM when `XAI_API_KEY` or `OPENAI_API_KEY` is set in `.secrets`. Otherwise it flags the item as "translation pending" and lists it in `data/ar_pending.json`.
- `CLOUDFLARE_ACCOUNT_ID` and `EXPORT_SECRET` are read from the untracked `.secrets` file.
