import os
import sys
import time
import threading
import urllib.request
import json

# Ensure UTF-8 output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

import uvicorn
from app.main import app

PORT = 8017

def test_staff_login_verification():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = f"http://127.0.0.1:{PORT}"
    all_passed = True

    print("\n==================================================================")
    print("  [GatiSetu] Staff Login Two-Column Design Verification Suite")
    print("==================================================================")

    # 1. Verify HTML Structure & Two-Column Elements
    print("\n[1] Verifying Staff Login HTML Structure in frontend/index.html:")
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    required_html_elements = [
        ("staffLoginModal", "Staff Login modal backdrop"),
        ("staff-login-dialog-container", "Two-column login dialog container"),
        ("staff-login-visual-col", "LEFT Column: Railway Visual & Telemetry Network"),
        ("railway-vector-art", "Modern railway vector illustration"),
        ("live-train-moving-group", "Aerodynamic live train group"),
        ("staff-login-form-col", "RIGHT Column: Staff Login card"),
        ("STAFF PORTAL", "Staff Portal heading"),
        ("btnQuickLoginStation", "1-Click Quick Login: Station Master"),
        ("btnQuickLoginOCC", "1-Click Quick Login: OCC Controller"),
        ("staffRoleSelect", "Role Authorization dropdown"),
        ("staffUsernameInput", "Staff ID / Employee ID input"),
        ("staffPasswordInput", "Password input field"),
        ("btnToggleStaffPassword", "Password show/hide toggle eye button"),
        ("btnForgotStaffPassword", "Forgot Password link"),
        ("staffLoginError", "Error alert container"),
        ("btn-staff-sign-in", "Sign In submit button")
    ]

    for elem_id, desc in required_html_elements:
        if elem_id in html:
            print(f"  [PASS] {desc:<52} -> Found ('{elem_id}')")
        else:
            print(f"  [FAIL] {desc:<52} -> MISSING ('{elem_id}')")
            all_passed = False

    # 2. Verify CSS Styling & Responsive Rules
    print("\n[2] Verifying Staff Login CSS in frontend/css/main.css:")
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "css", "main.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    required_css_rules = [
        (".staff-login-dialog-container", "Two-column grid layout for dialog"),
        (".staff-login-visual-col", "Left visual column gradient and telemetry styling"),
        (".railway-vector-art", "Railway vector illustration styling"),
        (".live-train-moving-group", "Live train movement animation"),
        (".staff-login-form-col", "Right login card styling"),
        (".btn-staff-sign-in", "GatiSetu green Sign In button"),
        (".btn-toggle-eye", "Password eye icon toggle styling"),
        ("@media (max-width: 1023px)", "Tablet breakpoint for login dialog"),
        ("@media (max-width: 767px)", "Mobile single-column stacking rule")
    ]

    for rule, desc in required_css_rules:
        if rule in css:
            print(f"  [PASS] {desc:<52} -> Found ('{rule}')")
        else:
            print(f"  [FAIL] {desc:<52} -> MISSING ('{rule}')")
            all_passed = False

    # 3. Verify JavaScript Logic in frontend/js/passenger_app.js
    print("\n[3] Verifying JavaScript Auth Handler in frontend/js/passenger_app.js:")
    js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "js", "passenger_app.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    required_js_symbols = [
        ("setupStaffAuthModal", "Staff authentication modal setup method"),
        ("performStaffLogin", "Staff login API dispatch & role router method"),
        ("btnToggleStaffPassword", "Password visibility toggle listener"),
        ("btnForgotStaffPassword", "Forgot Password credentials helper"),
        ("btnQuickLoginStation", "Station Master preset handler"),
        ("btnQuickLoginOCC", "OCC Controller preset handler")
    ]

    for sym, desc in required_js_symbols:
        if sym in js:
            print(f"  [PASS] {desc:<52} -> Found ('{sym}')")
        else:
            print(f"  [FAIL] {desc:<52} -> MISSING ('{sym}')")
            all_passed = False

    # 4. Verify Backend Auth API for Both Roles
    print("\n[4] Verifying Staff Authentication Endpoints:")
    credentials = [
        ("station_master", "railway123", "station_staff", "Station Superintendent Arun Sharma"),
        ("occ_controller", "admin123", "control_room", "Chief Controller Vikram Malhotra")
    ]
    for user, pwd, role, expected_name in credentials:
        payload = json.dumps({"username": user, "password": pwd, "role": role}).encode('utf-8')
        req = urllib.request.Request(
            f"{base_url}/api/auth/login",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as res:
                res_data = json.loads(res.read().decode('utf-8'))
                print(f"  [PASS] Login Success: User '{user}' -> Role '{res_data.get('role')}' ({res_data.get('name')})")
        except Exception as e:
            print(f"  [FAIL] Login Failed for '{user}': {e}")
            all_passed = False

    # 5. Verify Invalid Login Error Handling
    bad_payload = json.dumps({"username": "unknown_user", "password": "wrong_password", "role": "invalid_role"}).encode('utf-8')
    bad_req = urllib.request.Request(
        f"{base_url}/api/auth/login",
        data=bad_payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(bad_req)
        print("  [FAIL] Expected 401 Unauthorized for bad credentials, got 200 OK")
        all_passed = False
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"  [PASS] Invalid credentials correctly rejected (HTTP {e.code} Unauthorized)")
        else:
            print(f"  [WARN] Unexpected HTTP code: {e.code}")

    print("\n==================================================================")
    if all_passed:
        print("  ALL GATISETU STAFF LOGIN TESTS PASSED 100%!")
    else:
        print("  SOME STAFF LOGIN TESTS FAILED.")
    print("==================================================================")

    os._exit(0 if all_passed else 1)

if __name__ == '__main__':
    test_staff_login_verification()
