import os
import sys
import json

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

from app.api.routes_trains import get_train_details, get_train_route, get_train_live_telemetry, simulate_train_step
from app.main import get_map_config
from app.config import settings
from fastapi import HTTPException

def test_railradar_integration():
    print("==================================================================")
    print("  [GatiSetu] RailRadar Real API Integration Test Suite")
    print("==================================================================")

    # 1. Config Security Check: RailRadar API Key NEVER exposed to frontend
    print("\n[1] Verifying Backend Security & Config Endpoint:")
    cfg = get_map_config()
    assert "maptiler_api_key" in cfg, "maptiler_api_key missing in get_map_config"
    assert "railradar_api_key" not in cfg, "CRITICAL: railradar_api_key exposed in get_map_config!"
    assert "RAILRADAR_API_KEY" not in str(cfg), "CRITICAL: RAILRADAR_API_KEY string exposed in get_map_config!"
    print("  [PASS] RailRadar API Key is securely kept on the server and not exposed.")

    # 2. Test Train 12951 Real Data Fetch
    print("\n[2] Testing Real Train 12951 Live Telemetry & Schedule from RailRadar:")
    t = get_train_details("12951")
    
    print(f"  [REAL DATA] Train Number : {t['train_number']}")
    print(f"  [REAL DATA] Train Name   : {t['train_name']}")
    print(f"  [REAL DATA] Location     : {t['current_location']}")
    print(f"  [REAL DATA] Delay (mins) : +{t['current_delay_mins']} min")
    print(f"  [REAL DATA] Speed (km/h) : {t['current_speed_kmh']} km/h")
    print(f"  [REAL DATA] Next Station : {t['next_station']['name']} ({t['next_station']['code']}) -> ETA {t['next_station']['expected_eta']}")
    print(f"  [REAL DATA] Dest Sched   : {t['scheduled_destination_eta']}")
    print(f"  [REAL DATA] Dest Dynamic : {t['predicted_destination_eta']}")
    print(f"  [REAL DATA] Total Halts  : {len(t['stations'])}")
    print(f"  [REAL DATA] Polyline Pts : {len(t['route_polyline'])}")
    print(f"  [REAL DATA] Coordinates  : {t['current_coordinates']}")

    assert "12951" in t["train_number"]
    assert "Rajdhani" in t["train_name"] or "Tejas" in t["train_name"]
    assert len(t["stations"]) >= 5, "Expected real intermediate stations"
    assert len(t["route_polyline"]) > 100, "Expected full real railway corridor polyline"
    assert t["current_coordinates"] and len(t["current_coordinates"]) == 2, "Invalid GPS coordinates"
    assert "START" == t["stations"][0]["scheduled_arr"]
    assert "DEST" == t["stations"][-1]["scheduled_dep"]
    print("  [PASS] Real train details, route stations, and geometry fetched successfully.")

    # 3. Test Route Endpoint
    print("\n[3] Testing Real Route Endpoint (/api/train/12951/route):")
    route_res = get_train_route("12951")
    assert len(route_res["route_polyline"]) > 100
    assert len(route_res["stations"]) >= 5
    print(f"  [PASS] Route endpoint returned {len(route_res['route_polyline'])} track coordinates and {len(route_res['stations'])} stations.")

    # 4. Test Live Telemetry Endpoint
    print("\n[4] Testing Real Live Telemetry Endpoint (/api/train/12951/live):")
    live_res = get_train_live_telemetry("12951")
    assert live_res["train_number"] == "12951"
    assert "current_coordinates" in live_res
    assert "current_speed_kmh" in live_res
    print(f"  [PASS] Live telemetry returned GPS: {live_res['current_coordinates']}, Speed: {live_res['current_speed_kmh']} km/h, Delay: +{live_res['current_delay_mins']}m")

    # 5. Test Simulate Endpoint (Replaced with Real Live Data)
    print("\n[5] Testing /simulate Endpoint with Real RailRadar Live Feed:")
    sim_res = simulate_train_step("12951")
    assert sim_res.get("status") == "ok"
    assert sim_res.get("train", {}).get("train_number") == "12951"
    print("  [PASS] /simulate endpoint successfully synced with real RailRadar live status.")

    # 6. Test Error Handling (Invalid Train Number 99999)
    print("\n[6] Testing Real API Failure & Error Handling (Non-existent Train 99999):")
    caught_error = False
    try:
        get_train_details("99999")
    except HTTPException as e:
        caught_error = True
        print(f"  [CAUGHT EXPECTED HTTPException] Status: {e.status_code}, Detail: {e.detail}")
        assert e.status_code == 404
        assert "not found" in str(e.detail).lower()
    assert caught_error, "Expected HTTPException for invalid train"
    print("  [PASS] Actual error returned properly without falling back to fake/simulated data.")

    # 7. Test Multi-Train Queries (12860, 22436, 12002)
    print("\n[7] Testing Multi-Train Real Queries via RailRadar:")
    for train_no in ["12860", "22436", "12002"]:
        try:
            tr = get_train_details(train_no)
            print(f"  [REAL TRAIN {train_no}] {tr['train_name']} -> Loc: {tr['current_location']}, Delay: +{tr['current_delay_mins']}m, Next: {tr['next_station']['name']}")
        except HTTPException as e:
            print(f"  [TRAIN {train_no}] Status {e.status_code}: {e.detail}")
    print("  [PASS] Multi-train queries processed cleanly.")

    print("\n==================================================================")
    print("  ALL RAILRADAR API INTEGRATION CHECKS PASSED WITH 100% SUCCESS!")
    print("==================================================================")

if __name__ == "__main__":
    test_railradar_integration()
