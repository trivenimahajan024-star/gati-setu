import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.railradar import railradar_service
from app.db.store import store

def test_12951_consistency():
    print("=" * 60)
    print("TESTING TRAIN 12951 SINGLE SOURCE OF TRUTH CONSISTENCY")
    print("=" * 60)

    train = railradar_service.get_train_data("12951")
    assert train is not None, "Train 12951 not found"

    print(f"1. Train Info:")
    print(f"   - Number: {train.get('train_number')}")
    print(f"   - Name: {train.get('train_name')}")
    print(f"   - Source: {train.get('source')} ({train.get('source_code')})")
    print(f"   - Destination: {train.get('destination')} ({train.get('destination_code')})")
    assert train.get("train_number") == "12951", "Train number mismatch"

    print(f"\n2. Location & Coordinates (Map & Telemetry Single Source):")
    print(f"   - Current Location: {train.get('current_location')}")
    print(f"   - Coordinates: {train.get('current_coordinates')}")
    print(f"   - Speed: {train.get('current_speed_kmh')} km/h")
    print(f"   - Status: {train.get('current_status')}")
    print(f"   - Delay: +{train.get('current_delay_mins')} min")
    
    assert train.get("current_coordinates") == [21.7051, 72.9959], f"Unexpected coordinates: {train.get('current_coordinates')}"
    assert "Bharuch" in train.get("current_location", ""), f"Location should reference Bharuch"

    print(f"\n3. Destination ETA (Hero Card, Timeline & Route Timetable Single Source):")
    print(f"   - Scheduled ETA: {train.get('scheduled_destination_eta')}")
    print(f"   - Predicted ETA: {train.get('predicted_destination_eta')}")
    print(f"   - Arrival Window: {train.get('arrival_window')}")
    print(f"   - Confidence: {train.get('confidence_level')} ({train.get('confidence_pct')}%)")
    assert train.get("predicted_destination_eta") == "08:46 AM", f"Unexpected predicted ETA: {train.get('predicted_destination_eta')}"
    assert train.get("scheduled_destination_eta") == "08:32 AM", f"Unexpected scheduled ETA: {train.get('scheduled_destination_eta')}"

    print(f"\n4. Next Station & Intermediate Stops (Progress & Timeline):")
    next_stn = train.get("next_station", {})
    print(f"   - Next Station: {next_stn.get('name')} ({next_stn.get('code')})")
    print(f"   - Expected ETA: {next_stn.get('expected_eta')}")
    print(f"   - Scheduled ETA: {next_stn.get('scheduled_eta')}")
    print(f"   - Platform: PF {next_stn.get('platform')}")
    assert next_stn.get("code") == "BRC", f"Next station code should be BRC, got {next_stn.get('code')}"
    assert next_stn.get("expected_eta") == "09:41 PM", f"Next station ETA mismatch: {next_stn.get('expected_eta')}"

    print(f"\n5. Stations Timetable:")
    stations = train.get("stations", [])
    assert len(stations) == 7, f"Expected 7 stations, got {len(stations)}"
    for idx, s in enumerate(stations):
        print(f"   [{idx+1}] {s['code']:4s} | {s['name']:15s} | Sched: {s['scheduled_arr']:8s} / {s['scheduled_dep']:8s} | Pred: {s['predicted_arr']:8s} / {s['predicted_dep']:8s} | Delay: +{s['delay_mins']}m | Status: {s['status']}")

    print(f"\n6. Journey Progress:")
    print(f"   - Progress %: {train.get('journey_progress_pct')}%")
    print(f"   - Distance Covered: {train.get('distance_covered_km')} km")
    print(f"   - Distance Remaining: {train.get('distance_remaining_km')} km")
    print(f"   - Total Distance: {train.get('total_distance_km')} km")
    assert train.get("total_distance_km") == 1386.0 or train.get("total_distance_km") == 1386, "Total distance mismatch"

    print("\n" + "=" * 60)
    print("ALL DATA CONSISTENCY ASSERTIONS PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_12951_consistency()
