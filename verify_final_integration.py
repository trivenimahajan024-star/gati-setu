import os
import sys
import time
import threading
import urllib.request
import json
import re

# Ensure UTF-8 output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

import socket
import uvicorn
from app.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def run_all_integration_tests():
    PORT = find_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = f"http://127.0.0.1:{PORT}"
    all_passed = True

    print("\n==================================================================")
    print("  [GatiSetu] Final Integration, Live Data Sync & Responsive Suite")
    print("==================================================================")

    # -------------------------------------------------------------
    # 1. SHARED DATA SOURCE & PASSENGER ACCESS (NO LOGIN REQUIRED)
    # -------------------------------------------------------------
    print("\n[1] Verifying Public Passenger Access (No Auth Required):")
    try:
        with urllib.request.urlopen(f"{base_url}/") as res:
            assert res.status == 200
            html = res.read().decode('utf-8')
            assert 'id="view-passenger"' in html
            assert 'id="trainSearchInput"' in html
            print("  [PASS] Root application serves Passenger interface publicly without auth wall.")
    except Exception as e:
        print(f"  [FAIL] Public passenger access failed: {e}")
        all_passed = False

    # -------------------------------------------------------------
    # 2. TRAIN SEARCH & MULTI-TRAIN TELEMETRY
    # -------------------------------------------------------------
    print("\n[2] Testing Train Telemetry API for Active Trains:")
    train_ids = ["12951", "12860", "22436", "12002", "12259"]
    for t_id in train_ids:
        try:
            with urllib.request.urlopen(f"{base_url}/api/train/{t_id}") as res:
                assert res.status == 200
                data = json.loads(res.read().decode('utf-8'))
                assert data["train_number"] == t_id
                print(f"  [PASS] Train {t_id:<5} ({data['short_name']:<22}) -> ETA: {data['predicted_destination_eta']}, Delay: +{data['current_delay_mins']}m, Loc: {data['current_location']}")
        except Exception as e:
            print(f"  [FAIL] Failed to fetch train {t_id}: {e}")
            all_passed = False

    # -------------------------------------------------------------
    # 3. INTERMEDIATE STATIONS SEQUENCE (BEYOND ORIGIN/DESTINATION)
    # -------------------------------------------------------------
    print("\n[3] Verifying Complete Intermediate Stations Timeline for Train 12951:")
    try:
        with urllib.request.urlopen(f"{base_url}/api/train/12951") as res:
            data = json.loads(res.read().decode('utf-8'))
            stations = data.get("stations", [])
            assert len(stations) >= 5, f"Expected intermediate stations, got {len(stations)}"
            stn_names = [s["name"] for s in stations]
            print(f"  [PASS] Station Timeline ({len(stations)} stops): {' -> '.join(stn_names)}")
            assert "Mumbai Central" in stn_names
            assert "Surat" in stn_names
            assert "Vadodara Jn" in stn_names
            assert "Kota Jn" in stn_names
            assert "New Delhi" in stn_names
    except Exception as e:
        print(f"  [FAIL] Station sequence verification failed: {e}")
        all_passed = False

    # -------------------------------------------------------------
    # 4. STAFF AUTHENTICATION FLOW
    # -------------------------------------------------------------
    print("\n[4] Testing Staff Authentication for Station & OCC Roles:")
    for role, user, pwd in [("station_staff", "station_master", "railway123"), ("control_room", "occ_controller", "admin123")]:
        try:
            req_data = json.dumps({"username": user, "password": pwd, "role": role}).encode("utf-8")
            req = urllib.request.Request(f"{base_url}/api/auth/login", data=req_data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as res:
                auth = json.loads(res.read().decode('utf-8'))
                assert auth["role"] == role
                print(f"  [PASS] Authenticated {user:<15} as {auth['name']} ({auth['role']})")
        except Exception as e:
            print(f"  [FAIL] Staff auth failed for {user}: {e}")
            all_passed = False

    # -------------------------------------------------------------
    # 5. STATION DISPLAY BOARD (FIDS) VERIFICATION
    # -------------------------------------------------------------
    print("\n[5] Testing Station Display Board API (FIDS):")
    for stn in ["NDLS", "MMCT", "BRC", "HWH", "BPL"]:
        try:
            with urllib.request.urlopen(f"{base_url}/api/station/{stn}/display") as res:
                board = json.loads(res.read().decode('utf-8'))
                tot = len(board["arrivals"]) + len(board["departures"])
                print(f"  [PASS] Station Board {stn:<4} ({board['station_name']:<24}) -> {len(board['arrivals'])} Arrivals, {len(board['departures'])} Departures")
        except Exception as e:
            print(f"  [FAIL] Station board for {stn} failed: {e}")
            all_passed = False

    # -------------------------------------------------------------
    # 6. CONTROL ROOM & LIVE MULTI-INTERFACE DATA SYNC TEST
    # -------------------------------------------------------------
    print("\n[6] Testing Live Event Injection & Synchronized Multi-Interface Propagation:")
    try:
        # Step A: Get Baseline Train 12951 ETA in Passenger, Station Board, and OCC
        with urllib.request.urlopen(f"{base_url}/api/train/12951") as res:
            base_train = json.loads(res.read().decode('utf-8'))
            base_delay = base_train["current_delay_mins"]
            base_eta = base_train["predicted_destination_eta"]
            print(f"  [BASE] Train 12951 Delay: +{base_delay}m, Predicted ETA: {base_eta}")

        # Step B: Inject +10m Unscheduled Halt Event in Control Room
        inj_data = json.dumps({
            "train_number": "12951",
            "event_type": "halt",
            "delay_impact_mins": 10,
            "description": "Unscheduled track inspection halt near Bharuch Jn"
        }).encode("utf-8")
        req = urllib.request.Request(f"{base_url}/api/control/inject-event", data=inj_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as res:
            inj_res = json.loads(res.read().decode('utf-8'))
            new_train = inj_res["train"]
            new_delay = new_train["current_delay_mins"]
            new_eta = new_train["predicted_destination_eta"]
            print(f"  [PASS] Control Room Injected Event: Delay changed to +{new_delay}m, New ETA: {new_eta}")
            assert new_delay > base_delay, "Delay did not increase after event injection"

        # Step C: Verify Passenger Interface receives updated ETA
        with urllib.request.urlopen(f"{base_url}/api/train/12951") as res:
            p_train = json.loads(res.read().decode('utf-8'))
            assert p_train["current_delay_mins"] == new_delay
            assert p_train["predicted_destination_eta"] == new_eta
            print(f"  [PASS] Passenger Interface synchronized: Delay = +{p_train['current_delay_mins']}m, ETA = {p_train['predicted_destination_eta']}")

        # Step D: Verify Station Board (NDLS) receives updated ETA
        with urllib.request.urlopen(f"{base_url}/api/station/NDLS/display") as res:
            stn_board = json.loads(res.read().decode('utf-8'))
            t_entry = next((t for t in stn_board["arrivals"] if t["train_number"] == "12951"), None)
            assert t_entry is not None, "Train 12951 not found in NDLS arrivals"
            assert t_entry["predicted_time"] == new_eta, f"Expected {new_eta}, got {t_entry['predicted_time']}"
            print(f"  [PASS] Station Board (NDLS) synchronized: Delay = +{t_entry['delay_mins']}m, Predicted Arrival = {t_entry['predicted_time']}")

        # Step E: Reset/Clear Events to restore baseline
        clear_data = json.dumps({
            "train_number": "12951",
            "event_type": "clear",
            "delay_impact_mins": 0,
            "description": "Clear all active incidents"
        }).encode("utf-8")
        req = urllib.request.Request(f"{base_url}/api/control/inject-event", data=clear_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as res:
            clear_res = json.loads(res.read().decode('utf-8'))
            restored_train = clear_res["train"]
            print(f"  [PASS] Restored Normal Flow: Train 12951 Delay = +{restored_train['current_delay_mins']}m, ETA = {restored_train['predicted_destination_eta']}")

    except Exception as e:
        print(f"  [FAIL] Live sync propagation test failed: {e}")
        all_passed = False

    # -------------------------------------------------------------
    # 7. RESPONSIVENESS AND BREAKPOINT CSS CHECKS
    # -------------------------------------------------------------
    print("\n[7] Verifying Responsive CSS Breakpoints (320px to 1920px):")
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "css", "main.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    breakpoints = [
        ("@media (max-width: 767px)", "Mobile Breakpoint (320px - 767px)"),
        ("@media (min-width: 768px) and (max-width: 1023px)", "Tablet Breakpoint (768px - 1023px)"),
        ("@media (min-width: 1024px) and (max-width: 1439px)", "Desktop Breakpoint (1024px - 1439px)"),
        ("@media (min-width: 1440px)", "Large Screen & Monitor Breakpoint (1440px+)")
    ]

    for bp, desc in breakpoints:
        if bp in css:
            print(f"  [PASS] {desc:<48} -> Found")
        else:
            print(f"  [FAIL] {desc:<48} -> MISSING")
            all_passed = False

    print("\n==================================================================", flush=True)
    if all_passed:
        print("  ALL GATISETU FINAL INTEGRATION & SYNC TESTS PASSED WITH 100% SUCCESS!", flush=True)
    else:
        print("  SOME INTEGRATION TESTS FAILED. PLEASE CHECK LOGS.", flush=True)
    print("==================================================================\n", flush=True)
    server.should_exit = True
    return all_passed

if __name__ == "__main__":
    success = run_all_integration_tests()
    os._exit(0 if success else 1)

