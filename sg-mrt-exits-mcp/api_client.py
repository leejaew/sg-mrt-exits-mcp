import asyncio
import base64
import re
import time
import httpx
from config import API_USERNAME, API_TOKEN, get_api_url, CACHE_TTL_SECONDS, API_MAX_CONCURRENCY
from geo_utils import parse_coordinates


# ── Outbound concurrency limiter ──────────────────────────────────────────────
# Caps the number of simultaneous requests to the upstream API, preventing
# a burst of tool calls from overwhelming api.jael.ee.
_API_SEMAPHORE: asyncio.Semaphore = asyncio.Semaphore(API_MAX_CONCURRENCY)

# ── Full-dataset cache ────────────────────────────────────────────────────────
# Caches the parsed exit list from fetch_all_exits() for CACHE_TTL_SECONDS.
# Uses a double-checked locking pattern to prevent cache stampedes: multiple
# concurrent callers that all miss the cache will wait on _cache_lock and only
# the first one will actually hit the API.
_cache: dict = {"data": None, "ts": 0.0}
_cache_lock: asyncio.Lock = asyncio.Lock()

# ── Pre-encoded auth header ───────────────────────────────────────────────────
# Compute once at module load rather than re-encoding on every API call.
_AUTH_HEADER: dict[str, str] | None = None


def _build_auth_header() -> dict[str, str]:
    """Return the Basic Auth header, encoding credentials once and caching."""
    global _AUTH_HEADER
    if _AUTH_HEADER is not None:
        return _AUTH_HEADER
    if not API_USERNAME or not API_TOKEN:
        raise ValueError(
            "API authentication failed. Please check API_USERNAME and API_TOKEN in Replit Secrets."
        )
    credentials = base64.b64encode(f"{API_USERNAME}:{API_TOKEN}".encode()).decode()
    # Only Authorization header — Content-Type is not appropriate on GET requests.
    _AUTH_HEADER = {"Authorization": f"Basic {credentials}"}
    return _AUTH_HEADER


def normalize_station_query(query: str) -> str:
    """
    Normalise a user-supplied station name query so searches are always
    case-insensitive regardless of how the caller typed the input.

    Rules:
      - Strip leading/trailing whitespace
      - Uppercase all alphabetic characters
      - Preserve wildcard characters (*) exactly as supplied

    Examples:
        'orchard'        → 'ORCHARD'
        'Bright Hill'    → 'BRIGHT HILL'
        '*hill'          → '*HILL'
        'bishan*'        → 'BISHAN*'
        '*central*'      → '*CENTRAL*'
        '  Dhoby Ghaut ' → 'DHOBY GHAUT'
    """
    return query.strip().upper()


def _wildcard_to_regex(pattern: str) -> re.Pattern:
    """
    Convert a normalised (uppercased) wildcard pattern to a compiled regex.

    Always compiled with re.IGNORECASE as a safety net so that even if the
    caller forgets to normalise, matching against the API's uppercase station
    names will still succeed.

    Wildcard semantics (* = zero or more characters):
        '*HILL'      → matches any station name ending with 'HILL'
        'BISHAN*'    → matches any station name starting with 'BISHAN'
        '*CENTRAL*'  → matches any station name containing 'CENTRAL'
        'ORCHARD'    → matches any station name containing 'ORCHARD'
                       (no wildcard → treated as a substring / contains match)
    """
    if "*" not in pattern:
        escaped = re.escape(pattern)
        return re.compile(escaped, re.IGNORECASE)

    parts = pattern.split("*")
    regex_body = ".*".join(re.escape(p) for p in parts)
    return re.compile(regex_body, re.IGNORECASE)


async def _fetch_raw(params: dict) -> list[dict] | str:
    """
    Internal: send one HTTP request to the API and return raw records or an
    error string. Concurrency is capped by _API_SEMAPHORE.
    """
    try:
        headers = _build_auth_header()
    except ValueError as exc:
        return str(exc)

    url = get_api_url()

    async with _API_SEMAPHORE:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 401:
                    return (
                        "API authentication failed. "
                        "Please check API_USERNAME and API_TOKEN in Replit Secrets."
                    )
                response.raise_for_status()
                return response.json()

        except httpx.ConnectError:
            return (
                "Unable to reach the MRT exits API. "
                "Please check your network connection and try again."
            )
        except httpx.TimeoutException:
            return "Request to the MRT exits API timed out. Please try again."
        except httpx.HTTPStatusError as exc:
            return f"API request failed with status {exc.response.status_code}."
        except Exception as exc:
            return f"Unexpected error contacting the API: {type(exc).__name__}."


async def fetch_exits(station_name: str | None = None) -> list[dict] | str:
    """
    Fetch MRT exit records from the api.jael.ee LTA MRT Station Exit API.

    Search is always **case-insensitive**. The query is normalised (stripped and
    uppercased) via normalize_station_query() before any processing, so callers
    may pass any mix of cases — 'orchard', 'Orchard', 'ORCHARD' all behave the
    same way.

    Supported query formats:
        - Plain text:  'orchard'        → substring match across all stations
        - Full name:   'ORCHARD MRT STATION' → exact API match
        - Prefix glob: 'bishan*'        → API-native prefix search
        - Suffix glob: '*hill'          → client-side fallback (regex)
        - Infix glob:  '*central*'      → client-side fallback (regex)

    Two-step search strategy:
        Step 1 — send the normalised (uppercased) query directly to the API.
                 This handles exact names and prefix globs efficiently.
        Step 2 — if the API returns 0 results, fetch all exits (from cache)
                 and apply the wildcard pattern locally (re.IGNORECASE).

    Returns:
        A list of parsed exit dicts, or a plain-text error string on failure.
    """
    if not station_name:
        return await fetch_all_exits()

    normalised = normalize_station_query(station_name)

    # Step 1: Try the API with the normalised query
    raw = await _fetch_raw({"properties[STATION_NA]": normalised})
    if isinstance(raw, str):
        return raw

    if raw:
        return _parse_records(raw)

    # Step 2: Client-side fallback — use cached full dataset + regex
    all_exits = await fetch_all_exits()
    if isinstance(all_exits, str):
        return all_exits

    pattern = _wildcard_to_regex(normalised)
    return [e for e in all_exits if pattern.search(e.get("station_na", ""))]


async def fetch_all_exits() -> list[dict] | str:
    """
    Fetch every exit across the entire MRT/LRT network, with TTL caching.

    The full dataset is cached in memory for CACHE_TTL_SECONDS (default 5 min)
    to avoid redundant API calls. A double-checked locking pattern prevents
    cache stampedes when multiple tool calls arrive concurrently.

    On API failure, stale cache is returned if available so that transient
    outages don't immediately break all tools.
    """
    now = time.monotonic()

    # Fast path: serve from cache without acquiring the lock
    if _cache["data"] is not None and (now - _cache["ts"]) < CACHE_TTL_SECONDS:
        return _cache["data"]

    # Cache miss: acquire lock, re-check inside (stampede prevention)
    async with _cache_lock:
        now = time.monotonic()
        if _cache["data"] is not None and (now - _cache["ts"]) < CACHE_TTL_SECONDS:
            return _cache["data"]

        raw = await _fetch_raw({})
        if isinstance(raw, str):
            # On transient failure, return stale cache if any rather than erroring
            if _cache["data"] is not None:
                return _cache["data"]
            return raw

        parsed = _parse_records(raw)
        _cache["data"] = parsed
        _cache["ts"] = time.monotonic()
        return parsed


def _parse_records(raw_records: list[dict]) -> list[dict]:
    """Convert raw API records into clean, normalised exit dicts."""
    parsed = []
    skipped = 0
    for record in raw_records:
        props = record.get("properties", {})
        coord_str = record.get("geometry", {}).get("coordinates", "")
        try:
            lat, lng = parse_coordinates(coord_str)
        except Exception:
            skipped += 1
            continue

        parsed.append(
            {
                "object_id": props.get("OBJECT_ID"),
                "station_na": props.get("STATION_NA", ""),
                "exit_code": props.get("EXIT_CODE", ""),
                "inc_crc": props.get("INC_CRC", ""),
                "fmel_upd_d": props.get("FMEL_UPD_D", 0.0),
                "lat": lat,
                "lng": lng,
            }
        )
    if skipped:
        import sys
        print(f"[api_client] Warning: skipped {skipped} record(s) with unparseable coordinates.", file=sys.stderr)
    return parsed
