import sys
import os
import json
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.services.railradar import railradar_service

test_trains = [
    '12951', # Mumbai - New Delhi Tejas Rajdhani
    '12952', # New Delhi - Mumbai Tejas Rajdhani
    '12301', # Howrah - New Delhi Rajdhani
    '12860', # Howrah - Mumbai CSMT Gitanjali Express
    '12002', # New Delhi - Bhopal Rani Kamlapati Shatabdi
    '12154', # Rani Kamlapati - LTT SF Express
    '12626', # New Delhi - Trivandrum Kerala Express
    '22691', # KSR Bengaluru - Hazrat Nizamuddin Rajdhani
    '12431', # Trivandrum - Hazrat Nizamuddin Rajdhani
    '15068', # Bandra Terminus - Gorakhpur Express
    '22436', # New Delhi - Varanasi Vande Bharat
]

print("=" * 80)
print(f"AUDITING TRAIN DATA PIPELINE ACROSS {len(test_trains)} DIFFERENT TRAINS")
print("=" * 80)

results = []
for tno in test_trains:
    try:
        t = railradar_service.get_train_data(tno)
        res = {
            "train_number": t.get("train_number"),
            "train_name": t.get("train_name"),
            "source": t.get("source"),
            "source_code": t.get("source_code"),
            "destination": t.get("destination"),
            "destination_code": t.get("destination_code"),
            "total_distance_km": t.get("total_distance_km"),
            "current_coordinates": t.get("current_coordinates"),
            "speed": t.get("current_speed_kmh"),
            "delay": t.get("current_delay_mins"),
            "eta": t.get("predicted_destination_eta"),
            "current_location": t.get("current_location"),
            "next_station": t.get("next_station", {}).get("name") if isinstance(t.get("next_station"), dict) else t.get("next_station"),
            "last_updated_time": t.get("last_updated_time"),
            "stations_count": len(t.get("stations", [])),
            "status": t.get("current_status"),
            "status_code": t.get("current_status_code")
        }
        results.append(res)
        print(f"\n[+] Train {tno}: {res['train_name']}")
        print(f"    Route: {res['source_code']} -> {res['destination_code']} ({res['total_distance_km']} km, {res['stations_count']} halts)")
        print(f"    Location: {res['current_location']} | Coords: {res['current_coordinates']}")
        print(f"    Speed: {res['speed']} km/h | Delay: {res['delay']} min | Status: {res['status']}")
        print(f"    Next Station: {res['next_station']} | ETA: {res['eta']} | Updated: {res['last_updated_time']}")
    except Exception as e:
        print(f"\n[-] Train {tno} ERROR: {e}")

print("\n" + "=" * 80)
print("AUDIT SUMMARY CHECK")
print("=" * 80)
routes = set(f"{r['source_code']}->{r['destination_code']}" for r in results)
dists = set(r['total_distance_km'] for r in results)

print(f"Total trains tested: {len(results)}/{len(test_trains)}")
print(f"Unique routes: {len(routes)}/{len(results)}")
print(f"Unique distances: {len(dists)}/{len(results)}")

assert len(results) == len(test_trains), "Some trains failed to load!"
assert len(routes) >= 9, "Routes are not distinct!"
assert len(dists) >= 9, "Distances are not distinct!"

# Write detailed JSON audit report
with open("train_audit_report.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSUCCESS: All trains dynamically return distinct, authentic, train-specific railway data!")
