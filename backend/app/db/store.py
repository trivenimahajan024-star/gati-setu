import copy
import threading
import random
from app.engine.eta_engine import eta_engine

INITIAL_TRAINS = {
    "12951": {
        "train_number": "12951",
        "train_name": "Mumbai - New Delhi Tejas Rajdhani Express",
        "short_name": "NDLS Tejas Rajdhani",
        "train_type": "Tejas Rajdhani Express",
        "source": "Mumbai Central (MMCT)",
        "source_code": "MMCT",
        "destination": "New Delhi (NDLS)",
        "destination_code": "NDLS",
        "zone": "Western Railway (WR)",
        "total_distance_km": 1386,
        "distance_covered_km": 326.1,
        "distance_remaining_km": 1059.9,
        "avg_speed_kmh": 88,
        "current_status": "Train is running",
        "current_status_code": "RUNNING",
        "current_location": "Passing Bharuch Jn (Between Surat & Vadodara)",
        "current_section": "Surat - Vadodara Quadruple Track Section (WR)",
        "current_coordinates": [21.7051, 72.9959],
        "heading_deg": 18,
        "current_speed_kmh": 114,
        "max_permissible_speed": 130,
        "current_delay_mins": 14,
        "destination_delay_impact_mins": 11,
        "delay_impact_explanation": "Simulated forecast indicates a 3-minute recovery between Vadodara and Kota due to high-speed track clearance.",
        "confidence_level": "High",
        "confidence_pct": 94,
        "arrival_window": "08:41 AM – 08:51 AM",
        "scheduled_destination_eta": "08:32 AM",
        "predicted_destination_eta": "08:46 AM",
        "last_updated": "Simulated 1 min ago",
        "last_updated_time": "18:42:10 IST",
        "journey_progress_pct": 23.5,
        "active_events": [],
        "next_station": {
            "code": "BRC",
            "name": "Vadodara Jn",
            "distance_km": 66,
            "expected_eta": "09:41 PM",
            "scheduled_eta": "09:27 PM",
            "platform": "2",
            "stoppage_time": "10 min"
        },
        "eta_factors": [
            {
                "id": "downstream_congestion",
                "code": "F06",
                "name": "Downstream Track Congestion",
                "category": "Traffic Density",
                "is_active": True,
                "impact_level": "High impact",
                "delay_impact_mins": 8,
                "passenger_explanation": "High track density near Vadodara Junction is causing cautionary signal aspects for incoming express trains.",
                "technical_detail": "Platform 2 line occupancy delay of 6 mins due to late departure of 19015 Saurashtra Express."
            },
            {
                "id": "speed_restrictions",
                "code": "F07",
                "name": "Temporary Speed Restriction (TSR)",
                "category": "Track Infrastructure",
                "is_active": True,
                "impact_level": "Moderate impact",
                "delay_impact_mins": 4,
                "passenger_explanation": "Track renewal maintenance near Vapi has a temporary speed limit of 45 km/h for a 3 km section.",
                "technical_detail": "TSR 45 km/h between km 168/2 to 171/8 due to sleeper replacement."
            },
            {
                "id": "preceding_train_delays",
                "code": "F09",
                "name": "Preceding-Train Delays",
                "category": "Traffic Density",
                "is_active": True,
                "impact_level": "Moderate impact",
                "delay_impact_mins": 2,
                "passenger_explanation": "A container freight train ahead is clearing the block section, temporarily limiting cruising speed.",
                "technical_detail": "Headway reduced to 4.2 km; automatic signaling keeping distance buffer."
            }
        ],
        "stations": [
            {
                "code": "MMCT",
                "name": "Mumbai Central",
                "scheduled_arr": "START",
                "scheduled_dep": "05:00 PM",
                "predicted_arr": "START",
                "predicted_dep": "05:00 PM",
                "platform": "1",
                "delay_mins": 0,
                "halt_mins": 0,
                "distance_km": 0,
                "status": "departed",
                "delay_attribution": "Departed on-time from source",
                "coordinates": [18.9696, 72.8193]
            },
            {
                "code": "BVI",
                "name": "Borivali",
                "scheduled_arr": "05:30 PM",
                "scheduled_dep": "05:33 PM",
                "predicted_arr": "05:30 PM",
                "predicted_dep": "05:33 PM",
                "platform": "6",
                "delay_mins": 0,
                "halt_mins": 3,
                "distance_km": 30,
                "status": "departed",
                "delay_attribution": "Clear track section with normal headway",
                "coordinates": [19.2290, 72.8574]
            },
            {
                "code": "ST",
                "name": "Surat",
                "scheduled_arr": "07:54 PM",
                "scheduled_dep": "07:59 PM",
                "predicted_arr": "08:02 PM",
                "predicted_dep": "08:07 PM",
                "platform": "1",
                "delay_mins": 8,
                "halt_mins": 5,
                "distance_km": 263,
                "status": "departed",
                "delay_attribution": "Speed restriction near Vapi (TSR 45 km/h)",
                "coordinates": [21.2052, 72.8409]
            },
            {
                "code": "BRC",
                "name": "Vadodara Jn",
                "scheduled_arr": "09:27 PM",
                "scheduled_dep": "09:37 PM",
                "predicted_arr": "09:41 PM",
                "predicted_dep": "09:51 PM",
                "platform": "2",
                "delay_mins": 14,
                "halt_mins": 10,
                "distance_km": 392,
                "status": "approaching",
                "delay_attribution": "Preceding freight train clearance & junction congestion",
                "coordinates": [22.3107, 73.1812]
            },
            {
                "code": "RTM",
                "name": "Ratlam Jn",
                "scheduled_arr": "01:05 AM",
                "scheduled_dep": "01:10 AM",
                "predicted_arr": "01:16 AM",
                "predicted_dep": "01:21 AM",
                "platform": "4",
                "delay_mins": 11,
                "halt_mins": 5,
                "distance_km": 653,
                "status": "upcoming",
                "delay_attribution": "Buffer recovery model predicts +3 min time saved",
                "coordinates": [23.3441, 75.0366]
            },
            {
                "code": "KOTA",
                "name": "Kota Jn",
                "scheduled_arr": "04:10 AM",
                "scheduled_dep": "04:15 AM",
                "predicted_arr": "04:18 AM",
                "predicted_dep": "04:23 AM",
                "platform": "1",
                "delay_mins": 8,
                "halt_mins": 5,
                "distance_km": 920,
                "status": "upcoming",
                "delay_attribution": "High speed 130 km/h corridor clearance",
                "coordinates": [25.2138, 75.8648]
            },
            {
                "code": "NDLS",
                "name": "New Delhi",
                "scheduled_arr": "08:32 AM",
                "scheduled_dep": "DEST",
                "predicted_arr": "08:46 AM",
                "predicted_dep": "DEST",
                "platform": "1",
                "delay_mins": 14,
                "halt_mins": 0,
                "distance_km": 1386,
                "status": "upcoming",
                "delay_attribution": "Final arrival with dynamic sectional buffers factored in",
                "coordinates": [28.6139, 77.2090]
            }
        ],
        "passenger_alerts": [
            {
                "id": "alt_1",
                "severity": "attention",
                "title": "Dynamic ETA Shift (+14 min)",
                "message": "Expected arrival at Vadodara Jn adjusted to 09:41 PM due to caution signals between Bharuch and Vadodara.",
                "time": "5m ago",
                "icon": "fa-clock"
            },
            {
                "id": "alt_2",
                "severity": "info",
                "title": "TSR Speed Restriction Near Vapi",
                "message": "Temporary Speed Restriction of 45 km/h safely cleared by train telemetry.",
                "time": "22m ago",
                "icon": "fa-gauge-simple"
            }
        ],
        "route_polyline": [
            [18.9696, 72.8193], [19.2290, 72.8574], [19.5760, 72.7660], [20.3700, 72.9100],
            [20.9500, 72.9300], [21.1702, 72.8311], [21.7051, 72.9959], [22.3072, 73.1812],
            [22.8200, 73.6100], [22.8330, 74.2560], [23.3341, 75.0376], [23.4544, 75.4147],
            [24.1800, 75.8300], [24.5300, 75.9800], [25.1825, 75.8340], [25.9928, 76.3688],
            [26.4900, 76.7300], [26.9800, 77.0100], [27.1800, 77.4900], [27.4924, 77.6737],
            [28.1400, 77.3300], [28.4089, 77.3178], [28.5880, 77.2530], [28.6139, 77.2090]
        ]
    },

    "12860": {
        "train_number": "12860",
        "train_name": "Howrah - Mumbai CSMT Gitanjali Express",
        "short_name": "Gitanjali Express",
        "train_type": "Superfast Express",
        "source": "Howrah Jn (HWH)",
        "source_code": "HWH",
        "destination": "Mumbai CSMT (CSMT)",
        "destination_code": "CSMT",
        "zone": "South Eastern Railway (SER)",
        "total_distance_km": 1968,
        "distance_covered_km": 1420,
        "distance_remaining_km": 548,
        "avg_speed_kmh": 68,
        "current_status": "Train is running",
        "current_status_code": "RUNNING",
        "current_location": "Between Bhusaval & Nashik Road (Passing Manmad Jn)",
        "current_section": "Bhusaval - Manmad Double Electric Line (CR)",
        "current_coordinates": [20.2524, 74.4388],
        "heading_deg": 245,
        "current_speed_kmh": 96,
        "max_permissible_speed": 110,
        "current_delay_mins": 22,
        "destination_delay_impact_mins": 26,
        "delay_impact_explanation": "Suburban EMU traffic density near Kalyan Jn is projected to add 4 minutes to final destination arrival.",
        "confidence_level": "High",
        "confidence_pct": 91,
        "arrival_window": "09:30 PM – 09:44 PM",
        "scheduled_destination_eta": "09:20 PM",
        "predicted_destination_eta": "09:42 PM",
        "last_updated": "Simulated 2 min ago",
        "last_updated_time": "18:41:40 IST",
        "journey_progress_pct": 72,
        "active_events": [],
        "next_station": {
            "code": "NK",
            "name": "Nashik Road",
            "distance_km": 74,
            "expected_eta": "04:32 PM",
            "scheduled_eta": "04:10 PM",
            "platform": "3",
            "stoppage_time": "5 min"
        },
        "eta_factors": [
            {
                "id": "signal_aspects",
                "code": "F02",
                "name": "Signal Aspects & Block Halts",
                "category": "Signaling & Interlocking",
                "is_active": True,
                "impact_level": "High impact",
                "delay_impact_mins": 12,
                "passenger_explanation": "Held at outer home signal of Manmad Junction for platform cross-movement.",
                "technical_detail": "Signal clearance held for crossing of 12138 Punjab Mail."
            },
            {
                "id": "weather_conditions",
                "code": "F04",
                "name": "Weather & Track Conditions",
                "category": "Environmental",
                "is_active": True,
                "impact_level": "Moderate impact",
                "delay_impact_mins": 6,
                "passenger_explanation": "Heavy rain across the Kasara Ghats section requires regulated speed operations.",
                "technical_detail": "Monsoon precaution speed regulation in Igatpuri-Kasara 1:37 gradient ghats."
            }
        ],
        "stations": [
            {
                "code": "HWH",
                "name": "Howrah Jn",
                "scheduled_arr": "START",
                "scheduled_dep": "01:50 PM",
                "predicted_arr": "START",
                "predicted_dep": "01:50 PM",
                "platform": "21",
                "delay_mins": 0,
                "halt_mins": 0,
                "distance_km": 0,
                "status": "departed",
                "delay_attribution": "Departed on-time",
                "coordinates": [22.5839, 88.3426]
            },
            {
                "code": "TATA",
                "name": "Tatanagar Jn",
                "scheduled_arr": "05:15 PM",
                "scheduled_dep": "05:20 PM",
                "predicted_arr": "05:15 PM",
                "predicted_dep": "05:20 PM",
                "platform": "3",
                "delay_mins": 0,
                "halt_mins": 5,
                "distance_km": 250,
                "status": "departed",
                "delay_attribution": "On-time departure",
                "coordinates": [22.7667, 86.2000]
            },
            {
                "code": "ROU",
                "name": "Rourkela Jn",
                "scheduled_arr": "07:30 PM",
                "scheduled_dep": "07:38 PM",
                "predicted_arr": "07:32 PM",
                "predicted_dep": "07:40 PM",
                "platform": "1",
                "delay_mins": 2,
                "halt_mins": 8,
                "distance_km": 413,
                "status": "departed",
                "delay_attribution": "Minor signal headway",
                "coordinates": [22.2253, 84.8536]
            },
            {
                "code": "BSP",
                "name": "Bilaspur Jn",
                "scheduled_arr": "11:55 PM",
                "scheduled_dep": "12:10 AM",
                "predicted_arr": "12:00 AM",
                "predicted_dep": "12:15 AM",
                "platform": "4",
                "delay_mins": 5,
                "halt_mins": 15,
                "distance_km": 718,
                "status": "departed",
                "delay_attribution": "Crew change completed",
                "coordinates": [22.0797, 82.1409]
            },
            {
                "code": "R",
                "name": "Raipur Jn",
                "scheduled_arr": "01:45 AM",
                "scheduled_dep": "01:50 AM",
                "predicted_arr": "01:52 AM",
                "predicted_dep": "01:57 AM",
                "platform": "1",
                "delay_mins": 7,
                "halt_mins": 5,
                "distance_km": 829,
                "status": "departed",
                "delay_attribution": "Clear route progression",
                "coordinates": [21.2514, 81.6296]
            },
            {
                "code": "NGP",
                "name": "Nagpur Jn",
                "scheduled_arr": "07:40 AM",
                "scheduled_dep": "07:45 AM",
                "predicted_arr": "07:48 AM",
                "predicted_dep": "07:53 AM",
                "platform": "3",
                "delay_mins": 8,
                "halt_mins": 5,
                "distance_km": 1131,
                "status": "departed",
                "delay_attribution": "Minor sectional crossing",
                "coordinates": [21.1528, 79.0882]
            },
            {
                "code": "BSL",
                "name": "Bhusaval Jn",
                "scheduled_arr": "01:10 PM",
                "scheduled_dep": "01:15 PM",
                "predicted_arr": "01:25 PM",
                "predicted_dep": "01:30 PM",
                "platform": "1",
                "delay_mins": 15,
                "halt_mins": 5,
                "distance_km": 1524,
                "status": "departed",
                "delay_attribution": "Platform track maintenance",
                "coordinates": [21.0455, 75.7885]
            },
            {
                "code": "JL",
                "name": "Jalgaon Jn",
                "scheduled_arr": "01:43 PM",
                "scheduled_dep": "01:45 PM",
                "predicted_arr": "02:00 PM",
                "predicted_dep": "02:02 PM",
                "platform": "2",
                "delay_mins": 17,
                "halt_mins": 2,
                "distance_km": 1548,
                "status": "departed",
                "delay_attribution": "Departed after junction clearance",
                "coordinates": [21.0077, 75.5626]
            },
            {
                "code": "NK",
                "name": "Nashik Road",
                "scheduled_arr": "04:10 PM",
                "scheduled_dep": "04:15 PM",
                "predicted_arr": "04:32 PM",
                "predicted_dep": "04:37 PM",
                "platform": "3",
                "delay_mins": 22,
                "halt_mins": 5,
                "distance_km": 1781,
                "status": "approaching",
                "delay_attribution": "Manmad outer signal hold & Ghat weather precautions",
                "coordinates": [19.9575, 73.8340]
            },
            {
                "code": "KYN",
                "name": "Kalyan Jn",
                "scheduled_arr": "07:42 PM",
                "scheduled_dep": "07:45 PM",
                "predicted_arr": "08:06 PM",
                "predicted_dep": "08:09 PM",
                "platform": "5",
                "delay_mins": 24,
                "halt_mins": 3,
                "distance_km": 1914,
                "status": "upcoming",
                "delay_attribution": "Suburban corridor headway density",
                "coordinates": [19.2437, 73.1355]
            },
            {
                "code": "CSMT",
                "name": "Mumbai CSMT",
                "scheduled_arr": "09:20 PM",
                "scheduled_dep": "DEST",
                "predicted_arr": "09:42 PM",
                "predicted_dep": "DEST",
                "platform": "18",
                "delay_mins": 22,
                "halt_mins": 0,
                "distance_km": 1968,
                "status": "upcoming",
                "delay_attribution": "Final terminal arrival estimate",
                "coordinates": [18.9402, 72.8356]
            }
        ],
        "passenger_alerts": [
            {
                "id": "alt_201",
                "severity": "attention",
                "title": "Delay Alert (+22 min)",
                "message": "Running 22 mins behind schedule due to junction precedence and wet rail speed restrictions.",
                "time": "10m ago",
                "icon": "fa-triangle-exclamation"
            }
        ]
    },

    "22436": {
        "train_number": "22436",
        "train_name": "New Delhi - Varanasi Vande Bharat Express",
        "short_name": "Vande Bharat Express",
        "train_type": "Vande Bharat Express",
        "source": "New Delhi (NDLS)",
        "source_code": "NDLS",
        "destination": "Varanasi Jn (BSB)",
        "destination_code": "BSB",
        "zone": "Northern Railway (NR)",
        "total_distance_km": 759,
        "distance_covered_km": 440,
        "distance_remaining_km": 319,
        "avg_speed_kmh": 95,
        "current_status": "Train is running",
        "current_status_code": "RUNNING",
        "current_location": "Approaching Kanpur Central (Over Ganga Bridge)",
        "current_section": "Aligarh - Kanpur High-Speed Trunk Section (NCR)",
        "current_coordinates": [26.4670, 80.3500],
        "heading_deg": 110,
        "current_speed_kmh": 128,
        "max_permissible_speed": 130,
        "current_delay_mins": 0,
        "destination_delay_impact_mins": 0,
        "delay_impact_explanation": "High-priority green corridor assigned. Predicted on-time arrival at Varanasi Junction.",
        "confidence_level": "High",
        "confidence_pct": 98,
        "arrival_window": "02:00 PM – 02:06 PM",
        "scheduled_destination_eta": "02:00 PM",
        "predicted_destination_eta": "02:00 PM",
        "last_updated": "Simulated just now",
        "last_updated_time": "18:42:25 IST",
        "journey_progress_pct": 58,
        "active_events": [],
        "next_station": {
            "code": "CNB",
            "name": "Kanpur Central",
            "distance_km": 8,
            "expected_eta": "10:08 AM",
            "scheduled_eta": "10:08 AM",
            "platform": "1",
            "stoppage_time": "5 min"
        },
        "eta_factors": [
            {
                "id": "gps_telemetry",
                "code": "F01",
                "name": "Live GPS & Train Telemetry",
                "category": "Real-Time Telemetry",
                "is_active": True,
                "impact_level": "Positive (Time Saved)",
                "delay_impact_mins": 0,
                "passenger_explanation": "Train is maintaining optimal 128 km/h cruising speed along the dedicated Northern corridor.",
                "technical_detail": "Telemetry confirms 98.4% timekeeping across all monitored blocks."
            }
        ],
        "stations": [
            {
                "code": "NDLS",
                "name": "New Delhi",
                "scheduled_arr": "START",
                "scheduled_dep": "06:00 AM",
                "predicted_arr": "START",
                "predicted_dep": "06:00 AM",
                "platform": "16",
                "delay_mins": 0,
                "halt_mins": 0,
                "distance_km": 0,
                "status": "departed",
                "delay_attribution": "Departed on-time",
                "coordinates": [28.6139, 77.2090]
            },
            {
                "code": "CNB",
                "name": "Kanpur Central",
                "scheduled_arr": "10:08 AM",
                "scheduled_dep": "10:13 AM",
                "predicted_arr": "10:08 AM",
                "predicted_dep": "10:13 AM",
                "platform": "1",
                "delay_mins": 0,
                "halt_mins": 5,
                "distance_km": 440,
                "status": "approaching",
                "delay_attribution": "On-time arrival on dedicated high-speed line",
                "coordinates": [26.4539, 80.3507]
            },
            {
                "code": "PRYJ",
                "name": "Prayagraj Jn",
                "scheduled_arr": "12:08 PM",
                "scheduled_dep": "12:10 PM",
                "predicted_arr": "12:08 PM",
                "predicted_dep": "12:10 PM",
                "platform": "6",
                "delay_mins": 0,
                "halt_mins": 2,
                "distance_km": 635,
                "status": "upcoming",
                "delay_attribution": "Green signal path programmed",
                "coordinates": [25.4358, 81.8463]
            },
            {
                "code": "BSB",
                "name": "Varanasi Jn",
                "scheduled_arr": "02:00 PM",
                "scheduled_dep": "DEST",
                "predicted_arr": "02:00 PM",
                "predicted_dep": "DEST",
                "platform": "1",
                "delay_mins": 0,
                "halt_mins": 0,
                "distance_km": 759,
                "status": "upcoming",
                "delay_attribution": "Right-time destination arrival forecast",
                "coordinates": [25.3268, 82.9863]
            }
        ],
        "passenger_alerts": [
            {
                "id": "alt_301",
                "severity": "info",
                "title": "Right Time Operation",
                "message": "Vande Bharat Express is maintaining perfect schedule on the high-speed Delhi-Kanpur section.",
                "time": "Just now",
                "icon": "fa-circle-check"
            }
        ]
    },

    "12002": {
        "train_number": "12002",
        "train_name": "New Delhi - Bhopal Rani Kamlapati Shatabdi Express",
        "short_name": "Bhopal Shatabdi",
        "train_type": "Shatabdi Express",
        "source": "New Delhi (NDLS)",
        "source_code": "NDLS",
        "destination": "Rani Kamlapati (RKMP)",
        "destination_code": "RKMP",
        "zone": "Northern Railway (NR)",
        "total_distance_km": 708,
        "distance_covered_km": 199,
        "distance_remaining_km": 509,
        "avg_speed_kmh": 84,
        "current_status": "Train is running",
        "current_status_code": "RUNNING",
        "current_location": "Passing Mathura Jn (Km 141.2)",
        "current_section": "Palwal - Mathura 3rd Line (NCR)",
        "current_coordinates": [27.4924, 77.6737],
        "heading_deg": 165,
        "current_speed_kmh": 122,
        "max_permissible_speed": 150,
        "current_delay_mins": 6,
        "destination_delay_impact_mins": 2,
        "delay_impact_explanation": "High speed clearance on the Agra-Gwalior 150 km/h stretch will absorb 4 minutes of current delay.",
        "confidence_level": "High",
        "confidence_pct": 95,
        "arrival_window": "02:22 PM – 02:30 PM",
        "scheduled_destination_eta": "02:25 PM",
        "predicted_destination_eta": "02:27 PM",
        "last_updated": "Simulated 1 min ago",
        "last_updated_time": "18:42:00 IST",
        "journey_progress_pct": 28,
        "active_events": [],
        "next_station": {
            "code": "AGC",
            "name": "Agra Cantt",
            "distance_km": 54,
            "expected_eta": "07:56 AM",
            "scheduled_eta": "07:50 AM",
            "platform": "1",
            "stoppage_time": "5 min"
        },
        "eta_factors": [
            {
                "id": "level_crossings",
                "code": "F11",
                "name": "Level-Crossing Gate Clearance",
                "category": "Interlocking",
                "is_active": True,
                "impact_level": "Moderate impact",
                "delay_impact_mins": 4,
                "passenger_explanation": "Brief road traffic delay at a level-crossing gate near Kosi Kalan.",
                "technical_detail": "Interlocking signal opened 3 minutes late for road vehicular clearance."
            },
            {
                "id": "sectional_runtime",
                "code": "F03",
                "name": "Average Sectional Running Time",
                "category": "Section Performance",
                "is_active": True,
                "impact_level": "Positive (Time Saved)",
                "delay_impact_mins": -4,
                "passenger_explanation": "Approaching Agra Cantt to Gwalior section with 150 km/h high-speed buffer recovery.",
                "technical_detail": "Section MPS allows 4 mins slack buffer recovery."
            }
        ],
        "stations": [
            {
                "code": "NDLS",
                "name": "New Delhi",
                "scheduled_arr": "START",
                "scheduled_dep": "06:00 AM",
                "predicted_arr": "START",
                "predicted_dep": "06:00 AM",
                "platform": "1",
                "delay_mins": 0,
                "halt_mins": 0,
                "distance_km": 0,
                "status": "departed",
                "delay_attribution": "Departed on-time",
                "coordinates": [28.6139, 77.2090]
            },
            {
                "code": "AGC",
                "name": "Agra Cantt",
                "scheduled_arr": "07:50 AM",
                "scheduled_dep": "07:55 AM",
                "predicted_arr": "07:56 AM",
                "predicted_dep": "08:01 AM",
                "platform": "1",
                "delay_mins": 6,
                "halt_mins": 5,
                "distance_km": 199,
                "status": "approaching",
                "delay_attribution": "Level-crossing gate opening delay near Kosi Kalan",
                "coordinates": [27.1574, 78.0068]
            },
            {
                "code": "GWL",
                "name": "Gwalior Jn",
                "scheduled_arr": "09:23 AM",
                "scheduled_dep": "09:28 AM",
                "predicted_arr": "09:25 AM",
                "predicted_dep": "09:30 AM",
                "platform": "1",
                "delay_mins": 2,
                "halt_mins": 5,
                "distance_km": 318,
                "status": "upcoming",
                "delay_attribution": "High speed 150 km/h recovery in Agra-Gwalior block",
                "coordinates": [26.2183, 78.1828]
            },
            {
                "code": "VGLJ",
                "name": "VGL Jhansi Jn",
                "scheduled_arr": "10:40 AM",
                "scheduled_dep": "10:48 AM",
                "predicted_arr": "10:41 AM",
                "predicted_dep": "10:49 AM",
                "platform": "2",
                "delay_mins": 1,
                "halt_mins": 8,
                "distance_km": 415,
                "status": "upcoming",
                "delay_attribution": "On track with scheduled envelope",
                "coordinates": [25.4484, 78.5685]
            },
            {
                "code": "RKMP",
                "name": "Rani Kamlapati",
                "scheduled_arr": "02:25 PM",
                "scheduled_dep": "DEST",
                "predicted_arr": "02:27 PM",
                "predicted_dep": "DEST",
                "platform": "1",
                "delay_mins": 2,
                "halt_mins": 0,
                "distance_km": 708,
                "status": "upcoming",
                "delay_attribution": "Near right-time destination arrival",
                "coordinates": [23.2120, 77.4410]
            }
        ],
        "passenger_alerts": [
            {
                "id": "alt_401",
                "severity": "info",
                "title": "Buffer Recovery Expected",
                "message": "Minor 6 min gate delay will be recovered on the 150 km/h Agra-Gwalior stretch.",
                "time": "8m ago",
                "icon": "fa-bolt"
            }
        ]
    },

    "12259": {
        "train_number": "12259",
        "train_name": "Sealdah - Bikaner AC Duronto Express",
        "short_name": "Duronto Express",
        "train_type": "Duronto Express",
        "source": "Sealdah (SDAH)",
        "source_code": "SDAH",
        "destination": "New Delhi (NDLS)",
        "destination_code": "NDLS",
        "zone": "Eastern Railway (ER)",
        "total_distance_km": 1453,
        "distance_covered_km": 1210,
        "distance_remaining_km": 243,
        "avg_speed_kmh": 88,
        "current_status": "Train is running",
        "current_status_code": "RUNNING",
        "current_location": "Approaching New Delhi Outer",
        "current_section": "Kanpur - Ghaziabad Dedicated Track",
        "current_coordinates": [28.4200, 77.4000],
        "heading_deg": 320,
        "current_speed_kmh": 88,
        "max_permissible_speed": 130,
        "current_delay_mins": 20,
        "destination_delay_impact_mins": 20,
        "delay_impact_explanation": "Caution signal aspect approaching Ghaziabad yard.",
        "confidence_level": "High",
        "confidence_pct": 92,
        "arrival_window": "10:55 AM – 11:15 AM",
        "scheduled_destination_eta": "10:45 AM",
        "predicted_destination_eta": "11:05 AM",
        "last_updated": "Simulated just now",
        "last_updated_time": "18:43:00 IST",
        "journey_progress_pct": 83,
        "active_events": [],
        "next_station": {
            "code": "NDLS",
            "name": "New Delhi",
            "distance_km": 33,
            "expected_eta": "11:05 AM",
            "scheduled_eta": "10:45 AM",
            "platform": "4",
            "stoppage_time": "DEST"
        },
        "eta_factors": [
            {
                "id": "downstream_congestion",
                "code": "F06",
                "name": "Downstream Track Congestion",
                "category": "Traffic Density",
                "is_active": True,
                "impact_level": "High impact",
                "delay_impact_mins": 14,
                "passenger_explanation": "Platform line clearing delays at New Delhi terminal.",
                "technical_detail": "Terminal congestion at NDLS yard."
            },
            {
                "id": "speed_restrictions",
                "code": "F07",
                "name": "Temporary Speed Restriction (TSR)",
                "category": "Track Infrastructure",
                "is_active": True,
                "impact_level": "Moderate impact",
                "delay_impact_mins": 6,
                "passenger_explanation": "TSR 30 km/h on Ghaziabad approach curve.",
                "technical_detail": "TSR 30 km/h due to turnout maintenance."
            }
        ],
        "stations": [
            {
                "code": "SDAH",
                "name": "Sealdah",
                "scheduled_arr": "START",
                "scheduled_dep": "05:00 PM",
                "predicted_arr": "START",
                "predicted_dep": "05:00 PM",
                "platform": "9",
                "delay_mins": 0,
                "halt_mins": 0,
                "distance_km": 0,
                "status": "departed",
                "delay_attribution": "Departed on-time from origin",
                "coordinates": [22.5697, 88.3697]
            },
            {
                "code": "DHN",
                "name": "Dhanbad Jn",
                "scheduled_arr": "08:50 PM",
                "scheduled_dep": "08:55 PM",
                "predicted_arr": "08:50 PM",
                "predicted_dep": "08:55 PM",
                "platform": "2",
                "delay_mins": 0,
                "halt_mins": 5,
                "distance_km": 266,
                "status": "departed",
                "delay_attribution": "Clear line progression",
                "coordinates": [23.7957, 86.4304]
            },
            {
                "code": "DDU",
                "name": "Pt. DD Upadhyaya Jn",
                "scheduled_arr": "01:25 AM",
                "scheduled_dep": "01:35 AM",
                "predicted_arr": "01:30 AM",
                "predicted_dep": "01:40 AM",
                "platform": "6",
                "delay_mins": 5,
                "halt_mins": 10,
                "distance_km": 680,
                "status": "departed",
                "delay_attribution": "Yard routing precedence",
                "coordinates": [25.2818, 83.1207]
            },
            {
                "code": "CNB",
                "name": "Kanpur Central",
                "scheduled_arr": "05:30 AM",
                "scheduled_dep": "05:35 AM",
                "predicted_arr": "05:42 AM",
                "predicted_dep": "05:47 AM",
                "platform": "1",
                "delay_mins": 12,
                "halt_mins": 5,
                "distance_km": 1028,
                "status": "departed",
                "delay_attribution": "Sectional cautionary aspect",
                "coordinates": [26.4539, 80.3507]
            },
            {
                "code": "NDLS",
                "name": "New Delhi",
                "scheduled_arr": "10:45 AM",
                "scheduled_dep": "DEST",
                "predicted_arr": "11:05 AM",
                "predicted_dep": "DEST",
                "platform": "4",
                "delay_mins": 20,
                "halt_mins": 0,
                "distance_km": 1453,
                "status": "upcoming",
                "delay_attribution": "Terminal approach congestion",
                "coordinates": [28.6139, 77.2090]
            }
        ],
        "passenger_alerts": [
            {
                "id": "alt_501",
                "severity": "attention",
                "title": "Terminal Approach Delay (+20 min)",
                "message": "Train is holding at Ghaziabad outer awaiting platform line 4 clearance at New Delhi.",
                "time": "3m ago",
                "icon": "fa-clock"
            }
        ]
    },

    "12841": {
        "train_number": "12841",
        "train_name": "Howrah - MGR Chennai Central Coromandel Express",
        "short_name": "Coromandel Express",
        "train_type": "Superfast Express",
        "source": "Howrah Jn (HWH)",
        "source_code": "HWH",
        "destination": "MGR Chennai Central (MAS)",
        "destination_code": "MAS",
        "zone": "South Eastern Railway (SER)",
        "total_distance_km": 1662,
        "distance_covered_km": 290,
        "distance_remaining_km": 1372,
        "avg_speed_kmh": 78,
        "current_status": "Significant Delay (+2h 10m)",
        "current_status_code": "CRITICAL_DELAY",
        "current_location": "Passing Balasore Outer (Congestion Delay)",
        "current_section": "Kharagpur - Bhadrak Double Electric Line (SER)",
        "current_coordinates": [21.4934, 86.9135],
        "heading_deg": 195,
        "current_speed_kmh": 62,
        "max_permissible_speed": 130,
        "current_delay_mins": 130,
        "destination_delay_impact_mins": 130,
        "delay_impact_explanation": "Severe freight crossing congestion near Mughalsarai & Balasore yards.",
        "confidence_level": "Medium",
        "confidence_pct": 86,
        "arrival_window": "06:45 PM – 07:15 PM",
        "scheduled_destination_eta": "04:50 PM",
        "predicted_destination_eta": "07:00 PM",
        "last_updated": "Live Telemetry",
        "last_updated_time": "13:20:00 IST",
        "journey_progress_pct": 17.5,
        "active_events": [
            {
                "type": "congestion",
                "delay_impact_mins": 130,
                "description": "Due to congestion near Mughalsarai and Balasore"
            }
        ],
        "next_station": {
            "code": "BHC",
            "name": "Bhadrak",
            "distance_km": 68,
            "expected_eta": "04:20 PM",
            "scheduled_eta": "02:10 PM",
            "platform": "2",
            "stoppage_time": "2 min"
        },
        "eta_factors": [
            {
                "id": "downstream_congestion",
                "code": "F06",
                "name": "Downstream Track Congestion",
                "category": "Traffic Density",
                "is_active": True,
                "impact_level": "High impact",
                "delay_impact_mins": 130,
                "passenger_explanation": "Traffic congestion near major junction nodes.",
                "technical_detail": "Heavy freight crossing hold."
            }
        ],
        "stations": [
            {"code": "HWH", "name": "Howrah Jn", "coordinates": [22.5839, 88.3426], "scheduled_arr": "START", "scheduled_dep": "03:20 PM", "predicted_arr": "START", "predicted_dep": "03:20 PM", "status": "departed", "delay_mins": 0},
            {"code": "KGP", "name": "Kharagpur Jn", "coordinates": [22.3308, 87.3237], "scheduled_arr": "05:00 PM", "scheduled_dep": "05:05 PM", "predicted_arr": "05:00 PM", "predicted_dep": "05:05 PM", "status": "departed", "delay_mins": 0},
            {"code": "BLS", "name": "Balasore", "coordinates": [21.4934, 86.9135], "scheduled_arr": "06:30 PM", "scheduled_dep": "06:35 PM", "predicted_arr": "08:40 PM", "predicted_dep": "08:45 PM", "status": "departed", "delay_mins": 130},
            {"code": "BHC", "name": "Bhadrak", "coordinates": [21.0544, 86.4962], "scheduled_arr": "07:38 PM", "scheduled_dep": "07:40 PM", "predicted_arr": "09:48 PM", "predicted_dep": "09:50 PM", "status": "approaching", "delay_mins": 130},
            {"code": "BBS", "name": "Bhubaneswar", "coordinates": [20.2961, 85.8245], "scheduled_arr": "09:45 PM", "scheduled_dep": "09:50 PM", "predicted_arr": "11:55 PM", "predicted_dep": "12:00 AM", "status": "upcoming", "delay_mins": 130},
            {"code": "VSKP", "name": "Visakhapatnam", "coordinates": [17.7215, 83.2872], "scheduled_arr": "04:25 AM", "scheduled_dep": "04:45 AM", "predicted_arr": "06:35 AM", "predicted_dep": "06:55 AM", "status": "upcoming", "delay_mins": 130},
            {"code": "MAS", "name": "MGR Chennai Central", "coordinates": [13.0827, 80.2707], "scheduled_arr": "04:50 PM", "scheduled_dep": "DEST", "predicted_arr": "07:00 PM", "predicted_dep": "DEST", "status": "upcoming", "delay_mins": 130}
        ]
    },

    "12650": {
        "train_number": "12650",
        "train_name": "Hazrat Nizamuddin - Yesvantpur Karnataka Sampark Kranti",
        "short_name": "Karnataka Sampark Kranti",
        "train_type": "Sampark Kranti",
        "source": "Hazrat Nizamuddin (NZM)",
        "source_code": "NZM",
        "destination": "Yesvantpur Jn (YPR)",
        "destination_code": "YPR",
        "zone": "South Western Railway (SWR)",
        "total_distance_km": 2276,
        "distance_covered_km": 1680,
        "distance_remaining_km": 596,
        "avg_speed_kmh": 76,
        "current_status": "Running Late (+45m)",
        "current_status_code": "DELAYED",
        "current_location": "Signal halt at Vijayawada Outer",
        "current_section": "Warangal - Vijayawada Grand Trunk Route (SCR)",
        "current_coordinates": [16.5062, 80.6480],
        "heading_deg": 170,
        "current_speed_kmh": 42,
        "max_permissible_speed": 130,
        "current_delay_mins": 45,
        "destination_delay_impact_mins": 45,
        "delay_impact_explanation": "Signal halt at Vijayawada Junction awaiting platform clearance.",
        "confidence_level": "High",
        "confidence_pct": 92,
        "arrival_window": "07:35 PM – 08:05 PM",
        "scheduled_destination_eta": "07:05 PM",
        "predicted_destination_eta": "07:50 PM",
        "last_updated": "Live Telemetry",
        "last_updated_time": "12:55:00 IST",
        "journey_progress_pct": 73.8,
        "active_events": [
            {
                "type": "signal_halt",
                "delay_impact_mins": 45,
                "description": "Signal halt at Vijayawada"
            }
        ],
        "next_station": {
            "code": "BZA",
            "name": "Vijayawada Jn",
            "distance_km": 6,
            "expected_eta": "05:05 PM",
            "scheduled_eta": "04:20 PM",
            "platform": "1",
            "stoppage_time": "15 min"
        },
        "stations": [
            {"code": "NZM", "name": "Hazrat Nizamuddin", "coordinates": [28.5888, 77.2533], "scheduled_arr": "START", "scheduled_dep": "06:25 AM", "predicted_arr": "START", "predicted_dep": "06:25 AM", "status": "departed", "delay_mins": 0},
            {"code": "VGLJ", "name": "VGL Jhansi", "coordinates": [25.4484, 78.5685], "scheduled_arr": "11:30 AM", "scheduled_dep": "11:38 AM", "predicted_arr": "11:30 AM", "predicted_dep": "11:38 AM", "status": "departed", "delay_mins": 0},
            {"code": "BPL", "name": "Bhopal Jn", "coordinates": [23.2599, 77.4126], "scheduled_arr": "03:55 PM", "scheduled_dep": "04:05 PM", "predicted_arr": "03:55 PM", "predicted_dep": "04:05 PM", "status": "departed", "delay_mins": 0},
            {"code": "NGP", "name": "Nagpur Jn", "coordinates": [21.1528, 79.0882], "scheduled_arr": "10:20 PM", "scheduled_dep": "10:25 PM", "predicted_arr": "10:30 PM", "predicted_dep": "10:35 PM", "status": "departed", "delay_mins": 10},
            {"code": "BZA", "name": "Vijayawada Jn", "coordinates": [16.5062, 80.6480], "scheduled_arr": "04:20 PM", "scheduled_dep": "04:35 PM", "predicted_arr": "05:05 PM", "predicted_dep": "05:20 PM", "status": "approaching", "delay_mins": 45},
            {"code": "YPR", "name": "Yesvantpur Jn", "coordinates": [13.0238, 77.5503], "scheduled_arr": "07:05 PM", "scheduled_dep": "DEST", "predicted_arr": "07:50 PM", "predicted_dep": "DEST", "status": "upcoming", "delay_mins": 45}
        ]
    },

    "12740": {
        "train_number": "12740",
        "train_name": "Secunderabad - Visakhapatnam Garib Rath Express",
        "short_name": "Garib Rath Express",
        "train_type": "Garib Rath",
        "source": "Secunderabad Jn (SC)",
        "source_code": "SC",
        "destination": "Visakhapatnam (VSKP)",
        "destination_code": "VSKP",
        "zone": "South Central Railway (SCR)",
        "total_distance_km": 701,
        "distance_covered_km": 210,
        "distance_remaining_km": 491,
        "avg_speed_kmh": 72,
        "current_status": "Significant Delay (+1h 15m)",
        "current_status_code": "CRITICAL_DELAY",
        "current_location": "Near Kazipet Jn (Signal Precedence)",
        "current_section": "Secunderabad - Kazipet Electrified Section (SCR)",
        "current_coordinates": [17.9784, 79.5222],
        "heading_deg": 85,
        "current_speed_kmh": 68,
        "max_permissible_speed": 120,
        "current_delay_mins": 75,
        "destination_delay_impact_mins": 75,
        "delay_impact_explanation": "Signal precedence hold behind freight convoy at Kazipet.",
        "confidence_level": "Medium",
        "confidence_pct": 84,
        "arrival_window": "08:35 AM – 09:15 AM",
        "scheduled_destination_eta": "07:40 AM",
        "predicted_destination_eta": "08:55 AM",
        "last_updated": "Live Telemetry",
        "last_updated_time": "18:40:00 IST",
        "journey_progress_pct": 30.0,
        "active_events": [
            {
                "type": "congestion",
                "delay_impact_mins": 75,
                "description": "Preceding freight train clearance at Kazipet"
            }
        ],
        "next_station": {
            "code": "KZJ",
            "name": "Kazipet Jn",
            "distance_km": 14,
            "expected_eta": "10:40 PM",
            "scheduled_eta": "09:25 PM",
            "platform": "2",
            "stoppage_time": "5 min"
        },
        "stations": [
            {"code": "SC", "name": "Secunderabad Jn", "coordinates": [17.4344, 78.5015], "scheduled_arr": "START", "scheduled_dep": "08:30 PM", "predicted_arr": "START", "predicted_dep": "08:30 PM", "status": "departed", "delay_mins": 0},
            {"code": "KZJ", "name": "Kazipet Jn", "coordinates": [17.9784, 79.5222], "scheduled_arr": "09:25 PM", "scheduled_dep": "09:30 PM", "predicted_arr": "10:40 PM", "predicted_dep": "10:45 PM", "status": "approaching", "delay_mins": 75},
            {"code": "BZA", "name": "Vijayawada Jn", "coordinates": [16.5062, 80.6480], "scheduled_arr": "01:30 AM", "scheduled_dep": "01:45 AM", "predicted_arr": "02:45 AM", "predicted_dep": "03:00 AM", "status": "upcoming", "delay_mins": 75},
            {"code": "VSKP", "name": "Visakhapatnam", "coordinates": [17.7215, 83.2872], "scheduled_arr": "07:40 AM", "scheduled_dep": "DEST", "predicted_arr": "08:55 AM", "predicted_dep": "DEST", "status": "upcoming", "delay_mins": 75}
        ]
    },

    "12560": {
        "train_number": "12560",
        "train_name": "New Delhi - Banaras Shiv Ganga Express",
        "short_name": "Shiv Ganga Express",
        "train_type": "Superfast Express",
        "source": "New Delhi (NDLS)",
        "source_code": "NDLS",
        "destination": "Banaras (BSBS)",
        "destination_code": "BSBS",
        "zone": "North Eastern Railway (NER)",
        "total_distance_km": 757,
        "distance_covered_km": 630,
        "distance_remaining_km": 127,
        "avg_speed_kmh": 85,
        "current_status": "Running On Time",
        "current_status_code": "ON_TIME",
        "current_location": "Passing Prayagraj Rambag (Km 632)",
        "current_section": "Kanpur - Prayagraj - Varanasi Quadruple Line (NCR/NER)",
        "current_coordinates": [25.4410, 81.8540],
        "heading_deg": 105,
        "current_speed_kmh": 105,
        "max_permissible_speed": 130,
        "current_delay_mins": 0,
        "destination_delay_impact_mins": 0,
        "delay_impact_explanation": "Right-time green corridor running with scheduled speeds.",
        "confidence_level": "High",
        "confidence_pct": 98,
        "arrival_window": "07:10 AM – 07:20 AM",
        "scheduled_destination_eta": "07:15 AM",
        "predicted_destination_eta": "07:15 AM",
        "last_updated": "Live Telemetry",
        "last_updated_time": "19:15:00 IST",
        "journey_progress_pct": 83.2,
        "active_events": [],
        "next_station": {
            "code": "BSBS",
            "name": "Banaras",
            "distance_km": 127,
            "expected_eta": "07:15 AM",
            "scheduled_eta": "07:15 AM",
            "platform": "8",
            "stoppage_time": "DEST"
        },
        "stations": [
            {"code": "NDLS", "name": "New Delhi", "coordinates": [28.6139, 77.2090], "scheduled_arr": "START", "scheduled_dep": "08:05 PM", "predicted_arr": "START", "predicted_dep": "08:05 PM", "status": "departed", "delay_mins": 0},
            {"code": "CNB", "name": "Kanpur Central", "coordinates": [26.4539, 80.3507], "scheduled_arr": "01:00 AM", "scheduled_dep": "01:05 AM", "predicted_arr": "01:00 AM", "predicted_dep": "01:05 AM", "status": "departed", "delay_mins": 0},
            {"code": "PRYJ", "name": "Prayagraj Jn", "coordinates": [25.4358, 81.8463], "scheduled_arr": "03:45 AM", "scheduled_dep": "03:55 AM", "predicted_arr": "03:45 AM", "predicted_dep": "03:55 AM", "status": "departed", "delay_mins": 0},
            {"code": "BSBS", "name": "Banaras", "coordinates": [25.3176, 82.9739], "scheduled_arr": "07:15 AM", "scheduled_dep": "DEST", "predicted_arr": "07:15 AM", "predicted_dep": "DEST", "status": "upcoming", "delay_mins": 0}
        ]
    },

    "12302": {
        "train_number": "12302",
        "train_name": "New Delhi - Howrah Rajdhani Express (via Gaya)",
        "short_name": "Kolkata Rajdhani",
        "train_type": "Rajdhani Express",
        "source": "New Delhi (NDLS)",
        "source_code": "NDLS",
        "destination": "Howrah Jn (HWH)",
        "destination_code": "HWH",
        "zone": "Eastern Railway (ER)",
        "total_distance_km": 1451,
        "distance_covered_km": 980,
        "distance_remaining_km": 471,
        "avg_speed_kmh": 90,
        "current_status": "Running Late (+25m)",
        "current_status_code": "DELAYED",
        "current_location": "Passing Gaya Jn (Track Caution)",
        "current_section": "Pt. DD Upadhyaya - Gaya Grand Chord (ECR)",
        "current_coordinates": [24.7955, 84.9994],
        "heading_deg": 120,
        "current_speed_kmh": 110,
        "max_permissible_speed": 130,
        "current_delay_mins": 25,
        "destination_delay_impact_mins": 25,
        "delay_impact_explanation": "Speed restriction near Sasaram on the Grand Chord route.",
        "confidence_level": "High",
        "confidence_pct": 93,
        "arrival_window": "10:10 AM – 10:30 AM",
        "scheduled_destination_eta": "09:55 AM",
        "predicted_destination_eta": "10:20 AM",
        "last_updated": "Live Telemetry",
        "last_updated_time": "20:10:00 IST",
        "journey_progress_pct": 67.5,
        "active_events": [],
        "next_station": {
            "code": "DHN",
            "name": "Dhanbad Jn",
            "distance_km": 201,
            "expected_eta": "04:15 AM",
            "scheduled_eta": "03:50 AM",
            "platform": "1",
            "stoppage_time": "5 min"
        },
        "stations": [
            {"code": "NDLS", "name": "New Delhi", "coordinates": [28.6139, 77.2090], "scheduled_arr": "START", "scheduled_dep": "04:50 PM", "predicted_arr": "START", "predicted_dep": "04:50 PM", "status": "departed", "delay_mins": 0},
            {"code": "CNB", "name": "Kanpur Central", "coordinates": [26.4539, 80.3507], "scheduled_arr": "09:30 PM", "scheduled_dep": "09:35 PM", "predicted_arr": "09:35 PM", "predicted_dep": "09:40 PM", "status": "departed", "delay_mins": 5},
            {"code": "DDU", "name": "Pt. DD Upadhyaya", "coordinates": [25.2818, 83.1207], "scheduled_arr": "01:35 AM", "scheduled_dep": "01:45 AM", "predicted_arr": "01:55 AM", "predicted_dep": "02:05 AM", "status": "departed", "delay_mins": 20},
            {"code": "GAYA", "name": "Gaya Jn", "coordinates": [24.7955, 84.9994], "scheduled_arr": "03:38 AM", "scheduled_dep": "03:41 AM", "predicted_arr": "04:03 AM", "predicted_dep": "04:06 AM", "status": "departed", "delay_mins": 25},
            {"code": "DHN", "name": "Dhanbad Jn", "coordinates": [23.7957, 86.4304], "scheduled_arr": "03:50 AM", "scheduled_dep": "03:55 AM", "predicted_arr": "04:15 AM", "predicted_dep": "04:20 AM", "status": "approaching", "delay_mins": 25},
            {"code": "HWH", "name": "Howrah Jn", "coordinates": [22.5839, 88.3426], "scheduled_arr": "09:55 AM", "scheduled_dep": "DEST", "predicted_arr": "10:20 AM", "predicted_dep": "DEST", "status": "upcoming", "delay_mins": 25}
        ]
    },

    "12410": {
        "train_number": "12410",
        "train_name": "Hazrat Nizamuddin - Raigarh Gondwana Express",
        "short_name": "Gondwana Express",
        "train_type": "Superfast Express",
        "source": "Hazrat Nizamuddin (NZM)",
        "source_code": "NZM",
        "destination": "Raigarh (RIG)",
        "destination_code": "RIG",
        "zone": "South East Central Railway (SECR)",
        "total_distance_km": 1625,
        "distance_covered_km": 900,
        "distance_remaining_km": 725,
        "avg_speed_kmh": 65,
        "current_status": "Speed Restriction (+1h 00m)",
        "current_status_code": "CRITICAL_DELAY",
        "current_location": "Between Jabalpur & Katni (TSR 30 km/h)",
        "current_section": "Itarsi - Jabalpur - Katni Section (WCR)",
        "current_coordinates": [23.1815, 79.9864],
        "heading_deg": 65,
        "current_speed_kmh": 35,
        "max_permissible_speed": 110,
        "current_delay_mins": 60,
        "destination_delay_impact_mins": 60,
        "delay_impact_explanation": "Track maintenance block and TSR 30 km/h between Jabalpur and Katni.",
        "confidence_level": "Medium",
        "confidence_pct": 85,
        "arrival_window": "03:05 PM – 03:35 PM",
        "scheduled_destination_eta": "02:20 PM",
        "predicted_destination_eta": "03:20 PM",
        "last_updated": "Live Telemetry",
        "last_updated_time": "11:40:00 IST",
        "journey_progress_pct": 55.4,
        "active_events": [
            {
                "type": "tsr",
                "delay_impact_mins": 60,
                "description": "Due to maintenance work between Jabalpur and Katni"
            }
        ],
        "next_station": {
            "code": "KTE",
            "name": "Katni Jn",
            "distance_km": 91,
            "expected_eta": "04:55 AM",
            "scheduled_eta": "03:55 AM",
            "platform": "2",
            "stoppage_time": "5 min"
        },
        "stations": [
            {"code": "NZM", "name": "Hazrat Nizamuddin", "coordinates": [28.5888, 77.2533], "scheduled_arr": "START", "scheduled_dep": "03:05 PM", "predicted_arr": "START", "predicted_dep": "03:05 PM", "status": "departed", "delay_mins": 0},
            {"code": "GWL", "name": "Gwalior Jn", "coordinates": [26.2183, 78.1828], "scheduled_arr": "07:35 PM", "scheduled_dep": "07:40 PM", "predicted_arr": "07:35 PM", "predicted_dep": "07:40 PM", "status": "departed", "delay_mins": 0},
            {"code": "VGLJ", "name": "VGL Jhansi", "coordinates": [25.4484, 78.5685], "scheduled_arr": "09:05 PM", "scheduled_dep": "09:15 PM", "predicted_arr": "09:15 PM", "predicted_dep": "09:25 PM", "status": "departed", "delay_mins": 10},
            {"code": "JBP", "name": "Jabalpur Jn", "coordinates": [23.1815, 79.9864], "scheduled_arr": "02:15 AM", "scheduled_dep": "02:25 AM", "predicted_arr": "03:15 AM", "predicted_dep": "03:25 AM", "status": "departed", "delay_mins": 60},
            {"code": "KTE", "name": "Katni Jn", "coordinates": [23.8343, 80.3990], "scheduled_arr": "03:55 AM", "scheduled_dep": "04:00 AM", "predicted_arr": "04:55 AM", "predicted_dep": "05:00 AM", "status": "approaching", "delay_mins": 60},
            {"code": "BSP", "name": "Bilaspur Jn", "coordinates": [22.0797, 82.1409], "scheduled_arr": "09:55 AM", "scheduled_dep": "10:10 AM", "predicted_arr": "10:55 AM", "predicted_dep": "11:10 AM", "status": "upcoming", "delay_mins": 60},
            {"code": "RIG", "name": "Raigarh", "coordinates": [21.8974, 83.3950], "scheduled_arr": "02:20 PM", "scheduled_dep": "DEST", "predicted_arr": "03:20 PM", "predicted_dep": "DEST", "status": "upcoming", "delay_mins": 60}
        ]
    },

    "12618": {
        "train_number": "12618",
        "train_name": "Hazrat Nizamuddin - Ernakulam Mangala Lakshadweep Express",
        "short_name": "Mangala Lakshadweep",
        "train_type": "Superfast Express",
        "source": "Hazrat Nizamuddin (NZM)",
        "source_code": "NZM",
        "destination": "Ernakulam Jn (ERS)",
        "destination_code": "ERS",
        "zone": "Southern Railway (SR)",
        "total_distance_km": 2769,
        "distance_covered_km": 1950,
        "distance_remaining_km": 819,
        "avg_speed_kmh": 64,
        "current_status": "Running On Time",
        "current_status_code": "ON_TIME",
        "current_location": "Passing Mangaluru Jn (Konkan Coastal Line)",
        "current_section": "Madgaon - Mangaluru Konkan Railway (KR)",
        "current_coordinates": [12.8681, 74.8643],
        "heading_deg": 160,
        "current_speed_kmh": 90,
        "max_permissible_speed": 110,
        "current_delay_mins": 0,
        "destination_delay_impact_mins": 0,
        "delay_impact_explanation": "Right-time Konkan Railway coastal progression.",
        "confidence_level": "High",
        "confidence_pct": 96,
        "arrival_window": "11:45 PM – 11:55 PM",
        "scheduled_destination_eta": "11:50 PM",
        "predicted_destination_eta": "11:50 PM",
        "last_updated": "Live Telemetry",
        "last_updated_time": "23:50:00 IST",
        "journey_progress_pct": 70.4,
        "active_events": [],
        "next_station": {
            "code": "CAN",
            "name": "Kannur",
            "distance_km": 140,
            "expected_eta": "03:10 AM",
            "scheduled_eta": "03:10 AM",
            "platform": "1",
            "stoppage_time": "5 min"
        },
        "stations": [
            {"code": "NZM", "name": "Hazrat Nizamuddin", "coordinates": [28.5888, 77.2533], "scheduled_arr": "START", "scheduled_dep": "05:35 AM", "predicted_arr": "START", "predicted_dep": "05:35 AM", "status": "departed", "delay_mins": 0},
            {"code": "BPL", "name": "Bhopal Jn", "coordinates": [23.2599, 77.4126], "scheduled_arr": "04:30 PM", "scheduled_dep": "04:40 PM", "predicted_arr": "04:30 PM", "predicted_dep": "04:40 PM", "status": "departed", "delay_mins": 0},
            {"code": "BSL", "name": "Bhusaval Jn", "coordinates": [21.0455, 75.7885], "scheduled_arr": "10:35 PM", "scheduled_dep": "10:40 PM", "predicted_arr": "10:35 PM", "predicted_dep": "10:40 PM", "status": "departed", "delay_mins": 0},
            {"code": "PNVL", "name": "Panvel", "coordinates": [18.9894, 73.1175], "scheduled_arr": "06:15 AM", "scheduled_dep": "06:20 AM", "predicted_arr": "06:15 AM", "predicted_dep": "06:20 AM", "status": "departed", "delay_mins": 0},
            {"code": "MAJN", "name": "Mangaluru Jn", "coordinates": [12.8681, 74.8643], "scheduled_arr": "01:25 AM", "scheduled_dep": "01:35 AM", "predicted_arr": "01:25 AM", "predicted_dep": "01:35 AM", "status": "departed", "delay_mins": 0},
            {"code": "CAN", "name": "Kannur", "coordinates": [11.8745, 75.3704], "scheduled_arr": "03:10 AM", "scheduled_dep": "03:15 AM", "predicted_arr": "03:10 AM", "predicted_dep": "03:15 AM", "status": "approaching", "delay_mins": 0},
            {"code": "ERS", "name": "Ernakulam Jn", "coordinates": [9.9675, 76.2917], "scheduled_arr": "11:50 PM", "scheduled_dep": "DEST", "predicted_arr": "11:50 PM", "predicted_dep": "DEST", "status": "upcoming", "delay_mins": 0}
        ]
    }
}

def interpolate_along_route(polyline: list, progress_pct: float) -> list:
    if not polyline:
        return [22.0, 75.0]
    if len(polyline) == 1 or progress_pct <= 0:
        return list(polyline[0])
    if progress_pct >= 100:
        return list(polyline[-1])

    seg_dists = []
    total_dist = 0.0
    for i in range(len(polyline) - 1):
        lat1, lon1 = polyline[i]
        lat2, lon2 = polyline[i + 1]
        d = ((lat2 - lat1) ** 2 + ((lon2 - lon1) * 0.9) ** 2) ** 0.5
        seg_dists.append(d)
        total_dist += d

    if total_dist == 0:
        return list(polyline[0])

    target_dist = (progress_pct / 100.0) * total_dist
    accum = 0.0
    for i, d in enumerate(seg_dists):
        if accum + d >= target_dist:
            seg_t = (target_dist - accum) / d if d > 0 else 0.0
            lat = polyline[i][0] + seg_t * (polyline[i + 1][0] - polyline[i][0])
            lon = polyline[i][1] + seg_t * (polyline[i + 1][1] - polyline[i][1])
            return [round(lat, 4), round(lon, 4)]
        accum += d
    return list(polyline[-1])


def _enrich_train_telemetry(t: dict) -> dict:
    if not t or not isinstance(t, dict):
        return t
    coords = t.get("current_coordinates")
    lat = None
    lng = None
    if coords and isinstance(coords, (list, tuple)) and len(coords) >= 2:
        try:
            lat = float(coords[0])
            lng = float(coords[1])
        except (ValueError, TypeError):
            pass
    elif t.get("latitude") is not None and t.get("longitude") is not None:
        try:
            lat = float(t["latitude"])
            lng = float(t["longitude"])
        except (ValueError, TypeError):
            pass

    t["latitude"] = lat
    t["longitude"] = lng
    if lat is not None and lng is not None:
        t["current_coordinates"] = [lat, lng]

    speed = t.get("current_speed_kmh") if t.get("current_speed_kmh") is not None else t.get("speed", 0)
    try:
        t["speed"] = int(speed)
        t["current_speed_kmh"] = int(speed)
    except (ValueError, TypeError):
        t["speed"] = 0
        t["current_speed_kmh"] = 0

    status = t.get("current_status_code") or t.get("status") or t.get("current_status") or "RUNNING"
    t["status"] = str(status).upper()

    delay = t.get("current_delay_mins") if t.get("current_delay_mins") is not None else t.get("delay", 0)
    try:
        t["delay"] = int(delay)
        t["current_delay_mins"] = int(delay)
    except (ValueError, TypeError):
        t["delay"] = 0
        t["current_delay_mins"] = 0

    eta = t.get("predicted_destination_eta") or t.get("eta") or t.get("scheduled_destination_eta") or ""
    t["eta"] = str(eta)

    curr_stn = t.get("current_location") or t.get("current_station") or ""
    t["current_station"] = str(curr_stn)

    next_stn = t.get("next_station") or ""
    t["next_station"] = next_stn

    return t


class InMemoryRailwayStore:
    """
    Thread-safe unified in-memory state store for Indian Railways
    active trains, station display timetables, and operational events.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._trains = copy.deepcopy(INITIAL_TRAINS)
        for train_no, train in self._trains.items():
            if "route_polyline" not in train or not train["route_polyline"]:
                train["route_polyline"] = [stn["coordinates"] for stn in train.get("stations", []) if "coordinates" in stn]

    def recalculate_all(self):
        with self._lock:
            for train_no, train in self._trains.items():
                self._trains[train_no] = eta_engine.recalculate_train_etas(train)

    def get_train(self, train_number: str) -> dict:
        with self._lock:
            train = self._trains.get(str(train_number).strip())
            return _enrich_train_telemetry(copy.deepcopy(train)) if train else None

    def get_all_trains(self) -> list:
        with self._lock:
            return [_enrich_train_telemetry(copy.deepcopy(t)) for t in self._trains.values()]

    def update_train(self, train_data: dict):
        if not train_data or "train_number" not in train_data:
            return
        with self._lock:
            tno = str(train_data["train_number"]).strip()
            self._trains[tno] = copy.deepcopy(train_data)

    def get_station_board(self, station_code: str) -> dict:
        with self._lock:
            stn_upper = station_code.upper().strip()
            arrivals = []
            departures = []
            seen_arrivals = set()
            seen_departures = set()

            for train_no, train in self._trains.items():
                tno = str(train.get("train_number") or train_no).strip()
                for stn in train.get("stations", []):
                    code_norm = str(stn.get("code") or "").strip().upper()
                    if code_norm == stn_upper:
                        sched_arr = stn.get("scheduled_arr")
                        pred_arr = stn.get("predicted_arr")
                        sched_dep = stn.get("scheduled_dep")
                        pred_dep = stn.get("predicted_dep")

                        train_status_code = train.get("current_status_code") or train.get("status") or "RUNNING"
                        stn_status = "NOT_STARTED" if train_status_code == "NOT_STARTED" else stn.get("status", "upcoming")

                        if sched_arr != "START" and tno not in seen_arrivals:
                            seen_arrivals.add(tno)
                            arrivals.append({
                                "train_number": tno,
                                "train_name": train.get("train_name"),
                                "short_name": train.get("short_name"),
                                "source": train.get("source"),
                                "destination": train.get("destination"),
                                "platform": stn.get("platform", "1"),
                                "scheduled_time": sched_arr,
                                "predicted_time": pred_arr,
                                "delay_mins": stn.get("delay_mins", 0),
                                "status": stn_status,
                                "status_code": train_status_code,
                                "delay_attribution": stn.get("delay_attribution", "")
                            })

                        if sched_dep != "DEST" and tno not in seen_departures:
                            seen_departures.add(tno)
                            departures.append({
                                "train_number": tno,
                                "train_name": train.get("train_name"),
                                "short_name": train.get("short_name"),
                                "source": train.get("source"),
                                "destination": train.get("destination"),
                                "platform": stn.get("platform", "1"),
                                "scheduled_time": sched_dep,
                                "predicted_time": pred_dep,
                                "delay_mins": stn.get("delay_mins", 0),
                                "status": stn_status,
                                "status_code": train_status_code,
                                "delay_attribution": stn.get("delay_attribution", "")
                            })

            # If fewer than 8 arrivals/departures, enrich from full railway schedule database
            try:
                from app.services.railradar import railradar_service
                railradar_service._ensure_schedule_db_loaded()
                db_trains = list(railradar_service._station_to_trains.get(stn_upper, []))
                for tno in db_trains:
                    if len(arrivals) >= 12 and len(departures) >= 12:
                        break
                    route = railradar_service._schedule_routes.get(tno, [])
                    stop = next((r for r in route if r.get("station_code") == stn_upper), None)
                    if not stop:
                        continue
                    t_info = railradar_service._train_names_db.get(tno, {})
                    t_name = t_info.get("name") or f"Train {tno}"
                    src_code = route[0]["station_code"] if route else "ORIGIN"
                    dest_code = route[-1]["station_code"] if route else "DEST"
                    src_name = railradar_service.get_station_name_by_code(src_code)
                    dest_name = railradar_service.get_station_name_by_code(dest_code)

                    raw_arr = stop.get("arr")
                    raw_dep = stop.get("dep")
                    formatted_arr = railradar_service.format_iso_or_time(raw_arr) if raw_arr else None
                    formatted_dep = railradar_service.format_iso_or_time(raw_dep) if raw_dep else None

                    pf = str((int(tno[-1]) % 6) + 1) if tno[-1].isdigit() else "1"

                    if formatted_arr and formatted_arr != "--:--" and tno not in seen_arrivals and len(arrivals) < 12:
                        seen_arrivals.add(tno)
                        arrivals.append({
                            "train_number": tno,
                            "train_name": t_name,
                            "short_name": t_name.split("-")[0].strip(),
                            "source": f"{src_name} ({src_code})",
                            "destination": f"{dest_name} ({dest_code})",
                            "platform": pf,
                            "scheduled_time": formatted_arr,
                            "predicted_time": formatted_arr,
                            "delay_mins": 0,
                            "status": "Scheduled",
                            "status_code": "RUNNING",
                            "delay_attribution": "Timetable schedule"
                        })

                    if formatted_dep and formatted_dep != "--:--" and tno not in seen_departures and len(departures) < 12:
                        seen_departures.add(tno)
                        departures.append({
                            "train_number": tno,
                            "train_name": t_name,
                            "short_name": t_name.split("-")[0].strip(),
                            "source": f"{src_name} ({src_code})",
                            "destination": f"{dest_name} ({dest_code})",
                            "platform": pf,
                            "scheduled_time": formatted_dep,
                            "predicted_time": formatted_dep,
                            "delay_mins": 0,
                            "status": "Scheduled",
                            "status_code": "RUNNING",
                            "delay_attribution": "Timetable schedule"
                        })
            except Exception:
                pass

            return {"arrivals": arrivals, "departures": departures}

    def inject_event(self, train_number: str, event_type: str, delay_mins: int = 5, description: str = None) -> dict:
        with self._lock:
            train = self._trains.get(str(train_number))
            if not train:
                return None

            if event_type == "clear":
                train["active_events"] = []
                train["current_delay_mins"] = INITIAL_TRAINS.get(str(train_number), {}).get("current_delay_mins", 0)
            else:
                if "active_events" not in train:
                    train["active_events"] = []
                train["active_events"].append({
                    "type": event_type,
                    "delay_impact_mins": delay_mins,
                    "description": description or f"{event_type.upper()} incident injected"
                })

            updated_train = eta_engine.recalculate_train_etas(train)
            self._trains[train_number] = updated_train
            try:
                from app.services.railradar import railradar_service
                railradar_service.cache.pop(str(train_number), None)
            except Exception:
                pass
            return copy.deepcopy(updated_train)

    def advance_simulation_tick(self, train_number: str = None):
        with self._lock:
            if train_number:
                targets = [self._trains.get(str(train_number))]
            else:
                targets = list(self._trains.values())

            for train in targets:
                if not train:
                    continue
                poly = train.get("route_polyline") or [s["coordinates"] for s in train.get("stations", []) if "coordinates" in s]
                train["route_polyline"] = poly

                # Progressively advance train along railway corridor
                progress = train.get("journey_progress_pct", 38.0)
                progress = (progress + 0.35) if progress < 99.0 else 20.0
                train["journey_progress_pct"] = round(progress, 1)

                # Exactly interpolate along route polyline
                train["current_coordinates"] = interpolate_along_route(poly, progress)

                speed = train.get("current_speed_kmh", 100)
                train["current_speed_kmh"] = max(40, min(130, speed + random.choice([-2, -1, 0, 1, 2])))

            return copy.deepcopy(list(self._trains.values()))

    def get_active_alerts(self) -> list:
        alerts = []
        with self._lock:
            # 1. Include injected active events from any train
            for tno, train in self._trains.items():
                for ev in train.get("active_events", []):
                    desc = ev.get("description", "")
                    impact = int(ev.get("delay_impact_mins", 0))
                    alerts.append({
                        "id": f"occ_ev_{tno}_{len(alerts)}",
                        "train_number": tno,
                        "title": f"Train {tno} - {ev.get('type', 'alert').upper()} (+{impact}m)",
                        "description": desc or f"Operational event recorded for Train {tno}",
                        "time": "Active",
                        "severity": "critical" if impact >= 30 else ("warning" if impact >= 10 else "info"),
                        "type": ev.get("type", "alert")
                    })

            # 2. Derive alerts dynamically from trains with recorded delay > 5 minutes
            for tno, train in self._trains.items():
                delay = int(train.get("current_delay_mins") or train.get("delay") or 0)
                if delay > 5:
                    train_name = train.get("train_name", f"Train {tno}")
                    severity = "critical" if delay > 30 else "warning"
                    h = delay // 60
                    m = delay % 60
                    delay_str = f"{h}h {m}m" if h > 0 else f"{m}m"
                    curr_loc = train.get("current_location") or "en route"
                    alerts.append({
                        "id": f"delay_alert_{tno}",
                        "train_number": tno,
                        "title": f"Train {tno} ({train_name}) delayed by {delay_str}",
                        "description": f"Sectional delay recorded near {curr_loc}",
                        "time": train.get("last_updated_time") or "Live",
                        "severity": severity,
                        "type": "congestion" if delay > 30 else "delay"
                    })
            return alerts

store = InMemoryRailwayStore()
railway_store = store
