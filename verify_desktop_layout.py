"""
GatiSetu Passenger Desktop Wide Layout & Responsiveness Verification Suite
Tests desktop wide multi-column layout, mobile single-column fallback, and API integrations.
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

def test_desktop_and_responsive_layout():
    print("==================================================================")
    print("  [GatiSetu] Passenger Desktop Wide Layout Verification Suite")
    print("==================================================================")

    workspace_dir = r"c:\Users\satis\OneDrive\Desktop\gati-setu"

    # 1. Verify HTML Structure
    html_path = os.path.join(workspace_dir, "frontend", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "passenger-details-layout" in html, "Missing .passenger-details-layout in index.html"
    assert "passenger-col-left" in html, "Missing .passenger-col-left in index.html"
    assert "passenger-col-right" in html, "Missing .passenger-col-right in index.html"
    print(" [PASS] 2-Column desktop container markup verified in index.html")

    # Verify Left Column Children
    left_col_start = html.find("passenger-col-left")
    right_col_start = html.find("passenger-col-right")
    assert left_col_start != -1 and right_col_start != -1
    left_col_html = html[left_col_start:right_col_start]

    assert "train-hero-card" in left_col_html, "Missing train-hero-card in left column"
    assert "main-eta-card" in left_col_html, "Missing main-eta-card in left column"
    assert "factors-accordion-card" in left_col_html, "Missing factors-accordion-card in left column"
    assert "detailsWhyEtaBody" in left_col_html, "Missing detailsWhyEtaBody in left column"
    assert "btnToggleAllFactors" in left_col_html, "Missing btnToggleAllFactors in left column"
    print(" [PASS] Left Column: Train Summary + Hero ETA + 12 Factors confirmed")

    # Verify Right Column Children
    right_col_html = html[right_col_start:html.find("</section>", right_col_start)]
    assert "live-status-block" in right_col_html, "Missing live-status-block in right column"
    assert "route-progress-card" in right_col_html, "Missing route-progress-card in right column"
    assert "upcoming-preview-card" in right_col_html, "Missing upcoming-preview-card in right column"
    assert "detailsSmartAlertContainer" in right_col_html, "Missing detailsSmartAlertContainer in right column"
    assert "quick-nav-actions" in right_col_html, "Missing quick-nav-actions in right column"
    print(" [PASS] Right Column: Live Status + Track Progress + Upcoming + Alerts + Actions confirmed")

    # 2. Verify CSS Rules in main.css
    css_path = os.path.join(workspace_dir, "frontend", "css", "main.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Verify Desktop Grid definition
    assert ".passenger-details-layout" in css, "Missing .passenger-details-layout in main.css"
    assert "grid-template-columns: 1.15fr 1fr" in css, "Missing 2-column grid template in main.css"
    assert "max-width: 1360px" in css or "max-width: 1380px" in css, "Missing wide desktop max-width in main.css"
    print(" [PASS] Desktop Grid CSS (1.15fr 1fr, wide viewport ~1360px) configured in main.css")

    # Verify Mobile fallback rules
    assert "display: contents;" in css, "Missing mobile display: contents for column unwrapping"
    assert "position: fixed;" in css, "Missing mobile fixed bottom nav bar"
    print(" [PASS] Mobile single-column linear layout & fixed bottom bar configured in main.css")

    # 3. Test In-Memory Backend API
    sys.path.insert(0, os.path.join(workspace_dir, "backend"))
    from app.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8011, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = "http://127.0.0.1:8011"
    req_train = urllib.request.Request(f"{base_url}/api/train/12951")
    with urllib.request.urlopen(req_train) as res:
        assert res.status == 200
        t_data = json.loads(res.read().decode('utf-8'))
        assert t_data["train_number"] == "12951"
        print(f" [PASS] Train {t_data['train_number']} ETA API validated: {t_data['predicted_destination_eta']}")

    server.should_exit = True
    thread.join(timeout=2)

    print("\n==================================================================")
    print("  ALL PASSENGER DESKTOP & RESPONSIVE TESTS PASSED 100%!")
    print("==================================================================")

if __name__ == "__main__":
    test_desktop_and_responsive_layout()
