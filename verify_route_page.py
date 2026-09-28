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

import uvicorn
from app.main import app

PORT = 8016

def test_route_page_verification():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = f"http://127.0.0.1:{PORT}"
    all_passed = True

    print("\n==================================================================")
    print("  [GatiSetu] Comprehensive Passenger Route Page Test Suite")
    print("==================================================================")

    # 1. Verify HTML Structure & Element IDs
    print("\n[1] Verifying Route Page HTML Structure in frontend/index.html:")
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    required_html_elements = [
        ("screen-route", "Route screen section container"),
        ("passenger-route-layout", "Two-column Route screen layout wrapper"),
        ("routeScreenTrainNo", "Route screen Train number badge"),
        ("routeScreenRouteSubtitle", "Route screen Origin → Destination text"),
        ("routeScreenRunningStatusPill", "Route screen Running status delay badge"),
        ("routeVerticalTimelineCard", "Complete vertical station timeline card"),
        ("routeScreenTimelineContainer", "Dynamic vertical timeline spine container"),
        ("routeTimetableTableBody", "Route timetable comparison table body"),
        ("routePredictedETA", "Route screen hero dynamic predicted ETA"),
        ("routeScheduledETA", "Route screen scheduled arrival comparison"),
        ("routeDelayTag", "Route screen delay pill"),
        ("routeCurrentLocation", "Route screen live telemetry location tile"),
        ("routeCurrentSpeed", "Route screen live telemetry speed tile"),
        ("routeNextStationName", "Route screen live telemetry next stop tile"),
        ("routeScreenProgressTrackContainer", "Route screen progress track container"),
        ("btnToggleWhyEtaRoute", "Route screen 'Why is ETA changing?' accordion header"),
        ("routeWhyEtaBody", "Route screen active factors body container"),
        ("btnToggleAllFactorsRoute", "Route screen 'View all 12 factors' toggle button"),
        ("routeAllTwelveFactorsContainer", "Route screen all 12 factors drawer"),
        ("routeSmartAlertContainer", "Route screen contextual delay alert card"),
        ("phone-bottom-nav", "Floating bottom navigation bar")
    ]

    for elem_id, desc in required_html_elements:
        if elem_id in html:
            print(f"  [PASS] {desc:<50} -> Found ('{elem_id}')")
        else:
            print(f"  [FAIL] {desc:<50} -> MISSING ('{elem_id}')")
            all_passed = False

    # 2. Verify CSS Styling in frontend/css/main.css
    print("\n[2] Verifying Route Page CSS Selectors in frontend/css/main.css:")
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "css", "main.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    required_css_rules = [
        (".passenger-route-layout", "Grid layout for Route screen"),
        (".route-vertical-timeline-card", "Vertical station timeline card styling"),
        (".route-complete-timeline-spine", "Vertical station timeline spine"),
        (".route-timeline-station-node", "Station timeline node container"),
        (".route-node-bullet", "Station node bullet (completed, approaching, upcoming)"),
        (".route-node-card", "Station info card with times comparison"),
        (".route-live-train-position-block", "Live train position marker wrapper along route"),
        (".live-train-pos-card", "Distinctive glowing live train card along route"),
        (".live-train-pos-pulse", "Pulsing live train animation"),
        (".route-timetable-table-card", "Route timetable schedule comparison table card"),
        (".route-timetable-table", "Tabular station timetable comparison styling"),
        ("@media (max-width: 1023px)", "Tablet breakpoint for route layout"),
        ("@media (max-width: 767px)", "Mobile breakpoint for route layout")
    ]

    for rule, desc in required_css_rules:
        if rule in css:
            print(f"  [PASS] {desc:<50} -> Found ('{rule}')")
        else:
            print(f"  [FAIL] {desc:<50} -> MISSING ('{rule}')")
            all_passed = False

    # 3. Verify JavaScript Controllers in frontend/js/passenger_app.js
    print("\n[3] Verifying JavaScript Controller Methods in frontend/js/passenger_app.js:")
    js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "js", "passenger_app.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    required_js_symbols = [
        ("renderCompleteRouteTimeline", "Method to build complete vertical station timeline with intermediate stops"),
        ("renderRouteTimetableTable", "Method to populate tabular timetable comparison data"),
        ("routeScreenTimelineContainer", "Binding for dynamic vertical timeline container"),
        ("routeTimetableTableBody", "Binding for dynamic timetable table body"),
        ("route-live-train-position-block", "Dynamic injection of live train indicator on route"),
        ("btnToggleWhyEtaRoute", "Accordion listener for Route screen factors"),
        ("btnToggleAllFactorsRoute", "Toggle listener for Route screen 12-factor drawer"),
        ("routeScreenProgressTrackContainer", "Route screen progress timeline synchronizer")
    ]

    for sym, desc in required_js_symbols:
        if sym in js:
            print(f"  [PASS] {desc:<50} -> Found ('{sym}')")
        else:
            print(f"  [FAIL] {desc:<50} -> MISSING ('{sym}')")
            all_passed = False

    # 4. Verify Live API Endpoints for All Sample Trains
    print("\n[4] Verifying Dynamic Route Data & Intermediate Stations for Trains:")
    sample_trains = ["12951", "12860", "22436", "12002", "12259"]
    for tno in sample_trains:
        try:
            with urllib.request.urlopen(f"{base_url}/api/train/{tno}") as res:
                data = json.loads(res.read().decode('utf-8'))
                stns = data.get("stations", [])
                pred_eta = data.get("predicted_destination_eta", "")
                delay = data.get("current_delay_mins", 0)
                stn_names = [s.get("name") for s in stns]
                print(f"  [PASS] Train {tno} ({data.get('train_name')}):")
                print(f"         - Total Stations: {len(stns)} ({' -> '.join(stn_names[:3])} ... -> {stn_names[-1]})")
                print(f"         - Predicted ETA: {pred_eta}, Current Delay: +{delay} min")
                print(f"         - Current Location: {data.get('current_location')}, Speed: {data.get('current_speed_kmh')} km/h")
        except Exception as e:
            print(f"  [FAIL] Train {tno} API Fetch Failed: {e}")
            all_passed = False

    # 5. Verify 12 Factors Data Definition
    print("\n[5] Verifying 12 Problem Statement Factors Integrity in frontend/js/eta_factors.js:")
    factors_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "js", "eta_factors.js")
    with open(factors_path, "r", encoding="utf-8") as f:
        factors_js = f.read()

    twelve_factors = [
        "gps_telemetry", "signal_aspects", "sectional_runtime", "weather_conditions",
        "historical_patterns", "downstream_congestion", "speed_restrictions",
        "unscheduled_stoppages", "preceding_train_delays", "maintenance_blocks",
        "level_crossings", "operational_bottlenecks"
    ]
    for factor_id in twelve_factors:
        if factor_id in factors_js:
            print(f"  [PASS] Factor ID '{factor_id}' verified.")
        else:
            print(f"  [FAIL] Factor ID '{factor_id}' missing.")
            all_passed = False

    print("\n==================================================================")
    if all_passed:
        print("  ALL GATISETU ROUTE PAGE VERIFICATION TESTS PASSED 100%!")
    else:
        print("  SOME ROUTE PAGE TESTS FAILED.")
    print("==================================================================")

    os._exit(0 if all_passed else 1)

if __name__ == '__main__':
    test_route_page_verification()
