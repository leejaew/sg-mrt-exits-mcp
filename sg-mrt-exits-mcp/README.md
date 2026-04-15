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
pip install -r requirements.txt
```

### 2. Configure secrets

Add the following to **Replit Secrets** (or copy `.env.example` to `.env` for local development).
All four are **required** — the server will not start if any are missing.

> **You must provide your own API.** This server does not come with a shared or public API endpoint. Before setting these Secrets, read [**About the data source**](#about-the-data-source) below to understand your options.

| Secret | Example value | Description |
|--------|--------------|-------------|
| `API_BASE_URL` | `https://your-api-host.com` | Base URL of your API host |
| `API_ENDPOINT_PATH` | `/your/endpoint/path` | Path to the GeoJSON endpoint |
| `API_USERNAME` | `your_username` | Username for HTTP Basic Auth (omit if unauthenticated) |
| `API_TOKEN` | `your_token` | Token/password for HTTP Basic Auth (omit if unauthenticated) |

`API_BASE_URL` and `API_ENDPOINT_PATH` are kept separate so you can switch hosts or paths by updating a single Secret each, with no code changes.

**Example configuration (author's own instance):**

| Secret | Value |
|--------|-------|
| `API_BASE_URL` | `https://api.jael.ee` |
| `API_ENDPOINT_PATH` | `/JLEE/sg_lta_mrt_station_exit_geojson_api` |

> This instance is not publicly accessible — it is shown here only to illustrate what the values look like when filled in.

### 3. Optional configuration

These environment variables have sensible defaults and do not need to be set unless you want to tune behaviour:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `streamable-http` | Transport protocol. Options: `stdio` (local clients), `sse` (HTTP/SSE), `streamable-http` (HTTP/Streamable HTTP). Defaults to `streamable-http` for Replit deployment; override via Replit Secret to change without touching code. |
| `CACHE_TTL_SECONDS` | `300` | How long (in seconds) the full exit dataset is cached in memory before the next API fetch. Lower values keep data fresher; higher values reduce API calls. |
| `API_MAX_CONCURRENCY` | `5` | Maximum simultaneous outbound HTTP requests to the LTA API. |

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

## Deploying on Replit

The folder is self-contained and ships with a `.replit` file pre-configured for standalone deployment.

### Steps

1. Create a new **Python** Replit project.
2. Upload all files from this folder into the project root (including `.replit` and `requirements.txt`).
3. Add the following **Replit Secrets** in the new project:

   | Secret | Value |
   |--------|-------|
   | `API_BASE_URL` | Base URL of your API host |
   | `API_ENDPOINT_PATH` | Path to the GeoJSON endpoint |
   | `API_USERNAME` | Your API username (if required) |
   | `API_TOKEN` | Your API token (if required) |
   | `MCP_TRANSPORT` | `streamable-http` |

   See [**About the data source**](#about-the-data-source) for how to obtain or host an API for the underlying dataset.

4. **Publish the project.** Once deployed, the MCP server is live at:
   - Streamable HTTP: `https://<your-project>.<your-username>.replit.app/mcp`
   - SSE: `https://<your-project>.<your-username>.replit.app/sse`

> **All configuration is managed through Replit Secrets.** To change the API source or transport mode, update the relevant Secret and redeploy — no code changes required.

---

## Connection Config

### Manus AI — Streamable HTTP (recommended, tested ✓)

Requires `MCP_TRANSPORT=streamable-http` (the default for deployed Replit instances).

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

Requires `MCP_TRANSPORT=sse`.

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

### STDIO — local clients *(not tested)*

> **Note:** This configuration has not been tested. It should work with any MCP client that supports stdio transport.

No `MCP_TRANSPORT` change needed — stdio is the default when the Secret is not set.

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

Credentials (`API_BASE_URL`, `API_ENDPOINT_PATH`, `API_USERNAME`, `API_TOKEN`) are inherited from the host environment — set them in your shell profile or system env rather than hardcoding them in the config.

### Claude Desktop *(not tested)*

> **Note:** This configuration has not been tested. The format follows the Claude Desktop MCP documentation but has not been verified end-to-end.

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
| Base URL | Configured via `API_BASE_URL` Secret |
| Endpoint path | Configured via `API_ENDPOINT_PATH` Secret |
| Auth | HTTP Basic Auth (`API_USERNAME:API_TOKEN`, Base64-encoded) |
| Filter | `?properties[STATION_NA]=<name>` (optional; supports wildcards) |
| Dataset | 597 exits across 186 stations (full active MRT/LRT network) |

---

## About the Data Source

This server requires you to supply your own API that serves the LTA MRT Station Exit dataset. There is no shared or public endpoint included — the four API Secrets (`API_BASE_URL`, `API_ENDPOINT_PATH`, `API_USERNAME`, `API_TOKEN`) must point to an API you control or have credentials for.

### The underlying dataset

The data comes from the Land Transport Authority and is free to use:

> **LTA MRT Station Exit (GeoJSON)**
> https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view
> Licensed under the [Singapore Open Data Licence](https://data.gov.sg/open-data-licence) — free for personal and commercial use.

You can host this dataset yourself (e.g. via a simple REST API, a spreadsheet-to-API service, or any backend that can serve the GeoJSON), then point the four Secrets at your instance.

### Compatibility requirement

Your API must return GeoJSON records with the following structure for all 15 tools to work correctly:

```json
{
  "properties": {
    "STATION_NA": "ORCHARD MRT STATION",
    "EXIT_CODE":  "Exit A",
    "OBJECT_ID":  12345,
    "INC_CRC":    "ABC123",
    "FMEL_UPD_D": 20251201000000.0
  },
  "geometry": {
    "coordinates": "103.83260, 1.30420"
  }
}
```

The key fields are `STATION_NA` (station name in uppercase), `EXIT_CODE` (exit label), and `geometry.coordinates` (a `"longitude, latitude"` string). Optional filtering via `?properties[STATION_NA]=<name>` is also supported for station-name search performance, but the server will fall back to full-dataset filtering in memory if the parameter is not supported.

---

## Tool Behaviour Notes

### Flexible exit code matching

`get_exit_detail` and `get_exit_map_view` accept exit codes in any format — `"B"`, `"b"`, `"Exit B"`, or `"exit b"` all resolve to the same exit. The server normalises both the input and the stored value before comparing, so AI agents do not need to know the exact casing or prefix the API uses internally.

### Tourist guide — configurable result count

`tourist_guide_exits` accepts an optional `top_n` parameter (default `5`) to control how many nearby exits are returned.

### Commuter comparison — multi-station awareness

`commuter_exit_comparison` handles station name queries that match more than one station. When multiple stations are returned, each exit line is prefixed with its station name so the output is unambiguous.

### Radius search — resolved coordinates

`find_exits_within_radius` now shows the geocoded coordinates for landmark-name queries (consistent with `find_nearest_exit_by_landmark`), making it easy to verify the geocoding resolved to the correct location.

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
├── .replit                  # Standalone Replit deployment config
├── main.py                  # Entry point — run this to start the MCP server
├── server.py                # FastMCP instance and tool registration
├── config.py                # Centralised configuration (reads all values from env/Secrets)
├── api_client.py            # HTTP client with Basic Auth, three-tier fetch strategy, in-memory cache
├── geo_utils.py             # Haversine distance, coordinate parsing, exit code normalisation
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
├── validate.py              # Startup validation — checks all required Secrets and API connectivity
├── .env.example             # Example secrets file — never commit real credentials
└── requirements.txt
```

---

## Secrets Reference

A complete list of every environment variable / Secret the server reads:

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `API_BASE_URL` | Yes | — | Base URL of your API host (e.g. `https://your-api-host.com`) |
| `API_ENDPOINT_PATH` | Yes | — | Path to the GeoJSON endpoint (e.g. `/your/endpoint/path`) |
| `API_USERNAME` | Yes | — | Username for HTTP Basic Auth (required by server at startup; use a placeholder if your API is unauthenticated) |
| `API_TOKEN` | Yes | — | Token/password for HTTP Basic Auth (required by server at startup; use a placeholder if your API is unauthenticated) |
| `MCP_TRANSPORT` | No | `streamable-http` | Transport protocol: `stdio`, `sse`, or `streamable-http` |
| `CACHE_TTL_SECONDS` | No | `300` | In-memory cache TTL for the full exits dataset (seconds) |
| `API_MAX_CONCURRENCY` | No | `5` | Max simultaneous outbound HTTP requests |

No secret values are hardcoded anywhere in the codebase. `config.py` reads every value from the environment and raises an explicit `EnvironmentError` at startup if a required key is missing.

---

## Data Source

Land Transport Authority. (2019). LTA MRT Station Exit (GEOJSON) (2026) [Dataset]. data.gov.sg. Retrieved April 15, 2026 from https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view

Dataset license: Free forever for personal or commercial use, under the [Singapore Open Data Licence version 1.0](https://data.gov.sg/open-data-licence).

### Attribution

If you use this server in a product, application, or website, you must include the following notice:

> Contains information from LTA MRT Station Exit (GEOJSON) accessed on April 15, 2026 from LTA (Land Transport Authority) which is made available under the terms of the [Singapore Open Data Licence version 1.0](https://data.gov.sg/open-data-licence).

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
