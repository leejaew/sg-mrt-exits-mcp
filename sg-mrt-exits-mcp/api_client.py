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
        # Plain text: treat as a substring / contains match
        escaped = re.escape(pattern)
        return re.compile(escaped, re.IGNORECASE)

    # Convert glob wildcards to regex anchored at start/end
    parts = pattern.split("*")
    regex_body = ".*".join(re.escape(p) for p in parts)
    return re.compile(regex_body, re.IGNORECASE)


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
        Step 2 — if the API returns 0 results, fetch all exits and apply the
                 wildcard pattern locally (re.IGNORECASE). This handles leading
                 wildcards, infix globs, and plain-text partial searches that
                 the API does not support natively.

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

    # ── Normalise: strip whitespace + uppercase (case-insensitive entry point) ─
    normalised = normalize_station_query(station_name)

    # ── Step 1: Try the API with the normalised (uppercased) query ────────────
    raw = await _fetch_raw({"properties[STATION_NA]": normalised})
    if isinstance(raw, str):
        return raw

    if raw:
        return _parse_records(raw)

    # ── Step 2: Client-side fallback (leading wildcards / partial text) ────────
    # Build a regex from the normalised pattern. re.IGNORECASE is applied as an
    # additional safety net, though the pattern is already uppercased.
    all_raw = await _fetch_raw({})
    if isinstance(all_raw, str):
        return all_raw

    pattern = _wildcard_to_regex(normalised)
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
