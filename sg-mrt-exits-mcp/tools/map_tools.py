from api_client import fetch_exits
from geo_utils import format_coords_plain, display_station_name, normalize_exit_code
from maps_links import maps_link_block
from validators import validate_string


async def get_exit_map_view(station_name: str, exit_code: str) -> str:
    """
    Get the Google Maps view and directions links for a specific MRT exit.

    Use this tool only when the user explicitly requests a map view or directions.
    Returns the plain-text location description plus both Google Maps links.
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
    links = maps_link_block(match["lat"], match["lng"])

    return (
        f"Station: {display} — {match['exit_code']}\n"
        f"Location: {coords}\n\n"
        f"Google Maps links:\n{links}"
    )


def register(mcp) -> None:
    mcp.tool()(get_exit_map_view)
