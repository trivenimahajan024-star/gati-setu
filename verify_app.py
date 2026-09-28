import os
import sys
import time
import threading
import urllib.request
import socketserver
import http.server

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server(httpd):
    httpd.serve_forever()

def test_client():
    time.sleep(1.5)
    urls = [
        ('http://127.0.0.1:8000/', 'Passenger Home (index.html)'),
        ('http://127.0.0.1:8000/css/main.css', 'Railway Theme CSS (main.css)'),
        ('http://127.0.0.1:8000/js/passenger_app.js', 'Passenger Controller (passenger_app.js)'),
        ('http://127.0.0.1:8000/js/data_service.js', 'Passenger Data Service (data_service.js)'),
        ('http://127.0.0.1:8000/js/map_view.js', 'Interactive Leaflet Map (map_view.js)')
    ]
    
    all_ok = True
    print("\n--- Verifying GatiSetu Passenger Interface Assets ---")
    for url, name in urls:
        try:
            with urllib.request.urlopen(url) as res:
                content = res.read()
                print(f"[PASS] {name:<42} | Status: {res.status} | Size: {len(content):>6} bytes")
        except Exception as e:
            print(f"[FAIL] {name:<42} | Error: {e}")
            all_ok = False
            
    # Verify key code symbols and UI elements
    index_path = os.path.join(DIRECTORY, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
        assert "GatiSetu" in html, "GatiSetu branding missing"
        assert "screen-home" in html, "Passenger home screen missing"
        assert "screen-details" in html, "Train details screen missing"
        assert "screen-map" in html, "Live map screen missing"
        assert "screen-route" in html, "Route timeline screen missing"
        assert "screen-alerts" in html, "Alerts screen missing"
        assert "12951" in html, "Default demo train 12951 missing"
        assert "Station Board" not in html, "Station board should not be in passenger interface"
        assert "Control Room" not in html, "Control room should not be in passenger interface"
        assert "Staff Login" not in html, "Staff login should not be in passenger interface"
        print("[PASS] HTML structure and requirements fully validated")

    data_path = os.path.join(DIRECTORY, "js", "data_service.js")
    with open(data_path, "r", encoding="utf-8") as f:
        data_code = f.read()
        assert "12951" in data_code, "Train 12951 demo data missing"
        assert "12860" in data_code, "Train 12860 demo data missing"
        assert "22436" in data_code, "Train 22436 demo data missing"
        assert "dynamic_predicted_eta" in data_code or "predicted_arr" in data_code
        print("[PASS] Passenger Data Service and train timetables validated")

    if all_ok:
        print("\n==================================================")
        print("  ALL GATISETU PASSENGER TESTS PASSED SUCCESSFULLY! ")
        print("==================================================")
    else:
        print("\nVerification encountered errors.")
        
    os._exit(0 if all_ok else 1)

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        t = threading.Thread(target=test_client, daemon=True)
        t.start()
        run_server(httpd)
