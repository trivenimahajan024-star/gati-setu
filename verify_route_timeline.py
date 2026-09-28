"""
GatiSetu Route Timeline with Intermediate Stations Verification Suite
Validates intermediate station rendering along the route line for both Desktop and Mobile interfaces.
"""

import os
import sys
import json
import uvicorn
import threading
import time
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def test_route_timeline():
    print("==================================================================")
    print("  [GatiSetu] Route Timeline with Intermediate Stations Test Suite")
    print("==================================================================")

    workspace_dir = r"c:\Users\satis\OneDrive\Desktop\gati-setu"

    # 1. Verify HTML Structure
    html_path = os.path.join(workspace_dir, "frontend", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "routeTimelineTrackContainer" in html, "Missing #routeTimelineTrackContainer in index.html"
    assert "detailsSourceCode" in html, "Missing #detailsSourceCode in index.html"
    assert "detailsDestCode" in html, "Missing #detailsDestCode in index.html"
    assert "detailsProgressPct" in html, "Missing #detailsProgressPct in index.html"
    assert "detailsDistanceMeta" in html, "Missing #detailsDistanceMeta in index.html"
    print(" [PASS] index.html: Container and backward-compatible IDs verified")

    # 2. Verify CSS Rules in main.css
    css_path = os.path.join(workspace_dir, "frontend", "css", "main.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Desktop timeline classes
    assert ".route-timeline-desktop" in css, "Missing .route-timeline-desktop in main.css"
    assert ".timeline-h-rail-bg" in css, "Missing .timeline-h-rail-bg in main.css"
    assert ".timeline-h-rail-fill" in css, "Missing .timeline-h-rail-fill in main.css"
    assert ".timeline-h-train-pointer" in css, "Missing .timeline-h-train-pointer in main.css"
    assert ".h-train-marker-badge" in css, "Missing .h-train-marker-badge in main.css"
    assert ".timeline-h-stations-row" in css, "Missing .timeline-h-stations-row in main.css"
    assert ".h-stn-node" in css, "Missing .h-stn-node in main.css"
    assert ".h-node-bullet" in css, "Missing .h-node-bullet in main.css"
    assert ".node-completed" in css, "Missing .node-completed in main.css"
    assert ".node-approaching" in css, "Missing .node-approaching in main.css"
    assert ".node-upcoming" in css, "Missing .node-upcoming in main.css"
    print(" [PASS] main.css: Desktop horizontal timeline, rail, floating train badge, and node styles verified")

    # Mobile timeline classes
    assert ".route-timeline-mobile" in css, "Missing .route-timeline-mobile in main.css"
    assert ".timeline-v-scroll-container" in css, "Missing .timeline-v-scroll-container in main.css"
    assert ".timeline-v-track" in css, "Missing .timeline-v-track in main.css"
    assert ".timeline-v-station" in css, "Missing .timeline-v-station in main.css"
    assert ".v-node-dot" in css, "Missing .v-node-dot in main.css"
    assert ".v-current-badge" in css, "Missing .v-current-badge in main.css"
    print(" [PASS] main.css: Mobile vertical spine, bullet states, and live train position card verified")

    # Responsive Media Query
    assert "@media (max-width: 767px)" in css or "@media (max-width: 768px)" in css, "Missing media query for timeline"
    print(" [PASS] main.css: Responsive media query toggling desktop/mobile timelines verified")

    # 3. Verify JavaScript Logic in passenger_app.js
    js_path = os.path.join(workspace_dir, "frontend", "js", "passenger_app.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    assert "renderRouteTimeline(train)" in js, "Missing renderRouteTimeline in passenger_app.js"
    assert "route-timeline-desktop" in js, "renderRouteTimeline must generate .route-timeline-desktop"
    assert "route-timeline-mobile" in js, "renderRouteTimeline must generate .route-timeline-mobile"
    assert "h-train-marker-badge" in js, "renderRouteTimeline must generate .h-train-marker-badge"
    assert "v-current-badge" in js, "renderRouteTimeline must generate .v-current-badge"
    assert "train.stations" in js, "renderRouteTimeline must use train.stations dynamically"
    print(" [PASS] passenger_app.js: renderRouteTimeline dynamically constructs desktop and mobile timeline views")

    # 4. Verify Backend Data for Intermediate Stations
    sys.path.insert(0, os.path.join(workspace_dir, "backend"))
    from app.db.store import store

    all_trains = store.get_all_trains()
    assert len(all_trains) >= 4, f"Expected at least 4 trains, got {len(all_trains)}"
    
    for train in all_trains:
        t_num = train["train_number"]
        stations = train.get("stations", [])
        assert len(stations) >= 3, f"Train {t_num} has only {len(stations)} stations, expected intermediate stations"
        stn_names = [s.get("name", s.get("station_name", "")) for s in stations]
        print(f" [PASS] Train {t_num} ({train['train_name']}): {len(stations)} stations -> {' -> '.join(stn_names[:3])} ... -> {stn_names[-1]}")

    # 5. Start API Server and test endpoint
    from app.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8012, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = "http://127.0.0.1:8012"
    for t_num in ["12951", "12860", "22436", "12002"]:
        req = urllib.request.Request(f"{base_url}/api/train/{t_num}")
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            data = json.loads(res.read().decode('utf-8'))
            assert "stations" in data and len(data["stations"]) >= 3
            print(f" [PASS] API /api/train/{t_num} returns {len(data['stations'])} intermediate stations")

    server.should_exit = True
    thread.join(timeout=2)

    print("\n==================================================================")
    print("  ALL ROUTE TIMELINE VERIFICATION TESTS PASSED 100%!")
    print("==================================================================")

if __name__ == "__main__":
    test_route_timeline()
