
class GatiSetuApp {
    constructor() {
        this.currentTrainNumber = '12301';
        this.mapTracker = new RouteMapTracker('liveRouteMap');
        this.simLab = null;
        this.appMode = 'passenger'; // 'passenger' | 'station_staff' | 'control_room'
        this.currentRole = 'passenger';
        this.selectedStaffLoginRole = 'station_staff';
        this.notificationManager = new NotificationManager(this);
        this.userProfileManager = new UserProfileManager(this);
        this.activeTabId = 'tab-dashboard';
    }

    async init() {
        this.setupClock();
        this.setupTabs();
        this.setupSearch();
        this.setupStaffLoginHandlers();
        this.simLab = new SimulationLab(this);
        this.notificationManager.init();
        this.userProfileManager.init();

        const stnSelect = document.getElementById('fidsStationSelect');
        if (stnSelect) {
            stnSelect.addEventListener('change', (e) => {
                loadStationDisplayBoard(e.target.value);
            });
        }

        const refreshOCCBtn = document.getElementById('btnRefreshOCC');
        if (refreshOCCBtn) {
            refreshOCCBtn.addEventListener('click', () => loadControlRoomData());
        }

        await this.setAppMode('passenger');
        await this.selectTrain(this.currentTrainNumber);
        loadControlRoomData();
        loadStationDisplayBoard('NDLS');
    }

    setupClock() {
        const updateClocks = () => {
            const now = new Date();
            const timeStr = now.toTimeString().split(' ')[0];
            const clockEl = document.getElementById('liveClock');
            const fidsClock = document.getElementById('fidsClock');
            const phoneTime = document.getElementById('phoneTime');
            if (clockEl) clockEl.innerText = timeStr;
            if (fidsClock) fidsClock.innerText = timeStr;
            if (phoneTime) phoneTime.innerText = timeStr.slice(0, 5);
        };
        setInterval(updateClocks, 1000);
        updateClocks();
    }

    setupTabs() {
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.getAttribute('data-tab');
                this.switchTab(targetId);
            });
        });
    }

    setupStaffLoginHandlers() {
        const btnOpenLogin = document.getElementById('btnOpenStaffLogin');
        if (btnOpenLogin) {
            btnOpenLogin.addEventListener('click', () => this.openStaffLogin());
        }

        const btnLogoutStaff = document.getElementById('btnLogoutStaff');
        if (btnLogoutStaff) {
            btnLogoutStaff.addEventListener('click', () => this.logoutStaff());
        }

        const menuStaffPortal = document.getElementById('menuStaffPortal');
        if (menuStaffPortal) {
            menuStaffPortal.addEventListener('click', (e) => {
                e.preventDefault();
                this.openStaffLogin();
            });
        }

        const menuLogoutBtn = document.getElementById('menuLogoutBtn');
        if (menuLogoutBtn) {
            menuLogoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logoutStaff();
            });
        }

        const btnBackToPassenger = document.getElementById('btnBackToPassenger');
        if (btnBackToPassenger) {
            btnBackToPassenger.addEventListener('click', (e) => {
                e.preventDefault();
                this.setAppMode('passenger');
            });
        }

        const roleTabs = document.querySelectorAll('.sl-role-tab');
        const staffIdInput = document.getElementById('staffIdInput');
        roleTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                roleTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const role = tab.getAttribute('data-role');
                this.selectedStaffLoginRole = role;
                if (staffIdInput) {
                    staffIdInput.value = role === 'station_staff' ? 'BSL-STATION-01' : 'CR-OCC-884';
                }
            });
        });

        const loginForm = document.getElementById('staffLoginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.setAppMode(this.selectedStaffLoginRole);
            });
        }
    }

    openStaffLogin() {
        document.querySelectorAll('.dropdown-panel').forEach(p => p.classList.remove('show'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        const loginPane = document.getElementById('tab-staff-login');
        if (loginPane) loginPane.classList.add('active');
        this.activeTabId = 'tab-staff-login';
    }

    async logoutStaff() {
        await this.setAppMode('passenger');
    }

    async setAppMode(mode) {
        this.appMode = mode;
        this.currentRole = mode;
        this.userProfileManager.currentRole = mode;

        const brandTitle = document.querySelector('.brand-title');
        const brandSub = document.querySelector('.brand-sub');
        const simBanner = document.querySelector('.simulation-banner');

        if (mode === 'passenger') {
            if (brandTitle) brandTitle.innerHTML = 'GATI-SETU <span class="badge-sih">SIH 2026</span>';
            if (brandSub) brandSub.innerText = 'Dynamic ETA Forecasting Engine | Ministry of Railways';
            if (simBanner) simBanner.style.display = 'none';
        } else if (mode === 'station_staff') {
            if (brandTitle) brandTitle.innerHTML = 'GATI-SETU <span class="badge-sih" style="background:#0284c7;">STATION BOARD</span>';
            if (brandSub) brandSub.innerText = 'Station Operations & FIDS Display Control | Bhusawal Junction (BSL)';
            if (simBanner) simBanner.style.display = 'none';
        } else if (mode === 'control_room') {
            if (brandTitle) brandTitle.innerHTML = 'GATI-SETU <span class="badge-sih" style="background:#7c3aed;">CONTROL ROOM</span>';
            if (brandSub) brandSub.innerText = 'Central Railway Operations Control Center (OCC) | Bhusawal Division';
            if (simBanner) simBanner.style.display = 'flex';
        }

        const btnOpenLogin = document.getElementById('btnOpenStaffLogin');
        const btnLogoutStaff = document.getElementById('btnLogoutStaff');
        const menuStaffPortal = document.getElementById('menuStaffPortal');
        const menuLogoutBtn = document.getElementById('menuLogoutBtn');

        if (mode === 'passenger') {
            if (btnOpenLogin) btnOpenLogin.style.display = 'inline-flex';
            if (btnLogoutStaff) btnLogoutStaff.style.display = 'none';
            if (menuStaffPortal) menuStaffPortal.style.display = 'flex';
            if (menuLogoutBtn) menuLogoutBtn.style.display = 'none';
        } else {
            if (btnOpenLogin) btnOpenLogin.style.display = 'none';
            if (btnLogoutStaff) btnLogoutStaff.style.display = 'inline-flex';
            if (menuStaffPortal) menuStaffPortal.style.display = 'none';
            if (menuLogoutBtn) menuLogoutBtn.style.display = 'flex';
        }

        const tabBtns = document.querySelectorAll('#mainTabsBar .tab-btn');
        tabBtns.forEach(btn => {
            const modesAllowed = (btn.getAttribute('data-modes') || '').split(',');
            if (modesAllowed.includes(mode)) {
                btn.style.display = 'inline-flex';
            } else {
                btn.style.display = 'none';
            }
        });

        await this.userProfileManager.loadProfile(mode);
        await this.notificationManager.loadNotifications(mode);

        if (mode === 'passenger') {
            this.switchTab('tab-dashboard');
        } else if (mode === 'station_staff') {
            this.switchTab('tab-station-display');
        } else if (mode === 'control_room') {
            this.switchTab('tab-control-room');
        }
    }

    switchTab(targetId) {
        const allowedModesForTab = {
            'tab-dashboard': ['passenger', 'control_room'],
            'tab-control-room': ['control_room'],
            'tab-station-display': ['station_staff'],
            'tab-passenger-mobile': ['passenger'],
            'tab-user-profile': ['passenger', 'station_staff', 'control_room'],
            'tab-architecture': ['passenger'],
            'tab-staff-login': ['passenger', 'station_staff', 'control_room']
        };

        const allowed = allowedModesForTab[targetId] || ['passenger'];
        if (!allowed.includes(this.appMode) && targetId !== 'tab-staff-login') {
            console.warn(`Access denied to ${targetId} in mode ${this.appMode}`);
            return;
        }

        this.activeTabId = targetId;
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(t => {
            if (t.getAttribute('data-tab') === targetId) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        const targetPane = document.getElementById(targetId);
        if (targetPane) targetPane.classList.add('active');

        if (targetId === 'tab-dashboard' && this.mapTracker.map) {
            setTimeout(() => this.mapTracker.map.invalidateSize(), 200);
        } else if (targetId === 'tab-control-room') {
            loadControlRoomData();
        } else if (targetId === 'tab-station-display') {
            const stnSelect = document.getElementById('fidsStationSelect');
            loadStationDisplayBoard(stnSelect ? stnSelect.value : 'NDLS');
        } else if (targetId === 'tab-user-profile') {
            this.userProfileManager.renderProfilePane();
        }
    }

    setupSearch() {
        const form = document.getElementById('globalSearchForm');
        const input = document.getElementById('trainSearchInput');
        const chips = document.querySelectorAll('.quick-train-chips .chip');

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const val = input.value.trim();
            if (val) this.selectTrain(val);
        });

        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                chips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                const tNum = chip.getAttribute('data-train');
                input.value = tNum;
                this.selectTrain(tNum);
            });
        });

        const mSearchBtn = document.getElementById('btnMobileSearch');
        const mInput = document.getElementById('mobileSearchInput');
        if (mSearchBtn && mInput) {
            mSearchBtn.addEventListener('click', () => {
                const val = mInput.value.trim();
                if (val) this.selectTrain(val);
            });
        }
    }

    showAlert(message) {
        const banner = document.getElementById('alertBanner');
        if (banner) {
            banner.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${message}`;
            banner.classList.remove('hidden');
        }
    }

    hideAlert() {
        const banner = document.getElementById('alertBanner');
        if (banner) banner.classList.add('hidden');
    }

    async selectTrain(trainNumber) {
        this.hideAlert();
        this.currentTrainNumber = trainNumber;

        const input = document.getElementById('trainSearchInput');
        if (input) input.value = trainNumber;
        const mInput = document.getElementById('mobileSearchInput');
        if (mInput) mInput.value = trainNumber;

        document.querySelectorAll('.quick-train-chips .chip').forEach(c => {
            if (c.getAttribute('data-train') === trainNumber) c.classList.add('active');
            else c.classList.remove('active');
        });

        try {
            await this.loadTrainData(trainNumber);
        } catch (err) {
            this.showAlert(err.message);
        }
    }

    async refreshCurrentTrain() {
        try {
            await this.loadTrainData(this.currentTrainNumber);
        } catch (err) {
            console.error('Error refreshing train:', err);
        }
    }

    async loadTrainData(trainNumber) {
        const summary = await api.getTrainSummary(trainNumber);
        const route = await api.getTrainRoute(trainNumber);
        const telemetry = await api.getLiveTelemetry(trainNumber);
        const eta = await api.getDynamicETA(trainNumber);

        this.renderHero(summary, eta);
        this.mapTracker.renderRoute(route, telemetry);
        renderDynamicETATimeline(eta, route);
        renderExplainabilityCards(eta.explainable_reasons);
        this.renderMobileView(summary, eta, route);

        const hudCoords = document.getElementById('hudCoords');
        const hudHeading = document.getElementById('hudHeading');
        const hudNext = document.getElementById('hudNext');
        if (hudCoords) hudCoords.innerText = `${telemetry.current_lat}, ${telemetry.current_lon}`;
        if (hudHeading) hudHeading.innerText = `${telemetry.heading}°`;
        if (hudNext) hudNext.innerText = `${summary.next_station}`;
    }

    renderHero(summary, eta) {
        document.getElementById('heroTrainType').innerText = summary.train_type;
        document.getElementById('heroTrainTitle').innerText = `${summary.train_number} - ${summary.train_name}`;
        document.getElementById('heroSource').innerText = summary.source_station;
        document.getElementById('heroDestination').innerText = summary.destination_station;
        document.getElementById('heroZone').innerText = summary.zone;

        const statusEl = document.getElementById('heroStatusText');
        if (summary.current_delay_mins > 15) {
            statusEl.className = 'metric-value-status status-delayed';
            statusEl.innerText = 'DELAYED';
        } else if (summary.current_delay_mins > 0) {
            statusEl.className = 'metric-value-status status-slight';
            statusEl.innerText = 'SLIGHT DELAY';
        } else {
            statusEl.className = 'metric-value-status status-ontime';
            statusEl.innerText = 'ON TIME';
        }

        document.getElementById('heroLocationSub').innerText = summary.current_location;
        document.getElementById('heroSpeed').innerText = summary.current_speed_kmh;
        document.getElementById('heroWeather').innerText = `Weather: ${summary.weather}`;
        document.getElementById('heroDelay').innerText = `+${summary.current_delay_mins} min`;
        document.getElementById('heroDynamicETA').innerText = eta.dynamic_destination_eta;
        document.getElementById('heroScheduledETA').innerText = eta.scheduled_destination_eta;
        document.getElementById('heroPredictedDelayDelta').innerText = `+${eta.final_predicted_delay_mins}m`;
        document.getElementById('heroConfidence').innerText = `${eta.confidence_percent}%`;
        document.getElementById('heroWindow').innerText = `Window: ${eta.prediction_window_start} - ${eta.prediction_window_end}`;

        document.getElementById('progCurrStn').innerText = summary.current_station;
        document.getElementById('progNextStn').innerText = summary.next_station;
        document.getElementById('progPct').innerText = `${summary.journey_progress_percent}%`;
        document.getElementById('progBarFill').style.width = `${summary.journey_progress_percent}%`;
    }

    renderMobileView(summary, eta, route) {
        document.getElementById('pTrainNum').innerText = `${summary.train_number} ${summary.train_name}`;
        document.getElementById('pTrainRoute').innerText = `${summary.source_station.split(' (')[0]} → ${summary.destination_station.split(' (')[0]}`;
        document.getElementById('pDynamicETA').innerText = eta.dynamic_destination_eta;
        document.getElementById('pDelay').innerText = `+${summary.current_delay_mins} min`;
        document.getElementById('pWindow').innerText = `${eta.prediction_window_start} – ${eta.prediction_window_end}`;
        document.getElementById('pNextStn').innerText = summary.next_station;

        const timeline = document.getElementById('phoneTimeline');
        if (timeline) {
            timeline.innerHTML = '';
            const predMap = {};
            if (eta.section_predictions) {
                eta.section_predictions.forEach(p => predMap[p.to_station_code] = p);
            }

            route.stations.forEach(stn => {
                const node = document.createElement('div');
                let nodeState = 'node-upcoming';
                let icon = '<i class="fa-regular fa-circle"></i>';

                if (stn.passed) {
                    nodeState = 'node-passed';
                    icon = '<i class="fa-solid fa-check"></i>';
                } else if (stn.current) {
                    nodeState = 'node-current';
                    icon = '<i class="fa-solid fa-train"></i>';
                }

                node.className = `timeline-node ${nodeState}`;
                let timeVal = stn.scheduled_arrival;
                if (!stn.passed && predMap[stn.station_code]) {
                    timeVal = predMap[stn.station_code].predicted_arrival;
                }

                node.innerHTML = `
                    <div class="node-icon">${icon}</div>
                    <span class="node-stn-name">${stn.station_name}</span>
                    <span class="node-eta-time">${timeVal}</span>
                `;
                timeline.appendChild(node);
            });
        }

        const pReasons = document.getElementById('phoneReasons');
        if (pReasons) {
            pReasons.innerHTML = '';
            if (eta.explainable_reasons && eta.explainable_reasons.length > 0) {
                eta.explainable_reasons.slice(0, 3).forEach(r => {
                    const div = document.createElement('div');
                    div.style.fontSize = '12px';
                    div.style.marginBottom = '6px';
                    div.innerHTML = `<strong>• ${r.title}:</strong> ${r.delay_impact_mins >= 0 ? '+' : ''}${r.delay_impact_mins}m (${r.description})`;
                    pReasons.appendChild(div);
                });
            } else {
                pReasons.innerHTML = '<div style="font-size:12px; color:#64748b;">Green corridor clearance. Normal running.</div>';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.gatiApp = new GatiSetuApp();
    window.gatiApp.init();
});
