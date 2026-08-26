"""
Core geospatial operations: great-circle distance (haversine),
radius queries, and a bounding box over a set of stops. Pure-Python,
no external geodata library (no geopandas/shapely/pyproj was available
with confirmed install access in this sandbox), which keeps the
implementation fully inspectable and unit-testable against known
reference distances.
"""

from __future__ import annotations

import math

from src.stations import Stop

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points in kilometers."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def is_valid_coordinate(lat: float, lon: float) -> bool:
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def stops_within_radius(
    stops: list[Stop], center_lat: float, center_lon: float, radius_km: float
) -> list[tuple[Stop, float]]:
    """Returns (stop, distance_km) for every stop within radius_km of
    the given center point, sorted nearest-first. Skips stops with
    invalid coordinates rather than raising, so one bad row in a real
    dataset doesn't crash the whole query."""
    results = []
    for s in stops:
        if not is_valid_coordinate(s.lat, s.lon):
            continue
        d = haversine_km(center_lat, center_lon, s.lat, s.lon)
        if d <= radius_km:
            results.append((s, d))
    results.sort(key=lambda pair: pair[1])
    return results


def bounding_box(stops: list[Stop]) -> dict[str, float]:
    """Min/max lat/lon across a list of stops -- used to compute the
    map viewport for the static-map URL builder. Raises ValueError on
    an empty list rather than returning a nonsensical box."""
    if not stops:
        raise ValueError("bounding_box() requires at least one stop")
    lats = [s.lat for s in stops]
    lons = [s.lon for s in stops]
    return {
        "min_lat": min(lats),
        "max_lat": max(lats),
        "min_lon": min(lons),
        "max_lon": max(lons),
    }


def center_of(stops: list[Stop]) -> tuple[float, float]:
    """Simple centroid (mean lat/lon) of a list of stops -- adequate
    for choosing a default map center over a small local area; not a
    proper spherical centroid, which would matter over much larger
    areas than a single city network."""
    if not stops:
        raise ValueError("center_of() requires at least one stop")
    lat = sum(s.lat for s in stops) / len(stops)
    lon = sum(s.lon for s in stops) / len(stops)
    return (lat, lon)
