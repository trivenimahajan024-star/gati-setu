import urllib.request
import json
import re

def test_rainviewer_radar():
    print("Testing RainViewer Real-Time Radar API...")
    url = 'https://api.rainviewer.com/public/weather-maps.json'
    req = urllib.request.Request(url, headers={'User-Agent': 'GatiSetu-Railway-Weather/1.0'})
    res = urllib.request.urlopen(req, timeout=10)
    data = json.loads(res.read().decode())
    
    assert 'radar' in data, "RainViewer response missing radar data"
    assert 'past' in data['radar'], "RainViewer missing radar past frames"
    past_frames = data['radar']['past']
    assert len(past_frames) > 0, "No radar past frames returned"
    
    latest_frame = past_frames[-1]
    assert 'time' in latest_frame and 'path' in latest_frame, "Frame missing time or path"
    print(f"  [OK] RainViewer active with {len(past_frames)} real radar frames.")
    print(f"  [OK] Latest frame time: {latest_frame['time']}, path: {latest_frame['path']}")

def test_open_meteo():
    print("Testing Open-Meteo Real Weather Telemetry...")
    lat, lon = 21.7051, 72.9959 # Bharuch Jn
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,wind_speed_10m&timezone=auto"
    req = urllib.request.Request(url, headers={'User-Agent': 'GatiSetu-Weather/1.0'})
    res = urllib.request.urlopen(req, timeout=10)
    data = json.loads(res.read().decode())
    
    assert 'current' in data, "Open-Meteo missing current data"
    cur = data['current']
    print(f"  [OK] Open-Meteo live: Temp={cur.get('temperature_2m')}°C, Rain={cur.get('precipitation')}mm, Clouds={cur.get('cloud_cover')}%, Wind={cur.get('wind_speed_10m')}km/h, WMO Code={cur.get('weather_code')}")

def test_weather_map_and_train_sync():
    print("Testing Weather Map and Train Route Synchronization...")
    
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Verify separate screens
    assert 'id="screen-map"' in html, "Missing screen-map"
    assert 'id="screen-weather"' in html, "Missing screen-weather"
    assert 'id="liveTrackingMap"' in html, "Missing liveTrackingMap canvas"
    assert 'id="weatherTrackingMap"' in html, "Missing weatherTrackingMap canvas"
    
    # 2. Verify Weather Map HTML structure
    weather_match = re.search(r'<section id="screen-weather".*?</section>', html, re.DOTALL)
    assert weather_match, "screen-weather section not found"
    weather_html = weather_match.group(0)
    
    assert 'id="weatherScreenTrainNo"' in weather_html, "Missing weatherScreenTrainNo"
    assert 'id="weatherScreenRouteSubtitle"' in weather_html, "Missing weatherScreenRouteSubtitle"
    assert 'id="weatherTrainNumber"' in weather_html, "Missing weatherTrainNumber"
    assert 'id="weatherNextStationText"' in weather_html, "Missing weatherNextStationText"
    assert 'id="radarPlayerHud"' in weather_html, "Missing radarPlayerHud"
    assert 'id="mapWeatherLegend"' in weather_html, "Missing mapWeatherLegend"
    print("  [OK] screen-weather contains all dynamic train and radar controls.")

    # 3. Verify map_view.js WeatherMapTracker implementation
    with open('frontend/js/map_view.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    assert 'class WeatherMapTracker' in js, "Missing WeatherMapTracker class"
    assert 'renderTrainWeatherRoute' in js, "Missing renderTrainWeatherRoute in WeatherMapTracker"
    assert 'getRoutePolyline' in js, "Missing dynamic getRoutePolyline"
    assert 'weatherPane' in js, "Missing weatherPane"
    assert 'routePane' in js, "Missing routePane"
    assert 'stationsPane' in js, "Missing stationsPane"
    assert 'trainMarkerPane' in js, "Missing trainMarkerPane"
    
    # Verify Pane z-index hierarchy: weatherPane(400) < routePane(500) < stationsPane(600) < trainMarkerPane(700)
    assert "getPane('weatherPane').style.zIndex = 400" in js, "weatherPane zIndex should be 400"
    assert "getPane('routePane').style.zIndex = 500" in js, "routePane zIndex should be 500"
    assert "getPane('stationsPane').style.zIndex = 600" in js, "stationsPane zIndex should be 600"
    assert "getPane('trainMarkerPane').style.zIndex = 700" in js, "trainMarkerPane zIndex should be 700"
    print("  [OK] WeatherMapTracker strictly keeps railway tracks & train marker ABOVE weather layer.")

    # 4. Verify passenger_app.js shared state and navigation
    with open('frontend/js/passenger_app.js', 'r', encoding='utf-8') as f:
        p_js = f.read()
    
    assert 'window.selectedTrain = train' in p_js or 'window.selectedTrain = fallback' in p_js, "passenger_app.js missing global selectedTrain assignment"
    assert 'weatherMapTracker.renderTrainWeatherRoute' in p_js, "passenger_app.js missing renderTrainWeatherRoute call on screen switch"
    assert 'weatherScreenTrainNo' in p_js, "passenger_app.js missing weatherScreenTrainNo text update"
    print("  [OK] passenger_app.js stores global selected train and synchronizes Weather Map.")

if __name__ == '__main__':
    print("=== GATISETU WEATHER MAP & TRAIN SYNC VERIFICATION ===")
    test_rainviewer_radar()
    test_open_meteo()
    test_weather_map_and_train_sync()
    print("=== ALL VERIFICATION CHECKS PASSED PERFECTLY ===")
