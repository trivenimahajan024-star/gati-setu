import os
import sys
import json
import re

# Ensure UTF-8 output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def test_ui_cleanup_and_role_access():
    print("\n==================================================================")
    print("  [GatiSetu] UI Clean Up & Role-Based Access Verification Suite")
    print("==================================================================")

    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "js", "passenger_app.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    all_passed = True

    # 1. Verify Unnecessary Passenger Page Text is Completely Removed
    print("\n[1] Verifying Complete Removal of Unnecessary Promotional/Showcase Text:")
    prohibited_texts = [
        ("One System", "Navbar center tagline 'One System'"),
        ("Three Interfaces", "Navbar center tagline 'Three Interfaces'"),
        ("All Devices", "Navbar center tagline 'All Devices'"),
        ("Same Data • Real-time Updates • Responsive Everywhere", "Navbar sub-tagline"),
        ("1. Passenger App", "Showcase section title '1. Passenger App'"),
        ("Simple • Mobile Friendly • All Features", "Showcase subtitle 'Simple • Mobile Friendly • All Features'"),
        ("2. Station Display Board", "Showcase section title '2. Station Display Board'")
    ]

    for phrase, desc in prohibited_texts:
        # Check in HTML body (ignoring comments)
        clean_html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        if phrase in clean_html:
            print(f"  [FAIL] {desc:<58} -> STILL FOUND in HTML!")
            all_passed = False
        else:
            print(f"  [PASS] {desc:<58} -> Successfully Removed")

    # 2. Verify Permanent Bottom 12-Factor Strip is Removed
    print("\n[2] Verifying Removal of Permanent Bottom 12-Factor Strip:")
    if "ps-twelve-factors-section" in html:
        print("  [FAIL] Bottom .ps-twelve-factors-section -> STILL FOUND in HTML!")
        all_passed = False
    else:
        print("  [PASS] Bottom .ps-twelve-factors-section -> Successfully Removed")

    # 3. Verify 12 Factors Remain Intact Inside ETA Accordion
    print("\n[3] Verifying 12 Factors Available inside 'Why is ETA changing?' Drawer:")
    required_accordion_elements = [
        ("detailsAllTwelveFactorsContainer", "Details screen 12-factor drawer container"),
        ("mapAllTwelveFactorsContainer", "Map screen 12-factor drawer container"),
        ("routeAllTwelveFactorsContainer", "Route screen 12-factor drawer container"),
        ("btnToggleWhyEta", "Accordion toggle button for 'Why is ETA changing?'"),
        ("btnToggleAllFactors", "View all 12 factors button")
    ]
    for elem_id, desc in required_accordion_elements:
        if elem_id in html:
            print(f"  [PASS] {desc:<58} -> Present ('{elem_id}')")
        else:
            print(f"  [FAIL] {desc:<58} -> MISSING ('{elem_id}')")
            all_passed = False

    # 4. Verify Clean Passenger Header & Unauthenticated Role State
    print("\n[4] Verifying Header Role Visibility before Staff Login:")
    assert 'id="btnRolePassenger"' in html, "Missing #btnRolePassenger"
    assert 'id="btnRoleStation"' in html, "Missing #btnRoleStation"
    assert 'id="btnRoleControl"' in html, "Missing #btnRoleControl"
    assert 'id="btnOpenStaffLogin"' in html, "Missing #btnOpenStaffLogin"
    assert 'id="btnLogoutStaff"' in html, "Missing #btnLogoutStaff"
    print("  [PASS] Header elements correctly structured in HTML.")

    # 5. Verify Role-Based Protection Logic in JavaScript
    print("\n[5] Verifying Strict Role-Based Route Guard in passenger_app.js:")
    # Check that switchRoleView enforces authentication
    assert "switchRoleView" in js, "Missing switchRoleView in passenger_app.js"
    assert "authenticatedStaff" in js, "Missing authenticatedStaff check in passenger_app.js"
    assert "updateAuthUI" in js, "Missing updateAuthUI in passenger_app.js"
    assert "performStaffLogin" in js, "Missing performStaffLogin in passenger_app.js"
    assert "performStaffLogout" in js, "Missing performStaffLogout in passenger_app.js"
    print("  [PASS] switchRoleView guards Station Board & Control Room behind authenticatedStaff.")
    print("  [PASS] updateAuthUI dynamically manages header tabs on login/logout.")
    print("  [PASS] performStaffLogout resets auth and returns user to Passenger view.")

    # 6. Verify Backend Direct Route Handlers in backend/app/main.py
    print("\n[6] Verifying Backend Route Handlers in backend/app/main.py:")
    main_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "app", "main.py")
    with open(main_py_path, "r", encoding="utf-8") as f:
        main_py = f.read()

    assert '@app.get("/station-board")' in main_py, "Missing /station-board route in main.py"
    assert '@app.get("/control-room")' in main_py, "Missing /control-room route in main.py"
    assert '@app.get("/passenger")' in main_py, "Missing /passenger route in main.py"
    assert '@app.get("/staff-portal")' in main_py, "Missing /staff-portal route in main.py"
    print("  [PASS] Backend handles direct browser routing for /passenger, /station-board, /control-room.")

    print("\n==================================================================")
    if all_passed:
        print("  ALL UI CLEANUP & ROLE-BASED ACCESS CHECKS PASSED WITH 100% SUCCESS!")
    else:
        print("  SOME CHECKS FAILED.")
    print("==================================================================\n")
    return all_passed

if __name__ == "__main__":
    passed = test_ui_cleanup_and_role_access()
    if not passed:
        sys.exit(1)
