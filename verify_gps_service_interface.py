import os
import sys
import json
import socket
import threading
import time
import urllib.request

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

import uvicorn
from app.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def test_gps_service_interface():
    PORT = find_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = f"http://127.0.0.1:{PORT}"
    all_passed = True

    print("\n==================================================================")
    print("  [GatiSetu] GPS / RTIS Location Service Interface Test Suite")
    print("==================================================================")

    # 1. Test GPS status endpoint
    print("\n[1] Testing GPS Subsystem Status (/api/gps/status):")
    try:
        with urllib.request.urlopen(f"{base_url}/api/gps/status") as res:
            assert res.status == 200
            st = json.loads(res.read().decode('utf-8'))
            print(f"  Status: {st['status']}")
            print(f"  Provider: {st['provider']}")
            print(f"  Configured: {st['is_configured']}")
            print(f"  Supported Sources: {st['supported_sources']}")
            assert st["status"] == "GPS_SOURCE_NOT_CONFIGURED"
            assert st["is_configured"] is False
            print("  [PASS] GPS subsystem cleanly reports GPS_SOURCE_NOT_CONFIGURED.")
    except Exception as e:
        print(f"  [FAIL] GPS status test failed: {e}")
        all_passed = False

    # 2. Test Unconfigured GPS position query for Train 12951
    print("\n[2] Testing Train 12951 GPS Endpoint (/api/train/12951/gps):")
    try:
        with urllib.request.urlopen(f"{base_url}/api/train/12951/gps") as res:
            assert res.status == 200
            gps_data = json.loads(res.read().decode('utf-8'))
            print(f"  Response Status : {gps_data['status']}")
            print(f"  Train Number    : {gps_data['train_number']}")
            print(f"  Latitude        : {gps_data['latitude']}")
            print(f"  Longitude       : {gps_data['longitude']}")
            print(f"  Speed           : {gps_data['speed']}")
            print(f"  Heading         : {gps_data['heading']}")
            print(f"  Timestamp       : {gps_data['timestamp']}")
            print(f"  Source          : {gps_data['source']}")
            print(f"  Message         : {gps_data['message']}")

            # Verify schema & unconfigured contract
            assert gps_data["status"] == "GPS_SOURCE_NOT_CONFIGURED"
            assert gps_data["is_connected"] is False
            assert gps_data["train_number"] == "12951"
            assert gps_data["latitude"] is None
            assert gps_data["longitude"] is None
            assert gps_data["speed"] is None
            assert gps_data["source"] == "UNCONFIGURED"
            print("  [PASS] GPS endpoint returned exact GPS_SOURCE_NOT_CONFIGURED schema without mock/fake coordinates.")
    except Exception as e:
        print(f"  [FAIL] GPS endpoint test failed: {e}")
        all_passed = False

    # 3. Test Ingesting real GPS telemetry packet interface
    print("\n[3] Testing Real GPS Telemetry Ingest Interface (/api/gps/telemetry/ingest):")
    try:
        sample_packet = {
            "train_number": "12951",
            "latitude": 21.7051,
            "longitude": 72.9959,
            "speed": 114.5,
            "heading": 18.0,
            "timestamp": "2026-09-27T08:20:00Z",
            "source": "RTIS_ISRO_NAVIC"
        }
        req_data = json.dumps(sample_packet).encode('utf-8')
        req = urllib.request.Request(f"{base_url}/api/gps/telemetry/ingest", data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            ingest_res = json.loads(res.read().decode('utf-8'))
            assert ingest_res["status"] == "success"
            print(f"  [PASS] Successfully accepted GPS packet: {ingest_res['data']['source']} for Train {ingest_res['data']['train_number']}")

        # Verify query after ingestion
        with urllib.request.urlopen(f"{base_url}/api/train/12951/gps") as res:
            active_gps = json.loads(res.read().decode('utf-8'))
            assert active_gps["status"] == "LIVE_GPS_ACTIVE"
            assert active_gps["latitude"] == 21.7051
            assert active_gps["longitude"] == 72.9959
            assert active_gps["speed"] == 114.5
            assert active_gps["heading"] == 18.0
            assert active_gps["source"] == "RTIS_ISRO_NAVIC"
            print(f"  [PASS] Verified live GPS retrieval after ingestion: Lat {active_gps['latitude']}, Lng {active_gps['longitude']}, Source: {active_gps['source']}")

    except Exception as e:
        print(f"  [FAIL] GPS telemetry ingest test failed: {e}")
        all_passed = False

    # 4. Verify RailRadar endpoints remain completely intact
    print("\n[4] Verifying Existing RailRadar Endpoints (/api/train/12951, /live, /route):")
    try:
        with urllib.request.urlopen(f"{base_url}/api/train/12951") as res:
            assert res.status == 200
            t = json.loads(res.read().decode('utf-8'))
            assert t["train_number"] == "12951"
            assert "Mumbai" in t["source"]
            assert len(t["stations"]) >= 5
            print(f"  [PASS] Main train details API intact (Train: {t['train_name']}, Delay: +{t['current_delay_mins']}m)")

        with urllib.request.urlopen(f"{base_url}/api/train/12951/live") as res:
            assert res.status == 200
            live = json.loads(res.read().decode('utf-8'))
            assert live["train_number"] == "12951"
            print(f"  [PASS] Live telemetry summary API intact (Location: {live['current_location']})")

        with urllib.request.urlopen(f"{base_url}/api/train/12951/route") as res:
            assert res.status == 200
            rt = json.loads(res.read().decode('utf-8'))
            assert len(rt["route_polyline"]) > 10
            print(f"  [PASS] Route geometry API intact ({len(rt['route_polyline'])} track points)")

    except Exception as e:
        print(f"  [FAIL] RailRadar API check failed: {e}")
        all_passed = False

    print("\n==================================================================")
    if all_passed:
        print("  ALL GPS / RTIS INTERFACE & INTEGRITY CHECKS PASSED 100%!")
    else:
        print("  SOME CHECKS FAILED.")
    print("==================================================================\n")

    server.should_exit = True
    return all_passed

if __name__ == "__main__":
    ok = test_gps_service_interface()
    os._exit(0 if ok else 1)
