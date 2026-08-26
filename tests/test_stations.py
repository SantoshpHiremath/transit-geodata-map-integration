from src.stations import ROUTE_SEGMENTS, STOPS, get_stop


def test_get_stop_found():
    stop = get_stop("S01")
    assert stop is not None
    assert stop.name == "Rathausplatz"


def test_get_stop_not_found_returns_none():
    assert get_stop("NOPE") is None


def test_stops_have_unique_ids():
    ids = [s.stop_id for s in STOPS]
    assert len(ids) == len(set(ids))


def test_route_segments_have_unique_ids():
    ids = [seg.segment_id for seg in ROUTE_SEGMENTS]
    assert len(ids) == len(set(ids))


def test_stops_nonempty():
    assert len(STOPS) >= 5


def test_route_segments_nonempty():
    assert len(ROUTE_SEGMENTS) >= 5
