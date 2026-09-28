import re
import sys

def test_alerts_page():
    print("=" * 66)
    print("  [GatiSetu] Passenger Alerts Page Verification Suite")
    print("=" * 66)

    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    with open("frontend/css/main.css", "r", encoding="utf-8") as f:
        css_content = f.read()

    with open("frontend/js/passenger_app.js", "r", encoding="utf-8") as f:
        js_content = f.read()

    errors = []

    # 1. Verify absence of prohibited text
    print("\n[1] Verifying Clean Text (No Showcase/Promotional Headings):")
    prohibited_patterns = [
        ("1. Passenger App", r"1\.\s*Passenger\s*App"),
        ("Simple • Mobile Friendly", r"Simple\s*•\s*Mobile\s*Friendly"),
        ("Problem Statement Factors strip", r"class=[\"']ps-twelve-factors-section[\"']"),
    ]
    for label, pat in prohibited_patterns:
        if re.search(pat, html_content, re.IGNORECASE):
            print(f"  [FAIL] Found prohibited string '{label}' in HTML")
            errors.append(f"Prohibited text '{label}' found in index.html")
        else:
            print(f"  [PASS] Clean text confirmed: No '{label}' in UI")

    # 2. Verify Alerts Screen Structure
    print("\n[2] Verifying Alerts Screen Required Elements:")
    required_elements = [
        ("Screen section #screen-alerts", r'<section\s+id=["\']screen-alerts["\']'),
        ("Screen main title 'Operational Alerts'", r'<h2\s+class=["\']screen-main-title["\']>\s*(<i[^>]*></i>\s*)?Operational Alerts'),
        ("Screen subtitle", r'class=["\']screen-sub-title["\']'),
        ("Back button to Overview", r'data-target-screen=["\']screen-details["\']'),
        ("Train Summary Card train number", r'id=["\']alertsScreenTrainNo["\']'),
        ("Train Summary Card route", r'id=["\']alertsScreenRouteSubtitle["\']'),
        ("Train Summary Card running pill", r'id=["\']alertsScreenRunningStatusPill["\']'),
        ("Alerts feed card container", r'class=["\']alerts-feed-card["\']'),
        ("Alerts count badge", r'id=["\']alertsFeedCountBadge["\']'),
        ("Alerts list container #passengerAlertsList", r'id=["\']passengerAlertsList["\']'),
        ("Bottom Navigation with Alerts tab", r'data-target-screen=["\']screen-alerts["\']'),
    ]

    for label, pat in required_elements:
        if re.search(pat, html_content):
            print(f"  [PASS] {label:48} -> Present")
        else:
            print(f"  [FAIL] {label:48} -> MISSING")
            errors.append(f"Missing element: {label}")

    # 3. Verify CSS styling for clean, responsive alerts page
    print("\n[3] Verifying Alerts CSS Styling:")
    required_css = [
        (".passenger-alerts-layout", r"\.passenger-alerts-layout\s*\{"),
        (".alerts-feed-card", r"\.alerts-feed-card\s*\{"),
        (".alerts-feed-header", r"\.alerts-feed-header\s*\{"),
        (".alerts-feed-count-tag", r"\.alerts-feed-count-tag\s*\{"),
        (".passenger-alert-card", r"\.passenger-alert-card\s*\{"),
        (".passenger-alert-card.alert-severity-info", r"\.passenger-alert-card\.alert-severity-info"),
        (".passenger-alert-card.alert-severity-warning", r"\.passenger-alert-card\.alert-severity-warning"),
        (".passenger-alert-card.alert-severity-danger", r"\.passenger-alert-card\.alert-severity-danger"),
        (".alerts-empty-state", r"\.alerts-empty-state\s*\{"),
    ]

    for label, pat in required_css:
        if re.search(pat, css_content):
            print(f"  [PASS] {label:48} -> Defined in CSS")
        else:
            print(f"  [FAIL] {label:48} -> MISSING in CSS")
            errors.append(f"Missing CSS rule: {label}")

    # 4. Verify JS implementation
    print("\n[4] Verifying JavaScript Logic:")
    required_js = [
        ("renderPassengerAlerts method", r"renderPassengerAlerts\s*\(\s*train\s*\)"),
        ("alertsScreenTrainNo update", r"alertsScreenTrainNo"),
        ("alertsScreenRunningStatusPill update", r"alertsScreenRunningStatusPill"),
        ("alertsFeedCountBadge update", r"alertsFeedCountBadge"),
        ("renderPassengerAlerts called in renderTrainDetails", r"this\.renderPassengerAlerts\s*\(\s*train\s*\)"),
    ]

    for label, pat in required_js:
        if re.search(pat, js_content):
            print(f"  [PASS] {label:48} -> Implemented in JS")
        else:
            print(f"  [FAIL] {label:48} -> MISSING in JS")
            errors.append(f"Missing JS logic: {label}")

    print("\n" + "=" * 66)
    if errors:
        print(f"  FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)
    else:
        print("  ALL PASSENGER ALERTS PAGE CHECKS PASSED WITH 100% SUCCESS!")
        print("=" * 66)

if __name__ == "__main__":
    test_alerts_page()
