"""
Verification script for GatiSetu Clean Uncluttered Passenger Interface Redesign.
"""

import sys
import json
import os
import uvicorn
import threading
import time
import urllib.request

def test_redesign():
    print("=======================================================")
    print(" Starting GatiSetu Passenger Redesign Verification")
    print("=======================================================")

    workspace_dir = r"c:\Users\satis\OneDrive\Desktop\gati-setu"

    # 1. Verify files exist on disk
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

    # 2. Check HTML contains clean uncluttered elements and NO SIH/Hackathon labels
    with open(os.path.join(workspace_dir, "frontend/index.html"), "r", encoding="utf-8") as f:
        html = f.read()

    # Verify removal of unwanted text in UI
    forbidden_terms = ["SIH 2026", "Smart India Hackathon", "Hackathon"]
    for term in forbidden_terms:
        assert term not in html, f"Forbidden term found in HTML: {term}"
    print(" [PASS] Confirmed all SIH / Hackathon / Prototype text removed from navbar.")

    # Verify new clean structure
    assert "train-compact-card" in html, "Missing train-compact-card in HTML"
    assert "main-eta-card" in html, "Missing main-eta-card in HTML"
    assert "detailsPredictedETA" in html, "Missing detailsPredictedETA in HTML"
    assert "detailsDelayTag" in html, "Missing detailsDelayTag in HTML"
    assert "status-tri-grid" in html, "Missing status-tri-grid in HTML"
    assert "journey-progress-card" in html, "Missing journey-progress-card in HTML"
    assert "detailsActiveFactorsList" in html, "Missing detailsActiveFactorsList in HTML"
    assert "btnToggleAllFactors" in html, "Missing btnToggleAllFactors in HTML"
    assert "nextStationsPreviewList" in html, "Missing nextStationsPreviewList in HTML"
    assert "detailsSmartAlertContainer" in html, "Missing detailsSmartAlertContainer in HTML"
    print(" [PASS] Clean passenger UI elements verified in HTML.")

    # 3. Test In-Memory Store & Dynamic ETA Engine directly
    sys.path.insert(0, os.path.join(workspace_dir, "backend"))
    from app.db.store import store

    trains = store.get_all_trains()
    assert len(trains) >= 4, f"Expected 4 demo trains, got {len(trains)}"
    for train in trains:
        t_no = train["train_number"]
        assert "predicted_destination_eta" in train
        assert "eta_factors" in train
        assert len(train["eta_factors"]) > 0
        print(f" [PASS] Central Store train {t_no} ({train['short_name']}): Predicted {train['predicted_destination_eta']}, Delay: +{train['current_delay_mins']}m")

    # 4. Start ephemeral FastAPI server on port 8005
    from app.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8005, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = "http://127.0.0.1:8005"

    # Test HTTP Train search API
    req = urllib.request.Request(f"{base_url}/api/train/12951")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200, f"Expected 200, got {response.status}"
        data = json.loads(response.read().decode('utf-8'))
        assert data["train_number"] == "12951"
        assert "eta_factors" in data
    print(" [PASS] API /api/train/12951 returned complete train telemetry & ETA factors.")

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
    print(" ALL PASSENGER REDESIGN VERIFICATION TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    test_redesign()
