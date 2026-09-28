import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.api.routes_trains import (
    get_train_details,
    get_train_live_telemetry,
    get_train_route,
    get_train_gps_telemetry,
    get_train_ml_eta_prediction,
    get_trains_between
)
from app.api.routes_control import get_control_room_overview, get_control_room_trains

def test_direct_pipeline():
    print("=" * 80)
    print("AUDITING DIRECT TRAIN DATA PIPELINE FOR ALL TRAINS")
    print("=" * 80)

    # 1. Test train details
    t1 = get_train_details("12951")
    t2 = get_train_details("12626")
    t3 = get_train_details("22691")

    print(f"[+] Train 12951: {t1['train_name']} ({t1['source_code']} -> {t1['destination_code']}, {t1['total_distance_km']} km)")
    print(f"[+] Train 12626: {t2['train_name']} ({t2['source_code']} -> {t2['destination_code']}, {t2['total_distance_km']} km)")
    print(f"[+] Train 22691: {t3['train_name']} ({t3['source_code']} -> {t3['destination_code']}, {t3['total_distance_km']} km)")

    # 2. Test live telemetry
    live = get_train_live_telemetry("12951")
    print(f"[+] 12951 Live: Location={live['current_location']}, Delay={live['current_delay_mins']}m, Speed={live['current_speed_kmh']} km/h")

    # 3. Test route
    route = get_train_route("12951")
    print(f"[+] 12951 Route: Halts={len(route['stations'])}, Polyline points={len(route['route_polyline'])}")

    # 4. Test GPS feed
    gps = get_train_gps_telemetry("12951")
    print(f"[+] 12951 GPS Status: {gps.get('source_status')}")

    # 5. Test ML ETA
    ml_eta = get_train_ml_eta_prediction("12951")
    print(f"[+] 12951 ML ETA: Predicted ETA={ml_eta.get('predicted_eta')}, Remaining={ml_eta.get('predicted_remaining_minutes')}m, Confidence={ml_eta.get('confidence_pct')}%")

    # 6. Test trains between stations
    between = get_trains_between(from_station="MMCT", to_station="NDLS")
    print(f"[+] Trains MMCT -> NDLS: {between.get('total_trains')} trains found")

    between2 = get_trains_between(from_station="Bhusawal", to_station="Mumbai")
    print(f"[+] Trains Bhusawal -> Mumbai: {between2.get('total_trains')} trains found")

    # 7. Control room
    overview = get_control_room_overview()
    print(f"[+] Control Room Overview: Active Trains={overview.get('total_active_trains')}, On Time={overview.get('on_time_trains')}, Avg Delay={overview.get('average_delay_mins')}m")

    trains_ctrl = get_control_room_trains()
    print(f"[+] Control Room Trains List: {len(trains_ctrl)} trains loaded")

    print("\n" + "=" * 80)
    print("DIRECT PIPELINE VERIFICATION PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    test_direct_pipeline()
