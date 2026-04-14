"""
Entry point for the sg-mrt-exits-mcp MCP server.

Run with:
    python main.py

Transport is controlled by the MCP_TRANSPORT environment variable:
    stdio            — default; for Claude Desktop, Claude API, and local clients
    sse              — HTTP/SSE; for Claude.ai, Cursor, Windsurf, and SSE-compatible clients
    streamable-http  — HTTP/Streamable HTTP; for Manus AI and clients supporting the newer transport

Configuration is read from environment variables (Replit Secrets or .env):
    API_BASE_URL       — base URL of the api.jael.ee endpoint (required)
    API_USERNAME       — api.jael.ee API username
    API_TOKEN          — api.jael.ee API token
    API_ENDPOINT_PATH  — (optional) override the API endpoint path
    MCP_TRANSPORT      — (optional) transport protocol: stdio | sse | streamable-http (default: stdio)
"""
import sys
import os
from typing import Literal

# Ensure the project root is on sys.path so all modules resolve correctly
# when the server is invoked from an external working directory.
sys.path.insert(0, os.path.dirname(__file__))

from server import mcp

_VALID_TRANSPORTS = ("stdio", "sse", "streamable-http")

if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio").strip().lower()
    if transport not in _VALID_TRANSPORTS:
        print(
            f"[sg-mrt-exits-mcp] Invalid MCP_TRANSPORT '{transport}'. "
            f"Must be one of: {', '.join(_VALID_TRANSPORTS)}. Falling back to stdio.",
            file=sys.stderr,
        )
        transport = "stdio"
    mcp.run(transport=transport)  # type: ignore[arg-type]
