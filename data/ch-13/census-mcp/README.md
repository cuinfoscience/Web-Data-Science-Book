# The Census Bureau's MCP server: its tools, and one recorded session

The U.S. Census Bureau's [Data API MCP server](https://github.com/uscensusbureau/us-census-bureau-data-api-mcp) gives an AI assistant tools that query the Census Data API, the API chapter 11 used directly. It runs on your own computer, using Docker or Node, and needs a Census API key. So for chapter 13 and week 13's lab, it was run once, on 2026-11-09, and its answers were saved here. Students don't install anything: they read the server's real tool definitions, send them to a model, and run the model's chosen call themselves against `api.census.gov`, with the `CENSUS_KEY` from week 11.

| File | What it holds |
|---|---|
| `tools.json` | The server's answer to `tools/list`: five tools (`fetch-aggregate-data`, `fetch-dataset-geography`, `list-datasets`, `resolve-geography-fips`, `search-data-tables`), each with a `description` and an `inputSchema` written in JSON Schema. |
| `session.json` | The whole session, each message as sent and as received: `initialize`, `notifications/initialized`, `tools/list`, and one `tools/call` of `fetch-aggregate-data`. That call asks for table B19013 (median household income) for Boulder County, Colorado, from the 2024 ACS 5-year estimates. It returned 103,994 dollars with a margin of error of 2,268, the same figures chapter 11 got from the API directly. |

**How it was run:**
- The repository was at commit `5dcaa63` (2026-03-06), built with `npm ci` and `npm run build` under Node 22.
- It was started as `node dist/index.js`, with `CENSUS_API_KEY` set, and spoken to over standard input and output: one JSON-RPC message per line, the transport the server's own configuration uses.
- The server's local Postgres database wasn't set up. `tools/list` and `fetch-aggregate-data` don't use it; `resolve-geography-fips` and `search-data-tables` do, so they weren't called.
- The server answered `initialize` with protocol version `2025-03-26`.
- The server replaces the API key with `REDACTED` in the URL it reports, and neither file contains a key.

**License:** the server's code and these tool definitions are released by the Census Bureau under [CC0 1.0](https://github.com/uscensusbureau/us-census-bureau-data-api-mcp/blob/main/LICENSE).
