# sg-mrt-exits-mcp

A **Model Context Protocol (MCP) server** that wraps the Singapore LTA MRT Station Exit GeoJSON API. Exposes 15 tools for AI assistants (Claude, GPT-4, etc.) to answer real-world questions about Singapore's MRT network — covering navigation, accessibility, retail analytics, logistics, emergency response, and tourist use cases.

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

All three are required. `API_BASE_URL` is the base URL of the LTA SheetLabs endpoint. `API_USERNAME` and `API_TOKEN` are your SheetLabs credentials (see [https://sheetlabs.com](https://sheetlabs.com)).

The endpoint path can also be overridden via `API_ENDPOINT_PATH` if needed (default: `/JLEE/sg_lta_mrt_station_exit_geojson_api`).

### 3. Run the server

```bash
python main.py
```

The server communicates over **stdio** (standard MCP transport), making it compatible with Claude Desktop, the Claude API, and any MCP-compliant client.

---

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sg-mrt-exits-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/sg-mrt-exits-mcp/main.py"],
      "env": {
        "API_BASE_URL": "https://api.jael.ee",
        "API_USERNAME": "your_email@address.com",
        "API_TOKEN": "t_your_token_here"
      }
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
├── main.py              # Entry point — run this to start the MCP server
├── server.py            # FastMCP instance and tool registration
├── config.py            # Centralised configuration (API URL, credentials)
├── api_client.py        # HTTP client with Basic Auth, response parsing
├── geo_utils.py         # Haversine distance, coordinate parsing, formatting
├── geocoding.py         # Nominatim landmark-to-coordinates resolver
├── maps_links.py        # Google Maps URL builders
├── line_lookup.py       # Static MRT line → station mapping dictionary
├── tools/
│   ├── search_tools.py  # search_exits_by_station, get_exit_detail
│   ├── spatial_tools.py # nearest exit, radius search, urban density
│   ├── map_tools.py     # get_exit_map_view
│   ├── use_case_tools.py# retail, accessibility, emergency, logistics, tourist, commuter
│   └── line_tools.py    # list_exits_by_line, get_station_footprint
├── .env.example         # Example secrets file — never commit real credentials
└── requirements.txt
```

---

## Updating the API endpoint

To switch to a different base URL or path without modifying code, set environment variables:

```bash
# Example: switch to a staging endpoint
API_BASE_URL=https://staging.api.jael.ee
API_ENDPOINT_PATH=/JLEE/sg_lta_mrt_station_exit_geojson_api
```

The full URL is assembled at runtime by `config.get_api_url()`.

---

## Data Source

Land Transport Authority. (2019). LTA MRT Station Exit (GEOJSON) (2026) [Dataset]. data.gov.sg. Retrieved April 14, 2026 from https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view

Dataset license: Free forever for personal or commercial use, under the Open Data Licence (https://data.gov.sg/open-data-licence).
