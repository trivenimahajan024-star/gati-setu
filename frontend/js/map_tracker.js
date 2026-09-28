
class RouteMapTracker {
    constructor(mapElementId) {
        this.mapElementId = mapElementId;
        this.map = null;
        this.trainMarker = null;
        this.passedPolyline = null;
        this.upcomingPolyline = null;
        this.stationMarkers = [];
    }

    init() {
        if (this.map) return;
        this.map = L.map(this.mapElementId, {
            zoomControl: true,
            attributionControl: false
        }).setView([23.5, 80.0], 5);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd'
        }).addTo(this.map);
    }

    renderRoute(routeData, telemetry) {
        this.init();
        
        this.stationMarkers.forEach(m => this.map.removeLayer(m));
        this.stationMarkers = [];
        if (this.passedPolyline) this.map.removeLayer(this.passedPolyline);
        if (this.upcomingPolyline) this.map.removeLayer(this.upcomingPolyline);
        if (this.trainMarker) this.map.removeLayer(this.trainMarker);

        const stations = routeData.stations;
        if (!stations || stations.length === 0) return;

        const allLatLngs = stations.map(s => [s.lat, s.lon]);
        const currSecIdx = routeData.current_section_index;

        stations.forEach((stn, idx) => {
            let pinClass = 'pin-upcoming';
            if (stn.passed) pinClass = 'pin-passed';
            else if (stn.current) pinClass = 'pin-current';
            else if (idx === stations.length - 1) pinClass = 'pin-dest';

            const customIcon = L.divIcon({
                className: `station-pin ${pinClass}`,
                iconSize: [14, 14],
                iconAnchor: [7, 7]
            });

            const marker = L.marker([stn.lat, stn.lon], { icon: customIcon })
                .bindPopup(`
                    <div style="font-family: Inter, sans-serif; font-size: 12px;">
                        <strong>${stn.station_name} (${stn.station_code})</strong><br>
                        Distance: ${stn.distance_km} km<br>
                        Sched Arr: ${stn.scheduled_arrival} | Dep: ${stn.scheduled_departure}<br>
                        Platform: ${stn.platform}
                    </div>
                `)
                .addTo(this.map);

            this.stationMarkers.push(marker);
        });

        const passedPoints = allLatLngs.slice(0, currSecIdx + 1);
        if (telemetry && telemetry.current_lat) {
            passedPoints.push([telemetry.current_lat, telemetry.current_lon]);
        }

        const upcomingPoints = [];
        if (telemetry && telemetry.current_lat) {
            upcomingPoints.push([telemetry.current_lat, telemetry.current_lon]);
        }
        upcomingPoints.push(...allLatLngs.slice(currSecIdx + 1));

        if (passedPoints.length >= 2) {
            this.passedPolyline = L.polyline(passedPoints, {
                color: '#64748b',
                weight: 4,
                dashArray: '4, 6',
                opacity: 0.8
            }).addTo(this.map);
        }

        if (upcomingPoints.length >= 2) {
            this.upcomingPolyline = L.polyline(upcomingPoints, {
                color: '#0284c7',
                weight: 5,
                opacity: 0.95
            }).addTo(this.map);
        }

        if (telemetry && telemetry.current_lat) {
            const trainIcon = L.divIcon({
                className: 'train-live-marker',
                html: '<i class="fa-solid fa-train-subway"></i>',
                iconSize: [36, 36],
                iconAnchor: [18, 18]
            });

            this.trainMarker = L.marker([telemetry.current_lat, telemetry.current_lon], { icon: trainIcon })
                .bindPopup(`
                    <div style="font-family: Inter, sans-serif; font-size: 13px;">
                        <strong style="color: #2563eb;">Train #${telemetry.train_number}</strong><br>
                        Speed: <strong>${telemetry.speed_kmh} km/h</strong><br>
                        Heading: ${telemetry.heading}°<br>
                        Delay: <strong>+${telemetry.current_delay_mins} min</strong><br>
                        Status: <span style="color: green;">${telemetry.status}</span>
                    </div>
                `)
                .addTo(this.map);
        }

        this.map.fitBounds(L.latLngBounds(allLatLngs), { padding: [40, 40] });
    }

    updateTrainPosition(telemetry) {
        if (this.trainMarker && telemetry.current_lat) {
            this.trainMarker.setLatLng([telemetry.current_lat, telemetry.current_lon]);
        }
    }
}
