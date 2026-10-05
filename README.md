# Transit Geodata & Map-Service Integration

A tested Python project doing geospatial data operations over a transit
stop/route network and building (not just describing) a MapTiler-style
static-map request. It covers core geodata work: distance and radius
queries, data-quality checks on a stop/route network, route lengths, and
map-service request construction.

## Scope

**All stop names, coordinates, and route data are invented.**
`src/stations.py` contains 11 fictional stops and 9 fictional route
segments styled after a plausible German city transit network (U-Bahn/
Tram/Bus). The coordinate range is chosen near Nuremberg's real
latitude/longitude because a realistic range makes the demo legible;
none of the stop names, exact coordinates, or route/line numbers are
real, and no real transit systems, timetables, or APIs were accessed.

**No real MapTiler API key or network access to maptiler.com was
available in my sandbox.** `src/map_service.py` builds a valid MapTiler
Static Maps API request URL (correct base URL, path parameters, marker
encoding, and query parameters) and validates it (zoom range, image
dimensions, non-empty API key), but `fetch_static_map_bytes()` is an
explicit stub that raises `NotImplementedError` rather than pretending
to return a real map image. This is the same "structure is real, network
call is not" pattern used in `lidar-vms-integration-harness`'s RTSP URL
building.

## What it does

- **`src/stations.py`** — the synthetic stop and route-segment data,
  including one deliberately invalid-coordinate stop and one
  deliberately dangling route segment, used to exercise the
  data-quality checks below.
- **`src/geo.py`** — haversine great-circle distance, coordinate
  validation, radius queries (`stops_within_radius`), bounding box,
  and centroid — the core geospatial primitives.
- **`src/data_quality.py`** — flags stops with out-of-range
  coordinates and route segments referencing a stop id that doesn't
  exist, a common real-world transit-data integrity issue (a stop
  retired or renamed without the route table being updated).
- **`src/routes.py`** — per-segment and per-line route length in km,
  computed from stop coordinates via haversine distance.
- **`src/map_service.py`** — builds and validates a MapTiler-style
  static-map request URL for a set of stops, including correct
  lon-before-lat marker ordering (see bug note below).
- **`run_demo.py`** — runs the full flow end to end and prints a real
  console report (see sample output below, copied from an actual run).

## Testing

40 automated tests (`tests/`), all passing. The haversine
implementation was checked against a known real-world reference
distance (Berlin–Munich, ~504 km) as an external sanity check before
any transit-specific tests were written. One design pitfall the
project guards against and locks in with a test
(`test_build_marker_param_orders_lon_before_lat`) is that MapTiler (like
most map APIs) expects marker coordinates as `lon,lat`, the opposite
order from how this project's own `Stop` dataclass and `haversine_km`
store `lat, lon` — a natural, easy-to-introduce bug if the ordering
swap in `build_marker_param()` weren't deliberate and tested.

```bash
python3 -m pytest -v      # 40 tests, all passing
python3 run_demo.py       # runs the full demo end to end
```

## Sample output (from an actual run)

```
Loaded 11 stops and 9 route segments.

Data quality checks:
  Invalid coordinates: ['S11']
  Dangling segments:   ['R09']

Network centroid: (49.4523, 11.0779)

Stops within 1.5 km of centroid:
  Rathausplatz             0.089 km (ubahn)
  Buergerpark              0.634 km (tram)
  Werksviertel              0.959 km (tram)
  Universitaet Ost         0.995 km (tram)
  Nordbahnhof              1.017 km (ubahn)
  Suedmarkt                1.051 km (ubahn)

Total route length by line (km):
  B10    2.595 km
  T1     2.134 km
  T2     1.145 km
  U1     2.726 km
  U2     2.493 km

Bounding box over valid stops:
  {'min_lat': 49.4355, 'max_lat': 49.4701, 'min_lon': 11.0552, 'max_lon': 11.0955}

Static map URL (request built, NOT fetched -- see map_service.py):
  https://api.maptiler.com/maps/streets-v2/static/11.07790,49.45229,13/600x400.png?markers=11.07670,49.45210,0B5FFF|11.082...
```

Note line `B11` (the line the dangling segment `R09` belongs to)
correctly does not appear in the route-length report — `R09`
references a stop id (`S99`) that doesn't exist in `STOPS`, so
`total_length_by_line` skips it rather than silently reporting a
misleading zero-length or partial total. It is still surfaced
separately by the data-quality check.

## Notes

- All stop, route, and coordinate data is synthetic and invented.
- The MapTiler integration builds and validates a correctly-shaped
  request URL but never calls the MapTiler API or renders a map image,
  since no API key or confirmed network access was available.
  `fetch_static_map_bytes()` is an explicit stub for that missing piece.
- Geospatial operations are implemented directly with the haversine
  formula rather than a geodata library (geopandas/shapely/pyproj), to
  keep the logic small and fully inspectable at this scope; a
  production system handling polygons, projections, or large datasets
  would likely use one of those libraries.
- The centroid calculation is a simple mean of lat/lon, not a spherical
  centroid. It is adequate over a small local network but shouldn't be
  assumed correct at larger geographic scales.
