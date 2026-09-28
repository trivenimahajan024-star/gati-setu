from fastapi import APIRouter
from app.db.store import store

router = APIRouter()

MAJOR_STATIONS = [
    {"code": "NDLS", "name": "New Delhi", "zone": "NR"},
    {"code": "MMCT", "name": "Mumbai Central", "zone": "WR"},
    {"code": "CSMT", "name": "Mumbai CSMT", "zone": "CR"},
    {"code": "BRC", "name": "Vadodara Jn", "zone": "WR"},
    {"code": "HWH", "name": "Howrah Jn", "zone": "ER"},
    {"code": "BSB", "name": "Varanasi Jn", "zone": "NR"},
    {"code": "RKMP", "name": "Rani Kamlapati (Bhopal)", "zone": "WCR"},
    {"code": "KOTA", "name": "Kota Jn", "zone": "WCR"},
    {"code": "RTM", "name": "Ratlam Jn", "zone": "WR"},
    {"code": "NK", "name": "Nashik Road", "zone": "CR"}
]

@router.get("/stations")
def get_major_stations():
    return MAJOR_STATIONS

@router.get("/station/{station_code}/display")
def get_station_display(station_code: str):
    board = store.get_station_board(station_code)
    stn_info = next((s for s in MAJOR_STATIONS if s["code"] == station_code.upper().strip()), {"name": station_code.upper()})
    return {
        "station_code": station_code.upper(),
        "station_name": stn_info.get("name", station_code.upper()),
        "arrivals": board["arrivals"],
        "departures": board["departures"]
    }
