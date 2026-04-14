import os
from dotenv import load_dotenv

load_dotenv()

# ── API credentials ─────────────────────────────────────────────────────────
API_USERNAME: str = os.environ.get("API_USERNAME", "")
API_TOKEN: str = os.environ.get("API_TOKEN", "")

# ── API endpoint ─────────────────────────────────────────────────────────────
# API_BASE_URL is required — set it in Replit Secrets or a .env file.
# No hardcoded default; the server will raise at startup if it is missing.
_raw_base_url: str | None = os.environ.get("API_BASE_URL")
if not _raw_base_url:
    raise EnvironmentError(
        "API_BASE_URL is not set. Add it to Replit Secrets (or your .env file) "
        "before starting the server — e.g. API_BASE_URL=https://api.jael.ee"
    )
API_BASE_URL: str = _raw_base_url

API_ENDPOINT_PATH: str = os.environ.get(
    "API_ENDPOINT_PATH", "/JLEE/sg_lta_mrt_station_exit_geojson_api"
)

def get_api_url() -> str:
    """Return the fully resolved API endpoint URL."""
    base = API_BASE_URL.rstrip("/")
    path = API_ENDPOINT_PATH if API_ENDPOINT_PATH.startswith("/") else f"/{API_ENDPOINT_PATH}"
    return f"{base}{path}"

# ── Cache ─────────────────────────────────────────────────────────────────────
# How long (seconds) to cache the full exits dataset before re-fetching.
# Override via CACHE_TTL_SECONDS env var. Default: 5 minutes.
CACHE_TTL_SECONDS: int = int(os.environ.get("CACHE_TTL_SECONDS", "300"))

# ── Outbound concurrency ──────────────────────────────────────────────────────
# Maximum number of simultaneous outbound HTTP requests to the LTA API.
API_MAX_CONCURRENCY: int = int(os.environ.get("API_MAX_CONCURRENCY", "5"))

# ── Geocoding ────────────────────────────────────────────────────────────────
NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT: str = "sg-mrt-exits-mcp/1.0"

# ── MCP server identity ───────────────────────────────────────────────────────
MCP_SERVER_NAME: str = "sg-mrt-exits-mcp"
