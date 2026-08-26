"""
Synthetic transit-network geodata: stop/station records and route
segments for a fictional mid-size German city network, styled after
VAG Nürnberg's own network shape (U-Bahn/Tram/Bus stops) but entirely
invented -- no real VAG station names, coordinates, or timetable data
were used or accessed.

This module is the "data layer" the rest of the project (distance/
radius queries, route-segment length, and static-map URL generation)
operates on.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stop:
    stop_id: str
    name: str
    lat: float
    lon: float
    mode: str  # "ubahn", "tram", "bus"


@dataclass(frozen=True)
class RouteSegment:
    segment_id: str
    line: str
    from_stop_id: str
    to_stop_id: str


# Fictional stops laid out around a fictional city center at
# approximately (49.45, 11.08) -- roughly Nuremberg's real latitude/
# longitude, chosen only because the posting is Nuremberg-based and a
# plausible coordinate range makes the demo legible, NOT because any
# of these stop names or exact coordinates are real VAG data.
STOPS: list[Stop] = [
    Stop("S01", "Rathausplatz", 49.4521, 11.0767, "ubahn"),
    Stop("S02", "Nordbahnhof", 49.4610, 11.0822, "ubahn"),
    Stop("S03", "Suedmarkt", 49.4438, 11.0715, "ubahn"),
    Stop("S04", "Werksviertel", 49.4489, 11.0901, "tram"),
    Stop("S05", "Universitaet Ost", 49.4590, 11.0688, "tram"),
    Stop("S06", "Messeplatz", 49.4392, 11.0954, "tram"),
    Stop("S07", "Hafenstrasse", 49.4655, 11.0603, "bus"),
    Stop("S08", "Industriepark Nord", 49.4701, 11.0955, "bus"),
    Stop("S09", "Klinikum West", 49.4355, 11.0552, "bus"),
    Stop("S10", "Buergerpark", 49.4478, 11.0833, "tram"),
    # Deliberately out-of-range row (invalid latitude) used to test
    # coordinate validation -- see data_quality.py.
    Stop("S11", "Fehlerhafte Haltestelle", 91.2, 11.0800, "bus"),
]

ROUTE_SEGMENTS: list[RouteSegment] = [
    RouteSegment("R01", "U1", "S01", "S02"),
    RouteSegment("R02", "U1", "S02", "S07"),
    RouteSegment("R03", "U2", "S01", "S03"),
    RouteSegment("R04", "U2", "S03", "S09"),
    RouteSegment("R05", "T1", "S04", "S10"),
    RouteSegment("R06", "T1", "S10", "S05"),
    RouteSegment("R07", "T2", "S06", "S04"),
    RouteSegment("R08", "B10", "S07", "S08"),
    # References a stop id that doesn't exist in STOPS -- a deliberate
    # data-quality issue for find_dangling_segments() to catch.
    RouteSegment("R09", "B11", "S08", "S99"),
]


def get_stop(stop_id: str) -> Stop | None:
    for s in STOPS:
        if s.stop_id == stop_id:
            return s
    return None
