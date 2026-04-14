"""
Location-based spatial analysis tools.

These tools answer questions about MRT exit coverage around a specific point:
retail site selection, accessibility planning, and logistics delivery zoning.

All three tools share the same structure:
  1. Validate radius
  2. Resolve location (coordinates or landmark)
  3. Fetch full exit dataset (from cache)
  4. Filter to exits within radius via nearby_exits()
  5. Format and return domain-specific output
"""
from api_client import fetch_all_exits
from geocoding import resolve_coords_or_error
from geo_utils import format_coords_plain, format_distance, display_station_name, nearby_exits
from validators import validate_radius


async def retail_proximity_analysis(
    radius_metres: int = 500,
    latitude: float | None = None,
    longitude: float | None = None,
    landmark_name: str | None = None,
) -> str:
    """
    Analyse MRT exit density and proximity for a location to assist with retail
    site selection, lease pricing context, or footfall estimation.

    Answers questions like 'how many MRT exits are within 300 metres of this address?'
    Returns total exits, breakdown by station, nearest exit and distance, and a
    plain-text summary suited to retail or real estate contexts.
    """
    err = validate_radius(radius_metres)
    if err:
        return err

    coords = await resolve_coords_or_error(latitude, longitude, landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    close = nearby_exits(exits, lat, lng, radius_metres)
    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not close:
        return (
            f"No MRT exits found within {format_distance(radius_metres)} of "
            f"'{location_desc}'. This location has limited transit access."
        )

    by_station: dict[str, list[tuple]] = {}
    for e, d in close:
        by_station.setdefault(e["station_na"], []).append((e, d))

    nearest_e, nearest_d = close[0]
    nearest_display = display_station_name(nearest_e["station_na"])

    lines = [
        f"Retail proximity analysis for '{location_desc}':\n",
        f"Radius:         {format_distance(radius_metres)}",
        f"Total exits:    {len(close)}",
        f"Stations:       {len(by_station)}\n",
        "Breakdown by station:",
    ]
    for station_na, station_exits in sorted(by_station.items()):
        display = display_station_name(station_na)
        exit_summary = ", ".join(
            f"{e['exit_code']} ({format_distance(d)})" for e, d in station_exits
        )
        lines.append(f"  • {display}: {exit_summary}")

    strength = "Strong" if len(close) >= 4 else "Good" if len(close) >= 2 else "Limited"
    lines.append(
        f"\nSummary: This location has {len(close)} MRT exit(s) within "
        f"{format_distance(radius_metres)}, with the closest being "
        f"{nearest_display} {nearest_e['exit_code']} at {format_distance(nearest_d)}. "
        f"{strength} pedestrian transit access."
    )
    return "\n".join(lines)


async def accessibility_check(
    radius_metres: int = 500,
    latitude: float | None = None,
    longitude: float | None = None,
    landmark_name: str | None = None,
) -> str:
    """
    Identify MRT exits near a location and flag accessibility considerations.

    Since barrier-free access data is not available in the API, this tool lists
    nearby exits and directs users to LTA's official accessibility resources to
    verify barrier-free routes.
    """
    err = validate_radius(radius_metres)
    if err:
        return err

    coords = await resolve_coords_or_error(latitude, longitude, landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    close = nearby_exits(exits, lat, lng, radius_metres)
    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not close:
        return (
            f"No MRT exits found within {format_distance(radius_metres)} of "
            f"'{location_desc}'."
        )

    lines = [
        f"Nearby MRT exits within {format_distance(radius_metres)} of '{location_desc}':\n"
    ]
    for e, d in close:
        display = display_station_name(e["station_na"])
        lines.append(f"  • {display} — {e['exit_code']} ({format_distance(d)})")

    lines.append(
        "\nAccessibility note: Barrier-free access data (lifts, ramps, tactile paths) "
        "is not available through this API. Please verify barrier-free routes via "
        "LTA's official accessibility resources:\n"
        "https://www.lta.gov.sg/content/ltagov/en/getting_around/public_transport/"
        "mrt_and_lrt/accessibility.html"
    )
    return "\n".join(lines)


async def logistics_delivery_planning(
    radius_metres: int = 400,
    landmark_name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> str:
    """
    Identify MRT exits near a delivery zone or address for last-mile logistics planning.

    Useful for courier pickup zones, delivery locker positioning, or pedestrian
    transit access assessment for delivery addresses.
    """
    err = validate_radius(radius_metres)
    if err:
        return err

    coords = await resolve_coords_or_error(latitude, longitude, landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    close = nearby_exits(exits, lat, lng, radius_metres)
    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not close:
        return (
            f"No MRT exits within {format_distance(radius_metres)} of "
            f"'{location_desc}'. Limited pedestrian transit access for this delivery zone."
        )

    nearest_e, nearest_d = close[0]
    nearest_display = display_station_name(nearest_e["station_na"])
    strength = "strong" if len(close) >= 4 else "good" if len(close) >= 2 else "limited"

    lines = [f"Logistics delivery analysis for '{location_desc}':\n"]
    for e, d in close:
        display = display_station_name(e["station_na"])
        lines.append(f"  • {display} — {e['exit_code']} ({format_distance(d)})")

    lines.append(
        f"\nSummary: {len(close)} MRT exit(s) within {format_distance(radius_metres)} "
        f"of this delivery address, suggesting {strength} pedestrian transit access. "
        f"Nearest is {nearest_display} {nearest_e['exit_code']} at {format_distance(nearest_d)}."
    )
    return "\n".join(lines)


def register(mcp) -> None:
    mcp.tool()(retail_proximity_analysis)
    mcp.tool()(accessibility_check)
    mcp.tool()(logistics_delivery_planning)
