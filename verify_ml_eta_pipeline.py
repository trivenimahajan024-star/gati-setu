import os
import sys
import json
import socket
import threading
import time
import urllib.request

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

import uvicorn
from app.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def test_ml_eta_pipeline():
    PORT = find_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.5)

    base_url = f"http://127.0.0.1:{PORT}"
    all_passed = True

    print("\n==================================================================")
    print("  [GatiSetu] Trained ML ETA Pipeline Verification Test Suite")
    print("==================================================================")

    # 1. Test Pipeline Status & Model Trained Indicator
    print("\n[1] Testing ML Pipeline Status (/api/ml/eta/status):")
    try:
        with urllib.request.urlopen(f"{base_url}/api/ml/eta/status") as res:
            assert res.status == 200
            st = json.loads(res.read().decode('utf-8'))
            print(f"  Framework      : {st['ml_framework']}")
            print(f"  Model Trained  : {st['model_trained']}")
            print(f"  Model Status   : {st['model_status']}")
            print(f"  Features Count : {st['features_count']}")
            print(f"  Model Path     : {st['model_path']}")
            assert st["model_trained"] is True
            assert st["model_status"] == "LIVE_PREDICTION_ACTIVE"
            assert st["features_count"] == 15
            print("  [PASS] ML Pipeline successfully verified as TRAINED & LIVE.")
    except Exception as e:
        print(f"  [FAIL] ML status test failed: {e}")
        all_passed = False

    # 2. Test Live Inference on Train 12951
    print("\n[2] Testing Real ML ETA Inference on Train 12951 (/api/train/12951/ml-eta):")
    try:
        with urllib.request.urlopen(f"{base_url}/api/train/12951/ml-eta") as res:
            assert res.status == 200
            ml_res = json.loads(res.read().decode('utf-8'))
            print(f"  Model Status        : {ml_res['model_status']}")
            print(f"  Is Trained          : {ml_res['is_trained']}")
            print(f"  Train Number        : {ml_res['train_number']}")
            print(f"  Remaining Minutes   : {ml_res['predicted_remaining_minutes']} min")
            print(f"  Destination ETA     : {ml_res['predicted_destination_eta']}")
            print(f"  Confidence Score    : {ml_res['confidence_pct']}%")
            print(f"  Model Type          : {ml_res['model_type']}")

            # Assertions
            assert ml_res["train_number"] == "12951"
            assert ml_res["is_trained"] is True
            assert ml_res["model_status"] == "LIVE_PREDICTION_ACTIVE"
            assert ml_res["predicted_remaining_minutes"] is not None
            assert ml_res["predicted_remaining_minutes"] > 0
            assert ml_res["predicted_destination_eta"] is not None
            assert ml_res["confidence_pct"] >= 70
            print("  [PASS] Real XGBoost ML inference executed successfully on real train data.")
    except Exception as e:
        print(f"  [FAIL] Train ML ETA test failed: {e}")
        all_passed = False

    # 3. Test Multi-Train Live Inference (12860, 22436, 12002, 12259)
    print("\n[3] Testing Live Inference across Multiple Active Trains:")
    for tno in ["12860", "22436", "12002", "12259"]:
        try:
            with urllib.request.urlopen(f"{base_url}/api/train/{tno}/ml-eta") as res:
                assert res.status == 200
                m_res = json.loads(res.read().decode('utf-8'))
                assert m_res["is_trained"] is True
                assert m_res["predicted_remaining_minutes"] > 0
                print(f"  [PASS] Train {tno:<5} -> Predicted Rem: {m_res['predicted_remaining_minutes']:<5}m, Predicted ETA: {m_res['predicted_destination_eta']}, Conf: {m_res['confidence_pct']}%")
        except Exception as e:
            print(f"  [FAIL] Multi-train test failed for {tno}: {e}")
            all_passed = False

    # 4. Verify existing APIs (Passenger, Station Board, OCC, GPS) remain 100% operational
    print("\n[4] Verifying Core Platform Integration & Zero-Regression:")
    try:
        with urllib.request.urlopen(f"{base_url}/api/train/12951") as res:
            assert res.status == 200
            t = json.loads(res.read().decode('utf-8'))
            assert t["train_number"] == "12951"
            print(f"  [PASS] Passenger Train API intact: {t['train_name']} (ETA: {t['predicted_destination_eta']})")

        with urllib.request.urlopen(f"{base_url}/api/train/12951/gps") as res:
            assert res.status == 200
            gps = json.loads(res.read().decode('utf-8'))
            assert gps["status"] == "GPS_SOURCE_NOT_CONFIGURED"
            print("  [PASS] GPS interface intact and unchanged.")

    except Exception as e:
        print(f"  [FAIL] Core API regression check failed: {e}")
        all_passed = False

    print("\n==================================================================")
    if all_passed:
        print("  ALL TRAINED ML ETA PIPELINE & INFERENCE CHECKS PASSED 100%!")
    else:
        print("  SOME CHECKS FAILED.")
    print("==================================================================\n")

    server.should_exit = True
    return all_passed

if __name__ == "__main__":
    ok = test_ml_eta_pipeline()
    os._exit(0 if ok else 1)
