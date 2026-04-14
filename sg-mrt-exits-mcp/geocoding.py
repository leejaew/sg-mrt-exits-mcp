import asyncio
import sys
import time
import httpx
from config import NOMINATIM_BASE_URL, NOMINATIM_USER_AGENT

# ── Nominatim rate limiter ────────────────────────────────────────────────────
# Nominatim's usage policy requires a maximum of 1 request per second.
# _NOMINATIM_LOCK ensures requests are serialised; _last_call tracks timing
# so we sleep the remaining fraction of a second between calls.
_NOMINATIM_LOCK: asyncio.Semaphore = asyncio.Semaphore(1)
_last_nominatim_call: float = 0.0
_NOMINATIM_MIN_INTERVAL: float = 1.0  # seconds

# ── Landmark coordinate cache ─────────────────────────────────────────────────
# Geographic coordinates of named places don't change, so successful lookups
# are cached indefinitely for the lifetime of the process. Only successful
# results are cached — failed lookups (None) are not stored so that a user
# who retries with a corrected name gets a fresh attempt.
_landmark_cache: dict[str, tuple[float, float]] = {}


async def resolve_landmark(landmark_name: str) -> tuple[float, float] | None:
    """
    Geocode a landmark or address name in Singapore using Nominatim (OpenStreetMap).

    Always appends ', Singapore' to constrain results.
    Enforces Nominatim's 1 req/sec rate limit.
    Caches successful results in memory for the process lifetime — coordinates
    of named places don't change, so repeated lookups of the same landmark
    skip the rate-limit wait entirely and return in < 0.1 ms.
    Returns (latitude, longitude) or None if the lookup fails.
    """
    global _last_nominatim_call

    # Cache hit: return immediately without touching Nominatim
    cache_key = landmark_name.strip().lower()
    if cache_key in _landmark_cache:
        return _landmark_cache[cache_key]

    query = f"{landmark_name}, Singapore"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": NOMINATIM_USER_AGENT}

    async with _NOMINATIM_LOCK:
        # Re-check inside lock: another coroutine may have just populated it
        if cache_key in _landmark_cache:
            return _landmark_cache[cache_key]

        now = time.monotonic()
        elapsed = now - _last_nominatim_call
        if elapsed < _NOMINATIM_MIN_INTERVAL:
            await asyncio.sleep(_NOMINATIM_MIN_INTERVAL - elapsed)
        _last_nominatim_call = time.monotonic()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(NOMINATIM_BASE_URL, params=params, headers=headers)
                response.raise_for_status()
                results = response.json()
                if results:
                    lat = float(results[0]["lat"])
                    lon = float(results[0]["lon"])
                    coords = (lat, lon)
                    _landmark_cache[cache_key] = coords  # cache on success only
                    return coords
                return None

        except httpx.TimeoutException:
            print(
                f"[geocoding] Nominatim request timed out for '{landmark_name}'.",
                file=sys.stderr,
            )
        except httpx.HTTPStatusError as exc:
            print(
                f"[geocoding] Nominatim returned HTTP {exc.response.status_code} "
                f"for '{landmark_name}'.",
                file=sys.stderr,
            )
        except Exception as exc:
            print(
                f"[geocoding] Unexpected error resolving '{landmark_name}': "
                f"{type(exc).__name__}: {exc}",
                file=sys.stderr,
            )

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


async def resolve_coords_or_error(
    latitude: float | None,
    longitude: float | None,
    landmark_name: str | None,
) -> tuple[float, float] | str:
    """
    Unified location resolver used by all tools that accept either coordinates
    or a landmark name.

    Priority: explicit coordinates → landmark name → error.
    Coordinates are validated against Singapore's bounding box before returning.

    Returns (lat, lng) on success, or a plain-text error string on failure.
    """
    from validators import validate_coordinates, validate_string

    if latitude is not None and longitude is not None:
        err = validate_coordinates(latitude, longitude)
        if err:
            return err
        return latitude, longitude

    if landmark_name:
        err = validate_string(landmark_name, "landmark_name")
        if err:
            return err
        return await resolve_landmark_or_error(landmark_name)

    return "Please provide either coordinates (latitude + longitude) or a landmark_name."
