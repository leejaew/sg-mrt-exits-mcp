import math


def parse_coordinates(coord_string: str) -> tuple[float, float]:
    """
    Parse the API coordinate string and return (latitude, longitude).

    The API returns coordinates as a string in GeoJSON order: "longitude, latitude".
    This function swaps them to the conventional (lat, lng) tuple.

    Example input:  "103.83363541399386, 1.3640371821656152"
    Example output: (1.3640371821656152, 103.83363541399386)
    """
    parts = coord_string.strip().split(", ")
    lng = float(parts[0])
    lat = float(parts[1])
    return lat, lng


def haversine_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return the great-circle distance in metres between two (lat, lng) points."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearby_exits(
    exits: list[dict],
    lat: float,
    lng: float,
    radius_metres: int,
) -> list[tuple[dict, float]]:
    """
    Return all exits within radius_metres of (lat, lng), sorted by ascending distance.

    Computes all distances in one pass, filters before sorting so we sort only
    the matching subset rather than the full dataset. Each element is a
    (exit_dict, distance_metres) tuple.
    """
    with_dist = [(e, haversine_meters(lat, lng, e["lat"], e["lng"])) for e in exits]
    return sorted(
        [(e, d) for e, d in with_dist if d <= radius_metres],
        key=lambda x: x[1],
    )


def format_coords_plain(lat: float, lng: float) -> str:
    """Return coordinates in human-readable plain text to 4 decimal places."""
    lat_dir = "N" if lat >= 0 else "S"
    lng_dir = "E" if lng >= 0 else "W"
    return f"{abs(lat):.4f}° {lat_dir}, {abs(lng):.4f}° {lng_dir}"


def format_distance(metres: float) -> str:
    """Format a distance value: metres under 1000 m, km with 2 d.p. otherwise."""
    if metres < 1000:
        return f"{round(metres)} metres"
    return f"{metres / 1000:.2f} km"


def display_station_name(station_na: str) -> str:
    """
    Strip the ' MRT STATION' or ' LRT STATION' suffix and title-case the result.
    Example: 'BRIGHT HILL MRT STATION' → 'Bright Hill'
    """
    upper = station_na.upper()
    for suffix in (" MRT STATION", " LRT STATION", " MRT", " LRT"):
        if upper.endswith(suffix):
            return station_na[: -len(suffix)].strip().title()
    return station_na.title()


def format_timestamp(fmel_upd_d: float) -> str:
    """
    Convert the FMEL_UPD_D float (e.g. 2.02512e13) to a YYYY-MM-DD string.
    The value encodes a date as YYYYMMDD followed by zeroed time components.
    """
    try:
        ts_str = str(int(fmel_upd_d))
        if len(ts_str) >= 8:
            year = ts_str[0:4]
            month = ts_str[4:6]
            day = ts_str[6:8]
            m, d = int(month), int(day)
            if 1 <= m <= 12 and 1 <= d <= 31:
                return f"{year}-{month}-{day}"
            if 1 <= m <= 12:
                return f"{year}-{month}"
            return f"~{year}"
        return ts_str
    except Exception:
        return str(fmel_upd_d)


def bounding_box_description(exits: list[dict]) -> str:
    """
    Given a list of parsed exit dicts (each with 'lat' and 'lng'),
    return a plain-text description of the spatial spread across all exits.
    """
    if not exits:
        return "No exits to analyse."
    lats = [e["lat"] for e in exits]
    lngs = [e["lng"] for e in exits]
    mid_lng = (min(lngs) + max(lngs)) / 2
    mid_lat = (min(lats) + max(lats)) / 2
    ns_span = haversine_meters(min(lats), mid_lng, max(lats), mid_lng)
    ew_span = haversine_meters(mid_lat, min(lngs), mid_lat, max(lngs))
    return (
        f"Exits span approximately {format_distance(ns_span)} north to south "
        f"and {format_distance(ew_span)} east to west."
    )
