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


async def resolve_landmark(landmark_name: str) -> tuple[float, float] | None:
    """
    Geocode a landmark or address name in Singapore using Nominatim (OpenStreetMap).

    Always appends ', Singapore' to constrain results.
    Enforces Nominatim's 1 req/sec rate limit.
    Returns (latitude, longitude) or None if the lookup fails.
    """
    global _last_nominatim_call

    query = f"{landmark_name}, Singapore"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": NOMINATIM_USER_AGENT}

    async with _NOMINATIM_LOCK:
        # Enforce 1 req/sec rate limit
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
                    return lat, lon
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
