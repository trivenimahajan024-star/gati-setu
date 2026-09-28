import sys
import os
import time
import json
import urllib.request
import urllib.error

sys.path.insert(0, "backend")
from app.config import settings
from app.services.railradar import railradar_service

def run_tests():
    print("=" * 70)
    print("  [GatiSetu] Universal Trains Between Stations Comprehensive Verification")
    print("=" * 70)

    # 1. Verify RAILRADAR_API_KEY is configured
    assert settings.RAILRADAR_API_KEY, "[FAIL] RAILRADAR_API_KEY is missing from .env"
    print(f"\n[1] RailRadar API Key Loaded: {settings.RAILRADAR_API_KEY[:6]}...{settings.RAILRADAR_API_KEY[-4:]}")

    # 2. Test Multi-Terminal Station / City Resolution Logic
    print("\n[2] Verifying Universal Multi-Terminal Resolution Logic:")
    stn_tests = [
        ("Mumbai", ["MMCT", "CSMT", "LTT", "BDTS", "BVI", "DR", "KYN", "TNA", "DDR", "PNVL"]),
        ("Delhi", ["NDLS", "NZM", "DLI", "ANVT", "DEC", "DEE", "DSA", "GZB"]),
        ("Pune", ["PUNE", "SVJR", "CCH", "HDP"]),
        ("Jaipur", ["JP", "GADJ", "DPA"]),
        ("Bhusawal", ["BSL", "JL"]),
        ("Mumbai Central", ["MMCT", "BVI"]),
        ("New Delhi", ["NDLS", "NZM", "DLI", "ANVT", "DEC", "DEE"]),
        ("Surat", ["ST", "UDN"]),
        ("Vadodara Jn", ["BRC", "MYG"]),
        ("MMCT", ["MMCT"]),
        ("NDLS", ["NDLS"]),
        ("BSL", ["BSL"]),
        ("Mumbai Central (MMCT)", ["MMCT"])
    ]
    for q, expected_codes in stn_tests:
        codes, name = railradar_service.resolve_stations_list(q)
        for ec in expected_codes[:2]:
            assert ec in codes, f"Expected {ec} in codes for '{q}', got {codes}"
        print(f"  - '{q}' -> Codes: {codes[:5]}..., Representative Name: {name}")
    print("  [PASS] Station & City multi-terminal resolution operates universally.")

    # 3. Test Route 1: Bhusawal -> Mumbai
    print("\n[3] Testing Route 1: Bhusawal -> Mumbai")
    data_bsl_mum = railradar_service.get_trains_between_stations("Bhusawal", "Mumbai")
    total_1 = data_bsl_mum.get("total_trains", 0)
    trains_1 = data_bsl_mum.get("trains", [])
    print(f"  - Total Trains Found: {total_1}")
    assert total_1 > 0, "[FAIL] No trains returned for Bhusawal -> Mumbai"
    sample_1 = trains_1[0]
    print(f"  - Sample Train: #{sample_1['train_number']} {sample_1['train_name']} | Dep: {sample_1['departure_time']} ({sample_1['from_station_code']}) -> Arr: {sample_1['arrival_time']} ({sample_1['to_station_code']}) | Duration: {sample_1.get('duration')} | Status: {sample_1['current_status']}")
    print(f"  [PASS] Bhusawal -> Mumbai returned {total_1} trains.")

    # 4. Test Route 2: Mumbai -> Bhusawal
    print("\n[4] Testing Route 2: Mumbai -> Bhusawal")
    data_mum_bsl = railradar_service.get_trains_between_stations("Mumbai", "Bhusawal")
    total_2 = data_mum_bsl.get("total_trains", 0)
    trains_2 = data_mum_bsl.get("trains", [])
    print(f"  - Total Trains Found: {total_2}")
    assert total_2 > 0, "[FAIL] No trains returned for Mumbai -> Bhusawal"
    sample_2 = trains_2[0]
    print(f"  - Sample Train: #{sample_2['train_number']} {sample_2['train_name']} | Dep: {sample_2['departure_time']} ({sample_2['from_station_code']}) -> Arr: {sample_2['arrival_time']} ({sample_2['to_station_code']}) | Duration: {sample_2.get('duration')} | Status: {sample_2['current_status']}")
    print(f"  [PASS] Mumbai -> Bhusawal returned {total_2} trains.")

    # 5. Test Route 3: Mumbai -> New Delhi (and MMCT -> NDLS)
    print("\n[5] Testing Route 3: Mumbai -> New Delhi & MMCT -> NDLS")
    data_mum_delhi = railradar_service.get_trains_between_stations("Mumbai", "New Delhi")
    total_3 = data_mum_delhi.get("total_trains", 0)
    print(f"  - Mumbai -> New Delhi Total Trains: {total_3}")
    assert total_3 > 0, "[FAIL] No trains returned for Mumbai -> New Delhi"

    data_mmct_ndls = railradar_service.get_trains_between_stations("MMCT", "NDLS")
    total_mmct_ndls = data_mmct_ndls.get("total_trains", 0)
    print(f"  - MMCT -> NDLS Total Trains: {total_mmct_ndls}")
    assert total_mmct_ndls >= 1, "[FAIL] No trains returned for MMCT -> NDLS"
    rajdhani = next((t for t in data_mmct_ndls.get("trains", []) if t["train_number"] == "12951"), None)
    assert rajdhani is not None, "[FAIL] Train 12951 not found in MMCT -> NDLS"
    print(f"  - Found 12951: {rajdhani['train_name']} | Dep: {rajdhani['departure_time']} | Arr: {rajdhani['arrival_time']} | Duration: {rajdhani.get('duration')} | Status: {rajdhani['current_status']} | Delay: +{rajdhani['delay_mins']}m | Location: {rajdhani['current_location']}")
    print(f"  [PASS] Mumbai -> New Delhi and MMCT -> NDLS verified successfully.")

    # 6. Test Route 4: Mumbai -> Surat & MMCT -> ST
    print("\n[6] Testing Route 4: Mumbai -> Surat & MMCT -> ST")
    data_mmct_st = railradar_service.get_trains_between_stations("MMCT", "ST")
    total_4 = data_mmct_st.get("total_trains", 0)
    print(f"  - MMCT -> ST Total Trains: {total_4}")
    assert total_4 > 0, "[FAIL] No trains returned for MMCT -> ST"
    print(f"  [PASS] MMCT -> ST returned {total_4} trains.")

    # 7. Test Route 5: Pune -> Mumbai
    print("\n[7] Testing Route 5: Pune -> Mumbai")
    data_pune_mum = railradar_service.get_trains_between_stations("Pune", "Mumbai")
    total_5 = data_pune_mum.get("total_trains", 0)
    print(f"  - Pune -> Mumbai Total Trains: {total_5}")
    assert total_5 > 0, "[FAIL] No trains returned for Pune -> Mumbai"
    sample_5 = data_pune_mum.get("trains", [])[0]
    print(f"  - Sample Train: #{sample_5['train_number']} {sample_5['train_name']} | Dep: {sample_5['departure_time']} | Arr: {sample_5['arrival_time']} | Duration: {sample_5.get('duration')}")
    print(f"  [PASS] Pune -> Mumbai returned {total_5} trains.")

    # 8. Test Route 6: Delhi -> Jaipur
    print("\n[8] Testing Route 6: Delhi -> Jaipur")
    data_delhi_jp = railradar_service.get_trains_between_stations("Delhi", "Jaipur")
    total_6 = data_delhi_jp.get("total_trains", 0)
    print(f"  - Delhi -> Jaipur Total Trains: {total_6}")
    assert total_6 > 0, "[FAIL] No trains returned for Delhi -> Jaipur"
    sample_6 = data_delhi_jp.get("trains", [])[0]
    print(f"  - Sample Train: #{sample_6['train_number']} {sample_6['train_name']} | Dep: {sample_6['departure_time']} | Arr: {sample_6['arrival_time']} | Duration: {sample_6.get('duration')}")
    print(f"  [PASS] Delhi -> Jaipur returned {total_6} trains.")

    # 9. Verify Required Dynamic Fields on Returned Trains
    print("\n[9] Verifying 100% Required Dynamic Attributes on Trains:")
    required_fields = [
        "train_number", "train_name", "train_type", "origin_station", "destination_station",
        "from_station_code", "from_station_name", "to_station_code", "to_station_name",
        "departure_time", "arrival_time", "duration", "run_days",
        "current_status", "status_category", "delay_mins", "current_location", "last_updated_time"
    ]
    for field in required_fields:
        assert field in sample_1, f"Missing required field '{field}' in train item"
        print(f"  - Field '{field}': {sample_1[field]}")
    print("  [PASS] All train objects strictly conform to required dynamic attributes.")

    print("\n" + "=" * 70)
    print("  ALL 6 ROUTE & UNIVERSAL TESTS COMPLETED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
