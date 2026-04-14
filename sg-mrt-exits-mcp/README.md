# SG MRT Exits MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-00C7B7)](https://modelcontextprotocol.io)
[![Tools](https://img.shields.io/badge/tools-15-orange)](https://github.com/leejaew/sg-mrt-exits-mcp)
[![Remix on Replit](https://img.shields.io/badge/Remix%20on-Replit-667881?logo=replit&logoColor=white)](https://replit.com/@leejaew/SG-MRT-Exits-MCP?v=1)

A **Model Context Protocol (MCP) server** that wraps the Singapore LTA MRT Station Exit GeoJSON API. Exposes 15 tools for AI assistants (Claude, Manus AI, and other MCP-compatible agents) to answer real-world questions about Singapore's MRT network — covering navigation, accessibility, retail analytics, logistics, emergency response, and tourist use cases.

**Remix this project on Replit** and deploy your own instance in minutes: [replit.com/@leejaew/SG-MRT-Exits-MCP](https://replit.com/@leejaew/SG-MRT-Exits-MCP?v=1). New to Replit? [Sign up here](https://replit.com/refer/leejaew).

---

## Tools

| # | Tool name | Description |
|---|-----------|-------------|
| 1 | `search_exits_by_station` | Search exits by station name (supports wildcards) |
| 2 | `get_exit_detail` | Full details for a specific exit |
| 3 | `get_exit_map_view` | Google Maps view & directions links for an exit |
| 4 | `find_nearest_exit_by_coordinates` | Nearest exits to a lat/lng coordinate |
| 5 | `find_nearest_exit_by_landmark` | Nearest exits to a named landmark |
| 6 | `find_exits_within_radius` | All exits within a radius of a location |
| 7 | `list_exits_by_line` | All exits grouped by station on a given MRT line |
| 8 | `get_station_footprint` | Spatial spread of a station's exits |
| 9 | `retail_proximity_analysis` | Exit density analysis for retail site selection |
| 10 | `accessibility_check` | Nearby exits with LTA accessibility resource link |
| 11 | `emergency_response_exits` | Nearest exits with directions for first responders |
| 12 | `logistics_delivery_planning` | Exits near a delivery zone for last-mile planning |
| 13 | `tourist_guide_exits` | Best exit for a Singapore attraction or landmark |
| 14 | `commuter_exit_comparison` | Compare exits at a station ranked by destination |
| 15 | `urban_planning_exit_density` | Exit density analysis for urban planning |

---

## Tech Stack

- **Language:** Python 3.11+
- **MCP framework:** `mcp` (FastMCP)
- **HTTP client:** `httpx` (async)
- **Geocoding:** Nominatim / OpenStreetMap (no API key required)
- **Secrets:** Replit Secrets / environment variables

---

## Setup

### 1. Install dependencies

```bash
cd sg-mrt-exits-mcp
pip install -r requirements.txt
```

### 2. Configure secrets

Add the following to **Replit Secrets** (or copy `.env.example` to `.env` for local development):

```
API_BASE_URL=https://api.jael.ee
API_USERNAME=your_email@address.com
API_TOKEN=t_your_token_here
```

All three are required. `API_BASE_URL` is the base URL of the api.jael.ee endpoint. `API_USERNAME` and `API_TOKEN` are your api.jael.ee credentials.

The endpoint path can also be overridden via `API_ENDPOINT_PATH` if needed (default: `/JLEE/sg_lta_mrt_station_exit_geojson_api`).

### 3. Optional configuration

These environment variables have sensible defaults and do not need to be set unless you want to tune behaviour:

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_TTL_SECONDS` | `300` | How long (in seconds) the full exit dataset is cached in memory before the next API fetch. Lower values keep data fresher; higher values reduce API calls. |
| `API_MAX_CONCURRENCY` | `5` | Maximum simultaneous outbound HTTP requests to the LTA API. |
| `MCP_TRANSPORT` | `stdio` | Transport protocol the server runs on. Options: `stdio` (local clients), `sse` (HTTP/SSE), `streamable-http` (HTTP/Streamable HTTP). |

### 4. Run the server

```bash
python main.py
```

By default the server runs over **stdio**, which is correct for local clients (Claude Desktop, Claude API). To serve over HTTP for web-based or deployed clients, set `MCP_TRANSPORT` before starting:

```bash
# Streamable HTTP (Manus AI, newer clients)
MCP_TRANSPORT=streamable-http python main.py

# SSE (Claude.ai, Cursor, Windsurf, older clients)
MCP_TRANSPORT=sse python main.py
```

---

## Connection Config

### Manus AI — Streamable HTTP (recommended, tested)

Requires the server to be deployed and started with `MCP_TRANSPORT=streamable-http`. The `/mcp` endpoint is then available at your deployment URL.

```json
{
  "mcpServers": {
    "sg-mrt-exits": {
      "type": "streamableHttp",
      "url": "https://your-deployed-mcp-server.replit.app/mcp"
    }
  }
}
```

### SSE — Claude.ai, Cursor, Windsurf, and other SSE-compatible clients *(not tested)*

> **Note:** This configuration has not been tested. SSE (Server-Sent Events) is the older HTTP transport, superseded by Streamable HTTP but still widely supported.

Requires the server to be deployed and started with `MCP_TRANSPORT=sse`. The `/sse` endpoint is then available at your deployment URL.

```json
{
  "mcpServers": {
    "sg-mrt-exits": {
      "type": "sse",
      "url": "https://your-deployed-mcp-server.replit.app/sse"
    }
  }
}
```

Some clients (e.g. Cursor) omit the `type` key and infer SSE from the URL:

```json
{
  "mcpServers": {
    "sg-mrt-exits": {
      "url": "https://your-deployed-mcp-server.replit.app/sse"
    }
  }
}
```

### Manus AI — STDIO *(not tested)*

> **Note:** This configuration has not been tested. It should work with any MCP client that supports stdio transport, but your mileage may vary.

No `MCP_TRANSPORT` change needed — stdio is the default.

```json
{
  "mcpServers": {
    "sg-mrt-exits": {
      "transportType": "stdio",
      "command": "python3",
      "args": ["/path/to/sg-mrt-exits-mcp/main.py"]
    }
  }
}
```

Credentials (`API_BASE_URL`, `API_USERNAME`, `API_TOKEN`) are inherited from the host environment — set them in your shell profile or system env rather than hardcoding them in the config.

### Claude Desktop *(not tested)*

> **Note:** This configuration has not been tested. The format follows the Claude Desktop MCP documentation but has not been verified end-to-end.

No `MCP_TRANSPORT` change needed — stdio is the default.

```json
{
  "mcpServers": {
    "sg-mrt-exits-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/sg-mrt-exits-mcp/main.py"]
    }
  }
}
```

---

## API Details

| Property | Value |
|----------|-------|
| Endpoint | `https://api.jael.ee/JLEE/sg_lta_mrt_station_exit_geojson_api` |
| Auth | HTTP Basic Auth (`API_USERNAME:API_TOKEN`, Base64-encoded) |
| Filter | `?properties[STATION_NA]=<name>` (optional; supports wildcards) |
| Dataset | 597 exits across 186 stations (full active MRT/LRT network) |

---

## Performance

The server caches the full 597-exit dataset in memory after the first fetch. All subsequent calls to spatial, density, and line tools read from that in-memory cache at effectively zero cost. Station-name search tools use a three-tier strategy: in-memory filter first (when cache is warm), falling back to a filtered API query, then a full-dataset fallback.

Landmark geocoding results (Nominatim lookups) are also cached in memory for the process lifetime — repeated lookups of the same place skip the Nominatim round-trip entirely.

| Scenario | Typical latency |
|----------|----------------|
| Cold cache (first call, API fetch required) | ~250–950 ms |
| Warm cache — spatial / density / line tools | < 1 ms |
| Warm cache — station-name search tools | < 1 ms |
| Geocoding — first lookup (Nominatim, live) | ~90–1000 ms |
| Geocoding — repeated lookup (cached) | < 0.1 ms |
| 8 concurrent calls (warm cache) | ~3 ms wall time |

The cold-cache cost is paid at most once per `CACHE_TTL_SECONDS` window (default: 5 minutes).

---

## MRT Lines Supported

| Code | Line |
|------|------|
| NSL | North-South Line |
| EWL | East-West Line |
| NEL | North-East Line |
| CCL | Circle Line |
| DTL | Downtown Line |
| TEL | Thomson-East Coast Line |
| BPL | Bukit Panjang LRT |
| SLRT | Sengkang LRT |
| PLRT | Punggol LRT |

---

## Project Structure

```
sg-mrt-exits-mcp/
├── main.py                  # Entry point — run this to start the MCP server
├── server.py                # FastMCP instance and tool registration
├── config.py                # Centralised configuration (API URL, credentials, cache TTL)
├── api_client.py            # HTTP client with Basic Auth, three-tier fetch strategy, in-memory cache
├── geo_utils.py             # Haversine distance, coordinate parsing, nearby_exits() helper
├── geocoding.py             # Nominatim landmark resolver with in-memory coordinate cache
├── maps_links.py            # Google Maps URL builders
├── line_lookup.py           # Static MRT line → station mapping dictionary
├── validators.py            # Input validation (coordinates, radius, top_n, strings)
├── tools/
│   ├── __init__.py          # Empty package marker
│   ├── search_tools.py      # search_exits_by_station, get_exit_detail
│   ├── spatial_tools.py     # find_nearest_exit_by_coordinates, find_nearest_exit_by_landmark,
│   │                        #   find_exits_within_radius, urban_planning_exit_density
│   ├── map_tools.py         # get_exit_map_view
│   ├── line_tools.py        # list_exits_by_line, get_station_footprint
│   ├── location_tools.py    # retail_proximity_analysis, accessibility_check,
│   │                        #   logistics_delivery_planning
│   └── navigation_tools.py  # emergency_response_exits, tourist_guide_exits,
│                            #   commuter_exit_comparison
├── benchmark.py             # Live performance benchmark (37 test cases, phases 1–5)
├── validate.py              # MCP tool schema validation script
├── .env.example             # Example secrets file — never commit real credentials
└── requirements.txt
```

---

## Updating the API Endpoint

To switch to a different base URL or path without modifying code, set environment variables:

```bash
API_BASE_URL=https://api.jael.ee
API_ENDPOINT_PATH=/JLEE/sg_lta_mrt_station_exit_geojson_api
```

The full URL is assembled at runtime by `config.get_api_url()`.

---

## Data Source

Land Transport Authority. (2019). LTA MRT Station Exit (GEOJSON) (2026) [Dataset]. data.gov.sg. Retrieved April 14, 2026 from https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view

Dataset license: Free forever for personal or commercial use, under the [Open Data Licence](https://data.gov.sg/open-data-licence).

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
