import os
from dotenv import load_dotenv

load_dotenv()

# ── API credentials ─────────────────────────────────────────────────────────
API_USERNAME: str = os.environ.get("API_USERNAME", "")
API_TOKEN: str = os.environ.get("API_TOKEN", "")

# ── API endpoint (fully overridable via env vars) ────────────────────────────
# Base URL default: https://api.jael.ee
# Endpoint path default: /JLEE/sg_lta_mrt_station_exit_geojson_api
# Full default URL: https://api.jael.ee/JLEE/sg_lta_mrt_station_exit_geojson_api
API_BASE_URL: str = os.environ.get("API_BASE_URL", "https://api.jael.ee")
API_ENDPOINT_PATH: str = os.environ.get(
    "API_ENDPOINT_PATH", "/JLEE/sg_lta_mrt_station_exit_geojson_api"
)

def get_api_url() -> str:
    """Return the fully resolved API endpoint URL."""
    base = API_BASE_URL.rstrip("/")
    path = API_ENDPOINT_PATH if API_ENDPOINT_PATH.startswith("/") else f"/{API_ENDPOINT_PATH}"
    return f"{base}{path}"

# ── Geocoding ────────────────────────────────────────────────────────────────
NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT: str = "sg-mrt-exits-mcp/1.0"

# ── MCP server identity ───────────────────────────────────────────────────────
MCP_SERVER_NAME: str = "sg-mrt-exits-mcp"
