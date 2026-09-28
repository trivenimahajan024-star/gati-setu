import sys
import os
import json

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def test_api():
    print("Testing GatiSetu FastAPI Backend Initialization & Data Store...")
    try:
        from app.main import app
        from app.db.store import railway_store
        print(f"[PASS] FastAPI App loaded: {app.title} (v{app.version})")
        trains = railway_store.get_all_trains()
        print(f"[PASS] Train store loaded: {len(trains)} trains in database")
        assert len(trains) > 0, "Train database is empty"
    except Exception as e:
        print(f"[FAIL] Backend loading error: {e}")
        sys.exit(1)

    # Test key engine services
    try:
        from app.services.ml_eta_service import ml_eta_service
        from app.services.railradar import railradar_service
        print("[PASS] ML ETA Service and RailRadar Service loaded successfully")
    except Exception as e:
        print(f"[FAIL] Service loading error: {e}")
        sys.exit(1)

    # Test direct API route logic
    try:
        trains = railway_store.get_all_trains()
        assert len(trains) > 0, "get_all_trains returned empty"
        print(f"[PASS] get_all_trains() verified: {len(trains)} trains returned")
        
        # Test train details
        first_train_no = trains[0]["train_number"]
        details = railway_store.get_train(first_train_no)
        assert details is not None, f"Train {first_train_no} not found"
        print(f"[PASS] get_train('{first_train_no}') verified: {details.get('train_name')}")
        
        # Test station board
        stn_disp = railway_store.get_station_board("NDLS")
        assert stn_disp is not None, "Station board returned None"
        print(f"[PASS] get_station_board('NDLS') verified: {stn_disp.get('station_name')}")
    except Exception as e:
        print(f"[FAIL] Data store query error: {e}")
        sys.exit(1)

    print("\n--- ALL BACKEND CHECKS PASSED SUCCESSFULLY ---")

if __name__ == "__main__":
    test_api()
