"""
Static-map URL generation styled after MapTiler's Static Maps API
request shape (center/zoom/markers/style query parameters over a
tile-service base URL).

IMPORTANT DISCLOSURE: this sandbox has no MapTiler API key configured
and no confirmed outbound network access to maptiler.com, so this
module builds and validates the REQUEST -- the URL, its parameters,
and marker encoding -- but never calls the real MapTiler API and never
renders an actual map image. The structure is real and the network call is not,
as in lidar-vms-integration-harness (RTSP URL building) and
iot-timeseries-cloud-pipeline (cloud client interfaces). A real integration would need an
actual MapTiler API key and would swap fetch_static_map_bytes()'s stub
for a real HTTP GET -- the URL-building and validation logic here
would not need to change.
"""

from __future__ import annotations

from src.stations import Stop

MAPTILER_STATIC_BASE = "https://api.maptiler.com/maps/streets-v2/static"


class MapServiceError(ValueError):
    pass


def build_marker_param(stops: list[Stop], color: str = "0B5FFF") -> str:
    """Encodes a list of stops as MapTiler-style marker parameters:
    'lon,lat,color|lon,lat,color|...'. Note MapTiler (like most map
    APIs) takes lon before lat, the opposite order from how this
    project's Stop dataclass and haversine_km store lat/lon -- a real
    source of bugs if not handled deliberately (see the swapped-order
    bug documented in the README and covered by
    test_marker_param_orders_lon_before_lat)."""
    if not stops:
        raise MapServiceError("build_marker_param() requires at least one stop")
    return "|".join(f"{s.lon:.5f},{s.lat:.5f},{color}" for s in stops)


def build_static_map_url(
    stops: list[Stop],
    center_lat: float,
    center_lon: float,
    zoom: int,
    api_key: str,
    width: int = 600,
    height: int = 400,
) -> str:
    """Builds a MapTiler static-map request URL for a set of stops
    around a given center point. Raises MapServiceError on invalid
    zoom (MapTiler's documented range is 0-22) rather than sending a
    request that would fail server-side."""
    if not (0 <= zoom <= 22):
        raise MapServiceError(f"zoom must be between 0 and 22, got {zoom}")
    if not (1 <= width <= 2048 and 1 <= height <= 2048):
        raise MapServiceError("width/height must be between 1 and 2048 pixels")
    if not api_key:
        raise MapServiceError("api_key is required")

    markers = build_marker_param(stops)
    return (
        f"{MAPTILER_STATIC_BASE}/{center_lon:.5f},{center_lat:.5f},{zoom}/"
        f"{width}x{height}.png"
        f"?markers={markers}&key={api_key}"
    )


def fetch_static_map_bytes(url: str) -> bytes:
    """STUB ONLY -- does not make a real network call. A real
    implementation would `requests.get(url)` and return `.content`.
    Raises explicitly rather than silently returning fake image bytes,
    so any caller that forgets this is a stub fails loudly instead of
    getting a corrupt-looking success."""
    raise NotImplementedError(
        "fetch_static_map_bytes() is a stub: no MapTiler API key or "
        "confirmed network access is available in this sandbox. Swap "
        "this for a real `requests.get(url).content` call once a real "
        "API key is available; build_static_map_url()'s output is "
        "already a valid request URL for that call."
    )
