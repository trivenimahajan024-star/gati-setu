from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.db.store import store

router = APIRouter()

class EventInjectionRequest(BaseModel):
    train_number: str
    event_type: str # 'congestion' | 'tsr' | 'halt' | 'weather' | 'clear'
    delay_impact_mins: int = 5
    description: Optional[str] = None

from concurrent.futures import ThreadPoolExecutor

@router.get("/control/overview")
def get_control_room_overview():
    from app.services.railradar import railradar_service
    keys = list(store._trains.keys())
    with ThreadPoolExecutor(max_workers=min(12, len(keys) or 1)) as ex:
        trains = list(ex.map(lambda tno: railradar_service.get_train_data(tno) or store.get_train(tno), keys))
    trains = [t for t in trains if t]
    total = len(trains)
    on_time = sum(1 for t in trains if t.get("current_delay_mins", 0) <= 5)
    delayed = sum(1 for t in trains if 5 < t.get("current_delay_mins", 0) <= 30)
    significant_delay = sum(1 for t in trains if t.get("current_delay_mins", 0) > 30)
    avg_delay = round(sum(t.get("current_delay_mins", 0) for t in trains) / max(1, total), 1)
    
    active_tsr_count = sum(1 for t in trains for ev in t.get("active_events", []) if ev.get("type") == "tsr")
    congested_count = sum(1 for t in trains for ev in t.get("active_events", []) if ev.get("type") == "congestion")

    return {
        "total_active_trains": total,
        "on_time_trains": on_time,
        "delayed_trains": delayed,
        "significant_delay_trains": significant_delay,
        "on_time_pct": round((on_time / max(1, total)) * 100, 1),
        "average_delay_mins": avg_delay,
        "active_tsrs": max(1, active_tsr_count),
        "congested_sections": max(1, congested_count),
        "network_status": "NORMAL WITH ISOLATED CONGESTION" if delayed + significant_delay <= 2 else "ELEVATED DELAY CONGESTION"
    }

@router.get("/control/alerts")
def get_control_room_alerts():
    return store.get_active_alerts()

@router.get("/control/trains")
def get_control_room_trains():
    from app.services.railradar import railradar_service
    keys = list(store._trains.keys())
    with ThreadPoolExecutor(max_workers=min(12, len(keys) or 1)) as ex:
        trains = list(ex.map(lambda tno: railradar_service.get_train_data(tno) or store.get_train(tno), keys))
    return [t for t in trains if t]

@router.post("/control/inject-event")
def inject_operational_event(req: EventInjectionRequest):
    updated = store.inject_event(
        train_number=req.train_number,
        event_type=req.event_type,
        delay_mins=req.delay_impact_mins,
        description=req.description
    )
    return {
        "status": "success",
        "message": f"Event '{req.event_type}' (+{req.delay_impact_mins}m) injected for Train {req.train_number}",
        "train": updated
    }

@router.post("/control/simulate-tick")
def simulate_network_tick():
    updated_trains = store.advance_simulation_tick()
    return {"status": "ok", "trains": updated_trains}
