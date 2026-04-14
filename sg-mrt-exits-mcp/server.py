"""
MCP server setup and tool registration for sg-mrt-exits-mcp.

All 15 tools are registered here by importing each tools module and
calling its register() function with the shared FastMCP instance.

host and port are read from environment variables at construction time.
main.py sets FASTMCP_HOST and FASTMCP_PORT before importing this module
so that HTTP transports bind correctly in deployed environments.
"""
import os
from mcp.server.fastmcp import FastMCP
from config import MCP_SERVER_NAME

from tools import search_tools
from tools import map_tools
from tools import spatial_tools
from tools import line_tools
from tools import location_tools
from tools import navigation_tools

mcp = FastMCP(
    MCP_SERVER_NAME,
    host=os.environ.get("FASTMCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("FASTMCP_PORT", "8000")),
)

# ── Tool registration ─────────────────────────────────────────────────────────
search_tools.register(mcp)     # search_exits_by_station, get_exit_detail
map_tools.register(mcp)        # get_exit_map_view
spatial_tools.register(mcp)    # find_nearest_exit_by_coordinates,
                                # find_nearest_exit_by_landmark,
                                # find_exits_within_radius,
                                # urban_planning_exit_density
line_tools.register(mcp)       # list_exits_by_line, get_station_footprint
location_tools.register(mcp)   # retail_proximity_analysis, accessibility_check,
                                # logistics_delivery_planning
navigation_tools.register(mcp) # emergency_response_exits, tourist_guide_exits,
                                # commuter_exit_comparison
