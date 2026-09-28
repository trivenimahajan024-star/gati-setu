/**
 * GatiSetu - Unified API Client
 * Connects Frontend to FastAPI Backend with Automatic Local Mock Fallback
 */

function getApiBase() {
    if (typeof window !== 'undefined' && window.GATI_API_BASE) {
        return window.GATI_API_BASE;
    }
    if (typeof localStorage !== 'undefined') {
        const stored = localStorage.getItem('gatisetu_api_base');
        if (stored) return stored.replace(/\/+$/, '');
    }
    if (typeof window !== 'undefined' && window.location && window.location.protocol.startsWith('http') && !window.location.hostname.includes('appassets.androidplatform.net')) {
        return '/api';
    }
    return 'http://10.0.2.2:8000/api';
}

const API_BASE = getApiBase();

class RailwayApiClient {
    async fetchWithFallback(url, options = {}, fallbackFn = null) {
        try {
            const res = await fetch(url, options);
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: 'API Error' }));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            return await res.json();
        } catch (e) {
            console.warn(`API request to ${url} failed or offline, using fallback data service`, e);
            if (fallbackFn) {
                return await fallbackFn();
            }
            throw e;
        }
    }

    async getAllTrains() {
        return this.fetchWithFallback(`${API_BASE}/trains`, {});
    }

    async getTrainsBetweenStations(fromStation, toStation) {
        const fromEnc = encodeURIComponent(String(fromStation).trim());
        const toEnc = encodeURIComponent(String(toStation).trim());
        const res = await fetch(`${API_BASE}/trains/between?from_station=${fromEnc}&to_station=${toEnc}`);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Failed to find trains between stations' }));
            throw new Error(err.detail || `Error loading trains between ${fromStation} and ${toStation}`);
        }
        return await res.json();
    }

    async searchTrains(query, limit = 10) {
        const qEnc = encodeURIComponent(String(query).trim());
        try {
            const res = await fetch(`${API_BASE}/trains/search?q=${qEnc}&limit=${limit}`);
            if (!res.ok) {
                return [];
            }
            return await res.json();
        } catch (e) {
            console.warn("Search trains API error:", e);
            return [];
        }
    }

    async getTrainDetails(trainNumber) {
        const res = await fetch(`${API_BASE}/train/${trainNumber}`);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: `Train ${trainNumber} not found` }));
            throw new Error(err.detail || `Error loading train ${trainNumber} (HTTP ${res.status})`);
        }
        return await res.json();
    }

    async getTrainRoute(trainNumber) {
        const res = await fetch(`${API_BASE}/train/${trainNumber}/route`);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Route not found' }));
            throw new Error(err.detail || `Error loading route (HTTP ${res.status})`);
        }
        return await res.json();
    }

    async getLiveTelemetry(trainNumber) {
        const res = await fetch(`${API_BASE}/train/${trainNumber}/live`);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Live telemetry unavailable' }));
            throw new Error(err.detail || `Error loading telemetry (HTTP ${res.status})`);
        }
        return await res.json();
    }

    async simulateTrainStep(trainNumber) {
        const res = await fetch(`${API_BASE}/train/${trainNumber}/simulate`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Live update failed' }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        return await res.json();
    }

    async getStationDisplay(stationCode = 'NDLS') {
        return this.fetchWithFallback(`${API_BASE}/station/${stationCode}/display`, {}, () => {
            return {
                station_code: stationCode,
                station_name: stationCode,
                arrivals: [],
                departures: []
            };
        });
    }

    async getControlRoomOverview() {
        return this.fetchWithFallback(`${API_BASE}/control/overview`, {}, () => ({
            total_active_trains: 4,
            on_time_trains: 3,
            delayed_trains: 1,
            on_time_pct: 75.0,
            average_delay_mins: 9.0,
            active_tsrs: 1,
            congested_sections: 1,
            network_status: "NORMAL WITH ISOLATED CONGESTION"
        }));
    }

    async getControlRoomTrains() {
        return this.fetchWithFallback(`${API_BASE}/control/trains`, {}, () => window.dataService.getAvailableTrains());
    }

    async getControlRoomAlerts() {
        return this.fetchWithFallback(`${API_BASE}/control/alerts`, {}, () => []);
    }

    async injectEvent(trainNumber, eventType, delayMins = 5, description = null) {
        return this.fetchWithFallback(`${API_BASE}/control/inject-event`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                train_number: String(trainNumber),
                event_type: eventType,
                delay_impact_mins: delayMins,
                description: description
            })
        });
    }

    async simulateNetworkTick() {
        return this.fetchWithFallback(`${API_BASE}/control/simulate-tick`, { method: 'POST' });
    }

    async staffLogin(username, password, role) {
        return this.fetchWithFallback(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role })
        }, () => ({
            status: 'authenticated',
            role: role,
            name: role === 'station_staff' ? 'Station Master' : 'Chief Controller'
        }));
    }

    async getMapConfig() {
        return this.fetchWithFallback(`${API_BASE}/config`, {}, () => ({
            maptiler_api_key: ''
        }));
    }

    async fetchRealWeather(lat, lon) {
        if (lat === undefined || lon === undefined || lat === null || lon === null) {
            throw new Error("Invalid coordinates for weather");
        }
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,wind_speed_10m&timezone=auto`;
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`Open-Meteo HTTP ${res.status}`);
        }
        return await res.json();
    }
}

window.railwayApi = new RailwayApiClient();
