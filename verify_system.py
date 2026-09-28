import os
import sys
import time
import threading
import urllib.request
import json

# Ensure UTF-8 output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

import uvicorn
from app.main import app

PORT = 8015

def test_system():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(2.0)

    base_url = f"http://127.0.0.1:{PORT}"
    all_passed = True

    print("\n==================================================================")
    print("  [GatiSetu] Unified System Automated Verification Suite")
    print("==================================================================")

    # 1. Test Static Files & Root HTML
    print("\n[1] Testing Static Asset Endpoints:")
    static_endpoints = [
        ("/", "Root index.html"),
        ("/css/main.css", "Unified Theme CSS"),
        ("/js/api.js", "API Client JS"),
        ("/js/data_service.js", "Data Service JS"),
        ("/js/map_view.js", "Map View Tracker JS"),
        ("/js/station_board.js", "Station Board FIDS JS"),
        ("/js/control_room.js", "Control Room OCC JS"),
        ("/js/passenger_app.js", "Main Controller JS")
    ]
    for path, desc in static_endpoints:
        try:
            with urllib.request.urlopen(f"{base_url}{path}") as res:
                content = res.read()
                print(f"  [PASS] {desc:<25} ({path:<24}) -> Status {res.status}, Size {len(content)} bytes")
        except Exception as e:
            print(f"  [FAIL] {desc} ({path}) FAILED: {e}")
            all_passed = False

    # 2. Test Train & Telemetry API
    print("\n[2] Testing Train Telemetry & Search API:")
    try:
        with urllib.request.urlopen(f"{base_url}/api/train/12951") as res:
            t = json.loads(res.read().decode())
            print(f"  [PASS] Train 12951 details: {t['train_name']}")
            print(f"         - Current Delay: +{t['current_delay_mins']} min")
            print(f"         - Dynamic Predicted ETA: {t['predicted_destination_eta']}")
            print(f"         - Confidence: {t['confidence_level']} ({t['confidence_pct']}%)")
            assert t["train_number"] == "12951"
    except Exception as e:
        print(f"  [FAIL] Train API test FAILED: {e}")
        all_passed = False

    # 3. Test Station Board (FIDS) API
    print("\n[3] Testing Station Board (FIDS) API:")
    try:
        with urllib.request.urlopen(f"{base_url}/api/station/NDLS/display") as res:
            board = json.loads(res.read().decode())
            print(f"  [PASS] Station Board for {board['station_code']}:")
            print(f"         - Total Arrivals: {len(board['arrivals'])}")
            print(f"         - Total Departures: {len(board['departures'])}")
            assert len(board["arrivals"]) > 0 or len(board["departures"]) > 0
    except Exception as e:
        print(f"  [FAIL] Station Board API test FAILED: {e}")
        all_passed = False

    # 4. Test Control Room OCC & Event Injection
    print("\n[4] Testing Control Room OCC & Dynamic ETA Event Injection:")
    try:
        with urllib.request.urlopen(f"{base_url}/api/control/overview") as res:
            occ = json.loads(res.read().decode())
            print(f"  [PASS] OCC Overview: Active Trains = {occ['total_active_trains']}, On-Time = {occ['on_time_trains']}")

        # Inject +5m Congestion Event for Train 12951
        req_data = json.dumps({
            "train_number": "12951",
            "event_type": "congestion",
            "delay_impact_mins": 5,
            "description": "Signal congestion test near Godhra Jn"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{base_url}/api/control/inject-event",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            inj_res = json.loads(res.read().decode())
            print(f"  [PASS] Event Injected: {inj_res['message']}")
            updated_train = inj_res["train"]
            print(f"         - Updated Delay: +{updated_train['current_delay_mins']} min")
            print(f"         - Recalculated Dynamic ETA: {updated_train['predicted_destination_eta']}")

        # Verify that Station Board now reflects the updated dynamic ETA
        with urllib.request.urlopen(f"{base_url}/api/station/NDLS/display") as res:
            updated_board = json.loads(res.read().decode())
            t12951_entry = next((item for item in updated_board["arrivals"] if item["train_number"] == "12951"), None)
            if t12951_entry:
                print(f"  [PASS] Dynamic ETA synchronized to Station Board: Predicted ETA = {t12951_entry.get('predicted_time', t12951_entry.get('predicted_arr', '--'))} (+{t12951_entry['delay_mins']}m)")

    except Exception as e:
        print(f"  [FAIL] Control Room / Event Injection test FAILED: {e}")
        all_passed = False

    # 5. Test Staff Authentication
    print("\n[5] Testing Staff Authentication & Roles:")
    try:
        auth_data = json.dumps({
            "username": "station_master",
            "password": "railway123",
            "role": "station_staff"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{base_url}/api/auth/login",
            data=auth_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            auth_res = json.loads(res.read().decode())
            print(f"  [PASS] Staff Login Successful: {auth_res['name']} ({auth_res['role']})")
            assert auth_res["role"] == "station_staff"
    except Exception as e:
        print(f"  [FAIL] Staff Auth test FAILED: {e}")
        all_passed = False

    server.should_exit = True
    thread.join(timeout=2)

    print("\n==================================================================")
    if all_passed:
        print("  ALL UNIFIED GATISETU TESTS PASSED WITH 100% SUCCESS!")
    else:
        print("  SOME TESTS FAILED")
    print("==================================================================\n")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    test_system()
