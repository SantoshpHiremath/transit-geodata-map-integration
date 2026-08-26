from src.data_quality import (
    find_dangling_segments,
    find_invalid_coordinates,
    run_all_checks,
)
from src.stations import ROUTE_SEGMENTS, STOPS, RouteSegment, Stop


def test_find_invalid_coordinates_catches_known_bad_row():
    result = find_invalid_coordinates(STOPS)
    ids = [s.stop_id for s in result]
    assert "S11" in ids


def test_find_invalid_coordinates_empty_for_clean_list():
    clean = [s for s in STOPS if s.stop_id != "S11"]
    assert find_invalid_coordinates(clean) == []


def test_find_dangling_segments_catches_known_bad_row():
    result = find_dangling_segments(ROUTE_SEGMENTS, STOPS)
    ids = [seg.segment_id for seg in result]
    assert "R09" in ids


def test_find_dangling_segments_empty_when_all_resolve():
    stops = [Stop("A", "A", 49.0, 11.0, "bus"), Stop("B", "B", 49.1, 11.1, "bus")]
    segs = [RouteSegment("R1", "L1", "A", "B")]
    assert find_dangling_segments(segs, stops) == []


def test_find_dangling_segments_detects_bad_from_stop():
    stops = [Stop("A", "A", 49.0, 11.0, "bus")]
    segs = [RouteSegment("R1", "L1", "ZZZ", "A")]
    result = find_dangling_segments(segs, stops)
    assert len(result) == 1
    assert result[0].segment_id == "R1"


def test_run_all_checks_returns_both_keys():
    result = run_all_checks(STOPS, ROUTE_SEGMENTS)
    assert set(result.keys()) == {"invalid_coordinates", "dangling_segments"}
    assert len(result["invalid_coordinates"]) == 1
    assert len(result["dangling_segments"]) == 1
