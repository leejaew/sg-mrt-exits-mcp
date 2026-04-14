"""
Input validation helpers for sg-mrt-exits-mcp.

All validators return None on success, or a plain-text error string
that can be returned directly to the MCP caller.
"""
import math

# Singapore approximate bounding box
_SG_LAT_MIN: float = 1.15
_SG_LAT_MAX: float = 1.50
_SG_LNG_MIN: float = 103.57
_SG_LNG_MAX: float = 104.10

_MAX_RADIUS_METRES: int = 50_000
_MIN_RADIUS_METRES: int = 1
_MAX_TOP_N: int = 20
_MIN_TOP_N: int = 1
_MAX_STRING_LEN: int = 200


def validate_coordinates(lat: float, lng: float) -> str | None:
    """Return an error string if lat/lng are invalid; None if OK."""
    if math.isnan(lat) or math.isinf(lat):
        return "latitude must be a finite number."
    if math.isnan(lng) or math.isinf(lng):
        return "longitude must be a finite number."
    if not (-90.0 <= lat <= 90.0):
        return f"latitude {lat} is out of range (must be between -90 and 90)."
    if not (-180.0 <= lng <= 180.0):
        return f"longitude {lng} is out of range (must be between -180 and 180)."
    if not (_SG_LAT_MIN <= lat <= _SG_LAT_MAX) or not (_SG_LNG_MIN <= lng <= _SG_LNG_MAX):
        return (
            f"Coordinates ({lat}, {lng}) appear to be outside Singapore. "
            f"Expected latitude {_SG_LAT_MIN}–{_SG_LAT_MAX}, "
            f"longitude {_SG_LNG_MIN}–{_SG_LNG_MAX}."
        )
    return None


def validate_radius(radius_metres: int) -> str | None:
    """Return an error string if radius_metres is out of bounds; None if OK."""
    if radius_metres < _MIN_RADIUS_METRES:
        return f"radius_metres must be at least {_MIN_RADIUS_METRES}."
    if radius_metres > _MAX_RADIUS_METRES:
        return f"radius_metres must not exceed {_MAX_RADIUS_METRES:,} (50 km)."
    return None


def validate_top_n(top_n: int) -> str | None:
    """Return an error string if top_n is out of bounds; None if OK."""
    if top_n < _MIN_TOP_N:
        return f"top_n must be at least {_MIN_TOP_N}."
    if top_n > _MAX_TOP_N:
        return f"top_n must not exceed {_MAX_TOP_N}."
    return None


def validate_string(value: str, field: str = "input") -> str | None:
    """Return an error string if value is empty or too long; None if OK."""
    if not value or not value.strip():
        return f"'{field}' must not be empty."
    if len(value) > _MAX_STRING_LEN:
        return f"'{field}' is too long (max {_MAX_STRING_LEN} characters)."
    return None
