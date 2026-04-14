import httpx
from config import NOMINATIM_BASE_URL, NOMINATIM_USER_AGENT


async def resolve_landmark(landmark_name: str) -> tuple[float, float] | None:
    """
    Geocode a landmark or address name in Singapore using Nominatim (OpenStreetMap).

    Always appends ', Singapore' to constrain results.
    Returns (latitude, longitude) or None if the lookup fails.
    """
    query = f"{landmark_name}, Singapore"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": NOMINATIM_USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(NOMINATIM_BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            results = response.json()
            if results:
                lat = float(results[0]["lat"])
                lon = float(results[0]["lon"])
                return lat, lon
    except Exception:
        pass

    return None


async def resolve_landmark_or_error(landmark_name: str) -> tuple[float, float] | str:
    """
    Resolve landmark coordinates, returning a user-friendly error string on failure.
    Callers should check if the return value is a str (error) before using it as coords.
    """
    coords = await resolve_landmark(landmark_name)
    if coords is None:
        return (
            f"Could not resolve '{landmark_name}' to a location in Singapore. "
            "Please try a more specific name or provide coordinates directly."
        )
    return coords
