/**
 * GatiSetu - Station Display Board (FIDS) Controller
 * High-visibility Passenger Information Display for Station TVs & Monitors
 */

class StationBoardManager {
    constructor() {
        this.currentStation = 'NDLS';
        this.currentMode = 'arrivals'; // 'arrivals' | 'departures'
        this.autoRefreshTimer = null;
    }

    init() {
        this.setupListeners();
    }

    setupListeners() {
        const selectEl = document.getElementById('fidsStationSelect');
        if (selectEl) {
            selectEl.addEventListener('change', (e) => {
                this.currentStation = e.target.value;
                this.loadStationBoard(this.currentStation);
            });
        }

        const modeBtns = document.querySelectorAll('.fids-mode-btn');
        modeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                modeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentMode = btn.getAttribute('data-fids-mode') || 'arrivals';
                this.loadStationBoard(this.currentStation);
            });
        });

        const refreshBtn = document.getElementById('btnRefreshFids');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadStationBoard(this.currentStation);
            });
        }
    }

    startAutoRefresh() {
        if (this.autoRefreshTimer) clearInterval(this.autoRefreshTimer);
        this.autoRefreshTimer = setInterval(() => {
            const fidsPane = document.getElementById('view-station-board');
            if (fidsPane && fidsPane.classList.contains('active-view')) {
                this.loadStationBoard(this.currentStation, true);
            }
        }, 5000);
    }

    async loadStationBoard(stationCode = 'NDLS', silent = false) {
        const tbody = document.getElementById('fidsTableBody');
        const stnTitle = document.getElementById('fidsStationTitle');
        const stnCodeEl = document.getElementById('fidsStationCode');

        if (!silent && tbody) {
            tbody.innerHTML = `<tr><td colspan="7" class="fids-loading-row"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading live station board for ${stationCode}...</td></tr>`;
        }

        try {
            const data = await window.railwayApi.getStationDisplay(stationCode);
            if (stnTitle) stnTitle.textContent = `${data.station_name || stationCode} Junction`;
            if (stnCodeEl) stnCodeEl.textContent = stationCode;

            const items = this.currentMode === 'arrivals' ? data.arrivals : data.departures;
            this.renderTable(items);
        } catch (e) {
            console.error("Failed to load station display", e);
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="7" class="fids-empty-row"><i class="fa-solid fa-triangle-exclamation"></i> No scheduled trains currently at ${stationCode}.</td></tr>`;
            }
        }
    }

    renderTable(items) {
        const tbody = document.getElementById('fidsTableBody');
        if (!tbody) return;

        if (!items || items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="fids-empty-row">No active ${this.currentMode} found for this station.</td></tr>`;
            return;
        }

        // Deduplicate items by unique train_number
        const seen = new Set();
        const uniqueItems = items.filter(item => {
            const key = String(item.train_number || '').trim();
            if (!key || seen.has(key)) return false;
            seen.add(key);
            return true;
        });

        tbody.innerHTML = uniqueItems.map(item => {
            const isDelayed = item.delay_mins > 0;
            const delayClass = isDelayed ? 'fids-delay-warning' : 'fids-delay-ontime';
            const delayText = isDelayed ? `+${item.delay_mins}m` : 'On Time';

            const predTime = item.predicted_time || item.predicted_arr || item.predicted_dep || '--:--';
            const srcName = (item.source || '').split('(')[0].trim();
            const destName = (item.destination || '').split('(')[0].trim();

            const statusCode = (item.status_code || item.current_status_code || '').toUpperCase();
            const rawStatus = (item.status || item.current_status || '').toUpperCase();

            let statusBadgeClass = 'fids-status-upcoming';
            let statusText = 'On Time';

            if (statusCode === 'NOT_STARTED' || rawStatus === 'NOT STARTED' || rawStatus === 'NOT-STARTED' || rawStatus === 'NOT_STARTED') {
                statusBadgeClass = 'fids-status-not-started';
                statusText = 'NOT STARTED';
            } else if (statusCode === 'COMPLETED' || rawStatus === 'COMPLETED' || rawStatus === 'ARRIVED') {
                statusBadgeClass = 'fids-status-departed';
                statusText = 'Completed';
            } else if (isDelayed) {
                statusBadgeClass = 'fids-status-delayed';
                statusText = item.delay_mins > 15 ? 'Delayed' : 'Running Late';
            } else if (item.status === 'approaching') {
                statusBadgeClass = 'fids-status-approaching';
                statusText = 'Approaching';
            } else if (item.status === 'departed' || item.status === 'arrived') {
                statusBadgeClass = 'fids-status-departed';
                statusText = item.status === 'arrived' ? 'Arrived' : 'Departed';
            }

            return `
                <tr class="fids-row ${isDelayed ? 'row-delayed' : ''}">
                    <td class="fids-col-num"><strong>${item.train_number}</strong></td>
                    <td class="fids-col-name">
                        <div class="fids-tname">${item.short_name || item.train_name}</div>
                    </td>
                    <td class="fids-col-from">${srcName}</td>
                    <td class="fids-col-to">${destName}</td>
                    <td class="fids-col-dynamic">
                        <span class="fids-eta-val">${predTime}</span>
                    </td>
                    <td class="fids-col-delay">
                        <span class="fids-delay-pill ${delayClass}">${delayText}</span>
                    </td>
                    <td class="fids-col-platform">
                        <span class="fids-pf-badge">PF ${item.platform || '1'}</span>
                    </td>
                    <td class="fids-col-status">
                        <span class="fids-status-pill ${statusBadgeClass}">${statusText}</span>
                    </td>
                </tr>
            `;
        }).join('');
    }
}

window.stationBoardManager = new StationBoardManager();
