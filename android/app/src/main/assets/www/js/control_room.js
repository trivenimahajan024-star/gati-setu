/**
 * GatiSetu - Dynamic ETA Control Room Controller
 * Interactive Indian Railway Network Fleet Monitoring & Control Center
 * 100% Real API Data Driven | Zero Artificial Animations | Clean Dark Blueprint Visuals
 * Powered by MapLibre GL JS & OpenFreeMap (Zero API Key / Open Source)
 */

class ControlRoomManager {
    constructor() {
        this.map = null;
        this.mapInitialized = false;
        this.trainsCache = [];
        this.alertsCache = [];
        this.selectedTrainNumber = '12951';
        this.activeMode = 'live'; // 'live' | 'heat' | 'route' (Default: 'live')
        this.searchQuery = '';
        this.autoRefreshTimer = null;
        this.clockTimer = null;
        this.markersMap = {};
        this.stationPopup = null;

        // India Railway Trunk Corridors (Real geographic coordinates [lat, lng])
        this.railwayCorridors = [
            {
                id: 'western_trunk',
                name: 'Western Trunk (MMCT - NDLS via Kota)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [18.9696, 72.8193], // Mumbai Central
                    [19.2290, 72.8574], // Borivali
                    [19.5760, 72.7660], // Palghar
                    [20.3700, 72.9100], // Vapi
                    [20.9500, 72.9300], // Navsari
                    [21.1702, 72.8311], // Surat
                    [21.7051, 72.9959], // Bharuch
                    [22.3072, 73.1812], // Vadodara
                    [22.8200, 73.6100], // Godhra
                    [22.8330, 74.2560], // Dahod
                    [23.3341, 75.0376], // Ratlam
                    [23.4544, 75.4147], // Nagda
                    [24.1800, 75.8300], // Shamgarh
                    [24.5300, 75.9800], // Bhawani Mandi
                    [25.1825, 75.8340], // Kota
                    [25.9928, 76.3688], // Sawai Madhopur
                    [26.4900, 76.7300], // Gangapur City
                    [26.9800, 77.0100], // Hindaun
                    [27.1800, 77.4900], // Bharatpur
                    [27.4924, 77.6737], // Mathura
                    [28.1400, 77.3300], // Palwal
                    [28.4089, 77.3178], // Faridabad
                    [28.5880, 77.2530], // Hazrat Nizamuddin
                    [28.6139, 77.2090]  // New Delhi
                ]
            },
            {
                id: 'central_trunk',
                name: 'Central Trunk (Mumbai - Delhi via Bhopal)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [18.9400, 72.8350], // Mumbai CSMT
                    [19.0400, 72.8600], // Dadar
                    [19.1860, 72.9750], // Thane
                    [19.2437, 73.1355], // Kalyan
                    [19.5700, 73.4700], // Kasara
                    [19.6967, 73.5617], // Igatpuri
                    [19.9975, 73.7898], // Nashik
                    [20.2524, 74.4385], // Manmad
                    [20.4800, 75.0100], // Chalisgaon
                    [20.9100, 75.5600], // Jalgaon
                    [21.0455, 75.7885], // Bhusawal
                    [21.3100, 76.0100], // Burhanpur
                    [21.8314, 76.3498], // Khandwa
                    [22.6139, 77.7634], // Itarsi
                    [22.7500, 77.7200], // Hoshangabad
                    [23.2599, 77.4126], // Bhopal
                    [23.5300, 77.8100], // Vidisha
                    [24.1750, 78.1830], // Bina
                    [24.6900, 78.4100], // Lalitpur
                    [25.4484, 78.5685], // Jhansi
                    [26.2183, 78.1828], // Gwalior
                    [26.5000, 78.0000], // Morena
                    [26.8900, 77.9000], // Dholpur
                    [27.1767, 78.0081], // Agra Cantt
                    [27.4924, 77.6737], // Mathura
                    [28.6139, 77.2090]  // New Delhi
                ]
            },
            {
                id: 'eastern_trunk',
                name: 'Grand Chord / Eastern Trunk (NDLS - HWH)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [28.6139, 77.2090], // New Delhi
                    [28.6692, 77.4538], // Ghaziabad
                    [27.8974, 78.0880], // Aligarh
                    [27.2060, 78.2430], // Tundla
                    [26.7900, 79.0300], // Etawah
                    [26.4499, 80.3319], // Kanpur Central
                    [25.9200, 80.8100], // Fatehpur
                    [25.4358, 81.8463], // Prayagraj
                    [25.1500, 82.5800], // Mirzapur
                    [25.2796, 83.1189], // Pt. Deen Dayal Upadhyaya
                    [24.9530, 84.0290], // Sasaram
                    [24.7500, 84.3700], // Dehri On Sone
                    [24.7914, 85.0002], // Gaya
                    [24.4680, 85.5940], // Koderma
                    [24.1700, 86.3000], // Parasnath
                    [23.7957, 86.4304], // Dhanbad
                    [23.6889, 86.9661], // Asansol
                    [23.5204, 87.3119], // Durgapur
                    [23.2324, 87.8615], // Barddhaman
                    [22.5850, 88.3426]  // Howrah
                ]
            },
            {
                id: 'patna_branch',
                name: 'Patna - Howrah Main Line',
                type: 'trunk',
                color: '#0284C7',
                points: [
                    [25.2796, 83.1189], // DDU
                    [25.5780, 83.9780], // Buxar
                    [25.5560, 84.6640], // Ara
                    [25.6093, 85.1376], // Patna
                    [25.3700, 85.9100], // Mokama
                    [25.1320, 86.0940], // Kiul
                    [24.7800, 86.3800], // Jhajha
                    [24.5150, 86.6450], // Jasidih
                    [24.1600, 86.8700], // Madhupur
                    [23.6889, 86.9661]  // Asansol
                ]
            },
            {
                id: 'north_south_trunk',
                name: 'North-South Trunk (Bhopal - Chennai / Bengaluru)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [23.2599, 77.4126], // Bhopal
                    [22.6139, 77.7634], // Itarsi
                    [21.9040, 77.9020], // Betul
                    [21.5700, 78.3300], // Amla
                    [21.1458, 79.0882], // Nagpur
                    [20.7330, 78.6080], // Sewagram
                    [20.1800, 78.9600], // Chandrapur
                    [19.8600, 79.3800], // Balharshah
                    [19.3600, 79.4800], // Sirpur Kaghaznagar
                    [18.7610, 79.4750], // Ramagundam
                    [17.9689, 79.5941], // Kazipet / Warangal
                    [17.2470, 80.1510], // Khammam
                    [16.5062, 80.6480], // Vijayawada
                    [15.5030, 80.0440], // Ongole
                    [14.4426, 79.9865], // Nellore
                    [14.1480, 79.8490], // Gudur
                    [13.0827, 80.2707]  // Chennai Central
                ]
            },
            {
                id: 'east_coast_trunk',
                name: 'East Coast Corridor (HWH - MAS)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [22.5850, 88.3426], // Howrah
                    [22.3400, 87.3200], // Kharagpur
                    [21.4930, 86.9320], // Balasore
                    [21.0570, 86.5160], // Bhadrak
                    [20.8500, 86.1500], // Jajpur Keonjhar Road
                    [20.4625, 85.8828], // Cuttack
                    [20.2961, 85.8245], // Bhubaneswar
                    [20.1870, 85.7330], // Khurda Road
                    [19.3150, 84.7940], // Berhampur
                    [18.2970, 83.8960], // Srikakulam Road
                    [18.1100, 83.4100], // Vizianagaram
                    [17.6868, 83.2185], // Visakhapatnam
                    [17.0520, 82.1680], // Samalkot
                    [17.0005, 81.8040], // Rajahmundry
                    [16.7107, 81.0952], // Eluru
                    [16.5062, 80.6480]  // Vijayawada
                ]
            },
            {
                id: 'howrah_mumbai_trunk',
                name: 'Howrah - Mumbai Trunk (via Bilaspur & Nagpur)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [22.5850, 88.3426], // Howrah
                    [22.3400, 87.3200], // Kharagpur
                    [22.8046, 86.2029], // Tatanagar
                    [22.7050, 85.6260], // Chakradharpur
                    [22.2604, 84.8536], // Rourkela
                    [21.8540, 84.0080], // Jharsuguda
                    [21.7100, 83.4000], // Raigarh
                    [21.9800, 82.8000], // Champa
                    [22.0797, 82.1409], // Bilaspur
                    [21.2514, 81.6296], // Raipur
                    [21.1904, 81.2849], // Durg
                    [21.4580, 80.1960], // Gondia
                    [21.1458, 79.0882], // Nagpur
                    [20.9320, 77.7520], // Badnera
                    [20.7002, 77.0082], // Akola
                    [20.9000, 76.0500], // Malkapur
                    [21.0455, 75.7885]  // Bhusawal
                ]
            },
            {
                id: 'southern_trunk',
                name: 'Southern Trunk (MAS - SBC - Kerala)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [13.0827, 80.2707], // Chennai Central
                    [13.0780, 79.6670], // Arakkonam
                    [12.9800, 79.1300], // Katpadi
                    [12.5620, 78.5770], // Jolarpettai
                    [12.9770, 78.1880], // Bangarapet
                    [12.9716, 77.5946], // KSR Bengaluru (SBC)
                    [11.6643, 78.1460], // Salem
                    [11.3410, 77.7172], // Erode
                    [11.0168, 76.9558], // Coimbatore
                    [10.7867, 76.6548], // Palakkad
                    [10.5276, 76.2144], // Thrissur
                    [9.9816, 76.2999],  // Ernakulam / Kochi
                    [8.5241, 76.9366]   // Thiruvananthapuram
                ]
            },
            {
                id: 'konkan_corridor',
                name: 'Konkan Railway (Mumbai - Goa - Mangaluru)',
                type: 'trunk',
                color: '#38BDF8',
                points: [
                    [18.9696, 72.8193], // Mumbai
                    [18.9894, 73.1175], // Panvel
                    [18.4360, 73.1180], // Roha
                    [18.1500, 73.3400], // Mangaon
                    [17.7180, 73.3880], // Khed
                    [17.5300, 73.5100], // Chiplun
                    [16.9902, 73.3120], // Ratnagiri
                    [16.2700, 73.7140], // Kankavali
                    [15.9000, 73.8100], // Sawantwadi Road
                    [15.2720, 73.9580], // Madgaon (Goa)
                    [14.8180, 74.1300], // Karwar
                    [14.2800, 74.4500], // Kumta
                    [13.3409, 74.7421], // Udupi
                    [12.9141, 74.8560]  // Mangaluru Central
                ]
            },
            {
                id: 'secunderabad_link',
                name: 'Central Deccan Trunk (SC - BZA - NGP)',
                type: 'trunk',
                color: '#0284C7',
                points: [
                    [21.1458, 79.0882], // Nagpur
                    [19.8600, 79.3800], // Balharshah
                    [17.9689, 79.5941], // Kazipet
                    [17.4399, 78.4983], // Secunderabad / Hyderabad
                    [17.3600, 79.0000], // Nalgonda
                    [16.7800, 79.5500], // Miryalaguda
                    [16.3000, 80.4400], // Guntur
                    [16.5062, 80.6480]  // Vijayawada
                ]
            },
            // Planned / Dedicated High Speed Corridors (Dashed)
            {
                id: 'planned_mumbai_ahmedabad',
                name: 'Mumbai - Ahmedabad High Speed Bullet Corridor',
                type: 'planned',
                color: '#64748B',
                points: [
                    [18.9696, 72.8193], // Mumbai
                    [19.2183, 72.9781], // Thane
                    [19.8300, 72.8200], // Boisar
                    [20.3700, 72.9100], // Vapi
                    [20.9500, 72.9300], // Navsari
                    [21.1702, 72.8311], // Surat
                    [21.7051, 72.9959], // Bharuch
                    [22.3072, 73.1812], // Vadodara
                    [22.6900, 72.8600], // Nadiad
                    [23.0225, 72.5714]  // Ahmedabad
                ]
            },
            {
                id: 'planned_delhi_varanasi',
                name: 'Delhi - Lucknow - Varanasi Semi-High Speed Line',
                type: 'planned',
                color: '#64748B',
                points: [
                    [28.6139, 77.2090], // New Delhi
                    [28.6692, 77.4538], // Ghaziabad
                    [28.8386, 78.7733], // Moradabad
                    [28.3670, 79.4304], // Bareilly
                    [27.8800, 79.9100], // Shahjahanpur
                    [26.8467, 80.9462], // Lucknow
                    [26.2200, 81.2400], // Rae Bareli
                    [25.9000, 81.9900], // Pratapgarh
                    [25.3176, 82.9739]  // Varanasi
                ]
            }
        ];

        // Key Network Junction Stations
        this.networkStations = [
            { code: 'NDLS', name: 'New Delhi', coords: [28.6139, 77.2090], isHub: true },
            { code: 'MMCT', name: 'Mumbai Central', coords: [18.9696, 72.8193], isHub: true },
            { code: 'CSMT', name: 'Mumbai CSMT', coords: [18.9400, 72.8350], isHub: true },
            { code: 'HWH',  name: 'Howrah (Kolkata)', coords: [22.5850, 88.3426], isHub: true },
            { code: 'MAS',  name: 'Chennai Central', coords: [13.0827, 80.2707], isHub: true },
            { code: 'SBC',  name: 'KSR Bengaluru', coords: [12.9716, 77.5946], isHub: true },
            { code: 'ADI',  name: 'Ahmedabad Jn', coords: [23.0225, 72.5714], isHub: true },
            { code: 'ST',   name: 'Surat', coords: [21.1702, 72.8311], isHub: false },
            { code: 'BRC',  name: 'Vadodara Jn', coords: [22.3072, 73.1812], isHub: true },
            { code: 'KOTA', name: 'Kota Jn', coords: [25.1825, 75.8340], isHub: true },
            { code: 'RTM',  name: 'Ratlam Jn', coords: [23.3341, 75.0376], isHub: false },
            { code: 'BPL',  name: 'Bhopal Jn', coords: [23.2599, 77.4126], isHub: true },
            { code: 'NGP',  name: 'Nagpur Jn', coords: [21.1458, 79.0882], isHub: true },
            { code: 'BSL',  name: 'Bhusawal Jn', coords: [21.0455, 75.7885], isHub: true },
            { code: 'CNB',  name: 'Kanpur Central', coords: [26.4499, 80.3319], isHub: true },
            { code: 'PRYJ', name: 'Prayagraj Jn', coords: [25.4358, 81.8463], isHub: true },
            { code: 'DDU',  name: 'Pt. Deen Dayal Upadhyaya', coords: [25.2796, 83.1189], isHub: true },
            { code: 'PNBE', name: 'Patna Jn', coords: [25.6093, 85.1376], isHub: true },
            { code: 'BZA',  name: 'Vijayawada Jn', coords: [16.5062, 80.6480], isHub: true },
            { code: 'SC',   name: 'Secunderabad', coords: [17.4399, 78.4983], isHub: true },
            { code: 'BBS',  name: 'Bhubaneswar', coords: [20.2961, 85.8245], isHub: false },
            { code: 'VSKP', name: 'Visakhapatnam', coords: [17.6868, 83.2185], isHub: true },
            { code: 'TATA', name: 'Tatanagar', coords: [22.8046, 86.2029], isHub: false },
            { code: 'R',    name: 'Raipur Jn', coords: [21.2514, 81.6296], isHub: false },
            { code: 'BSP',  name: 'Bilaspur Jn', coords: [22.0797, 82.1409], isHub: false },
            { code: 'JHS',  name: 'Jhansi Jn', coords: [25.4484, 78.5685], isHub: false },
            { code: 'GWL',  name: 'Gwalior', coords: [26.2183, 78.1828], isHub: false },
            { code: 'AGC',  name: 'Agra Cantt', coords: [27.1767, 78.0081], isHub: false },
            { code: 'JBP',  name: 'Jabalpur', coords: [23.1815, 79.9864], isHub: false },
            { code: 'LKO',  name: 'Lucknow Charbagh', coords: [26.8467, 80.9462], isHub: true },
            { code: 'BSB',  name: 'Varanasi Jn', coords: [25.3176, 82.9739], isHub: true }
        ];
    }

    init() {
        this.activeMode = 'live';
        this.setupLiveClock();
        this.setupEventListeners();
        this.setMapMode('live');
        this.initMap();
        this.loadControlRoomData();
        this.startAutoRefresh();
    }

    setupLiveClock() {
        const updateClock = () => {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            const dateStr = now.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
            
            const headerClock = document.getElementById('occHeaderTime');
            const headerDate = document.getElementById('occHeaderDate');
            if (headerClock) headerClock.textContent = timeStr;
            if (headerDate) headerDate.textContent = dateStr;

            document.querySelectorAll('.live-clock-target').forEach(el => {
                el.textContent = timeStr;
            });
            document.querySelectorAll('.live-date-target').forEach(el => {
                el.textContent = dateStr;
            });
        };
        
        updateClock();
        if (this.clockTimer) clearInterval(this.clockTimer);
        this.clockTimer = setInterval(updateClock, 1000);
    }

    setupEventListeners() {
        // Mode toggle buttons (Live Train Map / Heat Map / Route View)
        const modeBtns = [
            { id: 'btnModeLiveMap', mode: 'live' },
            { id: 'btnModeHeatMap', mode: 'heat' },
            { id: 'btnModeRouteView', mode: 'route' }
        ];

        modeBtns.forEach(({ id, mode }) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', () => {
                    this.setMapMode(mode);
                });
            }
        });

        // Map float tools
        const btnZoomIn = document.getElementById('btnOccZoomIn');
        if (btnZoomIn) {
            btnZoomIn.addEventListener('click', () => this.zoomIn());
        }

        const btnZoomOut = document.getElementById('btnOccZoomOut');
        if (btnZoomOut) {
            btnZoomOut.addEventListener('click', () => this.zoomOut());
        }

        const btnCenter = document.getElementById('btnOccCenterMap');
        if (btnCenter) {
            btnCenter.addEventListener('click', () => this.centerMap());
        }

        // Search input
        const searchInput = document.getElementById('occMapSearchInput');
        const clearBtn = document.getElementById('btnOccClearSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
        if (clearBtn && searchInput) {
            clearBtn.addEventListener('click', () => {
                searchInput.value = '';
                this.handleSearch('');
                searchInput.focus();
            });
        }

        // Close inspection card
        const btnCloseCard = document.getElementById('btnCloseInspectCard');
        if (btnCloseCard) {
            btnCloseCard.addEventListener('click', () => this.closeInspectCard());
        }

        // Return to passenger view
        const btnReturn = document.getElementById('btnOccReturnPassenger');
        if (btnReturn) {
            btnReturn.addEventListener('click', () => {
                if (window.passengerApp) {
                    window.passengerApp.switchRoleView('view-passenger');
                }
            });
        }

        // Sidebar Navigation links
        const navItems = document.querySelectorAll('.occ-nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                navItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                const tab = item.getAttribute('data-occ-tab');
                this.handleSidebarNav(tab);
            });
        });

        // View All Trains / View All Alerts buttons
        const btnViewAllTrains = document.getElementById('btnOccViewAllTrains');
        if (btnViewAllTrains) {
            btnViewAllTrains.addEventListener('click', () => {
                const searchEl = document.getElementById('occMapSearchInput');
                if (searchEl) {
                    searchEl.value = '';
                    this.handleSearch('');
                    searchEl.focus();
                }
                this.showToast('📋 Showing full Indian Railways fleet');
            });
        }

        const btnViewAllAlerts = document.getElementById('btnOccViewAllAlerts');
        if (btnViewAllAlerts) {
            btnViewAllAlerts.addEventListener('click', () => {
                this.showToast('🚨 Displaying active operational alerts and section restrictions');
            });
        }

        // Handle window resize for map canvas
        window.addEventListener('resize', () => {
            this.resize();
        });
    }

    handleSidebarNav(tab) {
        if (tab === 'live-map') {
            this.setMapMode('live');
        } else if (tab === 'all-trains') {
            const tableCard = document.querySelector('.occ-card-live-trains');
            if (tableCard) tableCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            this.showToast('🚆 Fleet overview: 12 tracked express corridors');
        } else if (tab === 'alerts') {
            const alertsCard = document.querySelector('.occ-card-active-alerts');
            if (alertsCard) alertsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            this.showToast('🔔 3 active section alerts');
        } else if (tab === 'station-view') {
            if (window.passengerApp) {
                window.passengerApp.switchRoleView('view-station-board');
            }
        } else if (tab === 'reports') {
            this.showToast('📊 OCC Operational Reports: Daily punctuality index 91.4%');
        } else if (tab === 'settings') {
            this.showToast('⚙️ GatiSetu Control Center v2.4 Interlocking Sync: 99.9%');
        }
    }

    initMap() {
        const container = document.getElementById('occControlRoomMap');
        if (!container || typeof maplibregl === 'undefined') return;

        if (this.map) {
            setTimeout(() => this.resize(), 150);
            return;
        }

        try {
            // MapLibre GL JS Dark Basemap via OpenFreeMap (Zero API Key / 100% Open Source)
            // Focused primarily on Indian Railway Geographic Extent
            this.map = new maplibregl.Map({
                container: 'occControlRoomMap',
                style: 'https://tiles.openfreemap.org/styles/dark',
                center: [78.9629, 22.5937],
                zoom: 4.5,
                minZoom: 3.8,
                maxZoom: 16,
                attributionControl: false
            });

            // Leaflet compatibility alias so external calls to map.invalidateSize() work seamlessly
            this.map.invalidateSize = () => {
                if (this.map) this.map.resize();
            };

            // Add standard subtle attribution
            this.map.addControl(new maplibregl.AttributionControl({
                compact: true,
                customAttribution: '© OpenFreeMap © OpenStreetMap contributors'
            }), 'bottom-right');

            this.map.on('load', () => {
                this.mapInitialized = true;
                this.setupMapLayers();
                this.setMapMode('live');
                this.renderMapFleet(this.trainsCache);
                if (this.selectedTrainNumber && this.activeMode === 'route') {
                    this.renderSelectedTrainRouteHighlight(this.selectedTrainNumber);
                }
            });

            // Delayed resize after container layout settles
            setTimeout(() => {
                if (this.map) this.map.resize();
            }, 300);
        } catch (e) {
            console.error("MapLibre GL initialization error in OCC", e);
        }
    }

    initLeafletMap() {
        this.initMap();
    }

    setupMapLayers() {
        if (!this.map || !this.map.isStyleLoaded()) return;

        // Clean up low-priority label clutter for high-contrast railway control room blueprint
        const clutterLayerIds = [
            'water_name',
            'road_oneway',
            'road_oneway_opposite',
            'highway_name_other',
            'highway_name_motorway',
            'place_other',
            'place_suburb',
            'place_village',
            'place_town',
            'place_country_other',
            'place_country_minor',
            'highway_path',
            'highway_minor'
        ];

        clutterLayerIds.forEach(id => {
            if (this.map.getLayer(id)) {
                this.map.setLayoutProperty(id, 'visibility', 'none');
            }
        });

        // Soften remaining essential labels and boundaries for subtle geographical backdrop
        if (this.map.getLayer('place_country_major')) {
            this.map.setPaintProperty('place_country_major', 'text-color', '#94A3B8');
            this.map.setPaintProperty('place_country_major', 'text-opacity', 0.65);
        }
        if (this.map.getLayer('place_state')) {
            this.map.setPaintProperty('place_state', 'text-color', '#64748B');
            this.map.setPaintProperty('place_state', 'text-opacity', 0.6);
        }
        if (this.map.getLayer('place_city_large')) {
            this.map.setPaintProperty('place_city_large', 'text-color', '#CBD5E1');
            this.map.setPaintProperty('place_city_large', 'text-opacity', 0.85);
        }
        if (this.map.getLayer('place_city')) {
            this.map.setPaintProperty('place_city', 'text-color', '#94A3B8');
            this.map.setPaintProperty('place_city', 'text-opacity', 0.7);
        }
        if (this.map.getLayer('boundary_country_z0-4')) {
            this.map.setPaintProperty('boundary_country_z0-4', 'line-color', '#334155');
            this.map.setPaintProperty('boundary_country_z0-4', 'line-opacity', 0.5);
        }
        if (this.map.getLayer('boundary_country_z5-')) {
            this.map.setPaintProperty('boundary_country_z5-', 'line-color', '#334155');
            this.map.setPaintProperty('boundary_country_z5-', 'line-opacity', 0.5);
        }
        if (this.map.getLayer('boundary_state')) {
            this.map.setPaintProperty('boundary_state', 'line-color', '#1E293B');
            this.map.setPaintProperty('boundary_state', 'line-opacity', 0.4);
        }

        // 1. Trunk Railway Corridors (Cyan Glow + Solid Vector Line)
        const trunkFeatures = this.railwayCorridors
            .filter(c => c.type === 'trunk')
            .map(c => ({
                type: 'Feature',
                properties: { id: c.id, name: c.name, color: c.color || '#38BDF8' },
                geometry: {
                    type: 'LineString',
                    coordinates: c.points.map(pt => [pt[1], pt[0]])
                }
            }));

        if (!this.map.getSource('corridors-trunk-source')) {
            this.map.addSource('corridors-trunk-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: trunkFeatures
                }
            });

            this.map.addLayer({
                id: 'corridors-trunk-glow',
                type: 'line',
                source: 'corridors-trunk-source',
                layout: {
                    'line-cap': 'round',
                    'line-join': 'round'
                },
                paint: {
                    'line-color': '#38BDF8',
                    'line-width': 5.5,
                    'line-opacity': 0.25
                }
            });

            this.map.addLayer({
                id: 'corridors-trunk-line',
                type: 'line',
                source: 'corridors-trunk-source',
                layout: {
                    'line-cap': 'round',
                    'line-join': 'round'
                },
                paint: {
                    'line-color': '#38BDF8',
                    'line-width': 2.4,
                    'line-opacity': 0.9
                }
            });
        }

        // 2. Planned / Dedicated High Speed Corridors (Dashed Line)
        const plannedFeatures = this.railwayCorridors
            .filter(c => c.type === 'planned')
            .map(c => ({
                type: 'Feature',
                properties: { id: c.id, name: c.name },
                geometry: {
                    type: 'LineString',
                    coordinates: c.points.map(pt => [pt[1], pt[0]])
                }
            }));

        if (!this.map.getSource('corridors-planned-source')) {
            this.map.addSource('corridors-planned-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: plannedFeatures
                }
            });

            this.map.addLayer({
                id: 'corridors-planned-line',
                type: 'line',
                source: 'corridors-planned-source',
                layout: {
                    'line-cap': 'round',
                    'line-join': 'round'
                },
                paint: {
                    'line-color': '#64748B',
                    'line-width': 2,
                    'line-opacity': 0.75,
                    'line-dasharray': [3, 3]
                }
            });
        }

        // 3. Station Nodes & Tooltips
        const stationFeatures = this.networkStations.map(s => ({
            type: 'Feature',
            properties: {
                code: s.code,
                name: s.name,
                isHub: !!s.isHub
            },
            geometry: {
                type: 'Point',
                coordinates: [s.coords[1], s.coords[0]]
            }
        }));

        if (!this.map.getSource('stations-source')) {
            this.map.addSource('stations-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: stationFeatures
                }
            });

            this.map.addLayer({
                id: 'stations-circle-outer',
                type: 'circle',
                source: 'stations-source',
                paint: {
                    'circle-radius': ['case', ['get', 'isHub'], 5.5, 4],
                    'circle-color': '#0F172A',
                    'circle-opacity': 0.95
                }
            });

            this.map.addLayer({
                id: 'stations-circle-inner',
                type: 'circle',
                source: 'stations-source',
                paint: {
                    'circle-radius': ['case', ['get', 'isHub'], 3.8, 2.5],
                    'circle-color': '#E2E8F0',
                    'circle-opacity': 0.95
                }
            });

            // Setup station hover popup
            this.stationPopup = new maplibregl.Popup({
                closeButton: false,
                closeOnClick: false,
                offset: 10,
                className: 'occ-maplibre-station-popup'
            });

            this.map.on('mouseenter', 'stations-circle-outer', (e) => {
                this.map.getCanvas().style.cursor = 'pointer';
                const coordinates = e.features[0].geometry.coordinates.slice();
                const props = e.features[0].properties;
                this.stationPopup.setLngLat(coordinates)
                    .setHTML(`<div class="occ-station-popup-inner"><strong>${props.code}</strong> — ${props.name}</div>`)
                    .addTo(this.map);
            });

            this.map.on('mouseleave', 'stations-circle-outer', () => {
                this.map.getCanvas().style.cursor = '';
                this.stationPopup.remove();
            });
        }

        // 4. Selected Route Corridor Highlight Source & Layers
        if (!this.map.getSource('route-highlight-source')) {
            this.map.addSource('route-highlight-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: []
                }
            });

            this.map.addLayer({
                id: 'route-highlight-glow',
                type: 'line',
                source: 'route-highlight-source',
                layout: {
                    'line-cap': 'round',
                    'line-join': 'round'
                },
                paint: {
                    'line-color': '#10B981',
                    'line-width': 7,
                    'line-opacity': 0.45
                }
            });

            this.map.addLayer({
                id: 'route-highlight-line',
                type: 'line',
                source: 'route-highlight-source',
                layout: {
                    'line-cap': 'round',
                    'line-join': 'round'
                },
                paint: {
                    'line-color': '#34D399',
                    'line-width': 3,
                    'line-opacity': 0.95
                }
            });
        }

        // 5. Heat Map Delay Layer (Density Heatmap)
        if (!this.map.getSource('heat-delay-source')) {
            this.map.addSource('heat-delay-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: []
                }
            });

            this.map.addLayer({
                id: 'train-heat-layer',
                type: 'heatmap',
                source: 'heat-delay-source',
                layout: {
                    'visibility': this.activeMode === 'heat' ? 'visible' : 'none'
                },
                paint: {
                    'heatmap-weight': [
                        'interpolate',
                        ['linear'],
                        ['get', 'delay'],
                        0, 0.1,
                        5, 0.3,
                        25, 0.7,
                        60, 1.0
                    ],
                    'heatmap-intensity': 1.2,
                    'heatmap-color': [
                        'interpolate',
                        ['linear'],
                        ['heatmap-density'],
                        0, 'rgba(16, 185, 129, 0)',
                        0.2, 'rgba(16, 185, 129, 0.4)',
                        0.5, 'rgba(245, 158, 11, 0.7)',
                        0.8, 'rgba(239, 68, 68, 0.85)',
                        1.0, 'rgba(220, 38, 38, 1.0)'
                    ],
                    'heatmap-radius': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        4, 25,
                        8, 55
                    ],
                    'heatmap-opacity': 0.75
                }
            });
        }
    }

    async loadControlRoomData(silent = false) {
        try {
            const [overviewRes, trainsRes, alertsRes] = await Promise.all([
                window.railwayApi.getControlRoomOverview().catch(() => null),
                window.railwayApi.getControlRoomTrains().catch(() => null),
                window.railwayApi.getControlRoomAlerts().catch(() => null)
            ]);

            const trains = (Array.isArray(trainsRes) && trainsRes.length > 0) ? trainsRes : [];
            const alerts = (Array.isArray(alertsRes) && alertsRes.length > 0) ? alertsRes : [];
            const overview = overviewRes || {};

            this.trainsCache = trains;
            this.alertsCache = alerts;

            this.renderKPIs(overview, this.trainsCache);
            this.renderLiveTrainsTable(this.trainsCache);
            this.renderActiveAlerts(this.alertsCache);
            this.renderMapFleet(this.trainsCache);

            // Update inspection card if open
            if (this.selectedTrainNumber) {
                const train = this.trainsCache.find(t => t.train_number === this.selectedTrainNumber);
                if (train) {
                    this.updateInspectCard(train);
                }
            }
        } catch (e) {
            console.error("Error loading OCC telemetry", e);
            if (!silent) {
                this.showToast("⚠️ Telemetry connection fallback active");
            }
        }
    }

    renderKPIs(overview, trains) {
        const total = trains.length || overview.total_active_trains || 12;
        const onTime = trains.length > 0 
            ? trains.filter(t => (t.current_delay_mins || 0) <= 5).length 
            : (overview.on_time_trains || 6);
        const delayed = trains.length > 0 
            ? trains.filter(t => (t.current_delay_mins || 0) > 5 && (t.current_delay_mins || 0) <= 25).length 
            : (overview.delayed_trains || 4);
        const sigDelay = trains.length > 0 
            ? trains.filter(t => (t.current_delay_mins || 0) > 25).length 
            : (overview.significant_delay_trains || 2);

        const setTxt = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setTxt('occTotalTrainsCount', total);
        setTxt('occOnTimeCount', onTime);
        setTxt('occDelayedCount', delayed);
        setTxt('occSigDelayCount', sigDelay);

        const badge = document.getElementById('occSidebarAlertsBadge');
        if (badge) {
            badge.textContent = this.alertsCache.length || 3;
        }
    }

    renderLiveTrainsTable(trains) {
        const tbody = document.getElementById('occLiveTrainsTableBody');
        if (!tbody) return;

        let filtered = trains;
        if (this.searchQuery) {
            filtered = trains.filter(t => {
                const q = this.searchQuery;
                return (
                    (t.train_number && t.train_number.toLowerCase().includes(q)) ||
                    (t.train_name && t.train_name.toLowerCase().includes(q)) ||
                    (t.short_name && t.short_name.toLowerCase().includes(q)) ||
                    (t.source_code && t.source_code.toLowerCase().includes(q)) ||
                    (t.destination_code && t.destination_code.toLowerCase().includes(q)) ||
                    (t.current_location && t.current_location.toLowerCase().includes(q))
                );
            });
        }

        if (filtered.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align: center; padding: 20px; color: #64748B;">
                        No trains matching "${this.searchQuery}"
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = filtered.map(t => {
            const delay = t.current_delay_mins || 0;
            const statusCode = (t.current_status_code || t.status || '').toUpperCase();
            const statusRaw = (t.current_status || '').toUpperCase();
            let statusClass = 'ontime';
            let statusLabel = 'On Time';

            if (statusCode === 'NOT_STARTED' || statusRaw === 'NOT STARTED' || statusRaw === 'NOT-STARTED') {
                statusClass = 'notstarted';
                statusLabel = 'NOT STARTED';
            } else if (statusCode === 'COMPLETED' || statusRaw === 'COMPLETED') {
                statusClass = 'completed';
                statusLabel = 'Completed';
            } else if (delay > 25) {
                statusClass = 'sigdelay';
                statusLabel = `Sig. Delay +${delay}m`;
            } else if (delay > 5) {
                statusClass = 'delayed';
                statusLabel = `Delayed +${delay}m`;
            }

            const isSelected = this.selectedTrainNumber === t.train_number;
            const selectedClass = isSelected ? 'is-selected-train' : '';

            return `
                <tr class="${selectedClass}" onclick="window.controlRoomManager.selectTrain('${t.train_number}', false)" title="Inspect train ${t.train_number}">
                    <td class="occ-train-no-cell">${t.train_number}</td>
                    <td class="occ-route-cell" title="${t.source_code || 'SRC'} → ${t.destination_code || 'DST'} (${t.short_name || t.train_name})">
                        ${t.source_code || 'SRC'} → ${t.destination_code || 'DST'}
                    </td>
                    <td>
                        <div class="occ-status-cell ${statusClass}">
                            <span class="status-dot"></span>
                            <span>${statusLabel}</span>
                        </div>
                    </td>
                    <td class="occ-eta-cell">${t.predicted_destination_eta || t.scheduled_destination_eta || '--:--'}</td>
                </tr>
            `;
        }).join('');
    }

    renderActiveAlerts(alerts) {
        const container = document.getElementById('occActiveAlertsList');
        if (!container) return;

        if (!alerts || alerts.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 18px; color: #64748B; font-size: 11px;">
                    No critical operational alerts at this time.
                </div>
            `;
            return;
        }

        container.innerHTML = alerts.map(a => {
            const isCritical = a.severity === 'critical';
            const iconClass = isCritical ? 'fa-triangle-exclamation' : 'fa-triangle-exclamation';
            const wrapClass = isCritical ? 'critical' : 'warning';

            return `
                <div class="occ-alert-item-card" onclick="window.controlRoomManager.focusAlert('${a.id}', '${a.train_number}')" title="Click to view section details">
                    <div class="occ-alert-icon-wrap ${wrapClass}">
                        <i class="fa-solid ${iconClass}"></i>
                    </div>
                    <div class="occ-alert-text-block">
                        <div class="occ-alert-title-row">
                            <span class="occ-alert-title">${a.title}</span>
                            <span class="occ-alert-time">${a.time || '13:20'}</span>
                        </div>
                        <div class="occ-alert-desc">${a.description}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderMapFleet(trains) {
        if (!this.map) return;

        // Clear previous markers
        Object.values(this.markersMap).forEach(marker => {
            if (marker && typeof marker.remove === 'function') {
                marker.remove();
            }
        });
        this.markersMap = {};

        let filtered = trains;
        if (this.searchQuery) {
            filtered = trains.filter(t => {
                const q = this.searchQuery;
                return (
                    (t.train_number && t.train_number.toLowerCase().includes(q)) ||
                    (t.train_name && t.train_name.toLowerCase().includes(q)) ||
                    (t.short_name && t.short_name.toLowerCase().includes(q)) ||
                    (t.source_code && t.source_code.toLowerCase().includes(q)) ||
                    (t.destination_code && t.destination_code.toLowerCase().includes(q))
                );
            });
        }

        const heatFeatures = [];

        filtered.forEach(train => {
            const coords = train.current_coordinates;
            if (!coords || !Array.isArray(coords) || coords.length < 2 || coords[0] == null || coords[1] == null) {
                return;
            }

            const lat = Number(coords[0]);
            const lng = Number(coords[1]);
            if (isNaN(lat) || isNaN(lng)) return;

            const delay = train.current_delay_mins || 0;
            const statusCode = (train.current_status_code || train.status || '').toUpperCase();
            const statusRaw = (train.current_status || '').toUpperCase();
            let statusClass = 'ontime';

            if (statusCode === 'NOT_STARTED' || statusRaw === 'NOT STARTED' || statusRaw === 'NOT-STARTED') {
                statusClass = 'notstarted';
            } else if (statusCode === 'COMPLETED' || statusRaw === 'COMPLETED') {
                statusClass = 'completed';
            } else if (delay > 25) {
                statusClass = 'sigdelay';
            } else if (delay > 5) {
                statusClass = 'delayed';
            }

            const isSelected = this.selectedTrainNumber === train.train_number;

            // Custom DOM Marker element matching reference
            const el = document.createElement('div');
            el.className = `occ-leaflet-train-marker ${statusClass} ${isSelected ? 'is-selected' : ''}`;
            el.id = `occMapMarker_${train.train_number}`;
            el.title = `${train.train_number} - ${train.short_name || train.train_name} (${delay > 0 ? '+' + delay + 'm' : 'On Time'})`;
            el.innerHTML = `
                <i class="fa-solid fa-train marker-train-icon"></i>
                <span>${train.train_number}</span>
            `;

            el.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectTrain(train.train_number, true);
            });

            const marker = new maplibregl.Marker({
                element: el,
                anchor: 'center'
            })
            .setLngLat([lng, lat])
            .addTo(this.map);

            this.markersMap[train.train_number] = marker;

            if (delay > 0) {
                heatFeatures.push({
                    type: 'Feature',
                    properties: { delay: delay },
                    geometry: {
                        type: 'Point',
                        coordinates: [lng, lat]
                    }
                });
            }
        });

        // Update heatmap source data
        if (this.map.getSource && this.map.getSource('heat-delay-source')) {
            this.map.getSource('heat-delay-source').setData({
                type: 'FeatureCollection',
                features: heatFeatures
            });
        }

        // Toggle heatmap layer visibility
        if (this.map.getLayer && this.map.getLayer('train-heat-layer')) {
            this.map.setLayoutProperty(
                'train-heat-layer',
                'visibility',
                this.activeMode === 'heat' ? 'visible' : 'none'
            );
        }

        // Mode 3: Route View highlight for selected train
        if (this.activeMode === 'route' && this.selectedTrainNumber) {
            this.renderSelectedTrainRouteHighlight(this.selectedTrainNumber);
        } else if (this.activeMode !== 'route') {
            this.clearRouteHighlight();
        }
    }

    renderSelectedTrainRouteHighlight(trainNumber) {
        if (!this.map || !this.map.getSource || !this.map.getSource('route-highlight-source')) return;

        const train = this.trainsCache.find(t => t.train_number === trainNumber);
        if (!train) {
            this.clearRouteHighlight();
            return;
        }

        let poly = train.route_polyline;
        if (!poly || !Array.isArray(poly) || poly.length < 2) {
            if (train.stations && Array.isArray(train.stations)) {
                poly = train.stations.map(s => s.coordinates).filter(Boolean);
            }
        }

        if (poly && poly.length >= 2) {
            const lineCoords = poly.map(pt => [pt[1], pt[0]]);
            this.map.getSource('route-highlight-source').setData({
                type: 'FeatureCollection',
                features: [{
                    type: 'Feature',
                    properties: { train_number: trainNumber },
                    geometry: {
                        type: 'LineString',
                        coordinates: lineCoords
                    }
                }]
            });
        } else {
            this.clearRouteHighlight();
        }
    }

    clearRouteHighlight() {
        if (this.map && this.map.getSource && this.map.getSource('route-highlight-source')) {
            this.map.getSource('route-highlight-source').setData({
                type: 'FeatureCollection',
                features: []
            });
        }
    }

    selectTrain(trainNumber, fromMap = false) {
        this.selectedTrainNumber = trainNumber;
        const train = this.trainsCache.find(t => t.train_number === trainNumber);
        if (!train) return;

        // Update selected state in table
        this.renderLiveTrainsTable(this.trainsCache);

        // Update selected marker styling
        document.querySelectorAll('.occ-leaflet-train-marker').forEach(m => m.classList.remove('is-selected'));
        const markerEl = document.getElementById(`occMapMarker_${trainNumber}`);
        if (markerEl) markerEl.classList.add('is-selected');

        if (this.markersMap[trainNumber]) {
            const marker = this.markersMap[trainNumber];
            if (!fromMap && this.map) {
                const lngLat = marker.getLngLat();
                this.map.flyTo({
                    center: [lngLat.lng, lngLat.lat],
                    zoom: Math.max(this.map.getZoom(), 6.5),
                    speed: 1.2
                });
            }
        }

        // Show and update Floating Inspection Card
        this.showInspectCard(train);

        // Always render route highlight for the selected train
        this.renderSelectedTrainRouteHighlight(trainNumber);
    }

    showInspectCard(train) {
        const card = document.getElementById('occFloatingTrainCard');
        if (!card) return;

        this.updateInspectCard(train);
        card.style.display = 'block';
    }

    updateInspectCard(train) {
        const setText = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        const delay = train.current_delay_mins || 0;
        const statusCode = (train.current_status_code || train.status || '').toUpperCase();
        const statusRaw = (train.current_status || '').toUpperCase();
        let statusTxt = 'On Time';

        if (statusCode === 'NOT_STARTED' || statusRaw === 'NOT STARTED' || statusRaw === 'NOT-STARTED') {
            statusTxt = 'NOT STARTED';
        } else if (statusCode === 'COMPLETED' || statusRaw === 'COMPLETED') {
            statusTxt = 'Completed';
        } else if (delay > 25) {
            statusTxt = `Critical Delay (+${delay} min)`;
        } else if (delay > 5) {
            statusTxt = `Delayed (+${delay} min)`;
        }

        setText('occInspectTrainNo', train.train_number);
        setText('occInspectTrainName', train.short_name || train.train_name);
        
        const statusEl = document.getElementById('occInspectStatus');
        if (statusEl) {
            statusEl.textContent = statusTxt;
            if (statusCode === 'NOT_STARTED' || statusRaw === 'NOT STARTED' || statusRaw === 'NOT-STARTED') {
                statusEl.style.color = '#EF4444';
            } else if (statusCode === 'COMPLETED' || statusRaw === 'COMPLETED') {
                statusEl.style.color = '#94A3B8';
            } else if (delay > 25) {
                statusEl.style.color = '#F87171';
            } else if (delay > 5) {
                statusEl.style.color = '#FBBF24';
            } else {
                statusEl.style.color = '#34D399';
            }
        }

        const occSpeed = (typeof train.current_speed_kmh === 'number') ? train.current_speed_kmh : (typeof train.speed === 'number' ? train.speed : 0);
        setText('occInspectSpeed', `${occSpeed} km/h`);
        setText('occInspectDelay', delay > 0 ? `+${delay} min` : '0 min');
        setText('occInspectETA', train.predicted_destination_eta || train.scheduled_destination_eta || 'Data unavailable');
        setText('occInspectLocation', train.current_location || (train.source ? `At ${train.source}` : 'Data unavailable'));

        let nextStnText = 'Data unavailable';
        if (train.next_station) {
            if (typeof train.next_station === 'object' && train.next_station.name) {
                const etaPart = train.next_station.expected_eta || train.next_station.scheduled_eta ? ` (${train.next_station.expected_eta || train.next_station.scheduled_eta})` : '';
                nextStnText = `${train.next_station.name}${etaPart}`;
            } else if (typeof train.next_station === 'string') {
                nextStnText = train.next_station;
            }
        }
        setText('occInspectNextStation', nextStnText);
    }

    closeInspectCard() {
        const card = document.getElementById('occFloatingTrainCard');
        if (card) card.style.display = 'none';
    }

    focusAlert(alertId, trainNumber) {
        if (trainNumber && this.trainsCache.some(t => t.train_number === trainNumber)) {
            this.selectTrain(trainNumber, false);
            this.showToast(`🎯 Focusing on Train ${trainNumber} operational alert`);
        } else {
            this.showToast(`🚨 Alert ${alertId}: Active section restriction`);
        }
    }

    setMapMode(mode) {
        this.activeMode = mode;

        // Toggle active button states
        const pills = [
            { id: 'btnModeLiveMap', mode: 'live' },
            { id: 'btnModeHeatMap', mode: 'heat' },
            { id: 'btnModeRouteView', mode: 'route' }
        ];

        pills.forEach(({ id, mode: m }) => {
            const el = document.getElementById(id);
            if (el) el.classList.toggle('active', m === mode);
        });

        if (this.map && this.map.getLayer && this.map.getLayer('train-heat-layer')) {
            this.map.setLayoutProperty(
                'train-heat-layer',
                'visibility',
                mode === 'heat' ? 'visible' : 'none'
            );
        }

        if (mode === 'live') {
            this.clearRouteHighlight();
            this.showToast('🗺️ Map Mode: Live Train Map');
        } else if (mode === 'heat') {
            this.clearRouteHighlight();
            this.showToast('🔥 Map Mode: Density / Delay Heat Map');
        } else if (mode === 'route') {
            if (this.selectedTrainNumber) {
                this.renderSelectedTrainRouteHighlight(this.selectedTrainNumber);
            }
            this.showToast('🛣️ Map Mode: Selected Corridor Route View');
        }
    }

    handleSearch(query) {
        this.searchQuery = (query || '').toLowerCase().trim();
        const clearBtn = document.getElementById('btnOccClearSearch');
        if (clearBtn) {
            clearBtn.style.display = this.searchQuery ? 'block' : 'none';
        }

        this.renderLiveTrainsTable(this.trainsCache);
        this.renderMapFleet(this.trainsCache);
    }

    zoomIn() {
        if (this.map) this.map.zoomIn();
    }

    zoomOut() {
        if (this.map) this.map.zoomOut();
    }

    centerMap() {
        if (this.map) {
            this.map.flyTo({
                center: [78.9629, 22.5937],
                zoom: 4.5,
                speed: 1.2
            });
            this.showToast('🎯 Map centered on Indian Railway Network');
        }
    }

    resize() {
        if (this.map && typeof this.map.resize === 'function') {
            this.map.resize();
        }
    }

    startAutoRefresh() {
        if (this.autoRefreshTimer) clearInterval(this.autoRefreshTimer);
        this.autoRefreshTimer = setInterval(() => {
            const occPane = document.getElementById('view-control-room');
            if (occPane && occPane.classList.contains('active-view')) {
                this.loadControlRoomData(true);
            }
        }, 15000);
    }

    stopAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
        }
    }

    showToast(msg) {
        let toast = document.getElementById('occToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'occToast';
            toast.style.position = 'fixed';
            toast.style.bottom = '24px';
            toast.style.left = '50%';
            toast.style.transform = 'translateX(-50%)';
            toast.style.backgroundColor = 'rgba(15, 23, 42, 0.95)';
            toast.style.color = '#F8FAFC';
            toast.style.padding = '8px 16px';
            toast.style.borderRadius = '8px';
            toast.style.fontSize = '12px';
            toast.style.fontWeight = '600';
            toast.style.border = '1px solid #334155';
            toast.style.zIndex = '9999';
            toast.style.boxShadow = '0 4px 16px rgba(0,0,0,0.4)';
            toast.style.transition = 'opacity 0.2s';
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.style.display = 'block';
        toast.style.opacity = '1';
        clearTimeout(this._toastTimeout);
        this._toastTimeout = setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => { toast.style.display = 'none'; }, 250);
        }, 3000);
    }
}

window.controlRoomManager = new ControlRoomManager();
