"""
Runs the transit geodata + map-integration demo end to end: loads the
synthetic stop/route network, runs data-quality checks, computes a
radius query and route-length report, and builds (but does not fetch)
a static-map URL for the network. Prints a real console report.
"""

from src.data_quality import run_all_checks
from src.geo import bounding_box, center_of, stops_within_radius
from src.map_service import build_static_map_url
from src.routes import total_length_by_line
from src.stations import ROUTE_SEGMENTS, STOPS


def main():
    print(f"Loaded {len(STOPS)} stops and {len(ROUTE_SEGMENTS)} route segments.\n")

    dq = run_all_checks(STOPS, ROUTE_SEGMENTS)
    print("Data quality checks:")
    print(f"  Invalid coordinates: {[s.stop_id for s in dq['invalid_coordinates']]}")
    print(f"  Dangling segments:   {[s.segment_id for s in dq['dangling_segments']]}\n")

    valid_stops = [s for s in STOPS if s not in dq["invalid_coordinates"]]

    center_lat, center_lon = center_of(valid_stops)
    print(f"Network centroid: ({center_lat:.4f}, {center_lon:.4f})\n")

    print("Stops within 1.5 km of centroid:")
    nearby = stops_within_radius(valid_stops, center_lat, center_lon, 1.5)
    for stop, dist in nearby:
        print(f"  {stop.name:24s} {dist:.3f} km ({stop.mode})")

    print("\nTotal route length by line (km):")
    totals = total_length_by_line(ROUTE_SEGMENTS, STOPS)
    for line, length in sorted(totals.items()):
        print(f"  {line:6s} {length:.3f} km")

    print("\nBounding box over valid stops:")
    print(f"  {bounding_box(valid_stops)}")

    print("\nStatic map URL (request built, NOT fetched -- see map_service.py disclosure):")
    url = build_static_map_url(
        valid_stops, center_lat, center_lon, zoom=13, api_key="DEMO_KEY_NOT_REAL"
    )
    print(f"  {url[:120]}...")


if __name__ == "__main__":
    main()
