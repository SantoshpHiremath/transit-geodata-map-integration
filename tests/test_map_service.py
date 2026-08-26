import pytest

from src.map_service import (
    MapServiceError,
    build_marker_param,
    build_static_map_url,
    fetch_static_map_bytes,
)
from src.stations import Stop


def test_build_marker_param_orders_lon_before_lat():
    # MapTiler (like most map APIs) expects lon,lat order -- the
    # opposite of this project's internal Stop(lat, lon) order. This
    # test locks in the deliberate swap in build_marker_param(); see
    # README for the bug this caught during development.
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    param = build_marker_param(stops)
    lon_str, lat_str, color = param.split(",")
    assert float(lon_str) == pytest.approx(11.08)
    assert float(lat_str) == pytest.approx(49.45)
    assert color == "0B5FFF"


def test_build_marker_param_multiple_stops_joined_with_pipe():
    stops = [
        Stop("A", "A", 49.45, 11.08, "bus"),
        Stop("B", "B", 49.46, 11.09, "bus"),
    ]
    param = build_marker_param(stops)
    assert param.count("|") == 1


def test_build_marker_param_empty_raises():
    with pytest.raises(MapServiceError):
        build_marker_param([])


def test_build_static_map_url_contains_key_and_markers():
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    url = build_static_map_url(stops, 49.45, 11.08, zoom=13, api_key="TESTKEY")
    assert "key=TESTKEY" in url
    assert "markers=" in url
    assert url.startswith("https://api.maptiler.com/")


def test_build_static_map_url_rejects_invalid_zoom():
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    with pytest.raises(MapServiceError):
        build_static_map_url(stops, 49.45, 11.08, zoom=23, api_key="TESTKEY")


def test_build_static_map_url_rejects_negative_zoom():
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    with pytest.raises(MapServiceError):
        build_static_map_url(stops, 49.45, 11.08, zoom=-1, api_key="TESTKEY")


def test_build_static_map_url_rejects_missing_api_key():
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    with pytest.raises(MapServiceError):
        build_static_map_url(stops, 49.45, 11.08, zoom=10, api_key="")


def test_build_static_map_url_rejects_oversized_dimensions():
    stops = [Stop("A", "A", 49.45, 11.08, "bus")]
    with pytest.raises(MapServiceError):
        build_static_map_url(stops, 49.45, 11.08, zoom=10, api_key="K", width=5000, height=400)


def test_fetch_static_map_bytes_is_an_explicit_stub():
    with pytest.raises(NotImplementedError):
        fetch_static_map_bytes("https://api.maptiler.com/whatever")
