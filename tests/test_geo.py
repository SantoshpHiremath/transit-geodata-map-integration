import math

import pytest

from src.geo import (
    bounding_box,
    center_of,
    haversine_km,
    is_valid_coordinate,
    stops_within_radius,
)
from src.stations import Stop


def test_haversine_zero_distance_same_point():
    assert haversine_km(49.45, 11.08, 49.45, 11.08) == pytest.approx(0.0, abs=1e-9)


def test_haversine_known_reference_distance():
    # Berlin (52.5200, 13.4050) to Munich (48.1351, 11.5820): real,
    # independently known great-circle distance is ~504 km. Used as an
    # external sanity check on the haversine implementation, not
    # tied to this project's fictional stop data.
    d = haversine_km(52.5200, 13.4050, 48.1351, 11.5820)
    assert d == pytest.approx(504, rel=0.02)


def test_haversine_symmetric():
    d1 = haversine_km(49.45, 11.08, 49.46, 11.09)
    d2 = haversine_km(49.46, 11.09, 49.45, 11.08)
    assert d1 == pytest.approx(d2, abs=1e-9)


def test_is_valid_coordinate_true_for_normal_point():
    assert is_valid_coordinate(49.45, 11.08) is True


def test_is_valid_coordinate_false_for_out_of_range_lat():
    assert is_valid_coordinate(91.2, 11.08) is False


def test_is_valid_coordinate_false_for_out_of_range_lon():
    assert is_valid_coordinate(49.45, 200.0) is False


def test_is_valid_coordinate_boundary_values_are_valid():
    assert is_valid_coordinate(90.0, 180.0) is True
    assert is_valid_coordinate(-90.0, -180.0) is True


def test_stops_within_radius_finds_nearby_and_excludes_far():
    stops = [
        Stop("A", "Near", 49.4500, 11.0800, "bus"),
        Stop("B", "Far", 50.0000, 12.0000, "bus"),
    ]
    result = stops_within_radius(stops, 49.4500, 11.0800, radius_km=1.0)
    ids = [s.stop_id for s, _ in result]
    assert ids == ["A"]


def test_stops_within_radius_sorted_nearest_first():
    stops = [
        Stop("A", "Mid", 49.4520, 11.0800, "bus"),
        Stop("B", "Near", 49.4501, 11.0800, "bus"),
    ]
    result = stops_within_radius(stops, 49.4500, 11.0800, radius_km=5.0)
    assert [s.stop_id for s, _ in result] == ["B", "A"]


def test_stops_within_radius_skips_invalid_coordinates():
    stops = [
        Stop("A", "Valid", 49.4500, 11.0800, "bus"),
        Stop("B", "Invalid", 91.0, 11.0800, "bus"),
    ]
    result = stops_within_radius(stops, 49.4500, 11.0800, radius_km=10000.0)
    ids = [s.stop_id for s, _ in result]
    assert "B" not in ids
    assert "A" in ids


def test_bounding_box_basic():
    stops = [
        Stop("A", "A", 49.40, 11.00, "bus"),
        Stop("B", "B", 49.50, 11.20, "bus"),
    ]
    box = bounding_box(stops)
    assert box == {"min_lat": 49.40, "max_lat": 49.50, "min_lon": 11.00, "max_lon": 11.20}


def test_bounding_box_empty_raises():
    with pytest.raises(ValueError):
        bounding_box([])


def test_center_of_basic():
    stops = [
        Stop("A", "A", 49.0, 11.0, "bus"),
        Stop("B", "B", 51.0, 13.0, "bus"),
    ]
    lat, lon = center_of(stops)
    assert lat == pytest.approx(50.0)
    assert lon == pytest.approx(12.0)


def test_center_of_empty_raises():
    with pytest.raises(ValueError):
        center_of([])
