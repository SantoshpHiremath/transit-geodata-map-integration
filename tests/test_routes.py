import pytest

from src.routes import UnresolvedStopError, segment_length_km, total_length_by_line
from src.stations import Stop, RouteSegment


def test_segment_length_km_basic():
    stops = [
        Stop("A", "A", 49.4500, 11.0800, "bus"),
        Stop("B", "B", 49.4600, 11.0800, "bus"),
    ]
    seg = RouteSegment("R1", "L1", "A", "B")
    length = segment_length_km(seg, stops)
    assert length > 0
    # ~0.01 degree lat difference is roughly 1.1 km
    assert length == pytest.approx(1.11, rel=0.05)


def test_segment_length_km_raises_on_unknown_from_stop():
    stops = [Stop("B", "B", 49.46, 11.08, "bus")]
    seg = RouteSegment("R1", "L1", "MISSING", "B")
    with pytest.raises(UnresolvedStopError):
        segment_length_km(seg, stops)


def test_segment_length_km_raises_on_unknown_to_stop():
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    seg = RouteSegment("R1", "L1", "A", "MISSING")
    with pytest.raises(UnresolvedStopError):
        segment_length_km(seg, stops)


def test_total_length_by_line_sums_correctly():
    stops = [
        Stop("A", "A", 49.45, 11.08, "bus"),
        Stop("B", "B", 49.46, 11.08, "bus"),
        Stop("C", "C", 49.47, 11.08, "bus"),
    ]
    segs = [
        RouteSegment("R1", "L1", "A", "B"),
        RouteSegment("R2", "L1", "B", "C"),
        RouteSegment("R3", "L2", "A", "C"),
    ]
    totals = total_length_by_line(segs, stops)
    assert totals["L1"] == pytest.approx(
        segments_sum(segs[:2], stops)
    )
    assert "L2" in totals


def segments_sum(segs, stops):
    return sum(segment_length_km(s, stops) for s in segs)


def test_total_length_by_line_skips_dangling_segment_silently():
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    segs = [RouteSegment("R1", "L1", "A", "MISSING")]
    totals = total_length_by_line(segs, stops)
    assert totals == {}
