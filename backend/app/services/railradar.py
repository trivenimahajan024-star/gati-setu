import os
import json
import time
import re
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.config import settings

MAJOR_STATION_COORDS = {
    "NDLS": [28.6139, 77.2090],
    "MMCT": [18.9696, 72.8193],
    "CSMT": [18.9402, 72.8356],
    "LTT": [19.0699, 72.8906],
    "BDTS": [19.0635, 72.8407],
    "BVI": [19.2290, 72.8574],
    "ST": [21.2052, 72.8409],
    "BRC": [22.3107, 73.1812],
    "RTM": [23.3441, 75.0366],
    "KOTA": [25.2138, 75.8648],
    "NZM": [28.5888, 77.2533],
    "DLI": [28.6616, 77.2307],
    "ANVT": [28.6508, 77.3153],
    "GZB": [28.6678, 77.4334],
    "HWH": [22.5839, 88.3426],
    "SDAH": [22.5697, 88.3697],
    "KOAA": [22.6053, 88.3756],
    "SHM": [22.5574, 88.3188],
    "MAS": [13.0827, 80.2707],
    "MS": [13.0782, 80.2608],
    "TBM": [12.9249, 80.1194],
    "SBC": [12.9780, 77.5698],
    "YPR": [13.0238, 77.5503],
    "SMVB": [13.0035, 77.6534],
    "SC": [17.4344, 78.5015],
    "HYB": [17.3929, 78.4682],
    "KCG": [17.3916, 78.4988],
    "ADI": [23.0267, 72.5999],
    "BPL": [23.2599, 77.4126],
    "RKMP": [23.2120, 77.4410],
    "CNB": [26.4539, 80.3507],
    "PNBE": [25.6019, 85.1376],
    "BSB": [25.3268, 82.9863],
    "BSBS": [25.3176, 82.9739],
    "DDU": [25.2818, 83.1207],
    "NGP": [21.1528, 79.0882],
    "BSL": [21.0455, 75.7885],
    "JL": [21.0077, 75.5626],
    "MMR": [20.2524, 74.4388],
    "NK": [19.9575, 73.8340],
    "KYN": [19.2437, 73.1355],
    "TNA": [19.1860, 72.9759],
    "PNVL": [18.9894, 73.1175],
    "PUNE": [18.5284, 73.8744],
    "JP": [26.9185, 75.7880],
    "ASR": [31.6340, 74.8723],
    "GHY": [26.1824, 91.7516],
    "GKP": [26.7606, 83.3732],
    "AGC": [27.1574, 78.0068],
    "AF": [27.1852, 78.0163],
    "GWL": [26.2183, 78.1828],
    "VGLJ": [25.4484, 78.5685],
    "JBP": [23.1815, 79.9864],
    "KTE": [23.8343, 80.3990],
    "PRYJ": [25.4358, 81.8463],
    "LKO": [26.8322, 80.9234],
    "LJN": [26.8320, 80.9200],
    "CDG": [30.7046, 76.8188],
    "INDB": [22.7196, 75.8679],
    "TVC": [8.4870, 76.9525],
    "ERS": [9.9675, 76.2917],
    "MAJN": [12.8681, 74.8643],
    "CAN": [11.8745, 75.3704],
    "CLT": [11.2483, 75.7839],
    "BZA": [16.5062, 80.6480],
    "VSKP": [17.7215, 83.2872],
    "BBS": [20.2961, 85.8245],
    "CTC": [20.4632, 85.8828],
    "BLS": [21.4934, 86.9135],
    "BHC": [21.0544, 86.4962],
    "KGP": [22.3308, 87.3237],
    "TATA": [22.7667, 86.2000],
    "ROU": [22.2253, 84.8536],
    "BSP": [22.0797, 82.1409],
    "R": [21.2514, 81.6296],
    "DURG": [21.1904, 81.2849],
    "RIG": [21.8974, 83.3950],
    "DHN": [23.7957, 86.4304],
    "GAYA": [24.7955, 84.9994],
    "DNR": [25.6200, 85.0500],
    "PPTA": [25.6025, 85.0934],
    "MGS": [25.2818, 83.1207],
    "SVDK": [32.9930, 74.9350],
    "JAT": [32.7060, 74.8790],
    "UMB": [30.3470, 76.8280],
    "LDH": [30.9120, 75.8540],
    "JUC": [31.3260, 75.5760],
    "UJN": [23.1820, 75.7680],
    "SUR": [17.6599, 75.9064],
    "DD": [18.4650, 74.5820],
    "AK": [20.7002, 77.0082],
    "BD": [20.9167, 77.7500],
    "WR": [20.7453, 78.6022],
    "DDR": [19.0178, 72.8478],
    "DR": [19.0178, 72.8478],
    "VR": [19.4542, 72.8118],
    "PLG": [19.6974, 72.7663],
    "PL": [19.6974, 72.7663],
    "BOR": [20.0800, 72.7500],
    "VAPI": [20.3713, 72.9043],
    "BL": [20.6100, 72.9260],
    "BIM": [20.8000, 72.9300],
    "NVS": [20.9500, 72.9300],
    "BH": [21.7051, 72.9959],
    "NDB": [21.3667, 74.2333],
    "NUR": [21.3667, 74.2333],
    "DDE": [21.3200, 74.4800],
    "SNK": [21.3000, 74.7000],
    "AN": [21.0500, 75.0500],
    "DXG": [21.0100, 75.3000],
    "BHET": [21.1400, 72.8800],
    "CHM": [21.1800, 73.0500],
    "BIY": [21.2200, 73.2500],
    "VYA": [21.2800, 73.4000],
    "NWU": [21.3200, 73.7800],
    "NDN": [21.1200, 74.8800]
}

class RailRadarService:
    def __init__(self):
        self.cache = {}  # { train_no: { "data": ..., "timestamp": ... } }
        self.geom_cache = {}  # { train_no: polyline }
        self.sched_cache = {}  # { train_no: sched_data }
        self.station_trains_cache = {}  # { station_code: { "data": ..., "timestamp": ... } }
        self.live_summary_cache = {}  # { train_no: { "data": ..., "timestamp": ... } }
        self._station_names_db = {}
        self._train_names_db = {}
        self._schedule_routes = {}
        self._station_to_trains = {}
        self._schedule_db_loaded = False
        self.live_cache_ttl = 5.0  # 5 seconds TTL for live data
        self.static_cache_ttl = 600.0  # 10 minutes TTL for static geometry/schedule

    @property
    def api_key(self) -> str:
        return settings.RAILRADAR_API_KEY

    @property
    def base_url(self) -> str:
        return "https://api.railradar.in/v1"

    def _api_get(self, endpoint: str, retries: int = 4, retry_delay: float = 2.0) -> dict:
        key = self.api_key
        if not key:
            raise HTTPException(
                status_code=500,
                detail="RAILRADAR_API_KEY is not configured in .env"
            )

        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "User-Agent": "GatiSetu-RailRadar/2.0"
            }
        )

        for attempt in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=3) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)
                    if not data.get("success", False):
                        msg = data.get("message") or "RailRadar API request was unsuccessful"
                        raise HTTPException(status_code=400, detail=msg)
                    return data.get("data", {})
            except urllib.error.HTTPError as e:
                err_msg = f"HTTP {e.code}"
                try:
                    err_json = json.loads(e.read().decode("utf-8"))
                    err_msg = err_json.get("message") or err_json.get("detail") or err_msg
                except Exception:
                    pass
                if e.code == 429:
                    if attempt < retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        raise HTTPException(status_code=429, detail="RailRadar API rate limit exceeded. Please wait a moment.")
                if e.code == 404:
                    raise HTTPException(status_code=404, detail=f"Resource not found (RailRadar: {err_msg})")
                raise HTTPException(status_code=e.code, detail=f"RailRadar API Error: {err_msg}")
            except HTTPException:
                raise
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise HTTPException(status_code=502, detail=f"RailRadar API Connection Error: {str(e)}")
        return {}


    def format_iso_or_time(self, iso_or_time_str: str) -> str:
        if not iso_or_time_str:
            return "--:--"
        if "T" in iso_or_time_str:
            try:
                time_part = iso_or_time_str.split("T")[1].split("+")[0].split("-")[0]
                dt = datetime.strptime(time_part[:5], "%H:%M")
                return dt.strftime("%I:%M %p")
            except Exception:
                pass
        if ":" in iso_or_time_str:
            try:
                parts = iso_or_time_str.split(":")
                h, m = int(parts[0]), int(parts[1])
                dt = datetime(2026, 1, 1, h, m)
                return dt.strftime("%I:%M %p")
            except Exception:
                return iso_or_time_str
        return iso_or_time_str

    def add_delay_to_time(self, time_str: str, delay_mins: int) -> str:
        if not time_str or time_str in ("--:--", "START", "DEST"):
            return time_str
        try:
            if "AM" in time_str or "PM" in time_str:
                dt = datetime.strptime(time_str.strip(), "%I:%M %p")
            else:
                dt = datetime.strptime(time_str.strip()[:5], "%H:%M")
            new_dt = dt + timedelta(minutes=delay_mins)
            return new_dt.strftime("%I:%M %p")
        except Exception:
            return time_str

    def get_station_coordinates(self, code: str) -> list:
        if not code:
            return None
        code_u = str(code).strip().upper()
        if code_u in MAJOR_STATION_COORDS:
            return MAJOR_STATION_COORDS[code_u]
        return None

    def get_train_data(self, train_number: str) -> dict:
        import copy
        from app.db.store import store
        from app.services.gps_service import gps_service

        tno = str(train_number).strip()
        clean_tno = tno.lstrip("0") if tno.startswith("0") and len(tno) == 5 else tno
        now = time.time()

        # Check live cache
        cached = self.cache.get(tno)
        if cached and (now - cached["timestamp"] < self.live_cache_ttl):
            return cached["data"]

        self._ensure_schedule_db_loaded()
        db_route = self._schedule_routes.get(clean_tno) or self._schedule_routes.get(tno) or []
        db_train_info = self._train_names_db.get(clean_tno) or self._train_names_db.get(tno) or {}

        live_data = {}
        sched_data = {}
        route_polyline = []

        # 1. Fetch live running status from RailRadar API
        try:
            live_data = self._api_get(f"/trains/{tno}/live", retries=1, retry_delay=0.5)
        except Exception:
            live_data = {}

        # 2. Fetch train schedule from API (cached with static TTL)
        sched_cached = self.sched_cache.get(tno)
        if sched_cached and (now - sched_cached["timestamp"] < self.static_cache_ttl):
            sched_data = sched_cached["data"]
        else:
            try:
                sched_data = self._api_get(f"/trains/{tno}", retries=1, retry_delay=0.5)
                if sched_data:
                    self.sched_cache[tno] = {"data": sched_data, "timestamp": now}
            except Exception:
                sched_data = sched_cached["data"] if sched_cached else {}

        # 3. Fetch geometry coordinates from API (cached with static TTL)
        geom_cached = self.geom_cache.get(tno)
        if geom_cached and (now - geom_cached["timestamp"] < self.static_cache_ttl):
            route_polyline = geom_cached["data"]
        else:
            try:
                route_data = self._api_get(f"/trains/{tno}/route", retries=1, retry_delay=0.5)
                geojson = route_data.get("geojson", {})
                coords = geojson.get("geometry", {}).get("coordinates", [])
                # Convert [lon, lat] -> [lat, lon]
                route_polyline = [[round(c[1], 5), round(c[0], 5)] for c in coords if len(c) >= 2]
                if route_polyline:
                    self.geom_cache[tno] = {"data": route_polyline, "timestamp": now}
            except Exception:
                route_polyline = geom_cached["data"] if geom_cached else []

        # If neither RailRadar API nor local timetable database knows this train, return 404
        if not live_data and not sched_data and not db_route:
            store_train = store.get_train(tno)
            if not store_train:
                raise HTTPException(status_code=404, detail=f"Train {tno} not found on Indian Railways network")

        store_train = store.get_train(tno)

        train_info = live_data.get("train", {}) or sched_data.get("train", {})
        train_name = live_data.get("trainName") or train_info.get("name") or db_train_info.get("name") or (store_train.get("train_name") if store_train else f"Train {tno}")
        train_type = train_info.get("type") or db_train_info.get("type") or (store_train.get("train_type") if store_train else "Superfast Express")

        src = train_info.get("source", {})
        dest = train_info.get("destination", {})

        if db_route:
            db_src_code = db_route[0]["station_code"]
            db_dest_code = db_route[-1]["station_code"]
            db_src_name = self.get_station_name_by_code(db_src_code)
            db_dest_name = self.get_station_name_by_code(db_dest_code)
            db_total_dist = float(db_route[-1]["dist"] or 0)
        else:
            db_src_code, db_dest_code = "ORIGIN", "DEST"
            db_src_name, db_dest_name = "Origin", "Destination"
            db_total_dist = 0.0

        src_code = src.get("code") or (store_train.get("source_code") if store_train else db_src_code)
        src_name = src.get("name") or (store_train.get("source") if store_train else db_src_name)
        dest_code = dest.get("code") or (store_train.get("destination_code") if store_train else db_dest_code)
        dest_name = dest.get("name") or (store_train.get("destination") if store_train else db_dest_name)

        total_dist = float(train_info.get("distance") or (store_train.get("total_distance_km") if store_train and store_train.get("total_distance_km") else db_total_dist))

        # Check for control room injected active events on this train
        injected_delay = 0
        if store_train and store_train.get("active_events"):
            injected_delay = sum(int(ev.get("delay_impact_mins", 0)) for ev in store_train.get("active_events", []))

        api_delay = live_data.get("delayMinutes")
        if api_delay is not None:
            delay_mins = int(api_delay) + injected_delay
        elif injected_delay > 0:
            delay_mins = injected_delay
        else:
            delay_mins = 0

        current_loc = live_data.get("currentLocation", {})

        # Station map from schedule for lat/lng
        sched_route = sched_data.get("route", [])
        stn_coord_map = {}
        for r in sched_route:
            stn = r.get("station", {})
            code = stn.get("code")
            if code and stn.get("lat") and stn.get("lng"):
                stn_coord_map[code] = [stn.get("lat"), stn.get("lng")]

        # Build halts array
        live_route = live_data.get("route", [])
        halts_list = [r for r in live_route if r.get("isHalt")]
        if not halts_list and sched_route:
            halts_list = [r for r in sched_route if r.get("isHalt")]

        stations = []
        curr_seq = current_loc.get("sequence", 0)

        if halts_list:
            seen_codes = set()
            for idx, r in enumerate(halts_list):
                stn_code = r.get("stationCode") or (r.get("station", {}).get("code"))
                if not stn_code:
                    continue
                code_norm = str(stn_code).strip().upper()
                if code_norm in seen_codes:
                    continue
                seen_codes.add(code_norm)

                stn_name = r.get("stationName") or (r.get("station", {}).get("name")) or self.get_station_name_by_code(code_norm)
                seq = r.get("sequence", idx + 1)

                coords = stn_coord_map.get(code_norm) or self.get_station_coordinates(code_norm)
                if not coords and r.get("station"):
                    coords = [r.get("station", {}).get("lat"), r.get("station", {}).get("lng")]
                if not coords and idx == 0 and src.get("lat"):
                    coords = [src.get("lat"), src.get("lng")]
                if not coords and idx == len(halts_list) - 1 and dest.get("lat"):
                    coords = [dest.get("lat"), dest.get("lng")]

                is_start = (idx == 0)
                is_end = (idx == len(halts_list) - 1)

                raw_sched_arr = r.get("scheduledArrival") or r.get("arrival")
                raw_sched_dep = r.get("scheduledDeparture") or r.get("departure")

                sched_arr_fmt = "START" if is_start else self.format_iso_or_time(raw_sched_arr)
                sched_dep_fmt = "DEST" if is_end else self.format_iso_or_time(raw_sched_dep)

                stn_delay = int(r.get("delayArrival") or r.get("delayDeparture") or (delay_mins if seq >= curr_seq else 0))

                pred_arr_fmt = "START" if is_start else self.add_delay_to_time(sched_arr_fmt, stn_delay)
                pred_dep_fmt = "DEST" if is_end else self.add_delay_to_time(sched_dep_fmt, stn_delay)

                status = r.get("status")
                if not status:
                    if curr_seq > 0 and seq < curr_seq:
                        status = "departed"
                    elif curr_seq > 0 and seq == curr_seq:
                        status = "approaching"
                    else:
                        status = "upcoming" if not is_start else "departed"

                stations.append({
                    "code": code_norm,
                    "name": stn_name,
                    "coordinates": coords,
                    "distance_km": round(float(r.get("distance") or 0), 1),
                    "scheduled_arr": sched_arr_fmt,
                    "scheduled_dep": sched_dep_fmt,
                    "predicted_arr": pred_arr_fmt,
                    "predicted_dep": pred_dep_fmt,
                    "delay_mins": stn_delay,
                    "platform": str(r.get("platform") or "1"),
                    "status": status,
                    "delay_attribution": "Departed on-time" if stn_delay == 0 else f"+{stn_delay}m delay recorded"
                })
        elif db_route:
            # Build authentic halts from timetable database
            seen_codes = set()
            for idx, stop in enumerate(db_route):
                stn_code = stop["station_code"]
                if not stn_code:
                    continue
                code_norm = str(stn_code).strip().upper()
                if code_norm in seen_codes:
                    continue
                seen_codes.add(code_norm)

                stn_name = self.get_station_name_by_code(code_norm)
                is_start = (idx == 0)
                is_end = (idx == len(db_route) - 1)
                
                sched_arr_fmt = "START" if is_start else self.format_iso_or_time(stop["arr"])
                sched_dep_fmt = "DEST" if is_end else self.format_iso_or_time(stop["dep"])
                
                stn_delay = delay_mins if delay_mins > 0 else 0
                pred_arr_fmt = "START" if is_start else self.add_delay_to_time(sched_arr_fmt, stn_delay)
                pred_dep_fmt = "DEST" if is_end else self.add_delay_to_time(sched_dep_fmt, stn_delay)
                
                coords = self.get_station_coordinates(code_norm)
                
                stations.append({
                    "code": code_norm,
                    "name": stn_name,
                    "coordinates": coords,
                    "distance_km": round(float(stop["dist"] or 0), 1),
                    "scheduled_arr": sched_arr_fmt,
                    "scheduled_dep": sched_dep_fmt,
                    "predicted_arr": pred_arr_fmt,
                    "predicted_dep": pred_dep_fmt,
                    "delay_mins": stn_delay,
                    "platform": "1",
                    "status": "upcoming" if not is_start else "departed",
                    "delay_attribution": "Scheduled stop" if stn_delay == 0 else f"+{stn_delay}m delay expected"
                })
        elif store_train:
            seen_codes = set()
            raw_stations = copy.deepcopy(store_train.get("stations", []))
            for stn in raw_stations:
                code_norm = str(stn.get("code") or "").strip().upper()
                if code_norm and code_norm not in seen_codes:
                    seen_codes.add(code_norm)
                    stations.append(stn)

        # Build route polyline if empty
        if not route_polyline:
            route_polyline = [s["coordinates"] for s in stations if s.get("coordinates")]

        # Compute dynamic timetable baseline for authentic positioning
        tt_tracking = self.compute_dynamic_timetable_tracking(stations, total_dist, delay_mins)

        # 1. Coordinates resolution
        curr_stn_code = current_loc.get("stationCode")
        curr_coords = None

        # A. Hardware GPS feed if active
        gps_data = gps_service.get_gps_position(tno)
        if gps_data.get("status") == "ACTIVE" and gps_data.get("coordinates"):
            curr_coords = gps_data["coordinates"]

        # B. Real coordinates from live telemetry
        if not curr_coords:
            if current_loc.get("lat") and current_loc.get("lng"):
                curr_coords = [float(current_loc["lat"]), float(current_loc["lng"])]
            elif current_loc.get("latitude") and current_loc.get("longitude"):
                curr_coords = [float(current_loc["latitude"]), float(current_loc["longitude"])]
            elif current_loc.get("coordinates") and len(current_loc["coordinates"]) >= 2:
                curr_coords = [float(current_loc["coordinates"][0]), float(current_loc["coordinates"][1])]

        # C. Coordinates of current station if specified
        if not curr_coords and curr_stn_code:
            curr_coords = stn_coord_map.get(curr_stn_code) or self.get_station_coordinates(curr_stn_code)

        # D. Dynamic timetable coordinates along route
        if not curr_coords and tt_tracking:
            curr_coords = tt_tracking.get("current_coordinates")

        # E. Station origin coordinates fallback
        if not curr_coords and stations:
            curr_coords = stations[0].get("coordinates")

        # 2. Distance covered & progress
        dist_covered = None
        if current_loc.get("distanceFromOriginKm") is not None:
            dist_covered = round(float(current_loc["distanceFromOriginKm"]), 1)
        elif curr_stn_code and stations:
            matched_stn = next((s for s in stations if s["code"] == curr_stn_code), None)
            if matched_stn:
                dist_covered = round(float(matched_stn.get("distance_km") or 0.0), 1)

        if dist_covered is None:
            if tt_tracking:
                dist_covered = tt_tracking.get("dist_covered", 0.0)
            else:
                dist_covered = 0.0

        dist_covered = max(0.0, min(total_dist, dist_covered))
        dist_remaining = round(max(0.0, total_dist - dist_covered), 1)
        progress_pct = round((dist_covered / total_dist * 100), 1) if total_dist > 0 else 0.0

        # Update station statuses from dynamic timetable if live status is not per-station
        if tt_tracking and "station_statuses" in tt_tracking:
            for s in stations:
                if not live_data or not s.get("status"):
                    if s["code"] in tt_tracking["station_statuses"]:
                        s["status"] = tt_tracking["station_statuses"][s["code"]]

        # 3. Location text & station resolution
        loc_stn_name = current_loc.get("stationName") or (self.get_station_name_by_code(curr_stn_code) if curr_stn_code else None)
        current_station_code = curr_stn_code or (tt_tracking.get("current_station_code") if tt_tracking else (stations[0]["code"] if stations else src_code))
        current_station_name = loc_stn_name or (tt_tracking.get("current_station_name") if tt_tracking else (stations[0]["name"] if stations else src_name))

        if loc_stn_name:
            if current_loc.get("status") == "at-station":
                location_text = f"At {loc_stn_name}"
            elif current_loc.get("status") == "departed":
                location_text = f"Passing {loc_stn_name}"
            else:
                location_text = f"Approaching {loc_stn_name}"
        elif tt_tracking and tt_tracking.get("location_text"):
            location_text = tt_tracking["location_text"]
        elif stations:
            if dist_covered == 0.0:
                location_text = f"At {stations[0]['name']} (Origin)"
            else:
                location_text = f"En route ({src_code} -> {dest_code})"
        else:
            location_text = "En route"

        # 4. Destination ETA
        dest_station_obj = stations[-1] if stations else None
        sched_dest_eta = (dest_station_obj.get("scheduled_arr") if dest_station_obj else None) or (db_route[-1]["arr"] if db_route else "--:--")
        sched_dest_eta_fmt = self.format_iso_or_time(sched_dest_eta)
        pred_dest_eta = self.add_delay_to_time(sched_dest_eta_fmt, delay_mins) if sched_dest_eta_fmt != "--:--" else "--:--"

        # 5. Next Station resolution (Must NEVER be the same as current_station unless terminus)
        next_station_payload = None
        next_halt = live_data.get("nextHalt", {})
        next_stn_name = next_halt.get("stationName") if isinstance(next_halt, dict) else None
        next_stn_code = next_halt.get("stationCode") if isinstance(next_halt, dict) else None

        next_stn_obj = None
        if next_stn_code and next_stn_code != current_station_code:
            next_stn_obj = next((s for s in stations if s["code"] == next_stn_code), None)

        if not next_stn_obj:
            for s in stations:
                if s["code"] == current_station_code and s["code"] != dest_code:
                    continue
                if s["status"] in ("approaching", "upcoming"):
                    next_stn_obj = s
                    break

        if not next_stn_obj and tt_tracking and tt_tracking.get("next_station_payload"):
            next_station_payload = tt_tracking["next_station_payload"]
        elif next_stn_obj:
            n_code = next_stn_obj.get("code")
            n_name = next_stn_obj.get("name")
            n_sched = next_stn_obj.get("scheduled_arr") or next_stn_obj.get("scheduled_dep") or "--:--"
            n_pred = next_stn_obj.get("predicted_arr") or next_stn_obj.get("predicted_dep") or n_sched
            n_dist = round(max(0.0, float(next_stn_obj.get("distance_km") or 0) - dist_covered), 1)
            next_station_payload = {
                "code": n_code,
                "name": n_name,
                "distance_km": n_dist,
                "expected_eta": n_pred,
                "scheduled_eta": n_sched,
                "platform": str(next_stn_obj.get("platform", "1")),
                "stoppage_time": "2 min"
            }
        else:
            next_station_payload = {
                "code": dest_code,
                "name": dest_name,
                "distance_km": dist_remaining,
                "expected_eta": pred_dest_eta if delay_mins > 0 else sched_dest_eta_fmt,
                "scheduled_eta": sched_dest_eta_fmt,
                "platform": "1",
                "stoppage_time": "Terminus"
            }

        # 6. Authentic Status calculation
        raw_status = (live_data.get("status") or "").lower()
        if raw_status in ("completed", "arrived", "finished"):
            status_text = "Completed"
            status_code = "COMPLETED"
        elif raw_status in ("not-started", "not_started"):
            status_text = "NOT STARTED"
            status_code = "NOT_STARTED"
        elif tt_tracking:
            status_text = tt_tracking["status_text"]
            status_code = tt_tracking["status_code"]
        elif delay_mins > 5 or raw_status == "delayed":
            status_text = f"Running (+{delay_mins}m)"
            status_code = "DELAYED"
        else:
            status_text = "Running on-time" if delay_mins <= 0 else f"Running (+{delay_mins}m)"
            status_code = "RUNNING"

        # 7. Speed: only real telemetry or 0 if not started/completed, else None
        if gps_data.get("status") == "ACTIVE" and gps_data.get("speed") is not None:
            speed = int(gps_data["speed"])
        elif current_loc.get("speedKmh") is not None:
            speed = int(current_loc["speedKmh"])
        elif status_code in ("NOT_STARTED", "COMPLETED"):
            speed = 0
        else:
            speed = None

        # Last updated time
        last_updated_raw = live_data.get("lastUpdatedAt")
        if last_updated_raw:
            try:
                last_updated_time = datetime.fromisoformat(str(last_updated_raw)).strftime("%I:%M %p IST")
            except Exception:
                last_updated_time = "Live"
        elif live_data:
            last_updated_time = "Live Real-Time"
        else:
            last_updated_time = "Timetable Schedule"

        # Dynamic Operational Factors
        eta_factors = []
        if store_train and store_train.get("eta_factors") and store_train.get("active_events"):
            eta_factors = copy.deepcopy(store_train.get("eta_factors"))
        elif delay_mins > 0:
            eta_factors.append({
                "id": "traffic_congestion",
                "code": "F06",
                "name": "Sectional Traffic Density & Signals",
                "category": "Traffic Density",
                "is_active": True,
                "impact_level": "High impact" if delay_mins > 15 else "Moderate impact",
                "delay_impact_mins": delay_mins,
                "passenger_explanation": f"Train is navigating with cautionary signal clearances near {location_text}, accounting for +{delay_mins} min delay.",
                "technical_detail": f"Delay telemetry recorded at {last_updated_time}."
            })
        else:
            eta_factors.append({
                "id": "clear_corridor",
                "code": "F01",
                "name": "Clear Railway Corridor",
                "category": "Traffic Density",
                "is_active": False,
                "impact_level": "Low impact",
                "delay_impact_mins": 0,
                "passenger_explanation": "Train is cruising on-time with clear track signals ahead.",
                "technical_detail": "Nominal block section clearance confirmed."
            })

        lat = float(curr_coords[0]) if curr_coords and len(curr_coords) >= 2 and curr_coords[0] is not None else None
        lng = float(curr_coords[1]) if curr_coords and len(curr_coords) >= 2 and curr_coords[1] is not None else None

        result = {
            "train_number": str(tno),
            "train_name": train_name,
            "short_name": train_name.split("-")[0].strip() if "-" in train_name else train_name,
            "train_type": train_type,
            "source": f"{src_name}" if "(" in str(src_name) else f"{src_name} ({src_code})",
            "source_code": src_code,
            "destination": f"{dest_name}" if "(" in str(dest_name) else f"{dest_name} ({dest_code})",
            "destination_code": dest_code,
            "total_distance_km": total_dist,
            "distance_covered_km": dist_covered,
            "distance_remaining_km": dist_remaining,
            "journey_progress_pct": progress_pct,
            "avg_speed_kmh": float(train_info.get("avgSpeed") or 85),
            "current_status": status_text,
            "current_status_code": status_code,
            "current_location": location_text,
            "current_coordinates": [lat, lng] if (lat is not None and lng is not None) else None,
            "latitude": lat,
            "longitude": lng,
            "speed": int(speed) if speed is not None else None,
            "heading_deg": 0,
            "current_speed_kmh": int(speed) if speed is not None else None,
            "delay": delay_mins,
            "current_delay_mins": delay_mins,
            "confidence_level": "High" if delay_mins < 30 else "Moderate",
            "confidence_pct": 94 if delay_mins < 15 else 85,
            "arrival_window": f"{self.add_delay_to_time(pred_dest_eta, -5)} – {self.add_delay_to_time(pred_dest_eta, 5)}" if pred_dest_eta != "--:--" else "--:--",
            "scheduled_destination_eta": sched_dest_eta,
            "predicted_destination_eta": pred_dest_eta,
            "eta": pred_dest_eta,
            "last_updated": "Live Real-Time (RailRadar)" if live_data else "Timetable Schedule",
            "last_updated_time": last_updated_time,
            "next_station": next_station_payload,
            "stations": stations,
            "route_polyline": route_polyline,
            "eta_factors": eta_factors,
            "passenger_alerts": [
                {
                    "id": f"alt-{tno}",
                    "title": f"Train {tno} Status" if delay_mins == 0 else f"Delay Advisory (+{delay_mins} min)",
                    "message": f"Train {tno} is operating on-schedule ({src_code} -> {dest_code})." if delay_mins == 0 else f"Train {tno} is currently running {delay_mins} min behind schedule. Destination ETA: {pred_dest_eta}.",
                    "time": last_updated_time,
                    "severity": "info" if delay_mins == 0 else ("warning" if delay_mins < 30 else "danger")
                }
            ]
        }

        # Save to live cache and update store
        self.cache[tno] = {"data": result, "timestamp": now}
        store.update_train(result)
        return result

    def _ensure_schedule_db_loaded(self):
        if self._schedule_db_loaded:
            return
        self._schedule_db_loaded = True
        
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(backend_dir, "data")
        
        # 1. Load station full names
        stn_file = os.path.join(data_dir, "station_full_names.csv")
        if os.path.exists(stn_file):
            try:
                import csv
                with open(stn_file, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        code = (row.get("station_name") or "").strip().upper()
                        full_name = (row.get("station_full_name") or "").strip().title()
                        if code and full_name:
                            self._station_names_db[code] = full_name
            except Exception:
                pass
                
        # 2. Load train details
        train_file = os.path.join(data_dir, "train_details.csv")
        if os.path.exists(train_file):
            try:
                import csv
                with open(train_file, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        tno = (row.get("train_no") or "").strip()
                        tname = (row.get("train_name") or "").strip().title()
                        ttype = (row.get("type_code") or "").strip()
                        if tno:
                            info = {
                                "name": tname,
                                "type": "Superfast Express" if "SF" in ttype.upper() else ("Express" if "EXP" in ttype.upper() or not ttype else ttype)
                            }
                            self._train_names_db[tno] = info
                            self._train_names_db[tno.lstrip("0")] = info
            except Exception:
                pass

        # 3. Load combined schedule
        sched_file = os.path.join(data_dir, "combined_schedule.csv")
        if os.path.exists(sched_file):
            try:
                import csv
                with open(sched_file, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        tno = (row.get("train_no") or "").strip()
                        stn_code = (row.get("station_name") or "").strip().upper()
                        if not tno or not stn_code:
                            continue
                        
                        clean_tno = tno.lstrip("0") if tno.startswith("0") and len(tno) == 5 else tno
                        seq = int(row.get("station_no") or 0)
                        dist = float(row.get("distance_from_origin") or 0)
                        arr = (row.get("arrival_time") or "").strip()
                        dep = (row.get("departure_time") or "").strip()
                        arr_day = int(row.get("arrival_day") or 1)
                        dep_day = int(row.get("departure_day") or arr_day or 1)
                        
                        item = {
                            "station_code": stn_code,
                            "seq": seq,
                            "dist": dist,
                            "arr": arr,
                            "dep": dep,
                            "arr_day": arr_day,
                            "dep_day": dep_day
                        }
                        
                        keys = set(filter(None, (clean_tno, tno)))
                        for k in keys:
                            if k not in self._schedule_routes:
                                self._schedule_routes[k] = []
                            self._schedule_routes[k].append(item)
                            
                            if stn_code not in self._station_to_trains:
                                self._station_to_trains[stn_code] = set()
                            self._station_to_trains[stn_code].add(k)
                        
                for tno_key in self._schedule_routes:
                    self._schedule_routes[tno_key].sort(key=lambda x: x["seq"])
                    seen_codes = set()
                    unique_route = []
                    for stop in self._schedule_routes[tno_key]:
                        sc = stop["station_code"]
                        if sc not in seen_codes:
                            seen_codes.add(sc)
                            unique_route.append(stop)
                    self._schedule_routes[tno_key] = unique_route
            except Exception:
                pass

    def get_station_name_by_code(self, code: str) -> str:
        self._ensure_schedule_db_loaded()
        code_u = str(code).strip().upper()
        if code_u in self._station_names_db:
            return self._station_names_db[code_u]
        for k, v in MAJOR_STATION_MAP.items():
            if v[0] == code_u:
                return v[1]
        return code_u

    def parse_time_to_mins(self, t_str) -> int | None:
        if not t_str:
            return None
        clean_str = str(t_str).strip()
        if "T" in clean_str:
            clean_str = clean_str.split("T")[1][:5]
        elif "AM" in clean_str or "PM" in clean_str:
            try:
                dt = datetime.strptime(clean_str, "%I:%M %p")
                return dt.hour * 60 + dt.minute
            except Exception:
                pass
        if ":" in clean_str:
            try:
                parts = clean_str.split(":")
                return int(parts[0]) * 60 + int(parts[1][:2])
            except Exception:
                pass
        return None

    def compute_dynamic_timetable_tracking(self, stations: list, total_dist: float, delay_mins: int = 0) -> dict:
        if not stations:
            return {}
            
        now_utc = datetime.now(timezone.utc)
        ist_now = now_utc + timedelta(hours=5, minutes=30)
        curr_mins = ist_now.hour * 60 + ist_now.minute

        # Build absolute timeline for stations handling day transitions
        timeline = []
        t_offset = 0
        last_dep_mins = None
        
        for idx, s in enumerate(stations):
            is_start = (idx == 0)
            is_end = (idx == len(stations) - 1)
            
            raw_arr = s.get("scheduled_arr")
            raw_dep = s.get("scheduled_dep")
            
            arr_m = self.parse_time_to_mins(raw_arr) if not is_start else self.parse_time_to_mins(raw_dep)
            dep_m = self.parse_time_to_mins(raw_dep) if not is_end else arr_m
            
            if arr_m is None: arr_m = last_dep_mins or 0
            if dep_m is None: dep_m = arr_m
            
            if last_dep_mins is not None and arr_m < (last_dep_mins % 1440):
                t_offset += 1440
                
            abs_arr = arr_m + t_offset
            
            if dep_m < arr_m:
                t_offset += 1440
                
            abs_dep = dep_m + t_offset
            last_dep_mins = dep_m
            
            timeline.append({
                "index": idx,
                "station": s,
                "abs_arr": abs_arr,
                "abs_dep": abs_dep,
                "dist": float(s.get("distance_km") or 0.0)
            })
            
        t_start = timeline[0]["abs_dep"]
        t_end = timeline[-1]["abs_arr"]
        
        # Determine active trip
        if curr_mins < t_start:
            if (curr_mins + 1440) <= (t_end + delay_mins):
                t_active = curr_mins + 1440
            else:
                t_active = curr_mins  # Will be < t_start -> NOT_STARTED
        else:
            t_active = curr_mins

        # 1. NOT STARTED
        if t_active < t_start:
            stn_statuses = {s["code"]: "upcoming" for s in stations}
            return {
                "status_text": "NOT STARTED",
                "status_code": "NOT_STARTED",
                "dist_covered": 0.0,
                "dist_remaining": total_dist,
                "progress_pct": 0.0,
                "speed": 0,
                "location_text": f"At {stations[0]['name']} (Origin)",
                "current_station_code": stations[0]["code"],
                "current_station_name": stations[0]["name"],
                "current_station_seq": 0,
                "current_coordinates": stations[0].get("coordinates"),
                "next_station_payload": {
                    "code": stations[1]["code"] if len(stations) > 1 else stations[0]["code"],
                    "name": stations[1]["name"] if len(stations) > 1 else stations[0]["name"],
                    "distance_km": float(stations[1].get("distance_km") or 0.0) if len(stations) > 1 else 0.0,
                    "expected_eta": stations[1].get("predicted_arr") or stations[1].get("scheduled_arr") or "--:--" if len(stations) > 1 else "--:--",
                    "scheduled_eta": stations[1].get("scheduled_arr") or "--:--" if len(stations) > 1 else "--:--",
                    "platform": str(stations[1].get("platform", "1")) if len(stations) > 1 else "1",
                    "stoppage_time": "2 min"
                },
                "station_statuses": stn_statuses
            }

        # 2. COMPLETED
        if t_active >= (t_end + delay_mins):
            stn_statuses = {s["code"]: "departed" for s in stations}
            return {
                "status_text": "Completed",
                "status_code": "COMPLETED",
                "dist_covered": total_dist,
                "dist_remaining": 0.0,
                "progress_pct": 100.0,
                "speed": 0,
                "location_text": f"Arrived at {stations[-1]['name']} (Terminus)",
                "current_station_code": stations[-1]["code"],
                "current_station_name": stations[-1]["name"],
                "current_station_seq": len(stations) - 1,
                "current_coordinates": stations[-1].get("coordinates"),
                "next_station_payload": {
                    "code": stations[-1]["code"],
                    "name": stations[-1]["name"],
                    "distance_km": 0.0,
                    "expected_eta": stations[-1].get("predicted_arr") or "--:--",
                    "scheduled_eta": stations[-1].get("scheduled_arr") or "--:--",
                    "platform": str(stations[-1].get("platform", "1")),
                    "stoppage_time": "Terminus"
                },
                "station_statuses": stn_statuses
            }

        # 3. RUNNING
        stn_statuses = {}
        active_idx = 0
        is_at_station = False
        
        for i in range(len(timeline)):
            t_entry = timeline[i]
            code = t_entry["station"]["code"]
            
            if t_active < t_entry["abs_arr"]:
                stn_statuses[code] = "upcoming"
            elif t_entry["abs_arr"] <= t_active <= t_entry["abs_dep"]:
                stn_statuses[code] = "approaching"
                active_idx = i
                is_at_station = True
            else:
                stn_statuses[code] = "departed"
                active_idx = i

        curr_t = timeline[active_idx]
        next_t = timeline[active_idx + 1] if active_idx + 1 < len(timeline) else curr_t

        if is_at_station:
            dist_covered = curr_t["dist"]
            loc_text = f"At {curr_t['station']['name']}"
            curr_code = curr_t["station"]["code"]
            curr_name = curr_t["station"]["name"]
            next_code = next_t["station"]["code"]
            next_name = next_t["station"]["name"]
            next_dist = round(max(0.0, next_t["dist"] - dist_covered), 1)
            next_eta = next_t["station"].get("predicted_arr") or next_t["station"].get("scheduled_arr") or "--:--"
            next_sched = next_t["station"].get("scheduled_arr") or "--:--"
            curr_coords = curr_t["station"].get("coordinates")
        else:
            leg_dt = max(1, next_t["abs_arr"] - curr_t["abs_dep"])
            frac = min(1.0, max(0.0, (t_active - curr_t["abs_dep"]) / leg_dt))
            
            dist_covered = round(curr_t["dist"] + frac * (next_t["dist"] - curr_t["dist"]), 1)
            
            if frac > 0.7:
                loc_text = f"Approaching {next_t['station']['name']}"
            else:
                loc_text = f"Between {curr_t['station']['name']} and {next_t['station']['name']}"
                
            curr_code = curr_t["station"]["code"]
            curr_name = curr_t["station"]["name"]
            next_code = next_t["station"]["code"]
            next_name = next_t["station"]["name"]
            next_dist = round(max(0.0, next_t["dist"] - dist_covered), 1)
            next_eta = next_t["station"].get("predicted_arr") or next_t["station"].get("scheduled_arr") or "--:--"
            next_sched = next_t["station"].get("scheduled_arr") or "--:--"
            stn_statuses[next_code] = "approaching"

            c1 = curr_t["station"].get("coordinates")
            c2 = next_t["station"].get("coordinates")
            if c1 and c2 and len(c1) >= 2 and len(c2) >= 2:
                curr_coords = [
                    round(float(c1[0]) + frac * (float(c2[0]) - float(c1[0])), 6),
                    round(float(c1[1]) + frac * (float(c2[1]) - float(c1[1])), 6)
                ]
            else:
                curr_coords = c1 or c2

        dist_covered = max(0.0, min(total_dist, dist_covered))
        dist_remaining = round(max(0.0, total_dist - dist_covered), 1)
        progress_pct = round((dist_covered / total_dist * 100), 1) if total_dist > 0 else 0.0

        status_text = f"Running (+{delay_mins}m)" if delay_mins > 5 else ("Running (+{delay_mins}m)" if delay_mins > 0 else "Running on-time")
        status_code = "DELAYED" if delay_mins > 5 else "RUNNING"

        return {
            "status_text": status_text,
            "status_code": status_code,
            "dist_covered": dist_covered,
            "dist_remaining": dist_remaining,
            "progress_pct": progress_pct,
            "speed": None,
            "location_text": loc_text,
            "current_station_code": curr_code,
            "current_station_name": curr_name,
            "current_station_seq": active_idx + 1,
            "current_coordinates": curr_coords,
            "next_station_payload": {
                "code": next_code,
                "name": next_name,
                "distance_km": next_dist,
                "expected_eta": next_eta,
                "scheduled_eta": next_sched,
                "platform": str(next_t["station"].get("platform", "1")),
                "stoppage_time": "2 min"
            },
            "station_statuses": stn_statuses
        }

    def calculate_duration(self, raw_dep: str, raw_arr: str, dep_day: int = 1, arr_day: int = 1) -> str:
        try:
            d_mins = self.parse_time_to_mins(raw_dep)
            a_mins = self.parse_time_to_mins(raw_arr)

            if d_mins is None or a_mins is None:
                return "--"

            day_diff = arr_day - dep_day
            if day_diff < 0 or day_diff > 4:
                day_diff = 1 if a_mins < d_mins else 0
            elif day_diff == 0 and a_mins < d_mins:
                day_diff = 1

            total_arr_mins = a_mins + (day_diff * 1440)
            diff = total_arr_mins - d_mins
            if diff < 0:
                diff += 1440

            hrs = diff // 60
            mins = diff % 60
            return f"{hrs}h {mins:02d}m"
        except Exception:
            return "--"

    def resolve_stations_list(self, query: str) -> tuple[list[str], str]:
        if not query:
            return [], ""
        self._ensure_schedule_db_loaded()
        q = str(query).strip()
        q_lower = q.lower()

        # 1. Direct match in multi-terminal city map
        if q_lower in CITY_TERMINALS_MAP:
            codes = CITY_TERMINALS_MAP[q_lower]
            rep_name = self.get_station_name_by_code(codes[0]) or q.title()
            return list(dict.fromkeys(codes)), rep_name

        # 2. Check parenthetical format e.g. "Mumbai Central (MMCT)" or "Bhusawal (BSL)"
        if "(" in q and ")" in q:
            inside = q.split("(")[1].split(")")[0].strip()
            outside = q.split("(")[0].strip()
            for cand in (inside, outside):
                if cand.lower() in CITY_TERMINALS_MAP:
                    codes = CITY_TERMINALS_MAP[cand.lower()]
                    rep_name = self.get_station_name_by_code(codes[0]) or cand.title()
                    return list(dict.fromkeys(codes)), rep_name
                if 2 <= len(cand) <= 5 and cand.isalnum():
                    code_u = cand.upper()
                    return [code_u], self.get_station_name_by_code(code_u)

        # 3. Check slash format e.g. "MMCT / Mumbai Central"
        if "/" in q:
            parts = [p.strip() for p in q.split("/")]
            for p in parts:
                if p.lower() in CITY_TERMINALS_MAP:
                    codes = CITY_TERMINALS_MAP[p.lower()]
                    rep_name = self.get_station_name_by_code(codes[0]) or p.title()
                    return list(dict.fromkeys(codes)), rep_name
                if 2 <= len(p) <= 5 and p.isalnum():
                    code_u = p.upper()
                    return [code_u], self.get_station_name_by_code(code_u)

        # 4. Check if q itself is a valid station code
        code_u = q.upper()
        if 2 <= len(code_u) <= 5 and code_u.isalnum():
            if code_u in self._station_names_db or code_u in self._station_to_trains:
                return [code_u], self.get_station_name_by_code(code_u)

        # 5. Fuzzy / Substring match in station database
        matching_codes = []
        for code, full_name in self._station_names_db.items():
            if q_lower == full_name.lower():
                matching_codes.insert(0, code)
            elif q_lower in full_name.lower():
                matching_codes.append(code)
        
        if matching_codes:
            rep_name = self.get_station_name_by_code(matching_codes[0])
            return list(dict.fromkeys(matching_codes[:8])), rep_name

        return [code_u], self.get_station_name_by_code(code_u)

    def resolve_station(self, query: str) -> tuple[str, str]:
        codes, name = self.resolve_stations_list(query)
        if codes:
            return codes[0], name
        return str(query).upper(), str(query)

    def get_station_trains(self, station_code: str) -> list:
        stn = str(station_code).strip().upper()
        now = time.time()
        cached = self.station_trains_cache.get(stn)
        if cached and (now - cached["timestamp"] < self.static_cache_ttl):
            return cached["data"]
        
        try:
            data = self._api_get(f"/stations/{stn}/trains", retries=1, retry_delay=0.2)
            trains = data.get("trains", [])
            self.station_trains_cache[stn] = {"data": trains, "timestamp": now}
            return trains
        except Exception:
            if cached:
                return cached["data"]
            return []

    def get_train_live_summary(self, train_number: str, dep_time: str, arr_time: str) -> dict:
        tno = str(train_number).strip()
        now = time.time()
        
        cached_full = self.cache.get(tno)
        if cached_full and (now - cached_full["timestamp"] < self.live_cache_ttl * 6):
            data = cached_full["data"]
            delay = int(data.get("current_delay_mins") or 0)
            status_code = data.get("current_status_code", "RUNNING")
            
            if status_code in ("COMPLETED", "ARRIVED"):
                category = "completed"
                status_text = "Completed"
            elif status_code in ("NOT-STARTED", "NOT_STARTED", "SCHEDULED"):
                category = "not_started"
                status_text = "Not Started"
            elif delay > 5 or status_code == "DELAYED":
                category = "delayed"
                status_text = f"Delayed (+{delay}m)"
            else:
                category = "running"
                status_text = "Running on-time" if delay <= 0 else f"Running (+{delay}m)"
                
            return {
                "category": category,
                "status_code": status_code,
                "status_text": status_text,
                "delay_mins": delay,
                "current_location": data.get("current_location", "En route"),
                "next_station": data.get("next_station", {}).get("name", "--") if isinstance(data.get("next_station"), dict) else (data.get("next_station") or "--"),
                "last_updated_time": data.get("last_updated_time", "Live")
            }

        cached_sum = self.live_summary_cache.get(tno)
        if cached_sum and (now - cached_sum["timestamp"] < 30.0):
            return cached_sum["data"]

        try:
            live_data = self._api_get(f"/trains/{tno}/live", retries=2, retry_delay=1.0)
            delay = int(live_data.get("delayMinutes") or 0)
            raw_status = (live_data.get("status") or "running").lower()
            current_loc = live_data.get("currentLocation", {})
            next_halt = live_data.get("nextHalt", {})
            
            loc_stn_name = current_loc.get("stationName") or current_loc.get("stationCode") or "En route"
            if current_loc.get("status") == "at-station":
                location_text = f"At {loc_stn_name}"
            elif current_loc.get("status") == "departed":
                location_text = f"Passing {loc_stn_name}"
            else:
                location_text = f"Approaching {loc_stn_name}"
                
            next_stn_text = next_halt.get("stationName") or "--"
            
            last_updated_raw = live_data.get("lastUpdatedAt")
            if last_updated_raw:
                try:
                    last_updated_time = datetime.fromisoformat(last_updated_raw).strftime("%I:%M %p IST")
                except Exception:
                    last_updated_time = "Live"
            else:
                last_updated_time = "Live"

            if raw_status in ("completed", "arrived", "finished"):
                category = "completed"
                status_code = "COMPLETED"
                status_text = "Completed"
            elif raw_status in ("not-started", "not_started"):
                category = "not_started"
                status_code = "NOT_STARTED"
                status_text = "NOT STARTED"
            elif delay > 5 or raw_status == "delayed":
                category = "delayed"
                status_code = "DELAYED"
                status_text = f"Running (+{delay}m)"
            else:
                category = "running"
                status_code = "RUNNING"
                status_text = "Running on-time" if delay <= 0 else f"Running (+{delay}m)"

            res = {
                "category": category,
                "status_code": status_code,
                "status_text": status_text,
                "delay_mins": delay,
                "current_location": location_text,
                "next_station": next_stn_text,
                "last_updated_time": last_updated_time
            }
            self.live_summary_cache[tno] = {"data": res, "timestamp": now}
            return res
        except Exception:
            now_utc = datetime.now(timezone.utc)
            ist_now = now_utc + timedelta(hours=5, minutes=30)
            curr_ist_mins = ist_now.hour * 60 + ist_now.minute

            d_mins = self.parse_time_to_mins(dep_time)
            a_mins = self.parse_time_to_mins(arr_time)

            if d_mins is not None and curr_ist_mins < d_mins:
                cat = "not_started"
                st_code = "NOT_STARTED"
                st_text = "NOT STARTED"
            elif a_mins is not None and d_mins is not None and a_mins > d_mins and curr_ist_mins >= a_mins:
                cat = "completed"
                st_code = "COMPLETED"
                st_text = "Completed"
            else:
                cat = "running"
                st_code = "RUNNING"
                st_text = "Running on-time"

            res = {
                "category": cat,
                "status_code": st_code,
                "status_text": st_text,
                "delay_mins": 0,
                "current_location": "--",
                "next_station": "--",
                "last_updated_time": "Timetable Schedule"
            }
            return res

    def _search_schedule_db(self, from_codes: list[str], to_codes: list[str]) -> list:
        self._ensure_schedule_db_loaded()
        from_set = {c.upper() for c in from_codes}
        to_set = {c.upper() for c in to_codes}
        
        from_trains = set()
        for fc in from_set:
            from_trains.update(self._station_to_trains.get(fc, set()))
            
        to_trains = set()
        for tc in to_set:
            to_trains.update(self._station_to_trains.get(tc, set()))
            
        candidate_trains = from_trains & to_trains
        
        matches = []
        seen_trains = set()
        
        for tno in candidate_trains:
            if tno in seen_trains:
                continue
            route = self._schedule_routes.get(tno, [])
            if not route:
                continue
                
            f_idx, t_idx = -1, -1
            f_stop, t_stop = None, None
            
            for idx, stop in enumerate(route):
                sc = stop["station_code"]
                if sc in from_set and f_idx == -1:
                    f_idx = idx
                    f_stop = stop
                if sc in to_set and f_idx != -1 and idx > f_idx:
                    t_idx = idx
                    t_stop = stop
                    break
            
            if f_idx != -1 and t_idx != -1 and f_idx < t_idx:
                seen_trains.add(tno)
                raw_dep = f_stop["dep"] or f_stop["arr"] or "00:00"
                raw_arr = t_stop["arr"] or t_stop["dep"] or "00:00"
                dep_time = self.format_iso_or_time(raw_dep)
                arr_time = self.format_iso_or_time(raw_arr)
                
                dep_day = f_stop.get("dep_day", 1)
                arr_day = t_stop.get("arr_day", dep_day)
                duration_str = self.calculate_duration(raw_dep, raw_arr, dep_day, arr_day)
                
                origin_code = route[0]["station_code"]
                origin_name = self.get_station_name_by_code(origin_code)
                dest_code = route[-1]["station_code"]
                dest_name = self.get_station_name_by_code(dest_code)
                
                t_details = self._train_names_db.get(tno, {})
                t_name = t_details.get("name") or f"Express Train {tno}"
                t_type = t_details.get("type") or "Superfast Express"
                
                f_code = f_stop["station_code"]
                t_code = t_stop["station_code"]
                f_name = self.get_station_name_by_code(f_code)
                t_name_stn = self.get_station_name_by_code(t_code)
                
                matches.append({
                    "train_number": tno,
                    "train_name": t_name,
                    "train_type": t_type,
                    "origin_station": {"code": origin_code, "name": origin_name},
                    "destination_station": {"code": dest_code, "name": dest_name},
                    "from_station_code": f_code,
                    "from_station_name": f_name,
                    "to_station_code": t_code,
                    "to_station_name": t_name_stn,
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "duration": duration_str,
                    "raw_dep": raw_dep
                })
                
        matches.sort(key=lambda x: x.get("raw_dep", "99:99"))
        return matches

    def get_trains_between_stations(self, from_query: str, to_query: str) -> dict:
        from_codes, from_name = self.resolve_stations_list(from_query)
        to_codes, to_name = self.resolve_stations_list(to_query)

        if not from_codes or not to_codes:
            raise HTTPException(status_code=400, detail="Please provide valid source and destination stations.")

        # Disallow exact same single station code query
        if len(from_codes) == 1 and len(to_codes) == 1 and from_codes[0] == to_codes[0]:
            raise HTTPException(status_code=400, detail="Source and destination stations cannot be the same.")

        matched_trains_dict = {}
        from_set = {c.upper() for c in from_codes}
        to_set = {c.upper() for c in to_codes}

        # --- 1. Primary: Check configured/active store trains (e.g. 12951, 12860, 22436, 12002, 12259) ---
        try:
            from app.db.store import store
            all_store_trains = store.get_all_trains()
            for t in all_store_trains:
                tno = str(t.get("train_number", "")).strip()
                stations = t.get("stations", [])
                f_idx, t_idx = -1, -1
                f_stn, t_stn = None, None
                for idx, stn in enumerate(stations):
                    stn_code = str(stn.get("code", "")).strip().upper()
                    if stn_code in from_set and f_idx == -1:
                        f_idx = idx
                        f_stn = stn
                    if stn_code in to_set and f_idx != -1:
                        t_idx = idx
                        t_stn = stn
                        break
                
                if f_idx != -1 and t_idx != -1 and f_idx < t_idx:
                    raw_dep = f_stn.get("scheduled_dep") or f_stn.get("predicted_dep") or f_stn.get("scheduled_arr") or "00:00"
                    raw_arr = t_stn.get("scheduled_arr") or t_stn.get("predicted_arr") or t_stn.get("scheduled_dep") or "00:00"
                    dep_time = self.format_iso_or_time(raw_dep)
                    arr_time = self.format_iso_or_time(raw_arr)
                    duration_str = self.calculate_duration(raw_dep, raw_arr)
                    delay_mins = int(t.get("current_delay_mins", 0))
                    status_code = t.get("current_status_code", "RUNNING")
                    category = "running" if delay_mins <= 5 else "delayed"
                    status_text = "Running on-time" if delay_mins <= 0 else f"Running (+{delay_mins}m)"
                    
                    next_stn_name = "--"
                    if isinstance(t.get("next_station"), dict):
                        next_stn_name = t.get("next_station", {}).get("name", "--")
                    elif isinstance(t.get("next_station"), str):
                        next_stn_name = t.get("next_station")

                    origin_code = str(stations[0].get("code", "")) if stations else f_stn.get("code")
                    dest_code = str(stations[-1].get("code", "")) if stations else t_stn.get("code")

                    matched_trains_dict[tno] = {
                        "train_number": tno,
                        "train_name": t.get("train_name", f"Train {tno}"),
                        "train_type": t.get("train_type", "Superfast Express"),
                        "origin_station": {"code": origin_code, "name": self.get_station_name_by_code(origin_code)},
                        "destination_station": {"code": dest_code, "name": self.get_station_name_by_code(dest_code)},
                        "from_station_code": f_stn.get("code", from_codes[0]),
                        "from_station_name": f_stn.get("name") or self.get_station_name_by_code(f_stn.get("code")),
                        "to_station_code": t_stn.get("code", to_codes[0]),
                        "to_station_name": t_stn.get("name") or self.get_station_name_by_code(t_stn.get("code")),
                        "departure_time": dep_time,
                        "arrival_time": arr_time,
                        "duration": duration_str,
                        "run_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                        "current_status": status_text,
                        "current_status_code": status_code,
                        "status_category": category,
                        "delay_mins": delay_mins,
                        "current_location": t.get("current_location", "En route"),
                        "next_station": next_stn_name,
                        "last_updated_time": t.get("last_updated_time", "Live Real-Time"),
                        "raw_dep": raw_dep
                    }
        except Exception:
            pass

        # --- 2. Historical / Timetable schedule database (combined_schedule.csv) ---
        try:
            sched_matches = self._search_schedule_db(from_codes, to_codes)
            for sm in sched_matches:
                tno = sm["train_number"]
                if tno not in matched_trains_dict:
                    # Check if live data is available in cache or store
                    if tno in self.cache:
                        live_info = self.get_train_live_summary(tno, sm["departure_time"], sm["arrival_time"])
                    else:
                        now_utc = datetime.now(timezone.utc)
                        ist_now = now_utc + timedelta(hours=5, minutes=30)
                        curr_ist_mins = ist_now.hour * 60 + ist_now.minute

                        d_mins = self.parse_time_to_mins(sm.get("departure_time"))
                        a_mins = self.parse_time_to_mins(sm.get("arrival_time"))

                        if d_mins is not None and curr_ist_mins < d_mins:
                            cat = "not_started"
                            st_code = "NOT_STARTED"
                            st_text = "NOT STARTED"
                        elif a_mins is not None and d_mins is not None and a_mins > d_mins and curr_ist_mins >= a_mins:
                            cat = "completed"
                            st_code = "COMPLETED"
                            st_text = "Completed"
                        else:
                            cat = "running"
                            st_code = "RUNNING"
                            st_text = "Running on-time"

                        live_info = {
                            "category": cat,
                            "status_code": st_code,
                            "status_text": st_text,
                            "delay_mins": 0,
                            "current_location": "--",
                            "next_station": "--",
                            "last_updated_time": "Timetable Schedule"
                        }

                    matched_trains_dict[tno] = {
                        "train_number": tno,
                        "train_name": sm["train_name"],
                        "train_type": sm.get("train_type", "Superfast Express"),
                        "origin_station": sm["origin_station"],
                        "destination_station": sm["destination_station"],
                        "from_station_code": sm["from_station_code"],
                        "from_station_name": sm["from_station_name"],
                        "to_station_code": sm["to_station_code"],
                        "to_station_name": sm["to_station_name"],
                        "departure_time": sm["departure_time"],
                        "arrival_time": sm["arrival_time"],
                        "duration": sm.get("duration", "--"),
                        "run_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                        "current_status": live_info.get("status_text", "Live status unavailable"),
                        "current_status_code": live_info.get("status_code", "UNAVAILABLE"),
                        "status_category": live_info.get("category", "unavailable"),
                        "delay_mins": live_info.get("delay_mins", 0),
                        "current_location": live_info.get("current_location", "--"),
                        "next_station": live_info.get("next_station", "--"),
                        "last_updated_time": live_info.get("last_updated_time", "Timetable Schedule"),
                        "raw_dep": sm.get("raw_dep", "00:00")
                    }
        except Exception:
            pass

        # --- 3. Live RailRadar station trains API fallback if schedule database had 0 matches ---
        if len(matched_trains_dict) == 0:
            try:
                for fc in from_codes[:2]:
                    for tc in to_codes[:2]:
                        from_trains = self.get_station_trains(fc)
                        to_trains = self.get_station_trains(tc)
                        if not from_trains or not to_trains:
                            continue
                        from_map = {t["train"]["number"]: t for t in from_trains if "train" in t and "number" in t["train"]}
                        to_map = {t["train"]["number"]: t for t in to_trains if "train" in t and "number" in t["train"]}
                        common_numbers = set(from_map.keys()) & set(to_map.keys())
                        for tno in common_numbers:
                            str_tno = str(tno)
                            if str_tno not in matched_trains_dict:
                                f_item = from_map[tno]
                                t_item = to_map[tno]
                                f_stop = f_item.get("stop", {})
                                t_stop = t_item.get("stop", {})
                                f_seq = f_stop.get("sequence", 0)
                                t_seq = t_stop.get("sequence", 0)
                                f_dist = float(f_stop.get("distance") or 0)
                                t_dist = float(t_stop.get("distance") or 0)

                                if (f_seq > 0 and t_seq > 0 and f_seq < t_seq) or (f_dist > 0 and t_dist > 0 and f_dist < t_dist) or (f_stop.get("stopType") == "origin"):
                                    t_info = f_item.get("train", {})
                                    t_name = t_info.get("name") or f"Train {tno}"
                                    t_type = t_info.get("type") or "Express"
                                    raw_dep = f_stop.get("departure") or f_stop.get("arrival") or "00:00"
                                    raw_arr = t_stop.get("arrival") or t_stop.get("departure") or "00:00"
                                    dep_time = self.format_iso_or_time(raw_dep)
                                    arr_time = self.format_iso_or_time(raw_arr)
                                    duration_str = self.calculate_duration(raw_dep, raw_arr, f_seq, t_seq)
                                    live_info = self.get_train_live_summary(str_tno, dep_time, arr_time)

                                    origin_info = t_info.get("source", {})
                                    dest_info = t_info.get("destination", {})

                                    matched_trains_dict[str_tno] = {
                                        "train_number": str_tno,
                                        "train_name": t_name,
                                        "train_type": t_type,
                                        "origin_station": {"code": origin_info.get("code", fc), "name": origin_info.get("name", fc)},
                                        "destination_station": {"code": dest_info.get("code", tc), "name": dest_info.get("name", tc)},
                                        "from_station_code": fc,
                                        "from_station_name": self.get_station_name_by_code(fc),
                                        "to_station_code": tc,
                                        "to_station_name": self.get_station_name_by_code(tc),
                                        "departure_time": dep_time,
                                        "arrival_time": arr_time,
                                        "duration": duration_str,
                                        "run_days": t_info.get("runDays", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
                                        "current_status": live_info["status_text"],
                                        "current_status_code": live_info["status_code"],
                                        "status_category": live_info["category"],
                                        "delay_mins": live_info["delay_mins"],
                                        "current_location": live_info["current_location"],
                                        "next_station": live_info["next_station"],
                                        "last_updated_time": live_info["last_updated_time"],
                                        "raw_dep": raw_dep
                                    }
            except Exception:
                pass

        final_trains = list(matched_trains_dict.values())
        final_trains.sort(key=lambda x: x.get("raw_dep", "99:99"))

        # Remove temporary raw_dep key before returning
        for t in final_trains:
            t.pop("raw_dep", None)

        from_display_code = from_codes[0] if len(from_codes) == 1 else from_codes[0]
        to_display_code = to_codes[0] if len(to_codes) == 1 else to_codes[0]

        return {
            "from_station": {"code": from_display_code, "name": from_name},
            "to_station": {"code": to_display_code, "name": to_name},
            "total_trains": len(final_trains),
            "trains": final_trains
        }

    def search_trains(self, query: str, limit: int = 10) -> list:
        """
        Universal, high-speed indexed search across all Indian Railways trains.
        Supports train number, full name, partial name, keywords, and origin-destination routes.
        """
        q = (query or "").strip().lower()
        if not q:
            return []

        self._ensure_schedule_db_loaded()

        raw_query_words = [w for w in re.findall(r'[a-zA-Z0-9]+', q) if w]
        if not raw_query_words:
            return []

        # Keyword and abbreviation synonym expansion
        keyword_map = {
            "august": {"august", "aug", "ag"},
            "kranti": {"kranti", "kr"},
            "rajdhani": {"rajdhani", "raj", "rjdhn"},
            "shatabdi": {"shatabdi", "shtbdi"},
            "vande": {"vande", "vb"},
            "bharat": {"bharat", "bhrt", "vb"},
            "tejas": {"tejas", "tjs"},
            "gitanjali": {"gitanjali", "geetanjali", "gtj"},
            "express": {"express", "exp", "ex"},
            "superfast": {"superfast", "sf", "sfg", "sup"},
            "special": {"special", "spl", "hspl"},
            "mail": {"mail", "ml"},
            "passenger": {"passenger", "pass"},
            "central": {"central", "cntl", "cntrl", "ctrl", "c"},
            "mumbai": {"mumbai", "mmct", "csmt", "cstm", "bdts", "bvi", "ltt", "dr", "bombay"},
            "delhi": {"delhi", "ndls", "nzm", "dli", "anvt", "dec", "dee"},
            "howrah": {"howrah", "hwh"},
            "kolkata": {"kolkata", "hwh", "sdah", "koaa"},
            "varanasi": {"varanasi", "bsb", "ddu", "bsbs", "banaras"},
            "bhopal": {"bhopal", "rkmp", "bpl", "habibganj"},
            "chennai": {"chennai", "mas", "ms", "madras"},
            "bangalore": {"bangalore", "bengaluru", "sbc", "smvb", "ypr"},
            "ahmedabad": {"ahmedabad", "adi"},
            "pune": {"pune"},
            "surat": {"surat", "st"},
            "vadodara": {"vadodara", "brc", "baroda"},
            "kota": {"kota"},
            "ratlam": {"ratlam", "rtm"},
            "jaipur": {"jaipur", "jp"},
            "nagpur": {"nagpur", "ngp"},
            "amritsar": {"amritsar", "asr"},
            "secunderabad": {"secunderabad", "sc"},
            "hyderabad": {"hyderabad", "hyb"},
            "bhusawal": {"bhusawal", "bsl"},
            "lucknow": {"lucknow", "lko", "ljn"},
            "kanpur": {"kanpur", "cnb"},
            "patna": {"patna", "pnbe", "ppta"},
        }

        results = []
        seen = set()

        for tno, info in self._train_names_db.items():
            if tno.startswith("0") and len(tno) == 5:
                continue
            if tno in seen:
                continue

            tname = info.get("name", "")
            ttype = info.get("type", "Express")
            route = self._schedule_routes.get(tno, [])
            src_code = route[0]["station_code"] if route else ""
            dest_code = route[-1]["station_code"] if route else ""
            src_name = self.get_station_name_by_code(src_code) if src_code else ""
            dest_name = self.get_station_name_by_code(dest_code) if dest_code else ""

            # Standard clean display names
            if tno == "12951":
                display_name = "Mumbai–New Delhi Tejas Rajdhani Express"
            elif tno == "12952":
                display_name = "New Delhi–Mumbai Tejas Rajdhani Express"
            elif tno in ("12953", "12954"):
                display_name = "August Kranti Rajdhani Express"
            elif tno == "12860":
                display_name = "Howrah–Mumbai CSMT Gitanjali Express"
            elif tno == "12859":
                display_name = "Mumbai CSMT–Howrah Gitanjali Express"
            elif tno == "22436":
                display_name = "New Delhi–Varanasi Vande Bharat Express"
            elif tno == "22435":
                display_name = "Varanasi–New Delhi Vande Bharat Express"
            elif tno == "12002":
                display_name = "New Delhi–Rani Kamlapati Bhopal Shatabdi Express"
            elif tno == "12001":
                display_name = "Rani Kamlapati–New Delhi Bhopal Shatabdi Express"
            elif tname.endswith(" Exp"):
                display_name = tname[:-4] + " Express"
            elif tname.endswith(" Ex"):
                display_name = tname[:-3] + " Express"
            elif tname.endswith(" Shtbdi"):
                display_name = tname[:-7] + " Shatabdi Express"
            elif tname.endswith(" Rjdhn"):
                display_name = tname[:-6] + " Rajdhani Express"
            elif tname.endswith(" Pass"):
                display_name = tname[:-5] + " Passenger"
            elif tname.endswith(" Spl"):
                display_name = tname[:-4] + " Special"
            else:
                display_name = tname

            tno_lower = tno.lower()
            name_words = set(re.findall(r'[a-zA-Z0-9]+', f"{tname} {display_name}".lower()))
            route_words = set(re.findall(r'[a-zA-Z0-9]+', f"{src_code} {src_name} {dest_code} {dest_name} {ttype}".lower()))
            all_words = name_words | route_words

            score = 0

            # 1. Exact Train No Match
            if q == tno_lower:
                score += 1000
            # 2. Prefix Train No Match (e.g. '129' -> '12951')
            elif tno_lower.startswith(q) and q.isdigit():
                score += 700 - len(tno) * 10
            # 3. Exact full name match
            elif q == display_name.lower() or q == tname.lower():
                score += 600
            # 4. Display name starts with query
            elif display_name.lower().startswith(q) or tname.lower().startswith(q):
                score += 450
            # 5. Query substring in display name or raw name
            elif q in display_name.lower() or q in tname.lower():
                score += 350
            else:
                # 6. Multi-word concept matching
                matched_concepts = 0
                for qw in raw_query_words:
                    if qw in all_words:
                        matched_concepts += 1
                    elif any(w.startswith(qw) for w in all_words):
                        matched_concepts += 1
                    elif qw in keyword_map:
                        synonyms = keyword_map[qw]
                        if any(syn in all_words or any(w.startswith(syn) for w in all_words) for syn in synonyms):
                            matched_concepts += 1

                if matched_concepts == len(raw_query_words):
                    name_matches = sum(1 for qw in raw_query_words if (qw in name_words or any(syn in name_words for syn in keyword_map.get(qw, []))))
                    score += 250 + (name_matches * 50)

            if score > 0:
                seen.add(tno)
                results.append({
                    "score": score,
                    "train_number": tno,
                    "train_name": display_name,
                    "type": ttype,
                    "source": f"{src_name} ({src_code})" if src_code else "",
                    "destination": f"{dest_name} ({dest_code})" if dest_code else "",
                    "source_code": src_code,
                    "destination_code": dest_code,
                    "display_label": f"{tno} — {display_name}"
                })

        results.sort(key=lambda x: (-x["score"], x["train_number"]))
        return results[:limit]

CITY_TERMINALS_MAP = {
    # Mumbai Metropolitan Area
    "mumbai": ["MMCT", "CSMT", "LTT", "BDTS", "BVI", "DR", "KYN", "TNA", "DDR", "PNVL"],
    "bombay": ["MMCT", "CSMT", "LTT", "BDTS", "BVI", "DR", "KYN", "TNA", "DDR", "PNVL"],
    "mumbai central": ["MMCT", "BVI"],
    "mumbai csmt": ["CSMT", "DR", "KYN", "TNA"],
    "csmt": ["CSMT", "DR", "KYN", "TNA"],
    "cstm": ["CSMT", "DR", "KYN", "TNA"],
    "lokmanya tilak": ["LTT", "TNA", "KYN"],
    "ltt": ["LTT", "TNA", "KYN"],
    "bandra": ["BDTS", "BVI"],
    "bandra terminus": ["BDTS", "BVI"],
    "bdts": ["BDTS", "BVI"],
    "borivali": ["BVI"],
    "bvi": ["BVI"],
    "dadar": ["DR", "DDR"],
    "dr": ["DR", "DDR"],
    "kalyan": ["KYN"],
    "kyn": ["KYN"],
    "thane": ["TNA"],
    "tna": ["TNA"],
    "panvel": ["PNVL"],
    "pnvl": ["PNVL"],

    # Delhi NCR
    "delhi": ["NDLS", "NZM", "DLI", "ANVT", "DEC", "DEE", "DSA", "GZB"],
    "new delhi": ["NDLS", "NZM", "DLI", "ANVT", "DEC", "DEE"],
    "ndls": ["NDLS"],
    "hazrat nizamuddin": ["NZM"],
    "nizamuddin": ["NZM"],
    "nzm": ["NZM"],
    "old delhi": ["DLI"],
    "delhi jn": ["DLI"],
    "dli": ["DLI"],
    "anand vihar": ["ANVT"],
    "anand vihar terminal": ["ANVT"],
    "anvt": ["ANVT"],
    "delhi sarai rohilla": ["DEE"],
    "dee": ["DEE"],
    "delhi cantt": ["DEC"],
    "dec": ["DEC"],
    "ghaziabad": ["GZB"],
    "gzb": ["GZB"],

    # Pune
    "pune": ["PUNE", "SVJR", "CCH", "HDP"],
    "pune jn": ["PUNE", "SVJR", "CCH", "HDP"],
    "pune junction": ["PUNE", "SVJR", "CCH", "HDP"],
    "shivajinagar": ["SVJR"],
    "hadapsar": ["HDP"],
    "chinchwad": ["CCH"],

    # Jaipur
    "jaipur": ["JP", "GADJ", "DPA"],
    "jaipur jn": ["JP", "GADJ", "DPA"],
    "jp": ["JP", "GADJ", "DPA"],
    "gandhinagar jaipur": ["GADJ"],
    "durgapura": ["DPA"],

    # Bhusawal / Jalgaon Hub
    "bhusawal": ["BSL", "JL"],
    "bhusawal jn": ["BSL", "JL"],
    "bhusawal junction": ["BSL", "JL"],
    "bhusaval": ["BSL", "JL"],
    "bsl": ["BSL"],
    "jalgaon": ["JL"],
    "jalgaon jn": ["JL"],
    "jl": ["JL"],

    # Kolkata / Howrah
    "kolkata": ["HWH", "SDAH", "KOAA", "SHM", "SRC"],
    "howrah": ["HWH", "SHM", "SRC"],
    "howrah jn": ["HWH", "SHM", "SRC"],
    "hwh": ["HWH"],
    "sealdah": ["SDAH"],
    "sdah": ["SDAH"],
    "kolkata terminal": ["KOAA"],
    "koaa": ["KOAA"],
    "shalimar": ["SHM"],
    "santragachi": ["SRC"],

    # Chennai
    "chennai": ["MAS", "MS", "TBM", "PER"],
    "madras": ["MAS", "MS", "TBM", "PER"],
    "chennai central": ["MAS", "PER"],
    "mas": ["MAS"],
    "chennai egmore": ["MS", "TBM"],
    "ms": ["MS"],
    "tambaram": ["TBM"],
    "perambur": ["PER"],

    # Bengaluru
    "bangalore": ["SBC", "YPR", "SMVB", "BNC", "KJM"],
    "bengaluru": ["SBC", "YPR", "SMVB", "BNC", "KJM"],
    "ksr bengaluru": ["SBC", "BNC"],
    "sbc": ["SBC"],
    "yesvantpur": ["YPR"],
    "ypr": ["YPR"],
    "smvt bengaluru": ["SMVB"],
    "smvb": ["SMVB"],
    "krishnarajapuram": ["KJM"],
    "kjm": ["KJM"],

    # Hyderabad / Secunderabad
    "hyderabad": ["SC", "HYB", "KCG"],
    "secunderabad": ["SC", "HYB", "KCG"],
    "sc": ["SC"],
    "hyderabad deccan": ["HYB"],
    "hyb": ["HYB"],
    "kacheguda": ["KCG"],
    "kcg": ["KCG"],

    # Ahmedabad
    "ahmedabad": ["ADI", "SBT", "CLDY", "MAN"],
    "ahmedabad jn": ["ADI", "SBT", "CLDY", "MAN"],
    "adi": ["ADI"],
    "sabarmati": ["SBT"],
    "chandlodiya": ["CLDY"],
    "maninagar": ["MAN"],

    # Surat
    "surat": ["ST", "UDN"],
    "st": ["ST"],
    "udhna": ["UDN"],
    "udn": ["UDN"],

    # Vadodara
    "vadodara": ["BRC", "MYG"],
    "vadodara jn": ["BRC", "MYG"],
    "baroda": ["BRC", "MYG"],
    "brc": ["BRC"],

    # Bhopal
    "bhopal": ["BPL", "RKMP"],
    "bhopal jn": ["BPL", "RKMP"],
    "bpl": ["BPL"],
    "rani kamlapati": ["RKMP"],
    "rkmp": ["RKMP"],
    "habibganj": ["RKMP"],

    # Kanpur
    "kanpur": ["CNB", "CPA"],
    "kanpur central": ["CNB", "CPA"],
    "cnb": ["CNB"],

    # Patna
    "patna": ["PNBE", "PPTA", "DNR", "RJPB"],
    "patna jn": ["PNBE", "PPTA", "DNR", "RJPB"],
    "pnbe": ["PNBE"],
    "patliputra": ["PPTA"],
    "danapur": ["DNR"],
    "rajendra nagar": ["RJPB"],

    # Varanasi
    "varanasi": ["BSB", "DDU", "BCY", "BSBS"],
    "varanasi jn": ["BSB", "DDU", "BCY", "BSBS"],
    "bsb": ["BSB"],
    "pt deen dayal upadhyaya": ["DDU"],
    "ddu": ["DDU"],
    "mughalsarai": ["DDU"],
    "banaras": ["BSBS"],

    # Nagpur
    "nagpur": ["NGP", "AJNI"],
    "nagpur jn": ["NGP", "AJNI"],
    "ngp": ["NGP"],
    "ajni": ["AJNI"],

    # Amritsar
    "amritsar": ["ASR"],
    "asr": ["ASR"],

    # Guwahati
    "guwahati": ["GHY", "KYQ"],
    "ghy": ["GHY"],
    "kamakhya": ["KYQ"],

    # Gorakhpur
    "gorakhpur": ["GKP"],
    "gkp": ["GKP"],

    # Agra
    "agra": ["AGC", "AF", "IDH"],
    "agra cantt": ["AGC"],
    "agc": ["AGC"],
    "agra fort": ["AF"],

    # Lucknow
    "lucknow": ["LKO", "LJN"],
    "lucknow nr": ["LKO"],
    "lko": ["LKO"],
    "lucknow ner": ["LJN"],
    "ljn": ["LJN"],

    # Chandigarh
    "chandigarh": ["CDG"],
    "cdg": ["CDG"],

    # Gwalior
    "gwalior": ["GWL"],
    "gwl": ["GWL"],

    # Jabalpur
    "jabalpur": ["JBP"],
    "jbp": ["JBP"],

    # Prayagraj
    "prayagraj": ["PRYJ", "ALD", "ACOI", "NYN", "PRG", "PYGS"],
    "allahabad": ["PRYJ", "ALD", "ACOI", "NYN", "PRG", "PYGS"],
    "pryj": ["PRYJ"],

    # Indore
    "indore": ["INDB", "LMNR"],
    "indb": ["INDB"],

    # Kota
    "kota": ["KOTA", "DKNT"],
    "kota jn": ["KOTA"],
    "dakaniya talav": ["DKNT"],

    # Ratlam
    "ratlam": ["RTM"],
    "rtm": ["RTM"],

    # Nashik
    "nashik": ["NK"],
    "nashik road": ["NK"],
    "nk": ["NK"],

    # Manmad
    "manmad": ["MMR"],
    "mmr": ["MMR"],

    # Akola
    "akola": ["AK"],
    "ak": ["AK"],

    # Badnera
    "badnera": ["BD"],
    "bd": ["BD"],

    # Wardha
    "wardha": ["WR"],
    "wr": ["WR"],

    # Solapur
    "solapur": ["SUR"],
    "sur": ["SUR"],

    # Daund
    "daund": ["DD"],
    "dd": ["DD"],

    # Igatpuri
    "igatpuri": ["IGP"],
    "igp": ["IGP"]
}

MAJOR_STATION_MAP = {
    "mumbai central": ("MMCT", "Mumbai Central"),
    "mumbai": ("MMCT", "Mumbai Central"),
    "mmct": ("MMCT", "Mumbai Central"),
    "new delhi": ("NDLS", "New Delhi"),
    "delhi": ("NDLS", "New Delhi"),
    "ndls": ("NDLS", "New Delhi"),
    "surat": ("ST", "Surat"),
    "st": ("ST", "Surat"),
    "vadodara": ("BRC", "Vadodara Jn"),
    "vadodara jn": ("BRC", "Vadodara Jn"),
    "baroda": ("BRC", "Vadodara Jn"),
    "brc": ("BRC", "Vadodara Jn"),
    "kota": ("KOTA", "Kota Jn"),
    "kota jn": ("KOTA", "Kota Jn"),
    "ratlam": ("RTM", "Ratlam Jn"),
    "ratlam jn": ("RTM", "Ratlam Jn"),
    "borivali": ("BVI", "Borivali"),
    "bvi": ("BVI", "Borivali"),
    "csmt": ("CSMT", "Mumbai CSMT"),
    "mumbai csmt": ("CSMT", "Mumbai CSMT"),
    "howrah": ("HWH", "Howrah Jn"),
    "howrah jn": ("HWH", "Howrah Jn"),
    "kolkata": ("HWH", "Howrah Jn"),
    "hwh": ("HWH", "Howrah Jn"),
    "pune": ("PUNE", "Pune Jn"),
    "pune jn": ("PUNE", "Pune Jn"),
    "bhopal": ("RKMP", "Rani Kamlapati (Bhopal)"),
    "rani kamlapati": ("RKMP", "Rani Kamlapati"),
    "rkmp": ("RKMP", "Rani Kamlapati"),
    "bpl": ("BPL", "Bhopal Jn"),
    "hazrat nizamuddin": ("NZM", "Hazrat Nizamuddin"),
    "nizamuddin": ("NZM", "Hazrat Nizamuddin"),
    "nzm": ("NZM", "Hazrat Nizamuddin"),
    "ahmedabad": ("ADI", "Ahmedabad Jn"),
    "ahmedabad jn": ("ADI", "Ahmedabad Jn"),
    "adi": ("ADI", "Ahmedabad Jn"),
    "chennai": ("MAS", "Chennai Central"),
    "chennai central": ("MAS", "Chennai Central"),
    "mas": ("MAS", "Chennai Central"),
    "bangalore": ("SBC", "KSR Bengaluru"),
    "bengaluru": ("SBC", "KSR Bengaluru"),
    "ksr bengaluru": ("SBC", "KSR Bengaluru"),
    "sbc": ("SBC", "KSR Bengaluru"),
    "kanpur": ("CNB", "Kanpur Central"),
    "kanpur central": ("CNB", "Kanpur Central"),
    "cnb": ("CNB", "Kanpur Central"),
    "patna": ("PNBE", "Patna Jn"),
    "patna jn": ("PNBE", "Patna Jn"),
    "pnbe": ("PNBE", "Patna Jn"),
    "varanasi": ("BSB", "Varanasi Jn"),
    "varanasi jn": ("BSB", "Varanasi Jn"),
    "bsb": ("BSB", "Varanasi Jn"),
    "gorakhpur": ("GKP", "Gorakhpur Jn"),
    "gkp": ("GKP", "Gorakhpur Jn"),
    "nagpur": ("NGP", "Nagpur Jn"),
    "ngp": ("NGP", "Nagpur Jn"),
    "jaipur": ("JP", "Jaipur Jn"),
    "jp": ("JP", "Jaipur Jn"),
    "amritsar": ("ASR", "Amritsar Jn"),
    "asr": ("ASR", "Amritsar Jn"),
    "secunderabad": ("SC", "Secunderabad Jn"),
    "sc": ("SC", "Secunderabad Jn"),
    "hyderabad": ("HYB", "Hyderabad Deccan"),
    "hyb": ("HYB", "Hyderabad Deccan"),
    "guwahati": ("GHY", "Guwahati"),
    "ghy": ("GHY", "Guwahati"),
    "bhusawal": ("BSL", "Bhusawal Jn"),
    "bsl": ("BSL", "Bhusawal Jn")
}

railradar_service = RailRadarService()

