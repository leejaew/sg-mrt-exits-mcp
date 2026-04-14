def make_maps_view_link(lat: float, lng: float) -> str:
    """Return a Google Maps view link for the given coordinates."""
    return f"https://www.google.com/maps?q={lat},{lng}"


def make_maps_directions_link(lat: float, lng: float) -> str:
    """Return a Google Maps directions link to the given coordinates."""
    return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"


def maps_link_block(lat: float, lng: float) -> str:
    """
    Return a formatted block with both view and directions links.
    Only call this when the user has explicitly asked for map links.
    """
    return (
        f"• Map view: {make_maps_view_link(lat, lng)}\n"
        f"• Directions: {make_maps_directions_link(lat, lng)}"
    )
