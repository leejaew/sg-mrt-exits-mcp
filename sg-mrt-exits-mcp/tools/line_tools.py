from api_client import fetch_exits, fetch_all_exits
from geo_utils import (
    format_coords_plain,
    display_station_name,
    bounding_box_description,
)
from line_lookup import resolve_line_code, get_stations_for_line


async def list_exits_by_line(line_code: str) -> str:
    """
    List all MRT exits on a specific MRT/LRT line.

    Accepts a line code (e.g. 'TEL', 'NSL', 'CCL') or a full line name
    (e.g. 'Thomson-East Coast Line', 'Downtown Line'). Exits are grouped
    by station and described in plain text.
    """
    resolved = resolve_line_code(line_code)
    if resolved is None:
        return (
            f"Unrecognised line: '{line_code}'. Valid codes include: "
            "NSL, EWL, NEL, CCL, DTL, TEL, BPL, SLRT, PLRT. "
            "Full names like 'Thomson-East Coast Line' are also accepted."
        )

    stations = get_stations_for_line(resolved)
    if not stations:
        return f"No stations found for line '{resolved}'."

    lines_out: list[str] = [
        f"MRT exits on the {resolved} ({line_code.upper()}) line:\n"
    ]
    total_exits = 0

    for station_na in sorted(stations):
        exits = await fetch_exits(station_name=station_na)
        if isinstance(exits, str) or not exits:
            continue
        display = display_station_name(station_na)
        lines_out.append(f"\n{display} ({len(exits)} exit(s)):")
        for e in sorted(exits, key=lambda x: x["exit_code"]):
            coords = format_coords_plain(e["lat"], e["lng"])
            lines_out.append(f"  • {e['exit_code']} — {coords}")
        total_exits += len(exits)

    lines_out.append(f"\nTotal: {total_exits} exits across {len(stations)} station(s).")
    return "\n".join(lines_out)


async def get_station_footprint(station_name: str) -> str:
    """
    Get the complete spatial footprint of a station — all its exits with
    coordinates — to understand how it spreads across street level.

    Returns a list of exits, their coordinates, and a plain-text spread summary
    describing the bounding box (north-south and east-west span in metres).
    """
    exits = await fetch_exits(station_name=station_name)
    if isinstance(exits, str):
        return exits
    if not exits:
        return (
            f"No MRT exits found matching '{station_name}'. "
            "Try a broader search term or check the station name."
        )

    station_na = exits[0]["station_na"]
    display = display_station_name(station_na)
    bbox = bounding_box_description(exits)

    lines: list[str] = [
        f"Spatial footprint of {display} ({len(exits)} exit(s)):\n"
    ]
    for e in sorted(exits, key=lambda x: x["exit_code"]):
        coords = format_coords_plain(e["lat"], e["lng"])
        lines.append(f"  • {e['exit_code']} — {coords}")

    lines.append(f"\nSpread summary: {bbox}")
    return "\n".join(lines)


def register(mcp) -> None:
    mcp.tool()(list_exits_by_line)
    mcp.tool()(get_station_footprint)
