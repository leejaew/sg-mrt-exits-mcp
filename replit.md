# Workspace

## Overview

pnpm workspace monorepo (TypeScript) plus a Python MCP server project.

---

## TypeScript Stack (artifacts/)

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

### Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

---

## sg-mrt-exits-mcp (Python MCP Server)

A Model Context Protocol (MCP) server that wraps the Singapore LTA MRT Station Exit GeoJSON API.
Exposes **15 tools** for AI assistants to answer real-world questions about Singapore's MRT network.

### Location
`sg-mrt-exits-mcp/`

### Tech Stack
- **Language**: Python 3.11
- **MCP framework**: `mcp` (FastMCP), v1.27
- **HTTP client**: `httpx` (async)
- **Geocoding**: Nominatim / OpenStreetMap (free, no key needed)
- **Package manager**: uv (via Replit)

### Secrets Required
- `API_BASE_URL` — base URL of the api.jael.ee endpoint (required)
- `API_USERNAME` — api.jael.ee API username
- `API_TOKEN` — api.jael.ee API token

### API Endpoint Configuration
Fully configurable via env vars (no code changes needed):
- `API_BASE_URL` — base URL (required, stored in Replit Secrets)
- `API_ENDPOINT_PATH` — default: `/JLEE/sg_lta_mrt_station_exit_geojson_api`

Full URL assembled at runtime by `config.get_api_url()`.

### Key Commands
- `cd sg-mrt-exits-mcp && python3 validate.py` — validate setup and test API
- `cd sg-mrt-exits-mcp && python3 main.py` — start MCP server (stdio transport)

### MCP Tools (15 total)
1. `search_exits_by_station` — wildcard/partial station name search
2. `get_exit_detail` — full details for a specific exit
3. `get_exit_map_view` — Google Maps view + directions links
4. `find_nearest_exit_by_coordinates` — nearest exits to lat/lng
5. `find_nearest_exit_by_landmark` — nearest exits to a named place
6. `find_exits_within_radius` — all exits within a radius
7. `list_exits_by_line` — exits grouped by station for a given MRT line
8. `get_station_footprint` — spatial spread of a station's exits
9. `retail_proximity_analysis` — exit density for retail site selection
10. `accessibility_check` — nearby exits + LTA accessibility link
11. `emergency_response_exits` — nearest exits with directions links
12. `logistics_delivery_planning` — exits near a delivery zone
13. `tourist_guide_exits` — best exit for a Singapore attraction
14. `commuter_exit_comparison` — compare exits ranked by destination distance
15. `urban_planning_exit_density` — exit density analysis for urban planning

### MRT Lines Supported
NSL, EWL, NEL, CCL, DTL, TEL, BPL (Bukit Panjang LRT), SLRT (Sengkang LRT), PLRT (Punggol LRT)

### Architecture Notes
- `config.py` — centralised configuration (API URL, credentials, env var overrides)
- `api_client.py` — async HTTP client with Basic Auth; includes client-side wildcard fallback for leading-wildcard searches (`*hill`) that the API does not support natively
- `geo_utils.py` — Haversine distance, coordinate parsing (`"lng, lat"` string → `(lat, lng)` tuple), formatting helpers
- `geocoding.py` — Nominatim landmark resolver (always appends `, Singapore`)
- `line_lookup.py` — static `STATION_LINE_MAP` dict + `LINE_NAME_TO_CODE` for full line name resolution

### Claude Desktop Config
```json
{
  "mcpServers": {
    "sg-mrt-exits-mcp": {
      "command": "python3",
      "args": ["/absolute/path/to/sg-mrt-exits-mcp/main.py"],
      "env": {
        "API_USERNAME": "your_email",
        "API_TOKEN": "t_your_token"
      }
    }
  }
}
```
