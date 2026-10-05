"""
Data-quality checks over the transit geodata -- coordinate validation
and referential-integrity checks between stops and route segments.
It follows a "find and flag the bad row rather than silently drop
or crash on it" approach.
"""

from __future__ import annotations

from src.geo import is_valid_coordinate
from src.stations import RouteSegment, Stop


def find_invalid_coordinates(stops: list[Stop]) -> list[Stop]:
    """Stops whose lat/lon fall outside valid geographic ranges."""
    return [s for s in stops if not is_valid_coordinate(s.lat, s.lon)]


def find_dangling_segments(
    segments: list[RouteSegment], stops: list[Stop]
) -> list[RouteSegment]:
    """Route segments that reference a from_stop_id or to_stop_id not
    present in the stops list -- a common real-world transit-data
    integrity issue (a stop retired or renamed without updating the
    route table)."""
    known_ids = {s.stop_id for s in stops}
    return [
        seg
        for seg in segments
        if seg.from_stop_id not in known_ids or seg.to_stop_id not in known_ids
    ]


def run_all_checks(stops: list[Stop], segments: list[RouteSegment]) -> dict:
    return {
        "invalid_coordinates": find_invalid_coordinates(stops),
        "dangling_segments": find_dangling_segments(segments, stops),
    }
