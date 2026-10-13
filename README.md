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
