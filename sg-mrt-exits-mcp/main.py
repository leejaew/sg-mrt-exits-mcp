"""
Entry point for the sg-mrt-exits-mcp MCP server.

Run with:
    python main.py

The server uses stdio transport (default for MCP), making it compatible with
Claude Desktop, Claude API tool-use, and any MCP-compliant client.

Configuration is read from environment variables (Replit Secrets or .env):
    API_BASE_URL       — base URL of the api.jael.ee endpoint (required)
    API_USERNAME       — api.jael.ee API username
    API_TOKEN          — api.jael.ee API token
    API_ENDPOINT_PATH  — (optional) override the API endpoint path
"""
import sys
import os

# Ensure the project root is on sys.path so all modules resolve correctly
# when the server is invoked from an external working directory.
sys.path.insert(0, os.path.dirname(__file__))

from server import mcp

if __name__ == "__main__":
    mcp.run()
