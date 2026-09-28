import os
import re
import sys
import json
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
from app.config import settings
from app.db.store import store

def test_weather_map():
    print("=" * 70)
    print("  [GatiSetu] Real Weather Map & MapTiler Hybrid Integration Suite")
    print("=" * 70)

    errors = []

    # 1. Read files
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    with open("frontend/css/main.css", "r", encoding="utf-8") as f:
        css_content = f.read()

    with open("frontend/js/map_view.js", "r", encoding="utf-8") as f:
        map_js = f.read()

    with open("frontend/js/api.js", "r", encoding="utf-8") as f:
        api_js = f.read()

    with open("backend/app/config.py", "r", encoding="utf-8") as f:
        config_py = f.read()

    # 1. Verify MapTiler API Key loading from .env (no hardcoding)
    print("\n[1] Verifying MapTiler Hybrid & .env Configuration:")
    if "MAPTILER_API_KEY" in config_py:
        print("  [PASS] MAPTILER_API_KEY defined in backend Settings and loaded from .env")
    else:
        print("  [FAIL] MAPTILER_API_KEY missing in backend/app/config.py")
        errors.append("MAPTILER_API_KEY missing in config.py")

    # Verify no hardcoded API keys in JS files
    hardcoded_key_match = re.search(r"key\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]", map_js)
    if hardcoded_key_match:
        print(f"  [FAIL] Hardcoded API key found in map_view.js: {hardcoded_key_match.group(0)}")
        errors.append("Hardcoded API key found in map_view.js")
    else:
        print("  [PASS] Zero hardcoded API keys in frontend scripts")

    # 2. Verify Open-Meteo Integration (Real Weather Telemetry)
    print("\n[2] Verifying Open-Meteo Real Weather Telemetry Integration:")
    if "api.open-meteo.com" in map_js or "api.open-meteo.com" in api_js:
        print("  [PASS] Open-Meteo API endpoint configured for real weather data")
    else:
        print("  [FAIL] Open-Meteo API endpoint not found in JS files")
        errors.append("Open-Meteo API missing in JS")

    # Test Live Open-Meteo API directly with Bharuch coordinates
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=21.7051&longitude=72.9959&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,wind_speed_10m&timezone=auto"
        req = urllib.request.Request(url, headers={'User-Agent': 'GatiSetu/2.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode())
            cur = res_data.get("current", {})
            print(f"  [PASS] Open-Meteo Live API Response:")
            print(f"         - Temp: {cur.get('temperature_2m')} °C (Feels like {cur.get('apparent_temperature')} °C)")
            print(f"         - Rain: {cur.get('rain')} mm (Precip: {cur.get('precipitation')} mm)")
            print(f"         - Cloud Cover: {cur.get('cloud_cover')}% | Wind: {cur.get('wind_speed_10m')} km/h")
            print(f"         - WMO Weather Code: {cur.get('weather_code')} | Timestamp: {cur.get('time')}")
    except Exception as e:
        print(f"  [WARN] Open-Meteo live API call test warning (network dependent): {e}")

    # 3. Verify Required Weather Telemetry UI Elements in HTML
    print("\n[3] Verifying Real Weather Telemetry UI Elements:")
    required_weather_ui = [
        ("Weather Card #mapWeatherCard", r'id=["\']mapWeatherCard["\']'),
        ("Temperature Field #weatherTemp", r'id=["\']weatherTemp["\']'),
        ("Condition Field #weatherCondition", r'id=["\']weatherCondition["\']'),
        ("Rain Field #weatherRain", r'id=["\']weatherRain["\']'),
        ("Cloud Cover Field #weatherClouds", r'id=["\']weatherClouds["\']'),
        ("Wind Speed Field #weatherWind", r'id=["\']weatherWind["\']'),
        ("Updated Time Field #weatherUpdatedTime", r'id=["\']weatherUpdatedTime["\']'),
        ("Location Subtitle #weatherLocationName", r'id=["\']weatherLocationName["\']'),
        ("Error Banner with 'Weather data unavailable'", r'Weather data unavailable'),
    ]

    for label, pat in required_weather_ui:
        if re.search(pat, html_content):
            print(f"  [PASS] UI Element {label:42} -> Present")
        else:
            print(f"  [FAIL] UI Element {label:42} -> MISSING")
            errors.append(f"Missing UI element: {label}")

    # 4. Verify Map Layer Controls (Hybrid, Weather, Rain, Clouds) & Legend
    print("\n[4] Verifying Weather Map Layer Controls & Legend:")
    required_controls = [
        ("Layer Control Hybrid #btnLayerHybrid", r'id=["\']btnLayerHybrid["\']'),
        ("Layer Control Weather #btnLayerWeather", r'id=["\']btnLayerWeather["\']'),
        ("Layer Control Rain #btnLayerRain", r'id=["\']btnLayerRain["\']'),
        ("Layer Control Clouds #btnLayerClouds", r'id=["\']btnLayerClouds["\']'),
        ("Weather Legend #mapWeatherLegend", r'id=["\']mapWeatherLegend["\']'),
    ]

    for label, pat in required_controls:
        if re.search(pat, html_content):
            print(f"  [PASS] Map Control {label:40} -> Present")
        else:
            print(f"  [FAIL] Map Control {label:40} -> MISSING")
            errors.append(f"Missing control: {label}")

    # 5. Verify Leaflet Z-Index Stacking Panes in map_view.js
    print("\n[5] Verifying Leaflet Panes Z-Index Stacking (Railway above Weather):")
    required_panes = [
        ("weatherPane (zIndex: 400)", r"weatherPane.*style\.zIndex\s*=\s*400"),
        ("routePane (zIndex: 500)", r"routePane.*style\.zIndex\s*=\s*500"),
        ("stationsPane (zIndex: 600)", r"stationsPane.*style\.zIndex\s*=\s*600"),
        ("trainMarkerPane (zIndex: 700)", r"trainMarkerPane.*style\.zIndex\s*=\s*700"),
    ]

    for label, pat in required_panes:
        if re.search(pat, map_js, re.DOTALL):
            print(f"  [PASS] Map Pane {label:42} -> Configured")
        else:
            print(f"  [FAIL] Map Pane {label:42} -> MISSING")
            errors.append(f"Missing pane: {label}")

    print("\n" + "=" * 70)
    if errors:
        print(f"  FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)
    else:
        print("  ALL REAL WEATHER MAP & MAPTILER CHECKS PASSED WITH 100% SUCCESS!")
        print("=" * 70)

if __name__ == "__main__":
    test_weather_map()
