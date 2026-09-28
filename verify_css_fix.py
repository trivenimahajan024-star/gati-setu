import sys
import json
import os
import uvicorn
import threading
import time
import urllib.request

def test_css_and_ui():
    print("==================================================================")
    print("  GatiSetu Passenger UI CSS Fix Verification Suite")
    print("==================================================================")

    workspace_dir = r"c:\Users\satis\OneDrive\Desktop\gati-setu"

    # 1. Verify CSS file exists and has content
    css_path = os.path.join(workspace_dir, "frontend", "css", "main.css")
    assert os.path.exists(css_path), f"Missing {css_path}"
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    print(f" [PASS] CSS file loaded. Size: {len(css_content)} bytes")

    # 2. Verify all key class selectors exist in main.css
    required_classes = [
        "phone-frame-wrapper",
        "phone-screen-canvas",
        "phone-bottom-nav",
        "bottom-tab-item",
        "btn-search-main",
        "search-input",
        "popular-chips",
        "train-chip",
        "train-hero-card",
        "train-status-badge",
        "main-eta-card",
        "eta-big-time",
        "eta-delay-pill",
        "live-status-block",
        "tri-card",
        "route-progress-card",
        "factors-accordion-card",
        "factor-mini-row",
        "eta-pill",
        "pill-high",
        "pill-moderate",
        "pill-low",
        "pill-success",
        "pill-nominal",
        "upcoming-preview-card",
        "station-preview-item",
        "smart-alert-card",
        "station-timeline-card",
        "passenger-alert-card"
    ]

    for cls in required_classes:
        assert cls in css_content, f"Missing selector in main.css: {cls}"
        print(f" [PASS] CSS selector verified: .{cls}")

    # 3. Check HTML references
    html_path = os.path.join(workspace_dir, "frontend", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    forbidden_terms = ["SIH 2026", "Smart India Hackathon", "Hackathon", "Demo Prototype"]
    for term in forbidden_terms:
        assert term not in html_content, f"Forbidden term found in HTML: {term}"
    print(" [PASS] Clean branding confirmed (No SIH / Hackathon in HTML).")

    # 4. Start ephemeral server on port 8008 to test HTTP response and mime types
    sys.path.insert(0, os.path.join(workspace_dir, "backend"))
    from app.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8008, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = "http://127.0.0.1:8008"

    # Test /css/main.css delivery
    req_css = urllib.request.Request(f"{base_url}/css/main.css")
    with urllib.request.urlopen(req_css) as res:
        assert res.status == 200
        css_served = res.read().decode('utf-8')
        assert "GatiSetu" in css_served
        assert "btn-search-main" in css_served
    print(" [PASS] HTTP GET /css/main.css returned status 200 with full stylesheet.")

    # Test Root HTML delivery
    req_root = urllib.request.Request(f"{base_url}/")
    with urllib.request.urlopen(req_root) as res:
        assert res.status == 200
        html_served = res.read().decode('utf-8')
        assert "GatiSetu" in html_served
        assert "phone-bottom-nav" in html_served
    print(" [PASS] HTTP GET / returned status 200 with root index.html.")

    # Test API Telemetry
    req_api = urllib.request.Request(f"{base_url}/api/train/12951")
    with urllib.request.urlopen(req_api) as res:
        assert res.status == 200
        data = json.loads(res.read().decode('utf-8'))
        assert data["train_number"] == "12951"
        assert len(data["eta_factors"]) > 0
    print(" [PASS] Dynamic ETA API /api/train/12951 working seamlessly.")

    print("\n==================================================================")
    print("  ALL CSS & PASSENGER UI TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================================")

if __name__ == "__main__":
    test_css_and_ui()
