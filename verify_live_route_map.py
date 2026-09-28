import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
from app.db.store import store, interpolate_along_route

def test_live_route_map():
    print("=" * 68)
    print("  [GatiSetu] Passenger Live Route Map & Telemetry Verification Suite")
    print("=" * 68)

    errors = []

    # 1. Read files
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    with open("frontend/css/main.css", "r", encoding="utf-8") as f:
        css_content = f.read()

    with open("frontend/js/map_view.js", "r", encoding="utf-8") as f:
        map_js = f.read()

    with open("frontend/js/passenger_app.js", "r", encoding="utf-8") as f:
        app_js = f.read()

    with open("frontend/js/data_service.js", "r", encoding="utf-8") as f:
        ds_js = f.read()

    # 1. Verify Free Map Solution (Zero API Key, No Watermark)
    print("\n[1] Verifying Free Open-Source Map Infrastructure:")
    if "mapbox.com" in map_js or "googleapis.com/maps" in map_js or "apiKey" in map_js:
        print("  [FAIL] Found proprietary map API / key requirement in map_view.js")
        errors.append("Proprietary map API found in map_view.js")
    else:
        print("  [PASS] Free OpenStreetMap / CartoDB tile layer used without API keys")

    if re.search(r"cartocdn\.com|tile\.openstreetmap\.org", map_js):
        print("  [PASS] Free tile provider configured properly in map_view.js")
    else:
        print("  [FAIL] Free tile provider not found in map_view.js")
        errors.append("Free tile provider missing")

    # 2. Verify Railway Route Polyline & Station Markers
    print("\n[2] Verifying Railway Route Polyline & Intermediate Stations:")
    required_map_methods = [
        ("getRoutePolyline", r"getRoutePolyline\s*\("),
        ("calculatePositionAlongRoute", r"calculatePositionAlongRoute\s*\("),
        ("renderTrainRoute", r"renderTrainRoute\s*\("),
        ("updateTrainPosition", r"updateTrainPosition\s*\("),
        ("fitEntireRoute", r"fitEntireRoute\s*\("),
        ("centerOnTrain", r"centerOnTrain\s*\("),
    ]
    for label, pat in required_map_methods:
        if re.search(pat, map_js):
            print(f"  [PASS] Method {label:32} -> Implemented")
        else:
            print(f"  [FAIL] Method {label:32} -> MISSING")
            errors.append(f"Missing map method: {label}")

    # 3. Verify Animated Live Train Marker & Visual Styling
    print("\n[3] Verifying Animated Live Train Marker & CSS Styles:")
    required_css_rules = [
        (".custom-train-leaflet-icon", r"\.custom-train-leaflet-icon\s*\{"),
        (".live-train-marker-wrapper", r"\.live-train-marker-wrapper\s*\{"),
        (".train-radar-pulse", r"\.train-radar-pulse\s*\{"),
        ("@keyframes trainRadarWave", r"@keyframes\s+trainRadarWave\s*\{"),
        (".train-marker-pin", r"\.train-marker-pin\s*\{"),
        (".train-marker-label", r"\.train-marker-label\s*\{"),
        (".map-station-popup", r"\.map-station-popup"),
        (".map-train-popup", r"\.map-train-popup"),
    ]
    for label, pat in required_css_rules:
        if re.search(pat, css_content):
            print(f"  [PASS] CSS Rule {label:30} -> Present")
        else:
            print(f"  [FAIL] CSS Rule {label:30} -> MISSING in CSS")
            errors.append(f"Missing CSS rule: {label}")

    # 4. Mathematical Polyline Interpolation Accuracy Test
    print("\n[4] Testing Polyline Interpolation Mathematical Accuracy:")
    test_poly = [
        [18.9696, 72.8193], # MMCT
        [19.2290, 72.8574], # BVI
        [21.2052, 72.8409], # ST
        [22.3107, 73.1812], # BRC
        [23.3441, 75.0366], # RTM
        [25.2138, 75.8648], # KOTA
        [28.6139, 77.2090]  # NDLS
    ]

    p0 = interpolate_along_route(test_poly, 0.0)
    p38 = interpolate_along_route(test_poly, 38.0)
    p70 = interpolate_along_route(test_poly, 70.0)
    p100 = interpolate_along_route(test_poly, 100.0)

    print(f"  [POLY] 0%   (Origin: MMCT)    -> Lat: {p0[0]}, Lon: {p0[1]}")
    print(f"  [POLY] 38%  (En route: BRC)   -> Lat: {p38[0]}, Lon: {p38[1]}")
    print(f"  [POLY] 70%  (En route: KOTA)  -> Lat: {p70[0]}, Lon: {p70[1]}")
    print(f"  [POLY] 100% (Dest: NDLS)      -> Lat: {p100[0]}, Lon: {p100[1]}")

    if p0 == test_poly[0] and p100 == test_poly[-1]:
        print("  [PASS] Boundary conditions (0% and 100%) match exact endpoints")
    else:
        print("  [FAIL] Boundary conditions mismatch")
        errors.append("Boundary condition error in interpolation")

    if 21.0 <= p38[0] <= 24.0 and 72.5 <= p38[1] <= 75.5:
        print("  [PASS] Intermediate position (38%) correctly lies on Gujarat/MP railway corridor")
    else:
        print("  [FAIL] Intermediate position is outside corridor bounds")
        errors.append("Intermediate position calculation error")

    # 5. Live Simulation Coordinate Progression Test
    print("\n[5] Testing Live Simulation Progression Along Railway Corridor:")
    initial_train = store.get_train("12951")
    init_coords = initial_train["current_coordinates"]
    init_progress = initial_train["journey_progress_pct"]
    init_eta = initial_train["predicted_destination_eta"]

    print(f"  [BEFORE] Progress: {init_progress}%, Coords: {init_coords}, ETA: {init_eta}")

    store.advance_simulation_tick("12951")
    updated_train = store.get_train("12951")
    new_coords = updated_train["current_coordinates"]
    new_progress = updated_train["journey_progress_pct"]

    print(f"  [AFTER]  Progress: {new_progress}%, Coords: {new_coords}")

    if new_progress > init_progress and new_coords != init_coords:
        print("  [PASS] Simulation tick successfully advanced train position along railway tracks")
    else:
        print("  [FAIL] Train coordinates did not advance on simulation tick")
        errors.append("Simulation coordinate progression failed")

    print("\n" + "=" * 68)
    if errors:
        print(f"  FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)
    else:
        print("  ALL LIVE ROUTE MAP & TELEMETRY CHECKS PASSED WITH 100% SUCCESS!")
        print("=" * 68)

if __name__ == "__main__":
    test_live_route_map()
