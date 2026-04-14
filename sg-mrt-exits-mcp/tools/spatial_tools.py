from api_client import fetch_all_exits
from geocoding import resolve_coords_or_error, resolve_landmark_or_error
from geo_utils import (
    haversine_meters,
    format_coords_plain,
    format_distance,
    display_station_name,
    bounding_box_description,
    nearby_exits,
)
from validators import validate_coordinates, validate_radius, validate_top_n, validate_string


async def find_nearest_exit_by_coordinates(
    latitude: float,
    longitude: float,
    top_n: int = 3,
) -> str:
    """
    Find the closest MRT exits to a given latitude and longitude.

    Fetches all exits and ranks by Haversine distance. Returns the top_n nearest
    exits with station name, exit code, and distance in metres.
    """
    err = validate_coordinates(latitude, longitude) or validate_top_n(top_n)
    if err:
        return err

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits
    if not exits:
        return "No MRT exit data is available at this time."

    ranked = sorted(
        exits,
        key=lambda e: haversine_meters(latitude, longitude, e["lat"], e["lng"]),
    )[:top_n]

    lines = [f"Nearest {len(ranked)} MRT exit(s) to {format_coords_plain(latitude, longitude)}:\n"]
    for i, e in enumerate(ranked, 1):
        dist = haversine_meters(latitude, longitude, e["lat"], e["lng"])
        display = display_station_name(e["station_na"])
        lines.append(f"{i}. {display} — {e['exit_code']} ({format_distance(dist)})")
    return "\n".join(lines)


async def find_nearest_exit_by_landmark(
    landmark_name: str,
    top_n: int = 3,
) -> str:
    """
    Find the closest MRT exits to a named landmark or address in Singapore.

    Examples: 'Jewel Changi Airport', 'NUS', 'Marina Bay Sands'.
    Geocodes the landmark via OpenStreetMap, then ranks all exits by distance.
    """
    err = validate_string(landmark_name, "landmark_name") or validate_top_n(top_n)
    if err:
        return err

    coords = await resolve_landmark_or_error(landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits
    if not exits:
        return "No MRT exit data is available at this time."

    ranked = sorted(
        exits,
        key=lambda e: haversine_meters(lat, lng, e["lat"], e["lng"]),
    )[:top_n]

    lines = [
        f"Landmark resolved: '{landmark_name}' → {format_coords_plain(lat, lng)}\n",
        f"Nearest {len(ranked)} MRT exit(s):\n",
    ]
    for i, e in enumerate(ranked, 1):
        dist = haversine_meters(lat, lng, e["lat"], e["lng"])
        display = display_station_name(e["station_na"])
        lines.append(f"{i}. {display} — {e['exit_code']} ({format_distance(dist)})")
    return "\n".join(lines)


async def find_exits_within_radius(
    radius_metres: int,
    latitude: float | None = None,
    longitude: float | None = None,
    landmark_name: str | None = None,
) -> str:
    """
    Find all MRT exits within a specified radius (in metres) of a location.

    Supply either (latitude + longitude) or landmark_name. Results are sorted
    by distance and include total count, station name, exit code, and distance.
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
    if not exits:
        return "No MRT exit data is available at this time."

    close = nearby_exits(exits, lat, lng, radius_metres)
    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not close:
        return (
            f"No MRT exits found within {format_distance(radius_metres)} of "
            f"'{location_desc}'."
        )

    lines = [
        f"Found {len(close)} exit(s) within {format_distance(radius_metres)} "
        f"of '{location_desc}':\n"
    ]
    for e, dist in close:
        display = display_station_name(e["station_na"])
        lines.append(f"  • {display} — {e['exit_code']} ({format_distance(dist)})")
    return "\n".join(lines)


async def urban_planning_exit_density(
    radius_metres: int,
    landmark_name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> str:
    """
    Analyse MRT exit density across a defined area.

    Useful for urban planning, crowd modelling, or infrastructure assessment.
    Returns exit count, unique stations, spatial spread, and a density summary.
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
    if not exits:
        return "No MRT exit data is available at this time."

    close = nearby_exits(exits, lat, lng, radius_metres)
    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not close:
        return (
            f"No MRT exits found within {format_distance(radius_metres)} "
            f"of '{location_desc}'."
        )

    exit_list = [e for e, _ in close]
    unique_stations = sorted({e["station_na"] for e in exit_list})
    station_display = [display_station_name(s) for s in unique_stations]
    bbox = bounding_box_description(exit_list)

    total = len(close)
    station_count = len(unique_stations)
    avg_spacing = (radius_metres * 2) / (total ** 0.5) if total > 0 else 0

    return (
        f"Urban density analysis — {format_distance(radius_metres)} radius "
        f"around '{location_desc}':\n\n"
        f"Total exits:       {total}\n"
        f"Unique stations:   {station_count} ({', '.join(station_display)})\n"
        f"Spatial spread:    {bbox}\n\n"
        f"Density summary: {total} exit(s) across {station_count} station(s) "
        f"within {format_distance(radius_metres)}, averaging approximately one exit "
        f"every {format_distance(avg_spacing)}."
    )


def register(mcp) -> None:
    mcp.tool()(find_nearest_exit_by_coordinates)
    mcp.tool()(find_nearest_exit_by_landmark)
    mcp.tool()(find_exits_within_radius)
    mcp.tool()(urban_planning_exit_density)
