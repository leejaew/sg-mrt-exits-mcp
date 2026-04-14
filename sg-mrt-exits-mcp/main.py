"""
Entry point for the sg-mrt-exits-mcp MCP server.

Run with:
    python main.py

Transport is controlled by the MCP_TRANSPORT environment variable:
    stdio            — default; for Claude Desktop, Claude API, and local clients
    sse              — HTTP/SSE; for Claude.ai, Cursor, Windsurf, and SSE-compatible clients
    streamable-http  — HTTP/Streamable HTTP; for Manus AI and clients supporting the newer transport

For HTTP transports (sse, streamable-http) the server binds to:
    host — FASTMCP_HOST env var, or 0.0.0.0 if not set
    port — PORT env var (Replit's assigned port), then FASTMCP_PORT, then 8000

IMPORTANT: transport and host/port env vars must be resolved before importing
server.py, because FastMCP reads its Settings from the environment at
construction time (FastMCP(MCP_SERVER_NAME) in server.py).

Configuration is read from environment variables (Replit Secrets or .env):
    API_BASE_URL       — base URL of the api.jael.ee endpoint (required)
    API_USERNAME       — api.jael.ee API username
    API_TOKEN          — api.jael.ee API token
    API_ENDPOINT_PATH  — (optional) override the API endpoint path
    MCP_TRANSPORT      — (optional) transport protocol: stdio | sse | streamable-http (default: stdio)
"""
import sys
import os

# Ensure the project root is on sys.path so all modules resolve correctly
# when the server is invoked from an external working directory.
sys.path.insert(0, os.path.dirname(__file__))

_VALID_TRANSPORTS = ("stdio", "sse", "streamable-http")

# ── Resolve transport and configure FASTMCP env vars ──────────────────────────
# This MUST happen before `from server import mcp` because FastMCP reads its
# Settings (host, port) from the environment at construction time.
_transport = os.environ.get("MCP_TRANSPORT", "stdio").strip().lower()
if _transport not in _VALID_TRANSPORTS:
    print(
        f"[sg-mrt-exits-mcp] Invalid MCP_TRANSPORT '{_transport}'. "
        f"Must be one of: {', '.join(_VALID_TRANSPORTS)}. Falling back to stdio.",
        file=sys.stderr,
    )
    _transport = "stdio"

if _transport in ("sse", "streamable-http"):
    # Bind to all interfaces on the platform-assigned port so the server is
    # reachable in deployed environments (Replit, Railway, Fly, etc.).
    # Priority: $PORT (platform-assigned) → FASTMCP_PORT (user override) → 8000 (default)
    _port = os.environ.get("PORT") or os.environ.get("FASTMCP_PORT", "8000")
    os.environ["FASTMCP_HOST"] = os.environ.get("FASTMCP_HOST", "0.0.0.0")
    os.environ["FASTMCP_PORT"] = str(_port)

# ── Import server AFTER env vars are set ──────────────────────────────────────
from server import mcp  # noqa: E402

if __name__ == "__main__":
    mcp.run(transport=_transport)  # type: ignore[arg-type]
