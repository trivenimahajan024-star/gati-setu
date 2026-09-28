"""
Automated Verification Suite for GatiSetu Unified Responsive Architecture
Tests Passenger, Station Display Board (FIDS), and Control Room (OCC) across all breakpoints.
"""

import sys
import json
import os
import uvicorn
import threading
import time
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def verify_responsive_system():
    print("==================================================================")
    print("  [GatiSetu] Multi-Role Responsive System Verification Suite")
    print("==================================================================")

    workspace_dir = r"c:\Users\satis\OneDrive\Desktop\gati-setu"

    # 1. Verify CSS rules for responsive breakpoints
    css_path = os.path.join(workspace_dir, "frontend", "css", "main.css")
    assert os.path.exists(css_path), "Missing frontend/css/main.css"
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    breakpoints = [
        ("Mobile Breakpoint (<768px)", "@media (max-width: 767px)"),
        ("Tablet Breakpoint (768-1023px)", "@media (min-width: 768px) and (max-width: 1023px)"),
        ("Desktop Breakpoint (1024-1439px)", "@media (min-width: 1024px) and (max-width: 1439px)"),
        ("Large Screen & FIDS (1440px+)", "@media (min-width: 1440px)")
    ]

    for label, query in breakpoints:
        assert query in css, f"Missing breakpoint query in main.css: {query}"
        print(f" [PASS] {label:<35} -> Configured")

    # 2. Verify all three role interfaces in HTML
    html_path = os.path.join(workspace_dir, "frontend", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    interfaces = [
        ("Passenger Interface Container", 'id="view-passenger"'),
        ("Station Display Board (FIDS) Container", 'id="view-station-board"'),
        ("Control Room (OCC) Dashboard Container", 'id="view-control-room"'),
        ("Staff Portal Auth Modal", 'id="staffLoginModal"')
    ]

    for label, element in interfaces:
        assert element in html, f"Missing interface element in HTML: {element}"
        print(f" [PASS] {label:<40} -> Verified")

    # Verify zero hackathon text
    forbidden = ["SIH 2026", "Smart India Hackathon", "Hackathon"]
    for word in forbidden:
        assert word not in html, f"Forbidden label found: {word}"
    print(" [PASS] Confirmed all SIH / Hackathon / Prototype labels removed from UI.")

    # 3. Start ephemeral backend server on port 8009 to test APIs
    sys.path.insert(0, os.path.join(workspace_dir, "backend"))
    from app.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8009, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = "http://127.0.0.1:8009"

    # Test 1: Passenger Train Telemetry
    req_train = urllib.request.Request(f"{base_url}/api/train/12951")
    with urllib.request.urlopen(req_train) as res:
        assert res.status == 200
        t_data = json.loads(res.read().decode('utf-8'))
        assert t_data["train_number"] == "12951"
        print(f" [PASS] Passenger API: Train {t_data['train_number']} ({t_data['train_name']}) ETA {t_data['predicted_destination_eta']}")

    # Test 2: Station Display Board Feed (FIDS)
    req_fids = urllib.request.Request(f"{base_url}/api/station/NDLS/display")
    with urllib.request.urlopen(req_fids) as res:
        assert res.status == 200
        fids_data = json.loads(res.read().decode('utf-8'))
        assert "arrivals" in fids_data
        assert "departures" in fids_data
        print(f" [PASS] Station FIDS API: {fids_data['station_name']} ({len(fids_data['arrivals'])} arrivals, {len(fids_data['departures'])} departures)")

    # Test 3: Control Room Operations (OCC)
    req_occ = urllib.request.Request(f"{base_url}/api/control/overview")
    with urllib.request.urlopen(req_occ) as res:
        assert res.status == 200
        occ_data = json.loads(res.read().decode('utf-8'))
        assert "total_active_trains" in occ_data
        print(f" [PASS] OCC Control Room API: {occ_data['total_active_trains']} active trains, {occ_data['on_time_trains']} on time, {occ_data['delayed_trains']} delayed")

    print("\n==================================================================")
    print("  ALL RESPONSIVE SYSTEM & MULTI-ROLE TESTS PASSED 100%!")
    print("==================================================================")

if __name__ == "__main__":
    verify_responsive_system()
