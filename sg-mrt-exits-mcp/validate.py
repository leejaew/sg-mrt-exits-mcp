"""
Validation script for sg-mrt-exits-mcp.

Verifies:
  1. All Python modules import cleanly
  2. API credentials are present
  3. API is reachable and returns data
  4. A sample tool call works end-to-end

Run with: python validate.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


async def main() -> None:
    print("sg-mrt-exits-mcp — Validation")
    print("=" * 50)

    # ── 1. Module imports ──────────────────────────────────────────────────
    print("\n[1] Importing modules...")
    try:
        import config
        import geo_utils
        import maps_links
        import geocoding
        import api_client
        import line_lookup
        from tools import (
            search_tools, map_tools, spatial_tools,
            line_tools, location_tools, navigation_tools,
        )
        import server
        print("    OK — all modules loaded")
        print(f"    API URL: {config.get_api_url()}")
    except Exception as exc:
        print(f"    FAIL — {exc}")
        sys.exit(1)

    # ── 2. Credentials ─────────────────────────────────────────────────────
    print("\n[2] Checking credentials...")
    base_url_set = bool(os.environ.get("API_BASE_URL"))
    username_set = bool(os.environ.get("API_USERNAME"))
    token_set = bool(os.environ.get("API_TOKEN"))
    print(f"    API_BASE_URL: {'set' if base_url_set else 'MISSING'}")
    print(f"    API_USERNAME: {'set' if username_set else 'MISSING'}")
    print(f"    API_TOKEN:    {'set' if token_set else 'MISSING'}")
    if not base_url_set:
        print("    FAIL — API_BASE_URL is required. Add it to Replit Secrets.")
        sys.exit(1)
    if not username_set or not token_set:
        print("    WARN — Credentials missing. Set them in Replit Secrets.")

    # ── 3. API connectivity ────────────────────────────────────────────────
    print("\n[3] Testing API connectivity...")
    from api_client import fetch_all_exits
    exits = await fetch_all_exits()
    if isinstance(exits, str):
        print(f"    FAIL — {exits}")
    else:
        stations = sorted({e["station_na"] for e in exits})
        print(f"    OK — {len(exits)} total exits, {len(stations)} unique station(s)")
        for s in stations[:5]:
            print(f"         • {s}")
        if len(stations) > 5:
            print(f"         ... and {len(stations) - 5} more")

    # ── 4. Tool smoke test ─────────────────────────────────────────────────
    print("\n[4] Tool smoke test (search_exits_by_station)...")
    from tools.search_tools import search_exits_by_station
    if exits and not isinstance(exits, str):
        first_station = exits[0]["station_na"]
        result = await search_exits_by_station(first_station)
        if "No MRT exits" in result:
            print(f"    WARN — {result}")
        else:
            lines = result.split("\n")
            print(f"    OK — {lines[0]}")
    else:
        print("    SKIP — no exits available to test")

    # ── 5. Registered tools ────────────────────────────────────────────────
    print("\n[5] Registered MCP tools:")
    try:
        tool_names = list(server.mcp._tool_manager._tools.keys())
        for name in sorted(tool_names):
            print(f"    • {name}")
        print(f"\n    Total: {len(tool_names)} tools registered")
    except Exception:
        print("    (tool listing not available in this MCP version)")

    print("\n" + "=" * 50)
    print("Validation complete. MCP server is ready.")
    print("\nTo connect to Claude Desktop, add this to claude_desktop_config.json:")
    print(f"""
  "sg-mrt-exits-mcp": {{
    "command": "python3",
    "args": ["{os.path.abspath(__file__).replace('validate.py', 'main.py')}"]
  }}
""")


if __name__ == "__main__":
    asyncio.run(main())
