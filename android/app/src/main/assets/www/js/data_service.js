/**
 * GatiSetu - Passenger Data & Mock Service Layer
 * 
 * Provides realistic Indian Railways train schedules, live telemetry coordinates,
 * dynamic ETA predictions, 12 PS-based operational factors, delay impact forecasts,
 * and passenger alerts.
 * 
 * Designed to cleanly swap to FastAPI REST / WebSocket endpoints in future phases.
 */

const DEMO_TRAINS = {
    "12951": {
        train_number: "12951",
        train_name: "Mumbai - New Delhi Tejas Rajdhani Express",
        short_name: "NDLS Tejas Rajdhani",
        train_type: "Tejas Rajdhani Express",
        source: "Mumbai Central (MMCT)",
        source_code: "MMCT",
        destination: "New Delhi (NDLS)",
        destination_code: "NDLS",
        zone: "Western Railway (WR)",
        total_distance_km: 1386,
        distance_covered_km: 326.1,
        distance_remaining_km: 1059.9,
        avg_speed_kmh: 88,
        current_status: "Train is running",
        current_status_code: "RUNNING",
        current_location: "Passing Bharuch Jn (Between Surat & Vadodara)",
        current_section: "Surat - Vadodara Quadruple Track Section (WR)",
        current_coordinates: [21.7051, 72.9959],
        heading_deg: 18,
        current_speed_kmh: 114,
        max_permissible_speed: 130,
        current_delay_mins: 14,
        destination_delay_impact_mins: 11,
        delay_impact_explanation: "Simulated forecast indicates a 3-minute recovery between Vadodara and Kota due to high-speed track clearance.",
        confidence_level: "High",
        confidence_pct: 94,
        arrival_window: "08:41 AM – 08:51 AM",
        scheduled_destination_eta: "08:32 AM",
        predicted_destination_eta: "08:46 AM",
        last_updated: "Simulated 1 min ago",
        last_updated_time: "18:42:10 IST",
        journey_progress_pct: 23.5,
        next_station: {
            code: "BRC",
            name: "Vadodara Jn",
            distance_km: 66,
            expected_eta: "09:41 PM",
            scheduled_eta: "09:27 PM",
            platform: "2",
            stoppage_time: "10 min"
        },
        eta_factors: [
            {
                id: "downstream_congestion",
                code: "F06",
                name: "Downstream Track Congestion",
                category: "Traffic Density",
                is_active: true,
                impact_level: "High impact",
                delay_impact_mins: 8,
                passenger_explanation: "High track density near Vadodara Junction is causing cautionary signal aspects for incoming express trains.",
                technical_detail: "Platform 2 line occupancy delay of 6 mins due to late departure of 19015 Saurashtra Express."
            },
            {
                id: "speed_restrictions",
                code: "F07",
                name: "Temporary Speed Restriction (TSR)",
                category: "Track Infrastructure",
                is_active: true,
                impact_level: "Moderate impact",
                delay_impact_mins: 4,
                passenger_explanation: "Track renewal maintenance near Vapi has a temporary speed limit of 45 km/h for a 3 km section.",
                technical_detail: "TSR 45 km/h between km 168/2 to 171/8 due to sleeper replacement."
            },
            {
                id: "preceding_train_delays",
                code: "F09",
                name: "Preceding-Train Delays",
                category: "Traffic Density",
                is_active: true,
                impact_level: "Moderate impact",
                delay_impact_mins: 2,
                passenger_explanation: "A container freight train ahead is clearing the block section, temporarily limiting cruising speed.",
                technical_detail: "Headway reduced to 4.2 km; automatic signaling keeping distance buffer."
            },
            {
                id: "weather_conditions",
                code: "F04",
                name: "Weather & Track Conditions",
                category: "Environmental",
                is_active: false,
                impact_level: "Nominal",
                delay_impact_mins: 0,
                passenger_explanation: "Clear track weather and excellent visibility along the Western Railway corridor.",
                technical_detail: "Visibility > 2000m; rail temperature within standard green envelope (32°C)."
            },
            {
                id: "maintenance_blocks",
                code: "F10",
                name: "Temporary Maintenance Blocks",
                category: "Engineering Work",
                is_active: false,
                impact_level: "Nominal",
                delay_impact_mins: 0,
                passenger_explanation: "No scheduled mega maintenance blocks on this active mainline.",
                technical_detail: "No active engineering shadow block."
            },
            {
                id: "level_crossings",
                code: "F11",
                name: "Level-Crossing Gate Clearance",
                category: "Interlocking",
                is_active: false,
                impact_level: "Nominal",
                delay_impact_mins: 0,
                passenger_explanation: "All level crossing gates along this electrified section are fully interlocked and closed.",
                technical_detail: "All LC gates interlocked with automatic signal aspects."
            }
        ],
        stations: [
            {
                code: "MMCT",
                name: "Mumbai Central",
                scheduled_arr: "START",
                scheduled_dep: "05:00 PM",
                predicted_arr: "START",
                predicted_dep: "05:00 PM",
                platform: "1",
                delay_mins: 0,
                halt_mins: 0,
                distance_km: 0,
                status: "departed",
                delay_attribution: "Departed on-time from source",
                coordinates: [18.9696, 72.8193]
            },
            {
                code: "BVI",
                name: "Borivali",
                scheduled_arr: "05:30 PM",
                scheduled_dep: "05:33 PM",
                predicted_arr: "05:30 PM",
                predicted_dep: "05:33 PM",
                platform: "6",
                delay_mins: 0,
                halt_mins: 3,
                distance_km: 30,
                status: "departed",
                delay_attribution: "Clear track section with normal headway",
                coordinates: [19.2290, 72.8574]
            },
            {
                code: "ST",
                name: "Surat",
                scheduled_arr: "07:54 PM",
                scheduled_dep: "07:59 PM",
                predicted_arr: "08:02 PM",
                predicted_dep: "08:07 PM",
                platform: "1",
                delay_mins: 8,
                halt_mins: 5,
                distance_km: 263,
                status: "departed",
                delay_attribution: "Speed restriction near Vapi (TSR 45 km/h)",
                coordinates: [21.2052, 72.8409]
            },
            {
                code: "BRC",
                name: "Vadodara Jn",
                scheduled_arr: "09:27 PM",
                scheduled_dep: "09:37 PM",
                predicted_arr: "09:41 PM",
                predicted_dep: "09:51 PM",
                platform: "2",
                delay_mins: 14,
                halt_mins: 10,
                distance_km: 392,
                status: "approaching",
                delay_attribution: "Preceding freight train clearance & junction congestion",
                coordinates: [22.3107, 73.1812]
            },
            {
                code: "RTM",
                name: "Ratlam Jn",
                scheduled_arr: "01:05 AM",
                scheduled_dep: "01:10 AM",
                predicted_arr: "01:16 AM",
                predicted_dep: "01:21 AM",
                platform: "4",
                delay_mins: 11,
                halt_mins: 5,
                distance_km: 653,
                status: "upcoming",
                delay_attribution: "Buffer recovery model predicts +3 min time saved",
                coordinates: [23.3441, 75.0366]
            },
            {
                code: "KOTA",
                name: "Kota Jn",
                scheduled_arr: "04:10 AM",
                scheduled_dep: "04:15 AM",
                predicted_arr: "04:18 AM",
                predicted_dep: "04:23 AM",
                platform: "1",
                delay_mins: 8,
                halt_mins: 5,
                distance_km: 920,
                status: "upcoming",
                delay_attribution: "High speed 130 km/h corridor clearance",
                coordinates: [25.2138, 75.8648]
            },
            {
                code: "NDLS",
                name: "New Delhi",
                scheduled_arr: "08:32 AM",
                scheduled_dep: "DEST",
                predicted_arr: "08:46 AM",
                predicted_dep: "DEST",
                platform: "1",
                delay_mins: 14,
                halt_mins: 0,
                distance_km: 1386,
                status: "upcoming",
                delay_attribution: "Final arrival with dynamic sectional buffers factored in",
                coordinates: [28.6139, 77.2090]
            }
        ],
        passenger_alerts: [
            {
                id: "alt_1",
                severity: "attention",
                title: "Dynamic ETA Shift (+14 min)",
                message: "Expected arrival at Vadodara Jn adjusted to 09:41 PM due to caution signals between Bharuch and Vadodara.",
                time: "5m ago",
                icon: "fa-clock"
            },
            {
                id: "alt_2",
                severity: "info",
                title: "TSR Speed Restriction Near Vapi",
                message: "Temporary Speed Restriction of 45 km/h safely cleared by train telemetry.",
                time: "22m ago",
                icon: "fa-gauge-simple"
            },
            {
                id: "alt_3",
                severity: "info",
                title: "Approaching Vadodara Jn",
                message: "Train is 66 km away from Vadodara Jn (BRC). Estimated platform 2.",
                time: "Just now",
                icon: "fa-train-subway"
            }
        ],
        route_polyline: [
            [18.9696, 72.8193], [19.2290, 72.8574], [19.5760, 72.7660], [20.3700, 72.9100],
            [20.9500, 72.9300], [21.1702, 72.8311], [21.7051, 72.9959], [22.3072, 73.1812],
            [22.8200, 73.6100], [22.8330, 74.2560], [23.3341, 75.0376], [23.4544, 75.4147],
            [24.1800, 75.8300], [24.5300, 75.9800], [25.1825, 75.8340], [25.9928, 76.3688],
            [26.4900, 76.7300], [26.9800, 77.0100], [27.1800, 77.4900], [27.4924, 77.6737],
            [28.1400, 77.3300], [28.4089, 77.3178], [28.5880, 77.2530], [28.6139, 77.2090]
        ]
    },

    "12860": {
        train_number: "12860",
        train_name: "Howrah - Mumbai CSMT Gitanjali Express",
        short_name: "Gitanjali Express",
        train_type: "Superfast Express",
        source: "Howrah Jn (HWH)",
        source_code: "HWH",
        destination: "Mumbai CSMT (CSMT)",
        destination_code: "CSMT",
        zone: "South Eastern Railway (SER)",
        total_distance_km: 1968,
        distance_covered_km: 1420,
        distance_remaining_km: 548,
        avg_speed_kmh: 68,
        current_status: "Train is running",
        current_status_code: "RUNNING",
        current_location: "Between Bhusaval & Nashik Road (Passing Manmad Jn)",
        current_section: "Bhusaval - Manmad Double Electric Line (CR)",
        current_coordinates: [20.2524, 74.4388],
        heading_deg: 245,
        current_speed_kmh: 96,
        max_permissible_speed: 110,
        current_delay_mins: 22,
        destination_delay_impact_mins: 26,
        delay_impact_explanation: "Suburban EMU traffic density near Kalyan Jn is projected to add 4 minutes to final destination arrival.",
        confidence_level: "High",
        confidence_pct: 91,
        arrival_window: "09:30 PM – 09:44 PM",
        scheduled_destination_eta: "09:20 PM",
        predicted_destination_eta: "09:42 PM",
        last_updated: "Simulated 2 min ago",
        last_updated_time: "18:41:40 IST",
        journey_progress_pct: 72,
        next_station: {
            code: "NK",
            name: "Nashik Road",
            distance_km: 74,
            expected_eta: "04:32 PM",
            scheduled_eta: "04:10 PM",
            platform: "3",
            stoppage_time: "5 min"
        },
        eta_factors: [
            {
                id: "signal_aspects",
                code: "F02",
                name: "Signal Aspects & Block Halts",
                category: "Signaling & Interlocking",
                is_active: true,
                impact_level: "High impact",
                delay_impact_mins: 12,
                passenger_explanation: "Held at outer home signal of Manmad Junction for platform cross-movement.",
                technical_detail: "Signal clearance held for crossing of 12138 Punjab Mail."
            },
            {
                id: "weather_conditions",
                code: "F04",
                name: "Weather & Track Conditions",
                category: "Environmental",
                is_active: true,
                impact_level: "Moderate impact",
                delay_impact_mins: 6,
                passenger_explanation: "Heavy rain across the Kasara Ghats section requires regulated speed operations.",
                technical_detail: "Monsoon precaution speed regulation in Igatpuri-Kasara 1:37 gradient ghats."
            },
            {
                id: "operational_bottlenecks",
                code: "F12",
                name: "Operational Bottlenecks & Junctions",
                category: "Junction Capacity",
                is_active: true,
                impact_level: "Moderate impact",
                delay_impact_mins: 4,
                passenger_explanation: "Junction interlocking constraints at Manmad Jn.",
                technical_detail: "Single route diamond crossover operational bottleneck."
            }
        ],
        stations: [
            {
                code: "HWH",
                name: "Howrah Jn",
                scheduled_arr: "START",
                scheduled_dep: "01:50 PM",
                predicted_arr: "START",
                predicted_dep: "01:50 PM",
                platform: "21",
                delay_mins: 0,
                halt_mins: 0,
                distance_km: 0,
                status: "departed",
                delay_attribution: "Departed on-time",
                coordinates: [22.5839, 88.3426]
            },
            {
                code: "TATA",
                name: "Tatanagar Jn",
                scheduled_arr: "05:15 PM",
                scheduled_dep: "05:20 PM",
                predicted_arr: "05:15 PM",
                predicted_dep: "05:20 PM",
                platform: "3",
                delay_mins: 0,
                halt_mins: 5,
                distance_km: 250,
                status: "departed",
                delay_attribution: "On-time departure",
                coordinates: [22.7667, 86.2000]
            },
            {
                code: "ROU",
                name: "Rourkela Jn",
                scheduled_arr: "07:30 PM",
                scheduled_dep: "07:38 PM",
                predicted_arr: "07:32 PM",
                predicted_dep: "07:40 PM",
                platform: "1",
                delay_mins: 2,
                halt_mins: 8,
                distance_km: 413,
                status: "departed",
                delay_attribution: "Minor signal headway",
                coordinates: [22.2253, 84.8536]
            },
            {
                code: "BSP",
                name: "Bilaspur Jn",
                scheduled_arr: "11:55 PM",
                scheduled_dep: "12:10 AM",
                predicted_arr: "12:00 AM",
                predicted_dep: "12:15 AM",
                platform: "4",
                delay_mins: 5,
                halt_mins: 15,
                distance_km: 718,
                status: "departed",
                delay_attribution: "Crew change completed",
                coordinates: [22.0797, 82.1409]
            },
            {
                code: "R",
                name: "Raipur Jn",
                scheduled_arr: "01:45 AM",
                scheduled_dep: "01:50 AM",
                predicted_arr: "01:52 AM",
                predicted_dep: "01:57 AM",
                platform: "1",
                delay_mins: 7,
                halt_mins: 5,
                distance_km: 829,
                status: "departed",
                delay_attribution: "Clear route progression",
                coordinates: [21.2514, 81.6296]
            },
            {
                code: "NGP",
                name: "Nagpur Jn",
                scheduled_arr: "07:40 AM",
                scheduled_dep: "07:45 AM",
                predicted_arr: "07:48 AM",
                predicted_dep: "07:53 AM",
                platform: "3",
                delay_mins: 8,
                halt_mins: 5,
                distance_km: 1131,
                status: "departed",
                delay_attribution: "Minor sectional crossing",
                coordinates: [21.1528, 79.0882]
            },
            {
                code: "BSL",
                name: "Bhusaval Jn",
                scheduled_arr: "01:10 PM",
                scheduled_dep: "01:15 PM",
                predicted_arr: "01:25 PM",
                predicted_dep: "01:30 PM",
                platform: "1",
                delay_mins: 15,
                halt_mins: 5,
                distance_km: 1524,
                status: "departed",
                delay_attribution: "Platform track maintenance",
                coordinates: [21.0455, 75.7885]
            },
            {
                code: "JL",
                name: "Jalgaon Jn",
                scheduled_arr: "01:43 PM",
                scheduled_dep: "01:45 PM",
                predicted_arr: "02:00 PM",
                predicted_dep: "02:02 PM",
                platform: "2",
                delay_mins: 17,
                halt_mins: 2,
                distance_km: 1548,
                status: "departed",
                delay_attribution: "Departed after junction clearance",
                coordinates: [21.0077, 75.5626]
            },
            {
                code: "NK",
                name: "Nashik Road",
                scheduled_arr: "04:10 PM",
                scheduled_dep: "04:15 PM",
                predicted_arr: "04:32 PM",
                predicted_dep: "04:37 PM",
                platform: "3",
                delay_mins: 22,
                halt_mins: 5,
                distance_km: 1781,
                status: "approaching",
                delay_attribution: "Manmad outer signal hold & Ghat weather precautions",
                coordinates: [19.9575, 73.8340]
            },
            {
                code: "KYN",
                name: "Kalyan Jn",
                scheduled_arr: "07:42 PM",
                scheduled_dep: "07:45 PM",
                predicted_arr: "08:06 PM",
                predicted_dep: "08:09 PM",
                platform: "5",
                delay_mins: 24,
                halt_mins: 3,
                distance_km: 1914,
                status: "upcoming",
                delay_attribution: "Suburban corridor headway density",
                coordinates: [19.2437, 73.1355]
            },
            {
                code: "CSMT",
                name: "Mumbai CSMT",
                scheduled_arr: "09:20 PM",
                scheduled_dep: "DEST",
                predicted_arr: "09:42 PM",
                predicted_dep: "DEST",
                platform: "18",
                delay_mins: 22,
                halt_mins: 0,
                distance_km: 1968,
                status: "upcoming",
                delay_attribution: "Final terminal arrival estimate",
                coordinates: [18.9402, 72.8356]
            }
        ],
        passenger_alerts: [
            {
                id: "alt_201",
                severity: "attention",
                title: "Delay Alert (+22 min)",
                message: "Running 22 mins behind schedule due to junction precedence and wet rail speed restrictions.",
                time: "10m ago",
                icon: "fa-triangle-exclamation"
            },
            {
                id: "alt_202",
                severity: "info",
                title: "Igatpuri - Kasara Ghat Notice",
                message: "Banker locomotives attached for descending ghat section. Expect smooth controlled transit.",
                time: "35m ago",
                icon: "fa-mountain"
            }
        ]
    },

    "22436": {
        train_number: "22436",
        train_name: "New Delhi - Varanasi Vande Bharat Express",
        short_name: "Vande Bharat Express",
        train_type: "Vande Bharat Express",
        source: "New Delhi (NDLS)",
        source_code: "NDLS",
        destination: "Varanasi Jn (BSB)",
        destination_code: "BSB",
        zone: "Northern Railway (NR)",
        total_distance_km: 759,
        distance_covered_km: 440,
        distance_remaining_km: 319,
        avg_speed_kmh: 95,
        current_status: "Train is running",
        current_status_code: "RUNNING",
        current_location: "Approaching Kanpur Central (Over Ganga Bridge)",
        current_section: "Aligarh - Kanpur High-Speed Trunk Section (NCR)",
        current_coordinates: [26.4670, 80.3500],
        heading_deg: 110,
        current_speed_kmh: 128,
        max_permissible_speed: 130,
        current_delay_mins: 0,
        destination_delay_impact_mins: 0,
        delay_impact_explanation: "High-priority green corridor assigned. Predicted on-time arrival at Varanasi Junction.",
        confidence_level: "High",
        confidence_pct: 98,
        arrival_window: "02:00 PM – 02:06 PM",
        scheduled_destination_eta: "02:00 PM",
        predicted_destination_eta: "02:00 PM",
        last_updated: "Simulated just now",
        last_updated_time: "18:42:25 IST",
        journey_progress_pct: 58,
        next_station: {
            code: "CNB",
            name: "Kanpur Central",
            distance_km: 8,
            expected_eta: "10:08 AM",
            scheduled_eta: "10:08 AM",
            platform: "1",
            stoppage_time: "5 min"
        },
        eta_factors: [
            {
                id: "gps_telemetry",
                code: "F01",
                name: "Live GPS & Train Telemetry",
                category: "Real-Time Telemetry",
                is_active: true,
                impact_level: "Positive (Time Saved)",
                delay_impact_mins: 0,
                passenger_explanation: "Train is maintaining optimal 128 km/h cruising speed along the dedicated Northern corridor.",
                technical_detail: "Telemetry confirms 98.4% timekeeping across all monitored blocks."
            },
            {
                id: "signal_aspects",
                code: "F02",
                name: "Signal Aspects & Block Halts",
                category: "Signaling & Interlocking",
                is_active: false,
                impact_level: "Nominal",
                delay_impact_mins: 0,
                passenger_explanation: "Green corridor clearance with automatic block signaling active.",
                technical_detail: "All ahead signals showing double green (Clear)."
            }
        ],
        stations: [
            {
                code: "NDLS",
                name: "New Delhi",
                scheduled_arr: "START",
                scheduled_dep: "06:00 AM",
                predicted_arr: "START",
                predicted_dep: "06:00 AM",
                platform: "16",
                delay_mins: 0,
                halt_mins: 0,
                distance_km: 0,
                status: "departed",
                delay_attribution: "Departed on-time",
                coordinates: [28.6139, 77.2090]
            },
            {
                code: "CNB",
                name: "Kanpur Central",
                scheduled_arr: "10:08 AM",
                scheduled_dep: "10:13 AM",
                predicted_arr: "10:08 AM",
                predicted_dep: "10:13 AM",
                platform: "1",
                delay_mins: 0,
                halt_mins: 5,
                distance_km: 440,
                status: "approaching",
                delay_attribution: "On-time arrival on dedicated high-speed line",
                coordinates: [26.4539, 80.3507]
            },
            {
                code: "PRYJ",
                name: "Prayagraj Jn",
                scheduled_arr: "12:08 PM",
                scheduled_dep: "12:10 PM",
                predicted_arr: "12:08 PM",
                predicted_dep: "12:10 PM",
                platform: "6",
                delay_mins: 0,
                halt_mins: 2,
                distance_km: 635,
                status: "upcoming",
                delay_attribution: "Green signal path programmed",
                coordinates: [25.4358, 81.8463]
            },
            {
                code: "BSB",
                name: "Varanasi Jn",
                scheduled_arr: "02:00 PM",
                scheduled_dep: "DEST",
                predicted_arr: "02:00 PM",
                predicted_dep: "DEST",
                platform: "1",
                delay_mins: 0,
                halt_mins: 0,
                distance_km: 759,
                status: "upcoming",
                delay_attribution: "Right-time destination arrival forecast",
                coordinates: [25.3268, 82.9863]
            }
        ],
        passenger_alerts: [
            {
                id: "alt_301",
                severity: "info",
                title: "Right Time Operation",
                message: "Vande Bharat Express is maintaining perfect schedule on the high-speed Delhi-Kanpur section.",
                time: "Just now",
                icon: "fa-circle-check"
            }
        ]
    },

    "12002": {
        train_number: "12002",
        train_name: "New Delhi - Bhopal Rani Kamlapati Shatabdi Express",
        short_name: "Bhopal Shatabdi",
        train_type: "Shatabdi Express",
        source: "New Delhi (NDLS)",
        source_code: "NDLS",
        destination: "Rani Kamlapati (RKMP)",
        destination_code: "RKMP",
        zone: "Northern Railway (NR)",
        total_distance_km: 708,
        distance_covered_km: 199,
        distance_remaining_km: 509,
        avg_speed_kmh: 84,
        current_status: "Train is running",
        current_status_code: "RUNNING",
        current_location: "Passing Mathura Jn (Km 141.2)",
        current_section: "Palwal - Mathura 3rd Line (NCR)",
        current_coordinates: [27.4924, 77.6737],
        heading_deg: 165,
        current_speed_kmh: 122,
        max_permissible_speed: 150,
        current_delay_mins: 6,
        destination_delay_impact_mins: 2,
        delay_impact_explanation: "High speed clearance on the Agra-Gwalior 150 km/h stretch will absorb 4 minutes of current delay.",
        confidence_level: "High",
        confidence_pct: 95,
        arrival_window: "02:22 PM – 02:30 PM",
        scheduled_destination_eta: "02:25 PM",
        predicted_destination_eta: "02:27 PM",
        last_updated: "Simulated 1 min ago",
        last_updated_time: "18:42:00 IST",
        journey_progress_pct: 28,
        next_station: {
            code: "AGC",
            name: "Agra Cantt",
            distance_km: 54,
            expected_eta: "07:56 AM",
            scheduled_eta: "07:50 AM",
            platform: "1",
            stoppage_time: "5 min"
        },
        eta_factors: [
            {
                id: "level_crossings",
                code: "F11",
                name: "Level-Crossing Gate Clearance",
                category: "Interlocking",
                is_active: true,
                impact_level: "Moderate impact",
                delay_impact_mins: 4,
                passenger_explanation: "Brief road traffic delay at a level-crossing gate near Kosi Kalan.",
                technical_detail: "Interlocking signal opened 3 minutes late for road vehicular clearance."
            },
            {
                id: "sectional_runtime",
                code: "F03",
                name: "Average Sectional Running Time",
                category: "Section Performance",
                is_active: true,
                impact_level: "Positive (Time Saved)",
                delay_impact_mins: -4,
                passenger_explanation: "Approaching Agra Cantt to Gwalior section with 150 km/h high-speed buffer recovery.",
                technical_detail: "Section MPS allows 4 mins slack buffer recovery."
            }
        ],
        stations: [
            {
                code: "NDLS",
                name: "New Delhi",
                scheduled_arr: "START",
                scheduled_dep: "06:00 AM",
                predicted_arr: "START",
                predicted_dep: "06:00 AM",
                platform: "1",
                delay_mins: 0,
                halt_mins: 0,
                distance_km: 0,
                status: "departed",
                delay_attribution: "Departed on-time",
                coordinates: [28.6139, 77.2090]
            },
            {
                code: "AGC",
                name: "Agra Cantt",
                scheduled_arr: "07:50 AM",
                scheduled_dep: "07:55 AM",
                predicted_arr: "07:56 AM",
                predicted_dep: "08:01 AM",
                platform: "1",
                delay_mins: 6,
                halt_mins: 5,
                distance_km: 199,
                status: "approaching",
                delay_attribution: "Level-crossing gate opening delay near Kosi Kalan",
                coordinates: [27.1574, 78.0068]
            },
            {
                code: "GWL",
                name: "Gwalior Jn",
                scheduled_arr: "09:23 AM",
                scheduled_dep: "09:28 AM",
                predicted_arr: "09:25 AM",
                predicted_dep: "09:30 AM",
                platform: "1",
                delay_mins: 2,
                halt_mins: 5,
                distance_km: 318,
                status: "upcoming",
                delay_attribution: "High speed 150 km/h recovery in Agra-Gwalior block",
                coordinates: [26.2183, 78.1828]
            },
            {
                code: "VGLJ",
                name: "VGL Jhansi Jn",
                scheduled_arr: "10:40 AM",
                scheduled_dep: "10:48 AM",
                predicted_arr: "10:41 AM",
                predicted_dep: "10:49 AM",
                platform: "2",
                delay_mins: 1,
                halt_mins: 8,
                distance_km: 415,
                status: "upcoming",
                delay_attribution: "On track with scheduled envelope",
                coordinates: [25.4484, 78.5685]
            },
            {
                code: "RKMP",
                name: "Rani Kamlapati",
                scheduled_arr: "02:25 PM",
                scheduled_dep: "DEST",
                predicted_arr: "02:27 PM",
                predicted_dep: "DEST",
                platform: "1",
                delay_mins: 2,
                halt_mins: 0,
                distance_km: 708,
                status: "upcoming",
                delay_attribution: "Near right-time destination arrival",
                coordinates: [23.2120, 77.4410]
            }
        ],
        passenger_alerts: [
            {
                id: "alt_401",
                severity: "info",
                title: "Buffer Recovery Expected",
                message: "Minor 6 min gate delay will be recovered on the 150 km/h Agra-Gwalior stretch.",
                time: "8m ago",
                icon: "fa-bolt"
            }
        ]
    },

    "12259": {
        train_number: "12259",
        train_name: "Sealdah - Bikaner AC Duronto Express",
        short_name: "Duronto Express",
        train_type: "Duronto Express",
        source: "Sealdah (SDAH)",
        source_code: "SDAH",
        destination: "New Delhi (NDLS)",
        destination_code: "NDLS",
        zone: "Eastern Railway (ER)",
        total_distance_km: 1453,
        distance_covered_km: 1210,
        distance_remaining_km: 243,
        avg_speed_kmh: 88,
        current_status: "Train is running",
        current_status_code: "RUNNING",
        current_location: "Approaching New Delhi Outer",
        current_section: "Kanpur - Ghaziabad Dedicated Track",
        current_coordinates: [28.4200, 77.4000],
        heading_deg: 320,
        current_speed_kmh: 88,
        max_permissible_speed: 130,
        current_delay_mins: 20,
        destination_delay_impact_mins: 20,
        delay_impact_explanation: "Caution signal aspect approaching Ghaziabad yard.",
        confidence_level: "High",
        confidence_pct: 92,
        arrival_window: "10:55 AM – 11:15 AM",
        scheduled_destination_eta: "10:45 AM",
        predicted_destination_eta: "11:05 AM",
        last_updated: "Simulated just now",
        last_updated_time: "18:43:00 IST",
        journey_progress_pct: 83,
        next_station: {
            code: "NDLS",
            name: "New Delhi",
            distance_km: 33,
            expected_eta: "11:05 AM",
            scheduled_eta: "10:45 AM",
            platform: "4",
            stoppage_time: "DEST"
        },
        eta_factors: [
            {
                id: "downstream_congestion",
                code: "F06",
                name: "Downstream Track Congestion",
                category: "Traffic Density",
                is_active: true,
                impact_level: "High impact",
                delay_impact_mins: 14,
                passenger_explanation: "Platform line clearing delays at New Delhi terminal.",
                technical_detail: "Terminal congestion at NDLS yard."
            },
            {
                id: "speed_restrictions",
                code: "F07",
                name: "Temporary Speed Restriction (TSR)",
                category: "Track Infrastructure",
                is_active: true,
                impact_level: "Moderate impact",
                delay_impact_mins: 6,
                passenger_explanation: "TSR 30 km/h on Ghaziabad approach curve.",
                technical_detail: "TSR 30 km/h due to turnout maintenance."
            }
        ],
        stations: [
            {
                code: "SDAH",
                name: "Sealdah",
                scheduled_arr: "START",
                scheduled_dep: "05:00 PM",
                predicted_arr: "START",
                predicted_dep: "05:00 PM",
                platform: "9",
                delay_mins: 0,
                halt_mins: 0,
                distance_km: 0,
                status: "departed",
                delay_attribution: "Departed on-time from origin",
                coordinates: [22.5697, 88.3697]
            },
            {
                code: "DHN",
                name: "Dhanbad Jn",
                scheduled_arr: "08:50 PM",
                scheduled_dep: "08:55 PM",
                predicted_arr: "08:50 PM",
                predicted_dep: "08:55 PM",
                platform: "2",
                delay_mins: 0,
                halt_mins: 5,
                distance_km: 266,
                status: "departed",
                delay_attribution: "Clear line progression",
                coordinates: [23.7957, 86.4304]
            },
            {
                code: "DDU",
                name: "Pt. DD Upadhyaya Jn",
                scheduled_arr: "01:25 AM",
                scheduled_dep: "01:35 AM",
                predicted_arr: "01:30 AM",
                predicted_dep: "01:40 AM",
                platform: "6",
                delay_mins: 5,
                halt_mins: 10,
                distance_km: 680,
                status: "departed",
                delay_attribution: "Yard routing precedence",
                coordinates: [25.2818, 83.1207]
            },
            {
                code: "CNB",
                name: "Kanpur Central",
                scheduled_arr: "05:30 AM",
                scheduled_dep: "05:35 AM",
                predicted_arr: "05:42 AM",
                predicted_dep: "05:47 AM",
                platform: "1",
                delay_mins: 12,
                halt_mins: 5,
                distance_km: 1028,
                status: "departed",
                delay_attribution: "Sectional cautionary aspect",
                coordinates: [26.4539, 80.3507]
            },
            {
                code: "NDLS",
                name: "New Delhi",
                scheduled_arr: "10:45 AM",
                scheduled_dep: "DEST",
                predicted_arr: "11:05 AM",
                predicted_dep: "DEST",
                platform: "4",
                delay_mins: 20,
                halt_mins: 0,
                distance_km: 1453,
                status: "upcoming",
                delay_attribution: "Terminal approach congestion",
                coordinates: [28.6139, 77.2090]
            }
        ],
        passenger_alerts: [
            {
                id: "alt_501",
                severity: "attention",
                title: "Terminal Approach Delay (+20 min)",
                message: "Train is holding at Ghaziabad outer awaiting platform line 4 clearance at New Delhi.",
                time: "3m ago",
                icon: "fa-clock"
            }
        ]
    }
};

class PassengerDataService {
    constructor() {
        this.trains = DEMO_TRAINS;
        this.recentStorageKey = 'gatisetu_recent_searches';
        
        // Ensure all trains have valid route polylines from their station coordinates
        Object.values(this.trains).forEach(train => {
            if (!train.route_polyline || train.route_polyline.length === 0) {
                train.route_polyline = (train.stations || [])
                    .filter(s => s.coordinates && s.coordinates.length === 2)
                    .map(s => s.coordinates);
            }
        });
    }

    interpolateAlongRoute(polyline, progressPct) {
        if (!polyline || polyline.length === 0) return [22.0, 75.0];
        if (polyline.length === 1 || progressPct <= 0) return [...polyline[0]];
        if (progressPct >= 100) return [...polyline[polyline.length - 1]];

        const segDists = [];
        let totalDist = 0;
        for (let i = 0; i < polyline.length - 1; i++) {
            const [lat1, lon1] = polyline[i];
            const [lat2, lon2] = polyline[i + 1];
            const d = Math.sqrt(Math.pow(lat2 - lat1, 2) + Math.pow((lon2 - lon1) * 0.9, 2));
            segDists.push(d);
            totalDist += d;
        }

        if (totalDist === 0) return [...polyline[0]];

        const targetDist = (progressPct / 100) * totalDist;
        let accum = 0;
        for (let i = 0; i < segDists.length; i++) {
            const d = segDists[i];
            if (accum + d >= targetDist) {
                const segT = d > 0 ? (targetDist - accum) / d : 0;
                const lat = polyline[i][0] + segT * (polyline[i + 1][0] - polyline[i][0]);
                const lon = polyline[i][1] + segT * (polyline[i + 1][1] - polyline[i][1]);
                return [Number(lat.toFixed(4)), Number(lon.toFixed(4))];
            }
            accum += d;
        }
        return [...polyline[polyline.length - 1]];
    }

    getTrainByNumber(trainNo) {
        if (!trainNo) return null;
        const cleanNo = trainNo.toString().trim();
        return this.trains[cleanNo] || null;
    }

    getTrain(trainNo) {
        return this.getTrainByNumber(trainNo);
    }

    getAllTrainsList() {
        return Object.values(this.trains);
    }

    getAvailableTrains() {
        return this.getAllTrainsList();
    }

    advanceSimulationTick(trainNo) {
        const train = this.getTrainByNumber(trainNo);
        if (!train) return null;

        const poly = train.route_polyline || (train.stations || []).filter(s => s.coordinates).map(s => s.coordinates);
        train.route_polyline = poly;

        let progress = train.journey_progress_pct || 38.0;
        progress = (progress + 0.35) < 99.0 ? (progress + 0.35) : 20.0;
        train.journey_progress_pct = Number(progress.toFixed(1));

        train.current_coordinates = this.interpolateAlongRoute(poly, progress);
        train.current_speed_kmh = Math.max(40, Math.min(130, (train.current_speed_kmh || 100) + (Math.random() > 0.5 ? 1 : -1)));
        return train;
    }

    getRecentSearches() {
        try {
            const raw = localStorage.getItem(this.recentStorageKey);
            return raw ? JSON.parse(raw) : [
                { train_number: "12951", train_name: "Mumbai - New Delhi Tejas Rajdhani Express" },
                { train_number: "12860", train_name: "Howrah - Mumbai CSMT Gitanjali Express" },
                { train_number: "22436", train_name: "New Delhi - Varanasi Vande Bharat" }
            ];
        } catch (e) {
            return [];
        }
    }

    saveRecentSearch(train) {
        if (!train) return;
        try {
            let list = this.getRecentSearches();
            list = list.filter(item => item.train_number !== train.train_number);
            list.unshift({
                train_number: train.train_number,
                train_name: train.train_name,
                source: train.source,
                destination: train.destination
            });
            if (list.length > 5) list = list.slice(0, 5);
            localStorage.setItem(this.recentStorageKey, JSON.stringify(list));
        } catch (e) {
            console.warn('LocalStorage error', e);
        }
    }

    clearRecentSearches() {
        try {
            localStorage.removeItem(this.recentStorageKey);
        } catch (e) {}
    }
}

// Attach globally
window.dataService = new PassengerDataService();
window.DEMO_TRAINS = DEMO_TRAINS;

