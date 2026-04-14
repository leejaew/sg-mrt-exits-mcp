import base64
import re
import httpx
from config import API_USERNAME, API_TOKEN, get_api_url
from geo_utils import parse_coordinates


def _build_auth_header() -> dict[str, str]:
    """Construct the Basic Auth header from stored credentials."""
    if not API_USERNAME or not API_TOKEN:
        raise ValueError(
            "API authentication failed. Please check API_USERNAME and API_TOKEN in Replit Secrets."
        )
    credentials = base64.b64encode(f"{API_USERNAME}:{API_TOKEN}".encode()).decode()
    return {
        "Content-Type": "application/json",
        "Authorization": f"Basic {credentials}",
    }


def _wildcard_to_regex(pattern: str) -> re.Pattern:
    """
    Convert a simple wildcard pattern (using * as glob) to a compiled regex.
    Case-insensitive. Used for client-side fallback filtering.

    Examples:
        '*hill'      → matches any station name ending with 'hill'
        'bishan*'    → matches any station name starting with 'bishan'
        '*central*'  → matches any station name containing 'central'
        'orchard'    → matches any station name containing 'orchard'
    """
    if "*" not in pattern:
        # Plain text: treat as contains match
        escaped = re.escape(pattern)
        return re.compile(escaped, re.IGNORECASE)

    # Convert glob wildcards to regex
    parts = pattern.split("*")
    regex = ".*".join(re.escape(p) for p in parts)
    return re.compile(regex, re.IGNORECASE)


async def _fetch_raw(params: dict) -> list[dict] | str:
    """Internal: send one HTTP request to the API and return raw records or error string."""
    try:
        headers = _build_auth_header()
    except ValueError as exc:
        return str(exc)

    url = get_api_url()

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
            f"Unable to reach the MRT exits API at {url}. "
            "Please check your network connection and try again."
        )
    except httpx.HTTPStatusError as exc:
        return f"API request failed with status {exc.response.status_code}."
    except Exception as exc:
        return f"Unexpected error contacting the API: {exc}"


async def fetch_exits(station_name: str | None = None) -> list[dict] | str:
    """
    Fetch MRT exit records from the LTA SheetLabs API.

    Args:
        station_name: Optional station name filter. Supports:
                      - Exact names:  "ORCHARD MRT STATION"
                      - Prefix glob:  "bishan*"
                      - Suffix glob:  "*hill"  (uses client-side fallback)
                      - Infix glob:   "*central*"  (uses client-side fallback)
                      - Plain text:   "orchard"  (client-side contains match)
                      The query is automatically uppercased for API requests.
                      When the API returns 0 results, a client-side fallback
                      fetches all exits and filters locally using wildcard matching.

    Returns:
        A list of parsed exit dicts, or a plain-text error string on failure.
        Each dict contains:
            - object_id   (int)
            - station_na  (str)
            - exit_code   (str)
            - inc_crc     (str)
            - fmel_upd_d  (float)
            - lat         (float)
            - lng         (float)
    """
    if not station_name:
        raw = await _fetch_raw({})
        if isinstance(raw, str):
            return raw
        return _parse_records(raw)

    # ── Step 1: Try the API filter directly (uppercased) ─────────────────────
    raw = await _fetch_raw({"properties[STATION_NA]": station_name.upper()})
    if isinstance(raw, str):
        return raw

    if raw:
        return _parse_records(raw)

    # ── Step 2: Client-side fallback ─────────────────────────────────────────
    # The API does not reliably support leading wildcards. Fetch everything and
    # filter locally using the wildcard pattern.
    all_raw = await _fetch_raw({})
    if isinstance(all_raw, str):
        return all_raw

    pattern = _wildcard_to_regex(station_name)
    matching = [
        r for r in all_raw
        if pattern.search(r.get("properties", {}).get("STATION_NA", ""))
    ]
    return _parse_records(matching)


def _parse_records(raw_records: list[dict]) -> list[dict]:
    """Convert raw API records into clean, normalised exit dicts."""
    parsed = []
    for record in raw_records:
        props = record.get("properties", {})
        coord_str = record.get("geometry", {}).get("coordinates", "")
        try:
            lat, lng = parse_coordinates(coord_str)
        except Exception:
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
    return parsed


async def fetch_all_exits() -> list[dict] | str:
    """Fetch every exit across the entire MRT/LRT network."""
    return await fetch_exits(station_name=None)
