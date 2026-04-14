from api_client import fetch_all_exits, fetch_exits
from geocoding import resolve_landmark_or_error
from geo_utils import (
    haversine_meters,
    format_coords_plain,
    format_distance,
    display_station_name,
)
from maps_links import maps_link_block


async def _resolve_coords(
    latitude: float | None,
    longitude: float | None,
    landmark_name: str | None,
) -> tuple[float, float] | str:
    """Helper: resolve a location from coords or landmark, returning error str on failure."""
    if latitude is not None and longitude is not None:
        return latitude, longitude
    if landmark_name:
        return await resolve_landmark_or_error(landmark_name)
    return "Please provide either coordinates (latitude + longitude) or a landmark_name."


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
    coords = await _resolve_coords(latitude, longitude, landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    nearby = sorted(
        [(e, haversine_meters(lat, lng, e["lat"], e["lng"])) for e in exits],
        key=lambda x: x[1],
    )
    nearby = [(e, d) for e, d in nearby if d <= radius_metres]

    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not nearby:
        return (
            f"No MRT exits found within {format_distance(radius_metres)} of "
            f"'{location_desc}'. This location has limited transit access."
        )

    by_station: dict[str, list[tuple]] = {}
    for e, d in nearby:
        by_station.setdefault(e["station_na"], []).append((e, d))

    nearest_e, nearest_d = nearby[0]
    nearest_display = display_station_name(nearest_e["station_na"])

    lines = [
        f"Retail proximity analysis for '{location_desc}':\n",
        f"Radius:         {format_distance(radius_metres)}",
        f"Total exits:    {len(nearby)}",
        f"Stations:       {len(by_station)}\n",
        "Breakdown by station:",
    ]
    for station_na, station_exits in sorted(by_station.items()):
        display = display_station_name(station_na)
        exit_summary = ", ".join(
            f"{e['exit_code']} ({format_distance(d)})" for e, d in station_exits
        )
        lines.append(f"  • {display}: {exit_summary}")

    lines.append(
        f"\nSummary: This location has {len(nearby)} MRT exit(s) within "
        f"{format_distance(radius_metres)}, with the closest being "
        f"{nearest_display} {nearest_e['exit_code']} at {format_distance(nearest_d)}. "
        f"{'Strong' if len(nearby) >= 4 else 'Good' if len(nearby) >= 2 else 'Limited'} "
        f"pedestrian transit access."
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
    coords = await _resolve_coords(latitude, longitude, landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    nearby = sorted(
        [(e, haversine_meters(lat, lng, e["lat"], e["lng"])) for e in exits],
        key=lambda x: x[1],
    )
    nearby = [(e, d) for e, d in nearby if d <= radius_metres]

    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not nearby:
        return (
            f"No MRT exits found within {format_distance(radius_metres)} of "
            f"'{location_desc}'."
        )

    lines = [
        f"Nearby MRT exits within {format_distance(radius_metres)} of '{location_desc}':\n"
    ]
    for e, d in nearby:
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
    coords = await _resolve_coords(latitude, longitude, landmark_name)
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
        from maps_links import make_maps_directions_link
        directions = make_maps_directions_link(e["lat"], e["lng"])
        lines.append(
            f"{i}. {display} — {e['exit_code']} ({format_distance(dist)})\n"
            f"   Directions: {directions}"
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
    coords = await _resolve_coords(latitude, longitude, landmark_name)
    if isinstance(coords, str):
        return coords
    lat, lng = coords

    exits = await fetch_all_exits()
    if isinstance(exits, str):
        return exits

    nearby = sorted(
        [(e, haversine_meters(lat, lng, e["lat"], e["lng"])) for e in exits],
        key=lambda x: x[1],
    )
    nearby = [(e, d) for e, d in nearby if d <= radius_metres]

    location_desc = landmark_name if landmark_name else format_coords_plain(lat, lng)

    if not nearby:
        return (
            f"No MRT exits within {format_distance(radius_metres)} of "
            f"'{location_desc}'. Limited pedestrian transit access for this delivery zone."
        )

    nearest_e, nearest_d = nearby[0]
    nearest_display = display_station_name(nearest_e["station_na"])

    lines = [
        f"Logistics delivery analysis for '{location_desc}':\n"
    ]
    for e, d in nearby:
        display = display_station_name(e["station_na"])
        lines.append(f"  • {display} — {e['exit_code']} ({format_distance(d)})")

    transit_strength = (
        "strong" if len(nearby) >= 4 else "good" if len(nearby) >= 2 else "limited"
    )
    lines.append(
        f"\nSummary: {len(nearby)} MRT exit(s) within {format_distance(radius_metres)} "
        f"of this delivery address, suggesting {transit_strength} pedestrian transit access. "
        f"Nearest is {nearest_display} {nearest_e['exit_code']} at {format_distance(nearest_d)}."
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

    lines = [
        f"Tourist guide — MRT exits near '{destination}':\n"
    ]
    for i, e in enumerate(ranked, 1):
        dist = haversine_meters(lat, lng, e["lat"], e["lng"])
        display = display_station_name(e["station_na"])
        entry = (
            f"{i}. {display} — {e['exit_code']} "
            f"(approximately {format_distance(dist)} from {destination})"
        )
        if include_map_links:
            from maps_links import make_maps_view_link, make_maps_directions_link
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
    exits = await fetch_exits(station_name=station_name)
    if isinstance(exits, str):
        return exits
    if not exits:
        return (
            f"No MRT exits found matching '{station_name}'. "
            "Try a broader search term or check the station name."
        )

    display = display_station_name(exits[0]["station_na"])

    # Resolve destination coordinates if any
    dest_lat: float | None = None
    dest_lng: float | None = None

    if destination_latitude is not None and destination_longitude is not None:
        dest_lat, dest_lng = destination_latitude, destination_longitude
    elif destination_landmark:
        coords = await resolve_landmark_or_error(destination_landmark)
        if isinstance(coords, str):
            return coords
        dest_lat, dest_lng = coords

    if dest_lat is not None and dest_lng is not None:
        ranked = sorted(
            exits,
            key=lambda e: haversine_meters(dest_lat, dest_lng, e["lat"], e["lng"]),
        )
        dest_desc = destination_landmark if destination_landmark else format_coords_plain(
            dest_lat, dest_lng
        )
        lines = [
            f"{display} exits ranked by distance to '{dest_desc}':\n"
        ]
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
    mcp.tool()(retail_proximity_analysis)
    mcp.tool()(accessibility_check)
    mcp.tool()(emergency_response_exits)
    mcp.tool()(logistics_delivery_planning)
    mcp.tool()(tourist_guide_exits)
    mcp.tool()(commuter_exit_comparison)
