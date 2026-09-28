import sys
import os
import json
import socket
import threading
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import uvicorn
from app.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def run_tests():
    port = find_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    time.sleep(1.5)

    base = f"http://127.0.0.1:{port}"
    print(f"\n=======================================================", flush=True)
    print(f"  [GatiSetu] Train 12951 Single-Source-of-Truth Suite", flush=True)
    print(f"=======================================================", flush=True)

    passed = True

    # 1. Check Passenger API for Train 12951
    print("\n[1] Fetching Passenger Train Details from /api/train/12951:", flush=True)
    with urllib.request.urlopen(f"{base}/api/train/12951") as res:
        p_train = json.loads(res.read().decode('utf-8'))

    print(f"  Train: {p_train['train_number']} - {p_train['train_name']}", flush=True)
    print(f"  Current Location: {p_train['current_location']}", flush=True)
    print(f"  Current Coordinates: {p_train['current_coordinates']}", flush=True)
    print(f"  Delay: +{p_train['current_delay_mins']} min", flush=True)
    print(f"  Destination ETA: {p_train['predicted_destination_eta']} (Scheduled: {p_train['scheduled_destination_eta']})", flush=True)
    print(f"  Distance: {p_train['distance_covered_km']} km covered / {p_train['distance_remaining_km']} km remaining (Total: {p_train['total_distance_km']} km)", flush=True)
    print(f"  Journey Progress: {p_train['journey_progress_pct']}%", flush=True)
    print(f"  Next Station: {p_train['next_station']['name']} ({p_train['next_station']['code']}) -> ETA: {p_train['next_station']['expected_eta']}, Dist: {p_train['next_station']['distance_km']} km", flush=True)

    # Assertions for 12951
    assert p_train['train_number'] == '12951'
    assert p_train['current_coordinates'] == [21.7051, 72.9959]
    assert "Bharuch" in p_train['current_location']
    assert p_train['current_delay_mins'] == 14
    assert p_train['predicted_destination_eta'] == '08:46 AM'
    assert p_train['scheduled_destination_eta'] == '08:32 AM'
    assert p_train['next_station']['name'] == 'Vadodara Jn'
    assert p_train['next_station']['expected_eta'] == '09:41 PM'
    assert p_train['total_distance_km'] == 1386.0
    assert p_train['distance_covered_km'] == 326.1
    assert p_train['distance_remaining_km'] == 1059.9
    assert p_train['journey_progress_pct'] == 23.5
    print("  [PASS] Single Source of Truth verified for Train 12951 Passenger API", flush=True)

    # 2. Check Control Room API for Train 12951
    print("\n[2] Checking Control Room Synchronization (/api/control/trains):", flush=True)
    with urllib.request.urlopen(f"{base}/api/control/trains") as res:
        occ_trains = json.loads(res.read().decode('utf-8'))
        t12951 = next((t for t in occ_trains if t['train_number'] == '12951'), None)
        assert t12951 is not None, "Train 12951 missing in OCC"
        print(f"  OCC 12951 Coordinates: {t12951['current_coordinates']}", flush=True)
        print(f"  OCC 12951 Delay: +{t12951['current_delay_mins']} min", flush=True)
        print(f"  OCC 12951 ETA: {t12951['predicted_destination_eta']}", flush=True)
        print(f"  OCC 12951 Location: {t12951['current_location']}", flush=True)
        print(f"  OCC 12951 Progress: {t12951['journey_progress_pct']}%", flush=True)
        
        assert t12951['current_coordinates'] == p_train['current_coordinates']
        assert t12951['current_delay_mins'] == p_train['current_delay_mins']
        assert t12951['predicted_destination_eta'] == p_train['predicted_destination_eta']
        assert t12951['current_location'] == p_train['current_location']
        assert t12951['journey_progress_pct'] == p_train['journey_progress_pct']
        print("  [PASS] Control Room and Passenger Page 100% in sync for Train 12951", flush=True)

    # 3. Check HTML for unwanted hardcoded values
    print("\n[3] Checking HTML for removed hardcoded strings:", flush=True)
    html_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as fp:
        html = fp.read()

    banned_in_html = [
        '392 km covered',
        '994 km remaining',
        '38% completed',
        '28.3%',
        'ETA 09:40 PM',
        '>08:38 AM<'
    ]
    for b in banned_in_html:
        if b in html:
            print(f"  [FAIL] Found lingering hardcoded string in index.html: '{b}'", flush=True)
            passed = False
        else:
            print(f"  [PASS] No hardcoded '{b}' in index.html", flush=True)

    # 4. Check Map zero-API-key configuration
    print("\n[4] Checking Zero-API-Key Map & OpenFreeMap / OSM Basemaps:", flush=True)
    map_view_path = os.path.join(os.path.dirname(__file__), 'frontend', 'js', 'map_view.js')
    with open(map_view_path, 'r', encoding='utf-8') as fp:
        map_js = fp.read()
    
    assert "tile.openstreetmap.org" in map_js, "OSM tile fallback missing in map_view.js"
    assert "arcgisonline.com" in map_js, "ESRI base map layer missing in map_view.js"
    assert "cartocdn.com" in map_js, "CartoDB labels layer missing in map_view.js"
    print("  [PASS] Reliable zero-API-key basemaps and OSM fallbacks configured in map_view.js", flush=True)

    control_room_path = os.path.join(os.path.dirname(__file__), 'frontend', 'js', 'control_room.js')
    with open(control_room_path, 'r', encoding='utf-8') as fp:
        cr_js = fp.read()
    assert "tiles.openfreemap.org/styles/dark" in cr_js, "OpenFreeMap dark style missing in control_room.js"
    print("  [PASS] OpenFreeMap dark style configured for Control Room without API key requirements", flush=True)

    print(f"\n=======================================================", flush=True)
    if passed:
        print("  ALL TRAIN 12951 CONSISTENCY & MAP TESTS PASSED 100%!", flush=True)
    else:
        print("  SOME CHECKS FAILED.", flush=True)
    print(f"=======================================================\n", flush=True)

    server.should_exit = True
    return passed

if __name__ == '__main__':
    ok = run_tests()
    os._exit(0 if ok else 1)
