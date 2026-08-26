"""
Route-segment analysis: computes segment lengths from stop
coordinates and per-line total length -- a small piece of "usage-data
analysis" over network geodata, analogous to the kind of network
statistics a mobility-app team would compute over real ridership/
route data.
"""

from __future__ import annotations

from src.geo import haversine_km
from src.stations import RouteSegment, Stop, get_stop


class UnresolvedStopError(ValueError):
    pass


def segment_length_km(segment: RouteSegment, stops: list[Stop]) -> float:
    """Length of a single route segment in km, via haversine distance
    between its two stops. Raises UnresolvedStopError (rather than
    returning 0.0 or None) if either stop id isn't in the given stops
    list, so a dangling segment (see data_quality.py) can't silently
    produce a misleading zero-length segment in a report."""
    from_stop = next((s for s in stops if s.stop_id == segment.from_stop_id), None)
    to_stop = next((s for s in stops if s.stop_id == segment.to_stop_id), None)
    if from_stop is None or to_stop is None:
        missing = segment.from_stop_id if from_stop is None else segment.to_stop_id
        raise UnresolvedStopError(
            f"segment {segment.segment_id} references unknown stop id {missing!r}"
        )
    return haversine_km(from_stop.lat, from_stop.lon, to_stop.lat, to_stop.lon)


def total_length_by_line(
    segments: list[RouteSegment], stops: list[Stop]
) -> dict[str, float]:
    """Total route length per line, in km. Segments referencing an
    unknown stop are skipped (not silently zeroed) and reported
    separately by the caller via data_quality.find_dangling_segments --
    this function's job is a clean per-line total, not error
    reporting."""
    totals: dict[str, float] = {}
    for seg in segments:
        try:
            length = segment_length_km(seg, stops)
        except UnresolvedStopError:
            continue
        totals[seg.line] = totals.get(seg.line, 0.0) + length
    return totals
