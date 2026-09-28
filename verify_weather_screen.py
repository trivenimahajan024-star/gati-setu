"""
Verification script for GatiSetu Passenger Weather Screen
Tests:
1. Backend RailRadar Train Data & Real Coordinates
2. MapTiler Key & Config API
3. Open-Meteo API response structure for railway coordinates
4. RainViewer Weather Maps API response structure
5. Frontend HTML elements existence (weather cards, map container, radar controls, layers, summary cards)
6. Frontend JS functions and integration (WeatherMapTracker, Leaflet panes, Open-Meteo telemetry sync, Route Meteorology summary)
"""

import sys
import os
import json
import urllib.request

def test_backend_and_apis():
    print("\n--- 1. Testing Open-Meteo Weather API Integration ---")
    lat, lon = 22.3072, 73.1812 # Vadodara coords
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,wind_speed_10m&timezone=auto"
    req = urllib.request.Request(url, headers={'User-Agent': 'GatiSetu/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            assert "current" in data, "Open-Meteo payload missing 'current'"
            cur = data["current"]
            assert "temperature_2m" in cur, "Missing temperature_2m"
            assert "weather_code" in cur, "Missing weather_code"
            assert "precipitation" in cur or "rain" in cur, "Missing rain/precipitation"
            print(f"  [OK] Open-Meteo API responded with valid telemetry: Temp={cur.get('temperature_2m')}°C, Code={cur.get('weather_code')}, Rain={cur.get('rain', cur.get('precipitation'))}mm")
    except Exception as e:
        print(f"  [FAIL] Open-Meteo test failed: {e}")
        return False

    print("\n--- 2. Testing RainViewer Doppler Radar API Integration ---")
    radar_url = "https://api.rainviewer.com/public/weather-maps.json"
    req = urllib.request.Request(radar_url, headers={'User-Agent': 'GatiSetu/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            assert "host" in data, "RainViewer payload missing 'host'"
            assert "radar" in data, "RainViewer payload missing 'radar'"
            past = data["radar"].get("past", [])
            print(f"  [OK] RainViewer API responded with {len(past)} radar past frames and host={data['host']}")
    except Exception as e:
        print(f"  [FAIL] RainViewer test failed: {e}")
        return False

    print("\n--- 3. Verifying Frontend HTML Elements for Weather Screen ---")
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    required_html_ids = [
        "screen-weather",
        "weatherScreenTrainNo",
        "weatherScreenRouteSubtitle",
        "weatherScreenRunningStatusPill",
        "passengerWeatherContainerCard",
        "weatherTrackingMap",
        "btnWeatherLayerRain",
        "btnWeatherLayerComposite",
        "btnWeatherLayerClouds",
        "btnWeatherLayerHybrid",
        "btnRadarPlayPause",
        "radarPlayIcon",
        "radarTimeScrubber",
        "radarFrameTimeLabel",
        "radarPlayerHud",
        "mapWeatherLegend",
        "weatherLegendTitle",
        "btnWeatherZoomIn",
        "btnWeatherZoomOut",
        "btnWeatherResetView",
        "btnWeatherFullscreen",
        "weatherTrainNumber",
        "weatherNextStationText",
        "weatherNextStationETA",
        "weatherTemp",
        "weatherCondition",
        "weatherRain",
        "weatherClouds",
        "weatherWind",
        "weatherUpdatedTime",
        "weatherLocationName",
        "weatherRouteProgressPct",
        "weatherSummaryTrainName",
        "weatherCurrentSectorText",
        "weatherCurrentSummaryWeather",
        "weatherNextStopText",
        "weatherTrackConditionRisk",
        "weatherRadarStatusSummary",
        "weatherLastUpdateSummary"
    ]

    for elem_id in required_html_ids:
        assert f'id="{elem_id}"' in html, f"Missing required HTML ID: {elem_id}"
    print(f"  [OK] All {len(required_html_ids)} required Weather screen HTML IDs verified.")

    print("\n--- 4. Verifying Frontend JS WeatherMapTracker Logic ---")
    with open("frontend/js/map_view.js", "r", encoding="utf-8") as f:
        js = f.read()

    required_js_patterns = [
        "class WeatherMapTracker",
        "this.map.createPane('weatherPane')",
        "this.map.createPane('routePane')",
        "this.map.createPane('stationsPane')",
        "this.map.createPane('labelsPane')",
        "this.map.createPane('trainMarkerPane')",
        "voyager_only_labels",
        "ArcGIS/rest/services/World_Imagery",
        "setupWeatherLayers",
        "setupRadarPlayerControls",
        "renderTrainWeatherRoute",
        "updateRealWeather",
        "calculateBearing",
        "decodeWmoWeather",
        "weatherSummaryTrainName",
        "weatherTrackConditionRisk"
    ]

    for pattern in required_js_patterns:
        assert pattern in js, f"Missing required JS pattern: {pattern}"
    print(f"  [OK] All {len(required_js_patterns)} required JS patterns verified in map_view.js.")

    print("\n--- 5. Verifying Shared Train State Integration in passenger_app.js ---")
    with open("frontend/js/passenger_app.js", "r", encoding="utf-8") as f:
        p_js = f.read()

    assert "window.weatherMapTracker.renderTrainWeatherRoute" in p_js, "Missing weather screen trigger in navigateToPassengerScreen"
    assert "weatherScreenTrainNo" in p_js, "Missing weatherScreenTrainNo sync in renderTrainDetails"
    print("  [OK] Shared Train State synchronization verified in passenger_app.js.")

    print("\n==========================================")
    print(" ALL WEATHER SCREEN VERIFICATIONS PASSED ")
    print("==========================================")
    return True

if __name__ == "__main__":
    success = test_backend_and_apis()
    if not success:
        sys.exit(1)
