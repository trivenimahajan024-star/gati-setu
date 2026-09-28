/**
 * GatiSetu - Dedicated Route Map & Dedicated Weather Radar Map
 * 
 * 1. RouteMapTracker:
 *    - Pure train tracking on the Live Route Map screen (#liveTrackingMap)
 *    - Base map: MapTiler Hybrid / ESRI World Imagery + CartoDB Labels (zero watermarks)
 *    - Railway corridor tracks, station nodes, tooltips, popups, and live pulsing train marker
 *    - Zoom, Pan, Center on Train, Fit Full Route, Fullscreen
 * 
 * 2. WeatherMapTracker:
 *    - Dedicated regional meteorological map on the Weather tab (#weatherTrackingMap)
 *    - Always uses the SAME selected train as Live Tracking (shared state & real backend API)
 *    - Displays the selected train's real railway route and all station nodes strictly ABOVE the weather layer
 *    - Animated RainViewer Doppler radar sequence with Play/Pause and Timeline scrubber BELOW the railway route
 *    - Satellite infrared clouds overlay & 4-tier intensity legend (Light, Moderate, Heavy, Severe)
 *    - State, district, and city labels on labelsPane
 *    - 100% Real Live Weather Telemetry (Open-Meteo Free API)
 *    - Layer selector: Rain | Composite | Clouds | Hybrid
 */

// ============================================================================
// 1. PURE ROUTE MAP TRACKER (LIVE ROUTE MAP SCREEN)
// ============================================================================

class RouteMapTracker {
    constructor(containerId = 'liveTrackingMap') {
        this.containerId = containerId;
        this.map = null;
        this.maptilerKey = '';
        
        // Base Tile Layers
        this.baseSatelliteLayer = null;
        this.baseLabelsLayer = null;
        this.baseMaptilerLayer = null;
        
        // Railway Vector Layers
        this.routeLayer = null;
        this.stationMarkersLayer = null;
        this.trainMarker = null;
        
        // Train State
        this.currentTrain = null;
        this.isInitialized = false;
        this.isFullscreen = false;
    }

    /**
     * Initialize Leaflet map instance for Pure Train Route Tracking
     */
    async initMap() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        if (typeof L === 'undefined') {
            this.renderFallbackVisual(container);
            return;
        }

        if (this.map) {
            setTimeout(() => {
                if (this.map) this.map.invalidateSize();
            }, 120);
            return;
        }

        // Fetch MapTiler API key from backend config (.env) if present
        try {
            if (window.railwayApi && window.railwayApi.getMapConfig) {
                const cfg = await window.railwayApi.getMapConfig();
                if (cfg && cfg.maptiler_api_key) {
                    this.maptilerKey = cfg.maptiler_api_key.trim();
                }
            }
        } catch (e) {
            console.warn("Backend map config check:", e);
        }

        try {
            // Instantiate Leaflet map with standard legal attribution
            this.map = L.map(this.containerId, {
                zoomControl: false,
                attributionControl: true,
                inertia: true
            }).setView([22.5, 76.5], 6);

            // Add top-right zoom control
            L.control.zoom({ position: 'topright' }).addTo(this.map);

            // Custom Panes for strict vector and label stacking
            this.map.createPane('routePane');
            this.map.getPane('routePane').style.zIndex = 500;

            this.map.createPane('stationsPane');
            this.map.getPane('stationsPane').style.zIndex = 600;

            this.map.createPane('labelsPane');
            this.map.getPane('labelsPane').style.zIndex = 650;

            this.map.createPane('trainMarkerPane');
            this.map.getPane('trainMarkerPane').style.zIndex = 700;

            // Setup Base Satellite Layers & Geographic Labels
            this.setupBaseTileLayers();

            // Vector Layer Groups
            this.routeLayer = L.layerGroup([], { pane: 'routePane' }).addTo(this.map);
            this.stationMarkersLayer = L.layerGroup([], { pane: 'stationsPane' }).addTo(this.map);

            // Setup Navigation Actions
            this.setupMapActionControls();

            this.isInitialized = true;
        } catch (e) {
            console.error("Leaflet init error:", e);
            this.renderFallbackVisual(container);
        }
    }

    /**
     * Sets up Base Satellite & State/District/City Labels with required attribution
     */
    setupBaseTileLayers() {
        if (!this.map) return;

        // ESRI World Imagery Satellite Layer (High resolution satellite base)
        this.baseSatelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.esri.com/" target="_blank">Esri</a> &copy; Maxar'
        });

        // CartoDB Voyager Transparent Labels for States, Districts, and Cities
        this.baseLabelsLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd',
            pane: 'labelsPane',
            opacity: 0.95,
            attribution: '&copy; <a href="https://carto.com/" target="_blank">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
        });

        const osmFallback = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
        });

        this.baseSatelliteLayer.on('tileerror', () => {
            if (!this.map.hasLayer(osmFallback)) {
                osmFallback.addTo(this.map);
            }
        });

        // If a valid MapTiler key is configured in .env, use MapTiler Hybrid v4
        if (this.maptilerKey && this.maptilerKey.length > 5) {
            this.baseMaptilerLayer = L.tileLayer(`https://api.maptiler.com/maps/hybrid-v4/{z}/{x}/{y}.jpg?key=${this.maptilerKey}`, {
                maxZoom: 19,
                subdomains: 'abcd',
                attribution: '&copy; <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
            });

            this.baseMaptilerLayer.on('tileerror', () => {
                if (this.map.hasLayer(this.baseMaptilerLayer)) {
                    this.map.removeLayer(this.baseMaptilerLayer);
                }
                if (!this.map.hasLayer(this.baseSatelliteLayer)) {
                    this.baseSatelliteLayer.addTo(this.map);
                    this.baseLabelsLayer.addTo(this.map);
                }
            });

            this.baseMaptilerLayer.addTo(this.map);
        } else {
            // Default: High-Resolution Satellite + State & City Labels
            this.baseSatelliteLayer.addTo(this.map);
            this.baseLabelsLayer.addTo(this.map);
        }
    }

    /**
     * Setup Map Toolbar Controls (Zoom In/Out, Center, Fit Route, Fullscreen)
     */
    setupMapActionControls() {
        const btnZoomIn = document.getElementById('btnMapZoomIn');
        if (btnZoomIn) {
            btnZoomIn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.zoomIn();
            };
        }

        const btnZoomOut = document.getElementById('btnMapZoomOut');
        if (btnZoomOut) {
            btnZoomOut.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.zoomOut();
            };
        }

        const btnCenter = document.getElementById('btnCenterTrain');
        if (btnCenter) {
            btnCenter.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.centerOnTrain();
            };
        }

        const btnFit = document.getElementById('btnFitRoute');
        if (btnFit) {
            btnFit.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.fitEntireRoute();
            };
        }

        const btnFull = document.getElementById('btnMapFullscreen');
        if (btnFull) {
            btnFull.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleFullscreen();
            };
        }

        if (!this._hasEscListener) {
            this._hasEscListener = true;
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isFullscreen) {
                    this.toggleFullscreen();
                }
            });
        }
    }

    /**
     * Computes the ordered list of coordinates forming the train's real railway route
     */
    getRoutePolyline(train) {
        if (!train) return [];
        if (train.route_polyline && Array.isArray(train.route_polyline) && train.route_polyline.length >= 2) {
            return train.route_polyline;
        }
        if (train.stations && Array.isArray(train.stations)) {
            return train.stations
                .filter(s => s.coordinates && Array.isArray(s.coordinates) && s.coordinates.length === 2)
                .map(s => s.coordinates);
        }
        return [];
    }

    /**
     * Calculates compass bearing angle in degrees between two geographic coordinates
     */
    calculateBearing(c1, c2) {
        if (!c1 || !c2) return 0;
        const lat1 = (c1[0] * Math.PI) / 180;
        const lat2 = (c2[0] * Math.PI) / 180;
        const dLon = ((c2[1] - c1[1]) * Math.PI) / 180;
        const y = Math.sin(dLon) * Math.cos(lat2);
        const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
        const brng = (Math.atan2(y, x) * 180) / Math.PI;
        return (brng + 360) % 360;
    }

    /**
     * Calculates the exact [lat, lon] coordinates along the polyline for a given journey percentage
     */
    calculatePositionAlongRoute(polyline, progressPct) {
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

    /**
     * Helper to get compass direction string (e.g., NE, NNE, SW) from degrees
     */
    getCompassDirection(deg) {
        const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
        const idx = Math.round(((deg % 360) / 22.5)) % 16;
        return directions[idx];
    }

    /**
     * Render the complete railway route, intermediate stations, and live train marker
     */
    renderTrainRoute(train) {
        if (!train) return;
        this.currentTrain = train;
        this.initMap();

        if (!this.map || typeof L === 'undefined') {
            const container = document.getElementById(this.containerId);
            if (container) this.renderFallbackVisual(container);
            return;
        }

        setTimeout(() => {
            if (this.map) this.map.invalidateSize();
        }, 100);

        // Clear previous route layers
        this.routeLayer.clearLayers();
        this.stationMarkersLayer.clearLayers();
        if (this.trainMarker) {
            this.map.removeLayer(this.trainMarker);
            this.trainMarker = null;
        }

        const stations = train.stations || [];
        const poly = this.getRoutePolyline(train);
        if (poly.length === 0) return;

        // 1. Calculate and acquire current real train position
        let trainCoords = train.current_coordinates;
        if (!trainCoords || !Array.isArray(trainCoords) || trainCoords.length !== 2) {
            const progress = typeof train.journey_progress_pct === 'number' ? train.journey_progress_pct : 0;
            trainCoords = this.calculatePositionAlongRoute(poly, progress);
        }

        // 2. Separate route into Completed (passed) and Upcoming segments
        let passedCoords = [];
        let upcomingCoords = [];
        let foundUpcoming = false;

        stations.forEach(stn => {
            if (!stn.coordinates) return;
            if (stn.status === 'departed' && !foundUpcoming) {
                passedCoords.push(stn.coordinates);
            } else {
                foundUpcoming = true;
                upcomingCoords.push(stn.coordinates);
            }
        });

        const completedPoly = passedCoords.length > 0 ? [...passedCoords, trainCoords] : [poly[0], trainCoords];
        const upcomingPoly = upcomingCoords.length > 0 ? [trainCoords, ...upcomingCoords] : [trainCoords, poly[poly.length - 1]];

        // 3. Draw Completed Railway Route Section (Solid high-contrast green corridor)
        if (completedPoly.length >= 2) {
            // Ballast casing shadow
            this.routeLayer.addLayer(L.polyline(completedPoly, {
                color: '#0F172A',
                weight: 8,
                opacity: 0.95,
                lineCap: 'round',
                lineJoin: 'round',
                pane: 'routePane'
            }));
            // Solid emerald rail
            this.routeLayer.addLayer(L.polyline(completedPoly, {
                color: '#059669',
                weight: 5,
                opacity: 1.0,
                lineCap: 'round',
                lineJoin: 'round',
                pane: 'routePane'
            }));
            // Center white track line
            this.routeLayer.addLayer(L.polyline(completedPoly, {
                color: '#FFFFFF',
                weight: 2,
                opacity: 0.9,
                pane: 'routePane'
            }));
        }

        // 4. Draw Upcoming Railway Route Section (Dashed active railway corridor to destination)
        if (upcomingPoly.length >= 2) {
            // Ballast casing
            this.routeLayer.addLayer(L.polyline(upcomingPoly, {
                color: '#0F172A',
                weight: 7,
                opacity: 0.85,
                lineCap: 'round',
                lineJoin: 'round',
                pane: 'routePane'
            }));
            // Dashed active emerald line
            this.routeLayer.addLayer(L.polyline(upcomingPoly, {
                color: '#10B981',
                weight: 4.5,
                opacity: 0.98,
                dashArray: '8, 6',
                lineCap: 'round',
                lineJoin: 'round',
                pane: 'routePane'
            }));
            // Railway ties/sleepers
            this.routeLayer.addLayer(L.polyline(upcomingPoly, {
                color: '#CBD5E1',
                weight: 2,
                opacity: 0.85,
                dashArray: '4, 8',
                pane: 'routePane'
            }));
        }

        // 5. Add all intermediate station markers with clear names, codes, and status badges
        stations.forEach((stn, idx) => {
            if (!stn.coordinates) return;

            const isPassed = stn.status === 'departed';
            const isApproaching = stn.status === 'approaching';
            const isStart = idx === 0;
            const isEnd = idx === stations.length - 1;

            let markerColor = '#10B981'; // Upcoming green
            let markerRadius = 6.5;
            let strokeColor = '#FFFFFF';
            let strokeWidth = 2.5;
            let badgeText = '';

            if (isStart) {
                markerColor = '#0D5C3A'; // Origin deep emerald
                markerRadius = 9;
                strokeWidth = 3;
                badgeText = '<span class="stn-tag origin">ORIGIN</span>';
            } else if (isEnd) {
                markerColor = '#0F2C59'; // Destination deep navy
                markerRadius = 9;
                strokeWidth = 3;
                badgeText = '<span class="stn-tag dest">DEST</span>';
            } else if (isApproaching) {
                markerColor = '#F59E0B'; // Approaching vibrant amber
                markerRadius = 8;
                strokeWidth = 3;
                badgeText = '<span class="stn-tag approaching">NEXT STOP</span>';
            } else if (isPassed) {
                markerColor = '#64748B'; // Passed slate
                markerRadius = 5.5;
                strokeWidth = 2;
                badgeText = '<span class="stn-tag passed">PASSED</span>';
            }

            const circleMarker = L.circleMarker(stn.coordinates, {
                radius: markerRadius,
                fillColor: markerColor,
                color: strokeColor,
                weight: strokeWidth,
                opacity: 1,
                fillOpacity: 0.98,
                pane: 'stationsPane'
            });

            // Permanent high-contrast station name, code & status tooltip
            const tooltipHtml = `
                <div class="stn-map-tooltip-wrap">
                    <span class="stn-map-name">${stn.name}</span>
                    <span class="stn-map-code">${stn.code}</span>
                    ${badgeText}
                </div>
            `;
            circleMarker.bindTooltip(tooltipHtml, {
                permanent: true,
                direction: 'top',
                className: 'map-stn-tooltip',
                offset: [0, -7]
            });

            // Detailed clickable station timetable popup
            const delayText = stn.delay_mins > 0 ? `+${stn.delay_mins}m late` : 'On Time';
            const delayColor = stn.delay_mins > 0 ? '#D97706' : '#15803D';
            const popupContent = `
                <div class="map-station-popup">
                    <div class="popup-title"><strong>${stn.name} (${stn.code})</strong></div>
                    <div class="popup-row"><span>Status:</span> <span class="badge-${stn.status}">${(stn.status || 'SCHEDULED').toUpperCase()}</span></div>
                    <div class="popup-row"><span>Scheduled:</span> <span>${stn.scheduled_arr || '--:--'}</span></div>
                    <div class="popup-row"><span>Dynamic ETA:</span> <strong style="color: #0D5C3A;">${stn.predicted_arr || '--:--'}</strong></div>
                    <div class="popup-row"><span>Delay:</span> <span style="color: ${delayColor}; font-weight:700;">${delayText}</span></div>
                    <div class="popup-row"><span>Platform:</span> <strong>Platform ${stn.platform || '1'}</strong></div>
                    ${stn.delay_attribution ? `<div class="popup-attr">${stn.delay_attribution}</div>` : ''}
                </div>
            `;

            circleMarker.bindPopup(popupContent);
            this.stationMarkersLayer.addLayer(circleMarker);
        });

        // 6. Draw Live Train Marker
        this.updateTrainPosition(trainCoords, train);

        // 7. Fit map bounds to entire railway route with clean padding
        try {
            const bounds = L.latLngBounds(poly);
            this.map.fitBounds(bounds, { padding: [45, 45], maxZoom: 9 });
        } catch (e) {
            console.warn("Could not fit map bounds", e);
        }
    }

    /**
     * Update or create the animated live train marker along the route with direction bearing
     */
    updateTrainPosition(coords, trainData) {
        if (!this.map || typeof L === 'undefined') return;
        const train = trainData || this.currentTrain;
        if (!train) return;

        let validCoords = coords;
        const poly = this.getRoutePolyline(train);
        if (!validCoords || !Array.isArray(validCoords) || validCoords.length !== 2) {
            const progress = typeof train.journey_progress_pct === 'number' ? train.journey_progress_pct : 0;
            validCoords = this.calculatePositionAlongRoute(poly, progress);
        }

        // Calculate heading bearing angle from route progression or train metadata
        let headingDeg = train.heading_deg || 0;
        if (poly && poly.length >= 2) {
            const progress = typeof train.journey_progress_pct === 'number' ? train.journey_progress_pct : 0;
            const nextIdx = Math.min(poly.length - 1, Math.floor((progress / 100) * (poly.length - 1)) + 1);
            const targetCoord = poly[nextIdx];
            if (targetCoord) {
                headingDeg = Math.round(this.calculateBearing(validCoords, targetCoord));
            }
        }
        const compassDir = this.getCompassDirection(headingDeg);

        const trainNo = train.train_number || '';
        const trainSpeed = typeof train.current_speed_kmh === 'number' ? train.current_speed_kmh : 0;
        const trainDelay = typeof train.current_delay_mins === 'number' ? train.current_delay_mins : 0;
        const nextStnName = train.next_station ? train.next_station.name : 'En route';
        const nextStnETA = train.next_station ? (train.next_station.expected_eta || train.next_station.scheduled_eta) : '--:--';
        const lastUpdated = train.last_updated_time || train.last_updated || 'Live';

        const iconHtml = `
            <div class="live-train-marker-wrapper">
                <div class="train-radar-pulse"></div>
                <div class="train-marker-pin" style="transform: rotate(${headingDeg}deg);" title="Heading ${headingDeg}° (${compassDir})">
                    <i class="fa-solid fa-location-arrow"></i>
                </div>
                <div class="train-marker-label">
                    <span class="marker-train-no">${trainNo}</span>
                    <span class="marker-speed">${trainSpeed} km/h</span>
                    <span class="marker-delay ${trainDelay > 0 ? 'is-late' : 'is-ontime'}">${trainDelay > 0 ? '+' + trainDelay + 'm' : 'RT'}</span>
                </div>
            </div>
        `;

        const trainIcon = L.divIcon({
            className: 'custom-train-leaflet-icon',
            html: iconHtml,
            iconSize: [44, 44],
            iconAnchor: [22, 22]
        });

        const popupContent = `
            <div class="map-train-popup">
                <div class="popup-title"><strong>${trainNo} - ${train.short_name || train.train_name}</strong></div>
                <div class="popup-row"><span>Real Location:</span> <strong>${train.current_location || 'En route'}</strong></div>
                <div class="popup-row"><span>Speed & Heading:</span> <strong>${trainSpeed} km/h • ${headingDeg}° (${compassDir})</strong></div>
                <div class="popup-row"><span>Next Station:</span> <strong>${nextStnName} (ETA ${nextStnETA})</strong></div>
                <div class="popup-row"><span>Current Delay:</span> <strong style="color: ${trainDelay > 0 ? '#D97706' : '#15803D'};">${trainDelay > 0 ? '+' + trainDelay + ' min' : 'On Time'}</strong></div>
                <div class="popup-row"><span>Destination ETA:</span> <strong style="color: #0D5C3A;">${train.predicted_destination_eta || '--:--'}</strong></div>
                <div class="popup-row"><span>Last Updated:</span> <span style="color:#64748B;">${lastUpdated}</span></div>
            </div>
        `;

        if (this.trainMarker) {
            this.trainMarker.setLatLng(validCoords);
            this.trainMarker.setIcon(trainIcon);
            this.trainMarker.setPopupContent(popupContent);
        } else {
            this.trainMarker = L.marker(validCoords, {
                icon: trainIcon,
                zIndexOffset: 1000,
                pane: 'trainMarkerPane'
            }).addTo(this.map);
            this.trainMarker.bindPopup(popupContent);
        }

        // Sync Map Toolbar and HUD elements
        const speedChip = document.getElementById('mapToolbarSpeed');
        if (speedChip) speedChip.textContent = `${trainSpeed} km/h • GPS`;

        const hudTrainNo = document.getElementById('mapTrainNumber');
        if (hudTrainNo) hudTrainNo.textContent = trainNo;

        const hudNextStn = document.getElementById('mapNextStationText');
        if (hudNextStn) hudNextStn.textContent = `Next: ${nextStnName}`;

        const hudNextETA = document.getElementById('mapNextStationETA');
        if (hudNextETA) hudNextETA.textContent = `ETA ${nextStnETA} (+${trainDelay} min)`;

        const mapLoc = document.getElementById('mapCurrentLocation');
        if (mapLoc) mapLoc.textContent = train.current_location || 'En route';

        const mapSpeed = document.getElementById('mapCurrentSpeed');
        if (mapSpeed) mapSpeed.textContent = `${trainSpeed} km/h`;

        const mapNextName = document.getElementById('mapNextStationName');
        if (mapNextName) mapNextName.textContent = nextStnName;

        const mapNextDetail = document.getElementById('mapNextStationDetailETA');
        if (mapNextDetail) mapNextDetail.textContent = `ETA ${nextStnETA}`;
    }

    /**
     * Center map view on current live train
     */
    centerOnTrain() {
        if (this.trainMarker && this.map) {
            const pos = this.trainMarker.getLatLng();
            this.map.flyTo(pos, 9, { animate: true, duration: 0.8 });
        }
    }

    /**
     * Fit entire route in viewport
     */
    fitEntireRoute() {
        if (!this.map || !this.currentTrain) return;
        const poly = this.getRoutePolyline(this.currentTrain);
        if (poly.length > 0) {
            const bounds = L.latLngBounds(poly);
            this.map.fitBounds(bounds, { padding: [45, 45] });
        }
    }

    zoomIn() {
        if (this.map) this.map.zoomIn();
    }

    zoomOut() {
        if (this.map) this.map.zoomOut();
    }

    toggleFullscreen() {
        const card = document.getElementById('passengerMapContainerCard');
        if (!card) return;

        this.isFullscreen = !this.isFullscreen;
        card.classList.toggle('is-fullscreen', this.isFullscreen);

        const btnFull = document.getElementById('btnMapFullscreen');
        const btnIcon = document.querySelector('#btnMapFullscreen i');
        if (btnIcon) {
            btnIcon.className = this.isFullscreen ? 'fa-solid fa-compress' : 'fa-solid fa-expand';
        }
        if (btnFull) {
            btnFull.setAttribute('title', this.isFullscreen ? 'Exit Fullscreen (Esc)' : 'Expand Map Fullscreen');
        }

        setTimeout(() => {
            if (this.map) {
                this.map.invalidateSize();
                if (this.currentTrain) {
                    this.fitEntireRoute();
                }
            }
        }, 120);
    }

    renderFallbackVisual(container) {
        if (!container || container.querySelector('.map-fallback-schematic')) return;
        const train = this.currentTrain;
        const speed = (train && typeof train.current_speed_kmh === 'number') ? train.current_speed_kmh : 0;
        const loc = (train && train.current_location) ? train.current_location : (train && train.source ? `At ${train.source}` : 'En route');
        const trainNo = train ? train.train_number : '--';
        
        container.innerHTML = `
            <div class="map-fallback-schematic">
                <div class="schematic-radar-bg"></div>
                <div class="schematic-rail-track">
                    <div class="schematic-rail-line"></div>
                    <div class="schematic-train-node">
                        <div class="schematic-pulse"></div>
                        <div class="schematic-badge"><i class="fa-solid fa-train"></i> ${trainNo} • ${speed} km/h</div>
                    </div>
                </div>
                <div class="schematic-footer">
                    <span><i class="fa-solid fa-location-crosshairs"></i> ${loc} (Real-time GPS Active)</span>
                </div>
            </div>
        `;
    }
}


// ============================================================================
// 2. DEDICATED WEATHER & RADAR MAP TRACKER (WEATHER TAB)
// ============================================================================

class WeatherMapTracker {
    constructor(containerId = 'weatherTrackingMap') {
        this.containerId = containerId;
        this.map = null;
        this.maptilerKey = '';
        
        // Base Tile Layers (No watermarks)
        this.baseSatelliteLayer = null;
        this.baseLabelsLayer = null;
        this.baseMaptilerLayer = null;
        
        // Real-Time Radar & Satellite Animation State
        this.radarFrames = [];
        this.radarTileLayers = [];
        this.cloudLayer = null;
        this.currentFrameIdx = 0;
        this.isPlaying = false;
        this.playInterval = null;
        this.activeWeatherMode = 'rain'; // 'rain' | 'weather' | 'clouds' | 'hybrid'
        
        // Railway Vector Layers on Weather Map
        this.routeLayer = null;
        this.stationMarkersLayer = null;
        this.trainMarker = null;
        
        // Train & Telemetry State
        this.currentTrain = null;
        this.lastWeatherCoords = null;
        this.lastWeatherTime = 0;
        this.isInitialized = false;
        this.isFullscreen = false;
        this.weatherRefreshInterval = null;
        this.radarRefreshInterval = null;
    }

    /**
     * Initialize Leaflet map for dedicated Weather Radar & Cloud tracking
     */
    async initMap() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        if (typeof L === 'undefined') return;

        if (this.map) {
            setTimeout(() => {
                if (this.map) this.map.invalidateSize();
            }, 120);
            return;
        }

        // Fetch MapTiler API key from backend config (.env) if present
        try {
            if (window.railwayApi && window.railwayApi.getMapConfig) {
                const cfg = await window.railwayApi.getMapConfig();
                if (cfg && cfg.maptiler_api_key) {
                    this.maptilerKey = cfg.maptiler_api_key.trim();
                }
            }
        } catch (e) {
            console.warn("Weather backend map config check:", e);
        }

        try {
            // Instantiate Leaflet map centered over Indian subcontinent railway corridor
            this.map = L.map(this.containerId, {
                zoomControl: false,
                attributionControl: true,
                inertia: true
            }).setView([22.5, 75.5], 6);

            // Add standard zoom control at top-right
            L.control.zoom({ position: 'topright' }).addTo(this.map);

            // Create dedicated map panes for strict layer hierarchy:
            // weatherPane (400) -> routePane (500) -> stationsPane (600) -> labelsPane (650) -> trainMarkerPane (700)
            this.map.createPane('weatherPane');
            this.map.getPane('weatherPane').style.zIndex = 400;

            this.map.createPane('routePane');
            this.map.getPane('routePane').style.zIndex = 500;

            this.map.createPane('stationsPane');
            this.map.getPane('stationsPane').style.zIndex = 600;

            this.map.createPane('labelsPane');
            this.map.getPane('labelsPane').style.zIndex = 650;

            this.map.createPane('trainMarkerPane');
            this.map.getPane('trainMarkerPane').style.zIndex = 700;

            // Setup Base Satellite Layers
            this.setupBaseTileLayers();

            // Setup Real-Time Radar & Cloud Layers from RainViewer API
            await this.setupWeatherLayers();

            // Railway Vector Layer Groups on Weather Map
            this.routeLayer = L.layerGroup([], { pane: 'routePane' }).addTo(this.map);
            this.stationMarkersLayer = L.layerGroup([], { pane: 'stationsPane' }).addTo(this.map);

            // Setup Weather Layer Selector Controls
            this.setupLayerControls();

            // Setup Radar Animation Player Controls
            this.setupRadarPlayerControls();

            // Setup Weather Map Action Controls
            this.setupWeatherMapActionControls();

            // If a train is already selected, render its route on the weather map
            if (this.currentTrain || window.selectedTrain) {
                this.renderTrainWeatherRoute(this.currentTrain || window.selectedTrain);
            }

            // Start periodic auto-refresh tickers
            this.startWeatherTicker();

            this.isInitialized = true;
        } catch (e) {
            console.error("Weather map initialization error:", e);
        }
    }

    /**
     * Setup Base Satellite and City/State/District Labels without watermarks
     */
    setupBaseTileLayers() {
        if (!this.map) return;

        // ESRI World Imagery Satellite Layer (High resolution, zero watermark)
        this.baseSatelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.esri.com/" target="_blank">Esri</a> &copy; Maxar'
        });

        // CartoDB Voyager Transparent Labels for States, Districts, and Cities
        this.baseLabelsLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd',
            pane: 'labelsPane',
            opacity: 0.95,
            attribution: '&copy; <a href="https://carto.com/" target="_blank">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
        });

        const osmFallback = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
        });

        this.baseSatelliteLayer.on('tileerror', () => {
            if (!this.map.hasLayer(osmFallback)) {
                osmFallback.addTo(this.map);
            }
        });

        // If MapTiler Key is valid, try MapTiler Hybrid
        if (this.maptilerKey && this.maptilerKey.length > 5) {
            this.baseMaptilerLayer = L.tileLayer(`https://api.maptiler.com/maps/hybrid-v4/{z}/{x}/{y}.jpg?key=${this.maptilerKey}`, {
                maxZoom: 19,
                subdomains: 'abcd',
                attribution: '&copy; <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
            });

            this.baseMaptilerLayer.on('tileerror', () => {
                if (this.map.hasLayer(this.baseMaptilerLayer)) {
                    this.map.removeLayer(this.baseMaptilerLayer);
                }
                if (!this.map.hasLayer(this.baseSatelliteLayer)) {
                    this.baseSatelliteLayer.addTo(this.map);
                    this.baseLabelsLayer.addTo(this.map);
                }
            });

            this.baseMaptilerLayer.addTo(this.map);
        } else {
            // Default: 100% Watermark-free ESRI Satellite + CartoDB Labels
            this.baseSatelliteLayer.addTo(this.map);
            this.baseLabelsLayer.addTo(this.map);
        }
    }

    /**
     * Fetches real timestamped weather radar and cloud frames from RainViewer API
     */
    async setupWeatherLayers() {
        if (!this.map) return;

        try {
            const res = await fetch('https://api.rainviewer.com/public/weather-maps.json');
            if (!res.ok) throw new Error("RainViewer API status " + res.status);
            
            const data = await res.json();
            const host = data.host || 'https://tilecache.rainviewer.com';

            const pastRadar = (data.radar && data.radar.past) ? data.radar.past : [];
            const nowcastRadar = (data.radar && data.radar.nowcast) ? data.radar.nowcast : [];
            this.radarFrames = [...pastRadar, ...nowcastRadar];

            if (this.radarFrames.length > 0) {
                // Clear previous radar tile layers
                this.radarTileLayers.forEach(l => {
                    if (this.map.hasLayer(l)) this.map.removeLayer(l);
                });
                this.radarTileLayers = [];

                // Create pre-cached Leaflet TileLayers on weatherPane (zIndex 400)
                this.radarTileLayers = this.radarFrames.map(frame => {
                    const tileUrl = `${host}${frame.path}/256/{z}/{x}/{y}/2/1_1.png`;
                    return L.tileLayer(tileUrl, {
                        maxZoom: 18,
                        opacity: 0,
                        pane: 'weatherPane',
                        attribution: '&copy; <a href="https://www.rainviewer.com/api.html" target="_blank">RainViewer</a>'
                    });
                });

                // Default to latest live frame
                this.currentFrameIdx = this.radarFrames.length - 1;

                // Update timeline scrubber
                const scrubber = document.getElementById('radarTimeScrubber');
                if (scrubber) {
                    scrubber.min = '0';
                    scrubber.max = (this.radarFrames.length - 1).toString();
                    scrubber.value = this.currentFrameIdx.toString();
                }

                // Show latest frame
                this.showRadarFrame(this.currentFrameIdx);
            }

            // Satellite Infrared Clouds layer
            const pastSat = (data.satellite && data.satellite.infrared) ? data.satellite.infrared : [];
            if (pastSat.length > 0) {
                const latestSat = pastSat[pastSat.length - 1];
                const satTileUrl = `${host}${latestSat.path}/256/{z}/{x}/{y}/0/0_0.png`;
                this.cloudLayer = L.tileLayer(satTileUrl, {
                    maxZoom: 18,
                    opacity: 0.65,
                    pane: 'weatherPane',
                    attribution: '&copy; <a href="https://www.rainviewer.com/api.html" target="_blank">RainViewer</a>'
                });
            }
        } catch (e) {
            console.warn("Could not load real-time radar animation frames:", e);
            const lbl = document.getElementById('radarFrameTimeLabel');
            if (lbl) lbl.textContent = 'Radar stream temporarily unavailable';
        }
    }

    /**
     * Setup Radar Animation Player controls (Play/Pause, Timeline Scrubber)
     */
    setupRadarPlayerControls() {
        const btnPlayPause = document.getElementById('btnRadarPlayPause');
        if (btnPlayPause) {
            btnPlayPause.onclick = () => this.togglePlayPause();
        }

        const scrubber = document.getElementById('radarTimeScrubber');
        if (scrubber) {
            scrubber.oninput = (e) => {
                this.pauseRadar();
                const idx = parseInt(e.target.value, 10);
                if (!isNaN(idx)) {
                    this.showRadarFrame(idx);
                }
            };
        }
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.pauseRadar();
        } else {
            this.playRadar();
        }
    }

    playRadar() {
        if (this.radarFrames.length <= 1) return;
        this.isPlaying = true;

        const icon = document.getElementById('radarPlayIcon');
        if (icon) icon.className = 'fa-solid fa-pause';

        if (this.playInterval) clearInterval(this.playInterval);
        
        this.playInterval = setInterval(() => {
            let nextIdx = this.currentFrameIdx + 1;
            if (nextIdx >= this.radarFrames.length) {
                nextIdx = 0;
            }
            this.showRadarFrame(nextIdx);
        }, 700);
    }

    pauseRadar() {
        this.isPlaying = false;

        const icon = document.getElementById('radarPlayIcon');
        if (icon) icon.className = 'fa-solid fa-play';

        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
    }

    showRadarFrame(index) {
        if (!this.map || this.radarFrames.length === 0) return;
        if (index < 0 || index >= this.radarFrames.length) return;

        this.currentFrameIdx = index;

        if (this.activeWeatherMode === 'rain' || this.activeWeatherMode === 'weather') {
            this.radarTileLayers.forEach((layer, i) => {
                if (i === index) {
                    if (!this.map.hasLayer(layer)) {
                        layer.addTo(this.map);
                    }
                    layer.setOpacity(0.78);
                } else {
                    if (this.map.hasLayer(layer)) {
                        this.map.removeLayer(layer);
                    }
                }
            });
        }

        const scrubber = document.getElementById('radarTimeScrubber');
        if (scrubber && parseInt(scrubber.value, 10) !== index) {
            scrubber.value = index.toString();
        }

        this.updateRadarTimestampLabel(index);
    }

    updateRadarTimestampLabel(index) {
        const lbl = document.getElementById('radarFrameTimeLabel');
        if (!lbl || !this.radarFrames[index]) return;

        const frame = this.radarFrames[index];
        try {
            const date = new Date(frame.time * 1000);
            const timeStr = date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) + ' IST';
            const isLatest = index === this.radarFrames.length - 1;
            const diffMins = Math.max(0, Math.round((Date.now() - (frame.time * 1000)) / 60000));

            if (isLatest) {
                lbl.textContent = `Live Radar: ${timeStr}`;
            } else {
                lbl.textContent = `Radar: ${timeStr} (${diffMins}m ago)`;
            }
        } catch (e) {
            lbl.textContent = 'Real-time Radar Active';
        }
    }

    setupLayerControls() {
        const layerButtons = document.querySelectorAll('.btn-weather-layer');
        layerButtons.forEach(btn => {
            btn.onclick = () => {
                const mode = btn.getAttribute('data-layer');
                if (mode) {
                    this.switchWeatherLayerMode(mode);
                }
            };
        });
    }

    setupWeatherMapActionControls() {
        const btnZoomIn = document.getElementById('btnWeatherZoomIn');
        if (btnZoomIn) btnZoomIn.onclick = () => { if (this.map) this.map.zoomIn(); };

        const btnZoomOut = document.getElementById('btnWeatherZoomOut');
        if (btnZoomOut) btnZoomOut.onclick = () => { if (this.map) this.map.zoomOut(); };

        const btnReset = document.getElementById('btnWeatherResetView');
        if (btnReset) btnReset.onclick = () => this.fitEntireRoute();

        const btnFull = document.getElementById('btnWeatherFullscreen');
        if (btnFull) btnFull.onclick = () => this.toggleFullscreen();
    }

    switchWeatherLayerMode(mode) {
        this.activeWeatherMode = mode;

        document.querySelectorAll('.btn-weather-layer').forEach(b => {
            if (b.getAttribute('data-layer') === mode) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });

        if (!this.map) return;

        // Clean up active radar/clouds layers
        this.radarTileLayers.forEach(l => {
            if (this.map.hasLayer(l)) this.map.removeLayer(l);
        });
        if (this.cloudLayer && this.map.hasLayer(this.cloudLayer)) {
            this.map.removeLayer(this.cloudLayer);
        }

        const legend = document.getElementById('mapWeatherLegend');
        const legendTitle = document.getElementById('weatherLegendTitle');
        const playerHud = document.getElementById('radarPlayerHud');

        if (mode === 'hybrid') {
            this.pauseRadar();
            if (legend) legend.classList.remove('is-visible');
            if (playerHud) playerHud.classList.remove('is-visible');
        } else if (mode === 'weather') {
            this.showRadarFrame(this.currentFrameIdx);
            if (this.cloudLayer) this.cloudLayer.addTo(this.map);
            if (legend) {
                legend.classList.add('is-visible');
                if (legendTitle) legendTitle.textContent = 'Live Weather Composite';
            }
            if (playerHud) playerHud.classList.add('is-visible');
        } else if (mode === 'rain') {
            this.showRadarFrame(this.currentFrameIdx);
            if (legend) {
                legend.classList.add('is-visible');
                if (legendTitle) legendTitle.textContent = 'Precipitation Radar';
            }
            if (playerHud) playerHud.classList.add('is-visible');
        } else if (mode === 'clouds') {
            this.pauseRadar();
            if (this.cloudLayer) this.cloudLayer.addTo(this.map);
            if (legend) {
                legend.classList.add('is-visible');
                if (legendTitle) legendTitle.textContent = 'Satellite Cloud Cover';
            }
            if (playerHud) playerHud.classList.remove('is-visible');
        }
    }

    /**
     * Computes the list of coordinates forming the train's route polyline
     */
    getRoutePolyline(train) {
        if (!train) return [];
        if (train.route_polyline && Array.isArray(train.route_polyline) && train.route_polyline.length >= 2) {
            return train.route_polyline;
        }
        if (train.stations && Array.isArray(train.stations)) {
            return train.stations
                .filter(s => s.coordinates && Array.isArray(s.coordinates) && s.coordinates.length === 2)
                .map(s => s.coordinates);
        }
        return [];
    }

    /**
     * Calculates the exact [lat, lon] coordinates along the polyline for a given journey percentage
     */
    calculatePositionAlongRoute(polyline, progressPct) {
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

    calculateBearing(startCoord, endCoord) {
        if (!startCoord || !endCoord) return 0;
        const lat1 = startCoord[0] * Math.PI / 180;
        const lon1 = startCoord[1] * Math.PI / 180;
        const lat2 = endCoord[0] * Math.PI / 180;
        const lon2 = endCoord[1] * Math.PI / 180;
        const dLon = lon2 - lon1;

        const y = Math.sin(dLon) * Math.cos(lat2);
        const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
        const brng = Math.atan2(y, x) * 180 / Math.PI;
        return (brng + 360) % 360;
    }

    getCompassDirection(degrees) {
        const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
        const index = Math.round(degrees / 22.5) % 16;
        return directions[index];
    }

    /**
     * Render the selected train's real railway route, stations, and marker on the Weather Map
     */
    renderTrainWeatherRoute(train) {
        if (!train) return;
        this.currentTrain = train;
        this.initMap();

        if (!this.map || typeof L === 'undefined') return;

        setTimeout(() => {
            if (this.map) this.map.invalidateSize();
        }, 100);

        // Clear previous route vectors
        if (this.routeLayer) this.routeLayer.clearLayers();
        if (this.stationMarkersLayer) this.stationMarkersLayer.clearLayers();
        if (this.trainMarker) {
            this.map.removeLayer(this.trainMarker);
            this.trainMarker = null;
        }

        const poly = this.getRoutePolyline(train);
        if (poly.length === 0) return;

        // 1. Draw outer railway track ballast border line (dark slate)
        const trackBaseLine = L.polyline(poly, {
            color: '#0F172A',
            weight: 6,
            opacity: 0.92,
            lineCap: 'round',
            lineJoin: 'round',
            pane: 'routePane'
        });
        this.routeLayer.addLayer(trackBaseLine);

        // 2. Draw inner emerald railway corridor track line
        const trackInnerLine = L.polyline(poly, {
            color: '#10B981',
            weight: 3.5,
            opacity: 0.98,
            dashArray: '8, 5',
            pane: 'routePane'
        });
        this.routeLayer.addLayer(trackInnerLine);

        // 3. Draw intermediate station circle markers with complete Station Names & Tooltips
        const stations = train.stations || [];
        stations.forEach((stn, idx) => {
            if (!stn.coordinates) return;

            const isPassed = stn.status === 'departed';
            const isApproaching = stn.status === 'approaching';
            const isStart = idx === 0;
            const isEnd = idx === stations.length - 1;

            let markerColor = '#10B981'; // Upcoming emerald
            let markerRadius = 6.5;
            let strokeColor = '#FFFFFF';
            let strokeWidth = 2.5;
            let badgeText = '';

            if (isStart) {
                markerColor = '#0D5C3A'; // Origin deep emerald
                markerRadius = 9;
                strokeWidth = 3;
                badgeText = '<span class="stn-tag origin">ORIGIN</span>';
            } else if (isEnd) {
                markerColor = '#0F2C59'; // Destination navy
                markerRadius = 9;
                strokeWidth = 3;
                badgeText = '<span class="stn-tag dest">DEST</span>';
            } else if (isApproaching) {
                markerColor = '#F59E0B'; // Approaching amber
                markerRadius = 8;
                strokeWidth = 3;
                badgeText = '<span class="stn-tag approaching">NEXT STOP</span>';
            } else if (isPassed) {
                markerColor = '#64748B'; // Passed slate
                markerRadius = 5.5;
                strokeWidth = 2;
                badgeText = '<span class="stn-tag passed">PASSED</span>';
            }

            const circleMarker = L.circleMarker(stn.coordinates, {
                radius: markerRadius,
                fillColor: markerColor,
                color: strokeColor,
                weight: strokeWidth,
                opacity: 1,
                fillOpacity: 0.98,
                pane: 'stationsPane'
            });

            // Permanent high-contrast station name, code & status tooltip
            const tooltipHtml = `
                <div class="stn-map-tooltip-wrap">
                    <span class="stn-map-name">${stn.name}</span>
                    <span class="stn-map-code">${stn.code}</span>
                    ${badgeText}
                </div>
            `;
            circleMarker.bindTooltip(tooltipHtml, {
                permanent: true,
                direction: 'top',
                className: 'map-stn-tooltip',
                offset: [0, -7]
            });

            // Detailed clickable station popup with timetable & weather info
            const delayText = stn.delay_mins > 0 ? `+${stn.delay_mins}m late` : 'On Time';
            const popupContent = `
                <div class="map-station-popup">
                    <div class="popup-title"><strong>${stn.name} (${stn.code})</strong></div>
                    <div class="popup-row"><span>Status:</span> <span class="badge-${stn.status}">${(stn.status || 'SCHEDULED').toUpperCase()}</span></div>
                    <div class="popup-row"><span>Scheduled:</span> <span>${stn.scheduled_arr || '--:--'}</span></div>
                    <div class="popup-row"><span>Dynamic ETA:</span> <strong style="color: #0D5C3A;">${stn.predicted_arr || '--:--'}</strong></div>
                    <div class="popup-row"><span>Delay:</span> <strong>${delayText}</strong></div>
                    <div class="popup-row"><span>Platform:</span> <strong>Platform ${stn.platform || '1'}</strong></div>
                    <div class="popup-row" style="margin-top:4px; font-size:10px; color:#0284C7;"><i class="fa-solid fa-cloud-sun-rain"></i> <span>Live Weather Radar Active</span></div>
                </div>
            `;

            circleMarker.bindPopup(popupContent);
            this.stationMarkersLayer.addLayer(circleMarker);
        });

        // 4. Calculate and Draw Live Train Marker on Weather Map
        let trainCoords = train.current_coordinates;
        if (!trainCoords || !Array.isArray(trainCoords) || trainCoords.length !== 2) {
            const progress = typeof train.journey_progress_pct === 'number' ? train.journey_progress_pct : 0;
            trainCoords = this.calculatePositionAlongRoute(poly, progress);
        }

        this.updateTrainPosition(trainCoords, train);

        // 5. Fit map bounds to the selected train's railway route
        try {
            const bounds = L.latLngBounds(poly);
            this.map.fitBounds(bounds, { padding: [40, 40], maxZoom: 9 });
        } catch (e) {
            console.warn("Could not fit weather map bounds", e);
        }

        // 6. Fetch real Open-Meteo weather for this train's location
        this.updateRealWeather(trainCoords[0], trainCoords[1], train.current_location || train.short_name);

        // 7. Sync Weather Screen Train Hero Card and Summary Text
        const setTxt = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        const trainNo = train.train_number || '--';
        const trainName = train.short_name || train.train_name || 'Express';
        const nextStnName = train.next_station ? train.next_station.name : 'En route';
        const nextStnETA = train.next_station ? (train.next_station.expected_eta || train.next_station.scheduled_eta) : '--:--';
        const trainSpeed = typeof train.current_speed_kmh === 'number' ? train.current_speed_kmh : 0;
        const progressPct = typeof train.journey_progress_pct === 'number' ? train.journey_progress_pct : 0;

        setTxt('weatherScreenTrainNo', trainNo);
        setTxt('weatherScreenRouteSubtitle', `${train.source} → ${train.destination}`);
        setTxt('weatherTrainNumber', trainNo);
        setTxt('weatherNextStationText', `Next: ${nextStnName}`);
        setTxt('weatherNextStationETA', `ETA ${nextStnETA}`);
        setTxt('weatherToolbarSpeed', `${trainSpeed} km/h • GPS`);
        setTxt('weatherRouteProgressPct', `${progressPct.toFixed(1)}% completed`);
        setTxt('weatherSummaryTrainName', `${trainNo} - ${trainName}`);
        setTxt('weatherCurrentSectorText', `${train.current_location || 'En route'} (${trainCoords[0].toFixed(4)}° N, ${trainCoords[1].toFixed(4)}° E)`);
        setTxt('weatherNextStopText', `${nextStnName} (ETA ${nextStnETA})`);
    }

    /**
     * Update or create the animated live train marker along the route on the Weather Map
     */
    updateTrainPosition(coords, trainData) {
        if (!this.map || typeof L === 'undefined') return;
        const train = trainData || this.currentTrain;
        if (!train) return;

        let validCoords = coords;
        const poly = this.getRoutePolyline(train);
        if (!validCoords || !Array.isArray(validCoords) || validCoords.length !== 2) {
            const progress = typeof train.journey_progress_pct === 'number' ? train.journey_progress_pct : 0;
            validCoords = this.calculatePositionAlongRoute(poly, progress);
        }

        // Calculate heading bearing angle from route progression
        let headingDeg = train.heading_deg || 0;
        if (poly && poly.length >= 2) {
            const progress = typeof train.journey_progress_pct === 'number' ? train.journey_progress_pct : 0;
            const nextIdx = Math.min(poly.length - 1, Math.floor((progress / 100) * (poly.length - 1)) + 1);
            const targetCoord = poly[nextIdx];
            if (targetCoord) {
                headingDeg = Math.round(this.calculateBearing(validCoords, targetCoord));
            }
        }
        const compassDir = this.getCompassDirection(headingDeg);

        const trainNo = train.train_number || '--';
        const trainSpeed = typeof train.current_speed_kmh === 'number' ? train.current_speed_kmh : 0;
        const trainDelay = typeof train.current_delay_mins === 'number' ? train.current_delay_mins : 0;
        const nextStnName = train.next_station ? train.next_station.name : 'En route';
        const nextStnETA = train.next_station ? (train.next_station.expected_eta || train.next_station.scheduled_eta) : '--:--';

        const iconHtml = `
            <div class="live-train-marker-wrapper">
                <div class="train-radar-pulse"></div>
                <div class="train-marker-pin" style="transform: rotate(${headingDeg}deg);" title="Heading ${headingDeg}° (${compassDir})">
                    <i class="fa-solid fa-location-arrow"></i>
                </div>
                <div class="train-marker-label">
                    <span class="marker-train-no">${trainNo}</span>
                    <span class="marker-speed">${trainSpeed} km/h</span>
                    <span class="marker-delay ${trainDelay > 0 ? 'is-late' : 'is-ontime'}">${trainDelay > 0 ? '+' + trainDelay + 'm' : 'RT'}</span>
                </div>
            </div>
        `;

        const trainIcon = L.divIcon({
            className: 'custom-train-leaflet-icon',
            html: iconHtml,
            iconSize: [44, 44],
            iconAnchor: [22, 22]
        });

        const popupContent = `
            <div class="map-train-popup">
                <div class="popup-title"><strong>${trainNo} - ${train.short_name || train.train_name}</strong></div>
                <div class="popup-row"><span>Speed & Heading:</span> <strong>${trainSpeed} km/h • ${headingDeg}° (${compassDir})</strong></div>
                <div class="popup-row"><span>Location:</span> <span>${train.current_location || 'En route'}</span></div>
                <div class="popup-row"><span>Next Stop:</span> <strong>${nextStnName} (ETA ${nextStnETA})</strong></div>
                <div class="popup-row" style="margin-top:4px; font-size:10px; color:#0284C7;"><i class="fa-solid fa-cloud-sun-rain"></i> <span>Live Doppler Weather Overlay Active</span></div>
            </div>
        `;

        if (this.trainMarker) {
            this.trainMarker.setLatLng(validCoords);
            this.trainMarker.setIcon(trainIcon);
            this.trainMarker.setPopupContent(popupContent);
        } else {
            this.trainMarker = L.marker(validCoords, {
                icon: trainIcon,
                zIndexOffset: 1000,
                pane: 'trainMarkerPane'
            }).addTo(this.map);
            this.trainMarker.bindPopup(popupContent);
        }

        // Update real weather telemetry if train moved or >60s elapsed
        const now = Date.now();
        if (now - this.lastWeatherTime > 60000 || !this.lastWeatherCoords) {
            this.updateRealWeather(validCoords[0], validCoords[1], train.current_location || train.short_name);
        }
    }

    /**
     * Updates weather telemetry when train changes
     */
    updateWeatherForTrain(train) {
        if (!train) return;
        this.renderTrainWeatherRoute(train);
    }

    /**
     * Fit entire route in viewport
     */
    fitEntireRoute() {
        if (!this.map || !this.currentTrain) return;
        const poly = this.getRoutePolyline(this.currentTrain);
        if (poly.length > 0) {
            const bounds = L.latLngBounds(poly);
            this.map.fitBounds(bounds, { padding: [40, 40] });
        }
    }

    /**
     * Fetches and renders 100% Real Live Weather Telemetry from Open-Meteo API
     */
    async updateRealWeather(lat, lon, locationLabel = '') {
        const errorBanner = document.getElementById('weatherErrorBanner');
        const gridContent = document.getElementById('weatherGridContent');
        const locationSub = document.getElementById('weatherLocationName');
        const iconBadge = document.getElementById('weatherConditionIcon');

        if (lat === undefined || lon === undefined || lat === null || lon === null) {
            if (errorBanner) errorBanner.style.display = 'flex';
            return;
        }

        try {
            let data = null;
            if (window.railwayApi && window.railwayApi.fetchRealWeather) {
                data = await window.railwayApi.fetchRealWeather(lat, lon);
            } else {
                const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,wind_speed_10m&timezone=auto`;
                const res = await fetch(url);
                if (!res.ok) throw new Error("Open-Meteo API unavailable");
                data = await res.json();
            }

            if (!data || !data.current) {
                throw new Error("Invalid weather payload");
            }

            const cur = data.current;
            const tempNum = cur.temperature_2m !== undefined ? cur.temperature_2m : 25;
            const temp = `${tempNum.toFixed(1)} °C`;
            const apparent = cur.apparent_temperature !== undefined ? ` (Feels ${cur.apparent_temperature.toFixed(1)} °C)` : '';
            const rainVal = cur.rain !== undefined ? cur.rain : (cur.precipitation !== undefined ? cur.precipitation : 0);
            const rain = `${rainVal.toFixed(1)} mm`;
            const clouds = cur.cloud_cover !== undefined ? `${cur.cloud_cover} %` : '--';
            const windVal = cur.wind_speed_10m !== undefined ? cur.wind_speed_10m : 0;
            const wind = `${windVal.toFixed(1)} km/h`;
            
            const wmo = this.decodeWmoWeather(cur.weather_code);
            const condition = wmo.condition;

            let updatedTimeStr = 'Just now';
            if (cur.time) {
                try {
                    const d = new Date(cur.time);
                    updatedTimeStr = d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) + ' IST';
                } catch (e) {
                    updatedTimeStr = 'Live';
                }
            }

            const setTxt = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            };

            setTxt('weatherTemp', temp + apparent);
            setTxt('weatherCondition', condition);
            setTxt('weatherRain', rain);
            setTxt('weatherClouds', clouds);
            setTxt('weatherWind', wind);
            setTxt('weatherUpdatedTime', updatedTimeStr);

            if (locationSub) {
                locationSub.textContent = locationLabel ? `Live Weather near ${locationLabel} (${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E)` : `Corridor Coordinates: ${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E`;
            }

            if (iconBadge) {
                iconBadge.innerHTML = `<i class="fa-solid ${wmo.icon}"></i>`;
            }

            // Route Meteorology Summary Dynamic Calculation
            let trackRiskText = "Optimal Track Conditions - Clear Line of Sight";
            let trackRiskColor = "#10B981";

            if (rainVal >= 5.0) {
                trackRiskText = "Heavy Precipitation Alert - Wet Rail Surface Speed Caution";
                trackRiskColor = "#DC2626";
            } else if (rainVal > 0.4) {
                trackRiskText = "Light Rain / Drizzle - Standard Wet Rail Margin";
                trackRiskColor = "#0284C7";
            } else if (windVal > 45.0) {
                trackRiskText = "High Crosswind Advisory - Speed Restriction Notice";
                trackRiskColor = "#D97706";
            } else if (condition.toLowerCase().includes("fog") || condition.toLowerCase().includes("mist")) {
                trackRiskText = "Reduced Visibility Advisory - Cautionary Signal Aspect";
                trackRiskColor = "#D97706";
            }

            const riskEl = document.getElementById('weatherTrackConditionRisk');
            if (riskEl) {
                riskEl.textContent = trackRiskText;
                riskEl.style.color = trackRiskColor;
            }

            const radarSummaryEl = document.getElementById('weatherRadarStatusSummary');
            if (radarSummaryEl) {
                radarSummaryEl.textContent = this.radarFrames.length > 0 
                    ? `RainViewer Doppler Stream Active (${this.radarFrames.length} Frames)`
                    : 'RainViewer Doppler Feed Offline';
                radarSummaryEl.style.color = this.radarFrames.length > 0 ? '#0284C7' : '#94A3B8';
            }

            setTxt('weatherCurrentSummaryWeather', `${temp} (${condition}, Wind ${wind})`);
            setTxt('weatherLastUpdateSummary', updatedTimeStr);

            if (errorBanner) errorBanner.style.display = 'none';
            if (gridContent) gridContent.style.display = 'grid';

            this.lastWeatherCoords = [lat, lon];
            this.lastWeatherTime = Date.now();
        } catch (e) {
            console.warn("Real weather fetch failed:", e);
            if (errorBanner) errorBanner.style.display = 'flex';
        }
    }

    decodeWmoWeather(code) {
        switch (code) {
            case 0:
                return { condition: "Clear Sky", icon: "fa-sun" };
            case 1:
                return { condition: "Mainly Clear", icon: "fa-cloud-sun" };
            case 2:
                return { condition: "Partly Cloudy", icon: "fa-cloud-sun" };
            case 3:
                return { condition: "Overcast", icon: "fa-cloud" };
            case 45:
            case 48:
                return { condition: "Foggy / Mist", icon: "fa-smog" };
            case 51:
                return { condition: "Light Drizzle", icon: "fa-cloud-rain" };
            case 53:
                return { condition: "Moderate Drizzle", icon: "fa-cloud-rain" };
            case 55:
                return { condition: "Dense Drizzle", icon: "fa-cloud-showers-heavy" };
            case 61:
                return { condition: "Slight Rain", icon: "fa-cloud-rain" };
            case 63:
                return { condition: "Moderate Rain", icon: "fa-cloud-showers-heavy" };
            case 65:
                return { condition: "Heavy Rain", icon: "fa-cloud-showers-heavy" };
            case 71:
            case 73:
            case 75:
                return { condition: "Snow Fall", icon: "fa-snowflake" };
            case 80:
            case 81:
                return { condition: "Rain Showers", icon: "fa-cloud-sun-rain" };
            case 82:
                return { condition: "Violent Showers", icon: "fa-cloud-showers-heavy" };
            case 95:
                return { condition: "Thunderstorm", icon: "fa-bolt" };
            case 96:
            case 99:
                return { condition: "Severe Thunderstorm", icon: "fa-cloud-bolt" };
            default:
                return { condition: "Passing Clouds", icon: "fa-cloud" };
        }
    }

    startWeatherTicker() {
        if (this.weatherRefreshInterval) clearInterval(this.weatherRefreshInterval);
        this.weatherRefreshInterval = setInterval(() => {
            if (this.currentTrain) {
                const coords = this.getRoutePolyline(this.currentTrain);
                if (coords && coords.length > 0) {
                    this.updateRealWeather(this.lastWeatherCoords ? this.lastWeatherCoords[0] : coords[0][0], this.lastWeatherCoords ? this.lastWeatherCoords[1] : coords[0][1], this.currentTrain.current_location || this.currentTrain.short_name);
                }
            }
        }, 60000);

        if (this.radarRefreshInterval) clearInterval(this.radarRefreshInterval);
        this.radarRefreshInterval = setInterval(() => {
            this.setupWeatherLayers();
        }, 600000);
    }

    toggleFullscreen() {
        const card = document.getElementById('passengerWeatherContainerCard');
        if (!card) return;

        this.isFullscreen = !this.isFullscreen;
        card.classList.toggle('is-fullscreen', this.isFullscreen);

        const btnIcon = document.querySelector('#btnWeatherFullscreen i');
        if (btnIcon) {
            btnIcon.className = this.isFullscreen ? 'fa-solid fa-compress' : 'fa-solid fa-up-right-and-down-left-from-center';
        }

        setTimeout(() => {
            if (this.map) {
                this.map.invalidateSize();
                this.fitEntireRoute();
            }
        }, 150);
    }
}

// Global instances
window.routeMapTracker = new RouteMapTracker('liveTrackingMap');
window.weatherMapTracker = new WeatherMapTracker('weatherTrackingMap');

