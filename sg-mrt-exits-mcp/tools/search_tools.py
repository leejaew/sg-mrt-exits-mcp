from api_client import fetch_exits
from geo_utils import format_coords_plain, display_station_name, format_timestamp, normalize_exit_code
from validators import validate_string


async def search_exits_by_station(station_name: str) -> str:
    """
    Search for all MRT exits belonging to a station by name.

    Supports full, partial, and wildcard searches — e.g. 'Orchard', '*hill',
    'bishan*', '*central*'. Returns a plain-text list of matching exits.
    """
    err = validate_string(station_name, "station_name")
    if err:
        return err

    result = await fetch_exits(station_name=station_name)
    if isinstance(result, str):
        return result
    if not result:
        return (
            f"No MRT exits found matching '{station_name}'. "
            "Try a broader search term or check the station name."
        )

    lines: list[str] = [
        f"Found {len(result)} exit(s) matching '{station_name}':\n"
    ]
    grouped: dict[str, list[dict]] = {}
    for exit_rec in result:
        grouped.setdefault(exit_rec["station_na"], []).append(exit_rec)

    for station_na, exits in sorted(grouped.items()):
        display = display_station_name(station_na)
        lines.append(f"\n{display} ({len(exits)} exit(s)):")
        for e in sorted(exits, key=lambda x: x["exit_code"]):
            coords = format_coords_plain(e["lat"], e["lng"])
            lines.append(f"  • {e['exit_code']} — {coords}")

    return "\n".join(lines)


async def get_exit_detail(station_name: str, exit_code: str) -> str:
    """
    Get full details for a specific exit at a named station.

    Returns station name, exit code, coordinates, and the last-updated date.
    """
    err = validate_string(station_name, "station_name") or validate_string(exit_code, "exit_code")
    if err:
        return err

    result = await fetch_exits(station_name=station_name)
    if isinstance(result, str):
        return result
    if not result:
        return (
            f"No MRT exits found matching '{station_name}'. "
            "Try a broader search term or check the station name."
        )

    normalised_code = normalize_exit_code(exit_code)
    match = next(
        (e for e in result if normalize_exit_code(e["exit_code"]) == normalised_code),
        None,
    )

    if match is None:
        available = ", ".join(sorted({e["exit_code"] for e in result}))
        return (
            f"Exit '{exit_code}' not found at station matching '{station_name}'. "
            f"Available exits: {available}. "
            f"Tip: you can pass just the letter or number (e.g. 'B') or the full label (e.g. 'Exit B')."
        )

    display = display_station_name(match["station_na"])
    coords = format_coords_plain(match["lat"], match["lng"])
    updated = format_timestamp(match["fmel_upd_d"])

    return (
        f"Station:      {display}\n"
        f"Exit code:    {match['exit_code']}\n"
        f"Location:     {coords}\n"
        f"Object ID:    {match['object_id']}\n"
        f"Last updated: {updated}"
    )


def register(mcp) -> None:
    mcp.tool()(search_exits_by_station)
    mcp.tool()(get_exit_detail)
