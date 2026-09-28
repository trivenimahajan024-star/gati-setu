import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.services.railradar import railradar_service
from app.db.store import store

def test_station_deduplication():
    print("=" * 80)
    print("RUNNING COMPREHENSIVE STATION BOARD & ROUTE DEDUPLICATION AUDIT")
    print("=" * 80)

    # 1. Audit Schedule Database Routes
    railradar_service._ensure_schedule_db_loaded()
    dupes_in_db = 0
    total_routes = len(railradar_service._schedule_routes)
    for tno, route in railradar_service._schedule_routes.items():
        seen = set()
        for stop in route:
            sc = stop["station_code"]
            if sc in seen:
                dupes_in_db += 1
                break
            seen.add(sc)

    print(f"[+] Audited {total_routes} database routes: {dupes_in_db} duplicates found (Expected: 0)")
    assert dupes_in_db == 0, f"Found {dupes_in_db} routes with duplicate station codes in database!"

    # 2. Audit get_train_data stations array
    test_trains = [
        '12951', '12952', '12301', '12860', '12002', 
        '12154', '12626', '22691', '12431', '15068', '22436'
    ]

    for tno in test_trains:
        t = railradar_service.get_train_data(tno)
        stations = t.get("stations", [])
        seen_codes = set()
        for idx, stn in enumerate(stations):
            sc = stn.get("code")
            assert sc, f"Empty station code in train {tno} at index {idx}"
            assert sc not in seen_codes, f"Duplicate station code {sc} found in Train {tno}!"
            seen_codes.add(sc)
        print(f"[OK] Train {tno} ({t.get('train_name')}): {len(stations)} unique stations strictly preserved.")

    # 3. Audit Station Board for all major junctions
    major_stations = ["NDLS", "MMCT", "CSMT", "BRC", "HWH", "BSB", "RKMP", "KOTA", "RTM", "NK", "BSL"]
    for stn_code in major_stations:
        board = store.get_station_board(stn_code)
        arr_trains = [a["train_number"] for a in board["arrivals"]]
        dep_trains = [d["train_number"] for d in board["departures"]]
        
        assert len(arr_trains) == len(set(arr_trains)), f"Duplicate arrivals found in station {stn_code}: {arr_trains}"
        assert len(dep_trains) == len(set(dep_trains)), f"Duplicate departures found in station {stn_code}: {dep_trains}"
        print(f"[OK] Station {stn_code} Board: {len(arr_trains)} arrivals, {len(dep_trains)} departures (0 duplicates).")

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED: Zero duplicate stations across API, DB, and Station Board!")
    print("=" * 80)

if __name__ == "__main__":
    test_station_deduplication()
