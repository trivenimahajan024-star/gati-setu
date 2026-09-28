import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoints():
    print("=" * 80)
    print("TESTING ALL GATISETU API ENDPOINTS")
    print("=" * 80)

    # 1. Test get train details for multiple trains
    for tno in ["12951", "12626", "22691"]:
        resp = client.get(f"/api/train/{tno}")
        assert resp.status_code == 200, f"Failed /api/train/{tno}: {resp.text}"
        data = resp.json()
        print(f"[OK] /api/train/{tno} -> {data['train_name']} ({data['source_code']} -> {data['destination_code']}, {data['total_distance_km']} km)")

    # 2. Test live telemetry endpoint
    resp = client.get("/api/train/12951/live")
    assert resp.status_code == 200, f"Failed /api/train/12951/live: {resp.text}"
    print(f"[OK] /api/train/12951/live -> {resp.json().get('current_location')}, delay: {resp.json().get('current_delay_mins')}m")

    # 3. Test route polyline endpoint
    resp = client.get("/api/train/12951/route")
    assert resp.status_code == 200, f"Failed /api/train/12951/route: {resp.text}"
    print(f"[OK] /api/train/12951/route -> stations: {len(resp.json().get('stations', []))}, polyline points: {len(resp.json().get('route_polyline', []))}")

    # 4. Test GPS status endpoint
    resp = client.get("/api/train/12951/gps")
    assert resp.status_code == 200, f"Failed /api/train/12951/gps: {resp.text}"
    print(f"[OK] /api/train/12951/gps -> {resp.json()}")

    # 5. Test ML ETA endpoint
    resp = client.get("/api/train/12951/ml-eta")
    assert resp.status_code == 200, f"Failed /api/train/12951/ml-eta: {resp.text}"
    print(f"[OK] /api/train/12951/ml-eta -> predicted_eta: {resp.json().get('predicted_eta')}, confidence: {resp.json().get('confidence_pct')}%")

    # 6. Test Trains Between Stations
    resp = client.get("/api/trains/between-stations?from_station=MMCT&to_station=NDLS")
    assert resp.status_code == 200, f"Failed trains between: {resp.text}"
    data = resp.json()
    print(f"[OK] /api/trains/between-stations (MMCT -> NDLS) -> {data.get('total_trains')} trains found")

    resp2 = client.get("/api/trains/between-stations?from_station=Bhusawal&to_station=Mumbai")
    assert resp2.status_code == 200, f"Failed trains between BSL-CSMT: {resp2.text}"
    print(f"[OK] /api/trains/between-stations (Bhusawal -> Mumbai) -> {resp2.json().get('total_trains')} trains found")

    # 7. Test Control Room endpoints
    resp = client.get("/api/control/overview")
    assert resp.status_code == 200, f"Failed /api/control/overview: {resp.text}"
    print(f"[OK] /api/control/overview -> {resp.json()}")

    resp = client.get("/api/control/trains")
    assert resp.status_code == 200, f"Failed /api/control/trains: {resp.text}"
    print(f"[OK] /api/control/trains -> {len(resp.json())} trains in control room")

    print("\nALL API ENDPOINTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_api_endpoints()
