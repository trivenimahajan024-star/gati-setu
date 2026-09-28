from fastapi import APIRouter, HTTPException, Body
from app.db.store import store
from app.services.railradar import railradar_service
from app.services.gps_service import gps_service
from app.services.ml_eta_service import ml_eta_service

router = APIRouter()

@router.get("/trains")
def get_all_trains():
    return store.get_all_trains()

@router.get("/trains/between")
@router.get("/trains/between-stations")
def get_trains_between(from_station: str = "", to_station: str = "", fromStation: str = "", toStation: str = ""):
    src = from_station or fromStation
    dest = to_station or toStation
    if not src or not dest:
        raise HTTPException(status_code=400, detail="Missing required query parameters 'from_station' and 'to_station'.")
    return railradar_service.get_trains_between_stations(src, dest)

@router.get("/trains/search")
@router.get("/train/search")
@router.get("/trains/suggest")
@router.get("/train/suggest")
def search_trains(query: str = "", q: str = "", limit: int = 10):
    search_q = (query or q or "").strip()
    if not search_q:
        return []
    return railradar_service.search_trains(search_q, limit=limit)


@router.get("/train/{train_number}")
@router.get("/trains/{train_number}")
def get_train_details(train_number: str):
    train = railradar_service.get_train_data(train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train {train_number} not found on Indian Railways network")
    store.update_train(train)
    return train

@router.get("/train/{train_number}/route")
@router.get("/trains/{train_number}/route")
def get_train_route(train_number: str):
    train = railradar_service.get_train_data(train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train {train_number} not found")
    store.update_train(train)
    return {
        "train_number": train["train_number"],
        "route_polyline": train.get("route_polyline", []),
        "stations": train.get("stations", [])
    }

@router.get("/train/{train_number}/live")
@router.get("/trains/{train_number}/live")
def get_train_live_telemetry(train_number: str):
    train = railradar_service.get_train_data(train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train {train_number} not found")
    store.update_train(train)
    return {
        "train_number": train["train_number"],
        "current_coordinates": train["current_coordinates"],
        "current_speed_kmh": train["current_speed_kmh"],
        "current_delay_mins": train["current_delay_mins"],
        "current_location": train["current_location"],
        "heading_deg": train.get("heading_deg", 0),
        "predicted_destination_eta": train["predicted_destination_eta"],
        "arrival_window": train["arrival_window"],
        "confidence_level": train["confidence_level"],
        "last_updated_time": train.get("last_updated_time", "Live")
    }

@router.get("/train/{train_number}/gps")
@router.get("/trains/{train_number}/gps")
def get_train_gps_telemetry(train_number: str):
    """
    Dedicated GPS / RTIS / NavIC receiver feed endpoint.
    Returns 'GPS_SOURCE_NOT_CONFIGURED' when no live satellite/hardware provider is connected.
    """
    return gps_service.get_gps_position(train_number)

@router.get("/gps/status")
def get_gps_feed_status():
    """
    Returns the operational configuration status of the railway GPS / RTIS subsystem.
    """
    return gps_service.get_service_status()

@router.post("/gps/telemetry/ingest")
def ingest_gps_telemetry_packet(payload: dict = Body(...)):
    """
    Ingest interface endpoint for receiving live RTIS / NavIC / GPS IoT packets.
    """
    return gps_service.ingest_gps_telemetry(payload)

@router.get("/train/{train_number}/ml-eta")
@router.get("/trains/{train_number}/ml-eta")
def get_train_ml_eta_prediction(train_number: str):
    """
    Dedicated XGBoost ML ETA pipeline endpoint.
    Extracts real features and runs XGBoost inference when a trained model is available.
    """
    train = railradar_service.get_train_data(train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train {train_number} not found")
    return ml_eta_service.predict_remaining_time(train)

@router.get("/ml/eta/status")
@router.get("/ml/status")
def get_ml_pipeline_status():
    """
    Returns the operational status, feature schema, and dataset requirements of the XGBoost ETA pipeline.
    """
    return ml_eta_service.get_pipeline_status()

@router.post("/ml/eta/train")
def trigger_ml_training(payload: dict = Body(...)):
    """
    Triggers model training given historical trip training records.
    """
    records = payload.get("records", [])
    return ml_eta_service.train(records)

@router.post("/train/{train_number}/simulate")
@router.post("/trains/{train_number}/simulate")
def simulate_train_step(train_number: str):
    # Replaced simulated movement with real RailRadar live status
    train = railradar_service.get_train_data(train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train {train_number} not found")
    store.update_train(train)
    return {"status": "ok", "train": train}
