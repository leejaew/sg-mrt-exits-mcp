"""
Navigation and routing tools.

These tools help users decide which MRT exit to use for a specific journey:
emergency first-responder routing, tourist guidance, and commuter exit comparison.
"""
from api_client import fetch_all_exits, fetch_exits
from geocoding import resolve_coords_or_error, resolve_landmark_or_error
from geo_utils import (
    haversine_meters,
    format_coords_plain,
    format_distance,
    display_station_name,
)
from maps_links import make_maps_view_link, make_maps_directions_link
from validators import validate_top_n, validate_string, validate_coordinates


async def emergency_response_exits(
    top_n: int = 5,
    latitude: float | None = None,
    longitude: float | None = None,
    landmark_name: str | None = None,
) -> str:
    """
    Find the nearest MRT exits to an incident location for emergency or first-responder use.

    Returns ranked exits with distance and a Google Maps directions link for each,
    to assist rapid navigation.
    """
    err = validate_top_n(top_n)
    if err:
        return err

    coords = await resolve_coords_or_error(latitude, longitude, landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    ranked = sorted(
        exits,
        key=lambda e: haversine_meters(lat, lng, e["lat"], e["lng"]),
    )[:top_n]

    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)
    lines = [
        f"Emergency response — nearest {len(ranked)} MRT exit(s) to '{location_desc}':\n"
    ]
    for i, e in enumerate(ranked, 1):
        dist = haversine_meters(lat, lng, e["lat"], e["lng"])
        display = display_station_name(e["station_na"])
        directions = make_maps_directions_link(e["lat"], e["lng"])
        lines.append(
            f"{i}. {display} — {e['exit_code']} ({format_distance(dist)})\n"
            f"   Directions: {directions}"
        )
    return "\n".join(lines)


async def tourist_guide_exits(
    destination: str,
    include_map_links: bool = False,
) -> str:
    """
    Help tourists find the best MRT exit for a Singapore attraction or landmark.

    Returns the closest exits with distances and a friendly plain-text description
    of which exit to use. Set include_map_links to true to add Google Maps links.
    """
    err = validate_string(destination, "destination")
    if err:
        return err

    coords = await resolve_landmark_or_error(destination)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    ranked = sorted(
        exits,
        key=lambda e: haversine_meters(lat, lng, e["lat"], e["lng"]),
    )[:5]

    lines = [f"Tourist guide — MRT exits near '{destination}':\n"]
    for i, e in enumerate(ranked, 1):
        dist = haversine_meters(lat, lng, e["lat"], e["lng"])
        display = display_station_name(e["station_na"])
        entry = (
            f"{i}. {display} — {e['exit_code']} "
            f"(approximately {format_distance(dist)} from {destination})"
        )
        if include_map_links:
            entry += (
                f"\n   Map: {make_maps_view_link(e['lat'], e['lng'])}"
                f"\n   Directions: {make_maps_directions_link(e['lat'], e['lng'])}"
            )
        lines.append(entry)

    nearest = ranked[0]
    nearest_display = display_station_name(nearest["station_na"])
    nearest_dist = haversine_meters(lat, lng, nearest["lat"], nearest["lng"])
    lines.append(
        f"\nRecommendation: Take {nearest_display} station and use "
        f"{nearest['exit_code']}, which is {format_distance(nearest_dist)} "
        f"from {destination}."
    )
    return "\n".join(lines)


async def commuter_exit_comparison(
    station_name: str,
    destination_landmark: str | None = None,
    destination_latitude: float | None = None,
    destination_longitude: float | None = None,
) -> str:
    """
    Compare all exits at a station — useful when a commuter needs to know which
    exit is closest to their actual destination within a neighbourhood.

    If a destination is provided, exits are ranked by distance to it.
    Otherwise all exits are listed with plain-text coordinates.
    """
    err = validate_string(station_name, "station_name")
    if err:
        return err

    if destination_latitude is not None and destination_longitude is not None:
        err = validate_coordinates(destination_latitude, destination_longitude)
        if err:
            return err
    elif destination_landmark:
        err = validate_string(destination_landmark, "destination_landmark")
        if err:
            return err

    exits = await fetch_exits(station_name=station_name)
    if isinstance(exits, str):
        return exits
    if not exits:
        return (
            f"No MRT exits found matching '{station_name}'. "
            "Try a broader search term or check the station name."
        )

    display = display_station_name(exits[0]["station_na"])

    dest_lat: float | None = None
    dest_lng: float | None = None

    if destination_latitude is not None and destination_longitude is not None:
        dest_lat, dest_lng = destination_latitude, destination_longitude
    elif destination_landmark:
        dest_coords = await resolve_landmark_or_error(destination_landmark)
        if isinstance(dest_coords, str):
            return dest_coords
        dest_lat, dest_lng = dest_coords

    if dest_lat is not None and dest_lng is not None:
        ranked = sorted(
            exits,
            key=lambda e: haversine_meters(dest_lat, dest_lng, e["lat"], e["lng"]),
        )
        dest_desc = destination_landmark if destination_landmark else format_coords_plain(
            dest_lat, dest_lng
        )
        lines = [f"{display} exits ranked by distance to '{dest_desc}':\n"]
        for i, e in enumerate(ranked, 1):
            dist = haversine_meters(dest_lat, dest_lng, e["lat"], e["lng"])
            exit_coords = format_coords_plain(e["lat"], e["lng"])
            lines.append(
                f"{i}. {e['exit_code']} — {format_distance(dist)} from destination "
                f"(exit at {exit_coords})"
            )
        lines.append(f"\nBest exit: {ranked[0]['exit_code']}")
    else:
        lines = [f"All exits at {display}:\n"]
        for e in sorted(exits, key=lambda x: x["exit_code"]):
            coords = format_coords_plain(e["lat"], e["lng"])
            lines.append(f"  • {e['exit_code']} — {coords}")

    return "\n".join(lines)


def register(mcp) -> None:
    mcp.tool()(emergency_response_exits)
    mcp.tool()(tourist_guide_exits)
    mcp.tool()(commuter_exit_comparison)
