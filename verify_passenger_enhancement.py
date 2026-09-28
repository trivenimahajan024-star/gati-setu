"""
Verification script for GatiSetu Passenger Interface Enhancement.
Uses standard library urllib.request to avoid external dependency issues.
"""

import sys
import json
import os
import uvicorn
import threading
import time
import urllib.request

def test_system():
    print("=======================================================")
    print(" Starting GatiSetu Passenger Interface Enhancement Test")
    print("=======================================================")

    # 1. Verify files exist on disk
    workspace_dir = r"c:\Users\satis\OneDrive\Desktop\gati-setu"
    required_files = [
        "frontend/index.html",
        "frontend/css/main.css",
        "frontend/js/eta_factors.js",
        "frontend/js/data_service.js",
        "frontend/js/passenger_app.js",
        "backend/app/main.py",
        "backend/app/db/store.py",
        "backend/app/engine/eta_engine.py"
    ]

    for rel_path in required_files:
        full_path = os.path.join(workspace_dir, rel_path)
        assert os.path.exists(full_path), f"Missing required file: {rel_path}"
        print(f" [PASS] File exists: {rel_path}")

    # 2. Check HTML contains all required passenger UI elements
    with open(os.path.join(workspace_dir, "frontend/index.html"), "r", encoding="utf-8") as f:
        html_content = f.read()

    assert "dynamic-eta-core-card" in html_content, "Missing dynamic-eta-core-card in HTML"
    assert "eta-prominent-display" in html_content, "Missing eta-prominent-display in HTML"
    assert "detailsPredictedETA" in html_content, "Missing detailsPredictedETA element"
    assert "detailsConfidenceBadge" in html_content, "Missing detailsConfidenceBadge element"
    assert "live-status-card" in html_content, "Missing live-status-card in HTML"
    assert "detailsCurrentSpeed" in html_content, "Missing detailsCurrentSpeed in HTML"
    assert "detailsCurrentSection" in html_content, "Missing detailsCurrentSection in HTML"
    assert "eta-explainability-card" in html_content, "Missing eta-explainability-card in HTML"
    assert "whyEtaContent" in html_content, "Missing whyEtaContent in HTML"
    assert "delay-impact-card" in html_content, "Missing delay-impact-card in HTML"
    assert "upcoming-stations-list" in html_content, "Missing upcoming-stations-list in HTML"
    assert "passenger-alerts-list" in html_content, "Missing passenger-alerts-list in HTML"
    assert "eta_factors.js" in html_content, "Missing eta_factors.js script tag"
    print(" [PASS] HTML component structure verified.")

    # 3. Test In-Memory Store & Dynamic ETA Engine directly
    sys.path.insert(0, os.path.join(workspace_dir, "backend"))
    from app.db.store import railway_store
    from app.engine.eta_engine import eta_engine

    trains = railway_store.get_all_trains()
    assert len(trains) >= 4, f"Expected at least 4 demo trains, got {len(trains)}"
    print(f" [PASS] Central Store loaded {len(trains)} active coaching trains.")

    for train in trains:
        t_no = train["train_number"]
        assert "predicted_destination_eta" in train, f"Train {t_no} missing predicted_destination_eta"
        assert "arrival_window" in train, f"Train {t_no} missing arrival_window"
        assert "confidence_pct" in train, f"Train {t_no} missing confidence_pct"
        assert "eta_factors" in train, f"Train {t_no} missing eta_factors"
        assert "stations" in train, f"Train {t_no} missing stations"

        active_factors = [f for f in train["eta_factors"] if f.get("is_active")]
        print(f" [PASS] Train {t_no} ({train['short_name']}): Sched: {train.get('scheduled_destination_eta')}, Predicted: {train.get('predicted_destination_eta')}, Delay: +{train.get('current_delay_mins')}m, Active Factors: {len(active_factors)}")

    # 4. Start ephemeral FastAPI server on port 8004
    from app.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8004, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = "http://127.0.0.1:8004"

    # Test HTTP Train search API
    req = urllib.request.Request(f"{base_url}/api/trains/12951")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200, f"Expected 200, got {response.status}"
        data = json.loads(response.read().decode('utf-8'))
        assert data["train_number"] == "12951"
        assert "eta_factors" in data
        assert len(data["eta_factors"]) > 0
    print(" [PASS] API /api/trains/12951 returned complete train telemetry & ETA factors.")

    # Test Static Index delivery
    req_index = urllib.request.Request(f"{base_url}/")
    with urllib.request.urlopen(req_index) as response_index:
        assert response_index.status == 200
        html_resp = response_index.read().decode('utf-8')
        assert "GatiSetu" in html_resp
    print(" [PASS] Static web client served successfully.")

    # Stop server
    server.should_exit = True
    thread.join(timeout=2)

    print("\n=======================================================")
    print(" ALL PASSENGER ENHANCEMENT VERIFICATION TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    test_system()
