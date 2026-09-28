/**
 * GatiSetu - Clean, Modern, Uncluttered Passenger Controller
 * Coordinates Progressive Disclosure, Dynamic ETA Predictions,
 * 12 Problem Statement Factors, Station Display (FIDS), and OCC Operations.
 */

class UnifiedGatiSetuApp {
    constructor() {
        this.currentRole = 'passenger'; // 'passenger' | 'station_staff' | 'control_room'
        this.currentView = 'view-passenger';
        this.currentPassengerScreen = 'screen-home';
        this.currentTrain = null;
        this.simulationTimer = null;
        this.isSimulationRunning = true;
        this.authenticatedStaff = null;
        this.isShowingAllFactors = false;
    }

    async init() {
        this.setupEventListeners();
        this.setupLiveClock();
        this.setupGlobalFactorsSection();
        this.setupTrainsBetweenSection();
        this.renderRecentSearches();

        // Restore authenticated staff session from localStorage if present
        let savedAuth = null;
        try {
            const raw = localStorage.getItem('gatisetu_staff_auth');
            if (raw) savedAuth = JSON.parse(raw);
        } catch (e) {}

        if (savedAuth && savedAuth.role) {
            this.authenticatedStaff = savedAuth;
            this.currentRole = savedAuth.role;
            this.updateAuthUI(true, savedAuth);
        } else {
            this.authenticatedStaff = null;
            this.currentRole = 'passenger';
            this.updateAuthUI(false, null);
        }

        // Initialize sub-controllers for FIDS and OCC
        if (window.stationBoardManager) window.stationBoardManager.init();
        if (window.controlRoomManager) window.controlRoomManager.init();

        // Check URL pathname and hash for direct navigation attempt
        const pathname = window.location.pathname.toLowerCase();
        const hash = window.location.hash.toLowerCase();

        if (pathname === '/station-board' || hash === '#station-board') {
            if (this.authenticatedStaff) {
                this.switchRoleView('view-station-board');
            } else {
                window.location.href = '/staff/login';
                return;
            }
        } else if (pathname === '/control-room' || hash === '#control-room') {
            if (this.authenticatedStaff) {
                this.switchRoleView('view-control-room');
            } else {
                window.location.href = '/staff/login';
                return;
            }
        } else {
            this.switchRoleView('view-passenger');
        }

        // Setup Logout handlers
        const btnLogoutStaff = document.getElementById('btnLogoutStaff');
        if (btnLogoutStaff) {
            btnLogoutStaff.addEventListener('click', () => {
                this.performStaffLogout();
            });
        }
        const btnLogoutOCC = document.getElementById('btnLogoutStaffOCC');
        if (btnLogoutOCC) {
            btnLogoutOCC.addEventListener('click', () => {
                this.performStaffLogout();
            });
        }
        const btnOccReturn = document.getElementById('btnOccReturnPassenger');
        if (btnOccReturn) {
            btnOccReturn.addEventListener('click', () => {
                this.switchRoleView('view-passenger');
            });
        }

        // Default: Load real train 12951 from RailRadar
        try {
            const train = await window.railwayApi.getTrainDetails("12951");
            if (train) {
                this.applyTrainData(train);
            }
        } catch (e) {
            console.warn("Error fetching initial train from RailRadar", e);
        }

        // Start live simulation ticker
        this.startSimulationTicker();
    }

    setupLiveClock() {
        const updateClock = () => {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            const dateStr = now.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
            
            document.querySelectorAll('.live-clock-target').forEach(el => {
                el.textContent = timeStr;
            });
            document.querySelectorAll('.live-date-target').forEach(el => {
                el.textContent = dateStr;
            });
        };
        setInterval(updateClock, 1000);
        updateClock();
    }

    setupEventListeners() {
        // Search Form Submit
        const searchForm = document.getElementById('passengerSearchForm');
        const searchInput = document.getElementById('trainSearchInput');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.hideSuggestions();
                const query = searchInput ? searchInput.value.trim() : '';
                this.handleSearch(query);
            });
        }

        // Search Input & Suggestions
        this.initSearchSuggestions();

        // Search Input Clear Button
        const btnClear = document.getElementById('btnSearchClear');
        if (btnClear && searchInput) {
            btnClear.addEventListener('click', () => {
                searchInput.value = '';
                this.hideSuggestions();
                searchInput.focus();
                this.hideSearchError();
            });
        }

        // Quick Selection Chips (.train-chip and .quick-chip)
        const quickChips = document.querySelectorAll('.train-chip, .quick-chip');
        quickChips.forEach(chip => {
            chip.addEventListener('click', () => {
                quickChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                const trainNo = chip.getAttribute('data-train');
                if (trainNo) {
                    if (searchInput) searchInput.value = trainNo;
                    this.handleSearch(trainNo);
                }
            });
        });

        // Clear Recent Searches
        const btnClearRecent = document.getElementById('btnClearRecentSearches');
        if (btnClearRecent) {
            btnClearRecent.addEventListener('click', () => {
                window.dataService.clearRecentSearches();
                this.renderRecentSearches();
            });
        }

        // Accordion Toggle for "Why is ETA changing?" (Details Screen)
        const btnToggleWhy = document.getElementById('btnToggleWhyEta');
        if (btnToggleWhy) {
            btnToggleWhy.addEventListener('click', () => {
                const body = document.getElementById('detailsWhyEtaBody');
                const chevron = document.getElementById('detailsFactorsChevron');
                if (body) {
                    const isHidden = body.style.display === 'none' || body.style.display === '';
                    body.style.display = isHidden ? 'block' : 'none';
                    if (chevron) {
                        chevron.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
                    }
                }
            });
        }

        // Accordion Toggle for "Why is ETA changing?" (Map Screen)
        const btnToggleWhyMap = document.getElementById('btnToggleWhyEtaMap');
        if (btnToggleWhyMap) {
            btnToggleWhyMap.addEventListener('click', () => {
                const body = document.getElementById('mapWhyEtaBody');
                const chevron = document.getElementById('mapFactorsChevron');
                if (body) {
                    const isHidden = body.style.display === 'none' || body.style.display === '';
                    body.style.display = isHidden ? 'block' : 'none';
                    if (chevron) {
                        chevron.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
                    }
                }
            });
        }

        // Accordion Toggle for "Why is ETA changing?" (Route Screen)
        const btnToggleWhyRoute = document.getElementById('btnToggleWhyEtaRoute');
        if (btnToggleWhyRoute) {
            btnToggleWhyRoute.addEventListener('click', () => {
                const body = document.getElementById('routeWhyEtaBody');
                const chevron = document.getElementById('routeFactorsChevron');
                if (body) {
                    const isHidden = body.style.display === 'none' || body.style.display === '';
                    body.style.display = isHidden ? 'block' : 'none';
                    if (chevron) {
                        chevron.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
                    }
                }
            });
        }

        // Navigation links
        const navButtons = document.querySelectorAll('[data-target-screen]');
        navButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.getAttribute('data-target-screen');
                if (target) {
                    this.navigateToPassengerScreen(target);
                }
            });
        });

        // Top Role Switcher Tabs
        const viewTabs = document.querySelectorAll('[data-target-view]');
        viewTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetView = tab.getAttribute('data-target-view');
                if (targetView) {
                    this.switchRoleView(targetView);
                }
            });
        });

        // Toggle All Factors Buttons (Details, Map & Route)
        const btnToggleAll = document.getElementById('btnToggleAllFactors');
        if (btnToggleAll) {
            btnToggleAll.addEventListener('click', () => {
                this.toggleAllFactorsView();
            });
        }

        const btnToggleAllMap = document.getElementById('btnToggleAllFactorsMap');
        if (btnToggleAllMap) {
            btnToggleAllMap.addEventListener('click', () => {
                this.toggleAllFactorsView();
            });
        }

        const btnToggleAllRoute = document.getElementById('btnToggleAllFactorsRoute');
        if (btnToggleAllRoute) {
            btnToggleAllRoute.addEventListener('click', () => {
                this.toggleAllFactorsView();
            });
        }

    }

    toggleAllFactorsView() {
        this.isShowingAllFactors = !this.isShowingAllFactors;
        const btnDetails = document.getElementById('btnToggleAllFactors');
        const btnMap = document.getElementById('btnToggleAllFactorsMap');
        const btnRoute = document.getElementById('btnToggleAllFactorsRoute');
        const containerDetails = document.getElementById('detailsAllTwelveFactorsContainer');
        const containerMap = document.getElementById('mapAllTwelveFactorsContainer');
        const containerRoute = document.getElementById('routeAllTwelveFactorsContainer');

        const labelText = this.isShowingAllFactors ? 'Show less' : 'View all 12 factors';
        if (btnDetails) btnDetails.textContent = labelText;
        if (btnMap) btnMap.textContent = labelText;
        if (btnRoute) btnRoute.textContent = labelText;

        if (containerDetails) {
            containerDetails.style.display = this.isShowingAllFactors ? 'flex' : 'none';
        }
        if (containerMap) {
            containerMap.style.display = this.isShowingAllFactors ? 'flex' : 'none';
        }
        if (containerRoute) {
            containerRoute.style.display = this.isShowingAllFactors ? 'flex' : 'none';
        }

        if (this.isShowingAllFactors && this.currentTrain) {
            this.renderAllTwelveFactors(this.currentTrain);
        }
    }

    setupStaffAuthModal() {
        const modal = document.getElementById('staffLoginModal');
        const btnOpenModal = document.getElementById('btnOpenStaffLogin');
        const btnCloseModal = document.getElementById('btnCloseStaffModal');
        const loginForm = document.getElementById('staffLoginForm');
        const btnLogoutStaff = document.getElementById('btnLogoutStaff');

        if (btnOpenModal && modal) {
            btnOpenModal.addEventListener('click', () => {
                modal.classList.add('active-modal');
                modal.style.setProperty('display', 'flex', 'important');
            });
        }

        if (btnCloseModal && modal) {
            btnCloseModal.addEventListener('click', () => {
                modal.classList.remove('active-modal');
                modal.style.setProperty('display', 'none', 'important');
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active-modal');
                    modal.style.setProperty('display', 'none', 'important');
                }
            });
        }

        // Preset Logins
        const btnQuickStation = document.getElementById('btnQuickLoginStation');
        if (btnQuickStation) {
            btnQuickStation.addEventListener('click', () => {
                this.performStaffLogin('station_master', 'railway123', 'station_staff');
            });
        }

        const btnQuickOCC = document.getElementById('btnQuickLoginOCC');
        if (btnQuickOCC) {
            btnQuickOCC.addEventListener('click', () => {
                this.performStaffLogin('occ_controller', 'admin123', 'control_room');
            });
        }

        // Password Visibility Toggle
        const btnTogglePass = document.getElementById('btnToggleStaffPassword');
        const passInput = document.getElementById('staffPasswordInput');
        const eyeIcon = document.getElementById('eyeIcon');
        if (btnTogglePass && passInput) {
            btnTogglePass.addEventListener('click', () => {
                const isPassword = passInput.type === 'password';
                passInput.type = isPassword ? 'text' : 'password';
                if (eyeIcon) {
                    eyeIcon.className = isPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
                }
            });
        }

        // Forgot Password Helper
        const btnForgot = document.getElementById('btnForgotStaffPassword');
        if (btnForgot) {
            btnForgot.addEventListener('click', () => {
                const errBox = document.getElementById('staffLoginError');
                if (errBox) {
                    errBox.style.display = 'block';
                    errBox.style.backgroundColor = '#EFF6FF';
                    errBox.style.borderColor = '#BFDBFE';
                    errBox.style.color = '#1E40AF';
                    errBox.innerHTML = `<strong>Demo Staff Access:</strong><br>• Station Master: <code>station_master</code> / <code>railway123</code><br>• OCC Controller: <code>occ_controller</code> / <code>admin123</code>`;
                }
            });
        }

        // Form Submit
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const username = document.getElementById('staffUsernameInput').value;
                const password = document.getElementById('staffPasswordInput').value;
                const role = document.getElementById('staffRoleSelect').value;
                this.performStaffLogin(username, password, role);
            });
        }

        // Logout Buttons (Top Navbar & Control Room Header)
        const btnLogoutOCC = document.getElementById('btnLogoutStaffOCC');
        if (btnLogoutStaff) {
            btnLogoutStaff.addEventListener('click', () => {
                this.performStaffLogout();
            });
        }
        if (btnLogoutOCC) {
            btnLogoutOCC.addEventListener('click', () => {
                this.performStaffLogout();
            });
        }
    }

    async performStaffLogin(username, password, role) {
        try {
            const authRes = await window.railwayApi.staffLogin(username, password, role);
            this.authenticatedStaff = authRes;
            this.currentRole = authRes.role;

            const modal = document.getElementById('staffLoginModal');
            if (modal) {
                modal.classList.remove('active-modal');
                modal.style.setProperty('display', 'none', 'important');
            }

            this.updateAuthUI(true, authRes);

            if (authRes.role === 'station_staff') {
                this.switchRoleView('view-station-board');
            } else if (authRes.role === 'control_room') {
                this.switchRoleView('view-control-room');
            }
        } catch (e) {
            const errEl = document.getElementById('staffLoginError');
            if (errEl) {
                errEl.textContent = e.message || 'Invalid staff credentials';
                errEl.style.display = 'block';
            }
        }
    }

    performStaffLogout() {
        this.authenticatedStaff = null;
        this.currentRole = 'passenger';
        try {
            localStorage.removeItem('gatisetu_staff_auth');
        } catch (e) {}
        this.updateAuthUI(false, null);
        this.switchRoleView('view-passenger');
        if (window.location.pathname !== '/' && window.location.pathname !== '/passenger') {
            window.location.href = '/';
        }
    }

    updateAuthUI(isLoggedIn, staffData) {
        const btnOpenModal = document.getElementById('btnOpenStaffLogin');
        const btnLogoutStaff = document.getElementById('btnLogoutStaff');
        const roleBadge = document.getElementById('headerUserRoleBadge');
        const tabStation = document.querySelector('[data-target-view="view-station-board"]');
        const tabOCC = document.querySelector('[data-target-view="view-control-room"]');
        const btnRoleStation = document.getElementById('btnRoleStation');
        const btnRoleControl = document.getElementById('btnRoleControl');

        if (isLoggedIn && staffData) {
            if (btnOpenModal) btnOpenModal.style.display = 'none';
            if (btnLogoutStaff) btnLogoutStaff.style.display = 'inline-flex';
            if (roleBadge) {
                roleBadge.textContent = staffData.role === 'station_staff' ? 'Station Master' : 'OCC Controller';
                roleBadge.className = 'header-role-pill staff-active';
                roleBadge.style.display = 'inline-flex';
            }
            if (tabStation) tabStation.style.display = 'inline-flex';
            if (tabOCC) tabOCC.style.display = 'inline-flex';
            if (btnRoleStation) btnRoleStation.style.display = 'inline-flex';
            if (btnRoleControl) btnRoleControl.style.display = 'inline-flex';
        } else {
            if (btnOpenModal) btnOpenModal.style.display = 'inline-flex';
            if (btnLogoutStaff) btnLogoutStaff.style.display = 'none';
            if (roleBadge) {
                roleBadge.textContent = 'Passenger';
                roleBadge.className = 'header-role-pill';
                roleBadge.style.display = 'none';
            }
            if (tabStation) tabStation.style.display = 'none';
            if (tabOCC) tabOCC.style.display = 'none';
            if (btnRoleStation) btnRoleStation.style.display = 'none';
            if (btnRoleControl) btnRoleControl.style.display = 'none';
        }
    }

    switchRoleView(viewId) {
        // Enforce strict role checking: Block unauthenticated access to staff views
        if ((viewId === 'view-station-board' || viewId === 'view-control-room') && !this.authenticatedStaff) {
            window.location.href = '/staff/login';
            return;
        }

        document.querySelectorAll('.portal-view-container').forEach(v => v.classList.remove('active-view'));

        const target = document.getElementById(viewId);
        if (target) {
            target.classList.add('active-view');
            this.currentView = viewId;
        }

        document.querySelectorAll('[data-target-view]').forEach(tab => {
            if (tab.getAttribute('data-target-view') === viewId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Sync pill buttons
        const btnPass = document.getElementById('btnRolePassenger');
        const btnStn = document.getElementById('btnRoleStation');
        const btnOCC = document.getElementById('btnRoleControl');
        if (btnPass) btnPass.classList.toggle('active', viewId === 'view-passenger');
        if (btnStn) btnStn.classList.toggle('active', viewId === 'view-station-board');
        if (btnOCC) btnOCC.classList.toggle('active', viewId === 'view-control-room');

        if (viewId === 'view-station-board' && window.stationBoardManager) {
            window.stationBoardManager.loadStationBoard(window.stationBoardManager.currentStation);
            window.stationBoardManager.startAutoRefresh();
        } else if (viewId === 'view-control-room' && window.controlRoomManager) {
            window.controlRoomManager.initLeafletMap();
            window.controlRoomManager.loadControlRoomData();
            window.controlRoomManager.startAutoRefresh();
            setTimeout(() => {
                if (window.controlRoomManager.map) {
                    window.controlRoomManager.map.invalidateSize();
                }
            }, 150);
        }
    }

    setupGlobalFactorsSection() {
        const btnExpand = document.getElementById('btnFactorsBarExpand');
        const drawer = document.getElementById('globalFactorsDrawer');
        const chevron = document.getElementById('factorsBarChevron');

        if (btnExpand && drawer) {
            btnExpand.addEventListener('click', () => {
                const isHidden = drawer.style.display === 'none' || drawer.style.display === '';
                drawer.style.display = isHidden ? 'block' : 'none';
                if (chevron) {
                    chevron.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
                }
                const span = btnExpand.querySelector('span');
                if (span) {
                    span.textContent = isHidden ? 'Collapse factors' : 'View all factors';
                }
            });
        }

        // Chip click opens drawer
        const chips = document.querySelectorAll('.ps-factor-chip');
        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                const factorId = chip.getAttribute('data-factor-id');
                if (drawer) {
                    drawer.style.display = 'block';
                    if (chevron) chevron.style.transform = 'rotate(180deg)';
                    const span = btnExpand ? btnExpand.querySelector('span') : null;
                    if (span) span.textContent = 'Collapse factors';
                    
                    const targetCard = document.getElementById(`global-factor-card-${factorId}`);
                    if (targetCard) {
                        targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        targetCard.style.borderColor = 'var(--gatisetu-green-light)';
                        targetCard.style.boxShadow = '0 0 0 3px rgba(5, 150, 105, 0.2)';
                        setTimeout(() => {
                            targetCard.style.borderColor = '';
                            targetCard.style.boxShadow = '';
                        }, 2500);
                    }
                }
            });
        });
    }

    renderGlobalFactorsSection() {
        const container = document.getElementById('globalFactorsGrid');
        if (!container) return;

        const allTwelve = window.EtaFactorProcessor.getAllTwelveFactors(this.currentTrain);
        container.innerHTML = allTwelve.map((f, idx) => {
            const impactBadge = f.is_active && f.delay_impact_mins > 0
                ? `<span class="eta-pill pill-high">+${f.delay_impact_mins} min</span>`
                : (f.is_active ? window.EtaFactorProcessor.getImpactBadge(f.impact_level) : `<span class="eta-pill pill-nominal">Normal</span>`);

            return `
                <div class="ps-factor-detail-card" id="global-factor-card-${f.id}">
                    <div class="ps-factor-card-top">
                        <span class="ps-factor-card-title">
                            <i class="fa-solid ${f.icon}" style="color:var(--gatisetu-green-light);"></i>
                            <span>${idx + 1}. ${f.name}</span>
                        </span>
                        ${impactBadge}
                    </div>
                    <div class="ps-factor-card-desc">${f.passenger_explanation}</div>
                </div>
            `;
        }).join('');
    }

    applyTrainData(train) {
        if (!train) return;

        // Ensure each station appears only once by station code while preserving chronological route order
        if (train && Array.isArray(train.stations)) {
            const seen = new Set();
            train.stations = train.stations.filter(stn => {
                const code = String(stn.code || '').trim().toUpperCase();
                if (!code || seen.has(code)) return false;
                seen.add(code);
                return true;
            });
        }

        this.currentTrain = train;
        window.selectedTrain = train;
        window.selectedTrainNumber = train.train_number;

        try {
            localStorage.setItem('gatisetu_selected_train', JSON.stringify(train));
            localStorage.setItem('gatisetu_selected_train_number', train.train_number);
        } catch(e) {}

        this.renderTrainDetails(train);
        this.renderGlobalFactorsSection();

        if (this.isShowingAllFactors) {
            this.renderAllTwelveFactors(train);
        }

        // Sync Map & Weather trackers
        if (window.routeMapTracker) {
            window.routeMapTracker.currentTrain = train;
            if (this.currentPassengerScreen === 'screen-map' && this.currentView === 'view-passenger') {
                window.routeMapTracker.renderTrainRoute(train);
            }
        }

        if (window.weatherMapTracker) {
            window.weatherMapTracker.currentTrain = train;
            if (this.currentPassengerScreen === 'screen-weather' && this.currentView === 'view-passenger') {
                window.weatherMapTracker.renderTrainWeatherRoute(train);
            }
        }
    }

    /**
     * Search Suggestions & Autocomplete
     */
    initSearchSuggestions() {
        const searchInput = document.getElementById('trainSearchInput');
        const suggestionsBox = document.getElementById('searchSuggestionsBox');
        if (!searchInput || !suggestionsBox) return;

        let debounceTimer = null;
        let selectedIdx = -1;

        searchInput.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            if (debounceTimer) clearTimeout(debounceTimer);
            this.hideSearchError();

            if (!val) {
                this.hideSuggestions();
                return;
            }

            debounceTimer = setTimeout(() => {
                this.fetchAndRenderSuggestions(val);
            }, 180);
        });

        searchInput.addEventListener('focus', () => {
            const val = searchInput.value.trim();
            if (val.length >= 2) {
                this.fetchAndRenderSuggestions(val);
            }
        });

        searchInput.addEventListener('keydown', (e) => {
            const items = suggestionsBox.querySelectorAll('.search-suggestion-item');
            if (!items || items.length === 0 || suggestionsBox.style.display === 'none') {
                if (e.key === 'Escape') this.hideSuggestions();
                return;
            }

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIdx = (selectedIdx + 1) % items.length;
                this.highlightSuggestion(items, selectedIdx);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIdx = (selectedIdx - 1 + items.length) % items.length;
                this.highlightSuggestion(items, selectedIdx);
            } else if (e.key === 'Enter') {
                if (selectedIdx >= 0 && selectedIdx < items.length) {
                    e.preventDefault();
                    items[selectedIdx].click();
                }
            } else if (e.key === 'Escape') {
                this.hideSuggestions();
            }
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            const wrap = searchInput.closest('.search-input-wrap');
            if (wrap && !wrap.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    highlightSuggestion(items, index) {
        items.forEach((item, idx) => {
            if (idx === index) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    async fetchAndRenderSuggestions(query) {
        const suggestionsBox = document.getElementById('searchSuggestionsBox');
        const suggestionsList = document.getElementById('searchSuggestionsList');
        const searchInput = document.getElementById('trainSearchInput');
        if (!suggestionsBox || !suggestionsList || !searchInput) return;

        try {
            const results = await window.railwayApi.searchTrains(query, 6);
            if (searchInput.value.trim().toLowerCase() !== query.toLowerCase() && !query.startsWith(searchInput.value.trim().toLowerCase())) {
                return;
            }

            if (!results || results.length === 0) {
                suggestionsList.innerHTML = `<div class="suggestion-empty"><i class="fa-solid fa-circle-exclamation" style="margin-right:4px;"></i> No trains matching "${query}"</div>`;
                suggestionsBox.style.display = 'block';
                return;
            }

            const headerEl = suggestionsBox.querySelector('.search-suggestions-header');
            if (headerEl) headerEl.textContent = `Search Results (${results.length})`;

            suggestionsList.innerHTML = results.map(item => `
                <div class="search-suggestion-item" data-train="${item.train_number}" onclick="passengerApp.selectSuggestion('${item.train_number}', '${(item.train_name || '').replace(/'/g, "\\'")}')">
                    <div class="search-suggestion-left">
                        <div class="search-suggestion-title">
                            <span class="search-suggestion-badge">${item.train_number}</span>
                            <span>${item.train_name}</span>
                        </div>
                        <div class="search-suggestion-route">
                            <i class="fa-solid fa-route" style="font-size: 9px; color: var(--primary-navy, #0F52BA);"></i>
                            <span>${item.source || 'Origin'} → ${item.destination || 'Destination'}</span>
                        </div>
                    </div>
                    <div class="search-suggestion-right">
                        <i class="fa-solid fa-arrow-right"></i>
                    </div>
                </div>
            `).join('');

            suggestionsBox.style.display = 'block';
        } catch (e) {
            console.warn("Error rendering search suggestions:", e);
        }
    }

    selectSuggestion(trainNumber, trainName) {
        const searchInput = document.getElementById('trainSearchInput');
        if (searchInput) searchInput.value = trainNumber;
        this.hideSuggestions();
        this.handleSearch(trainNumber);
    }

    hideSuggestions() {
        const suggestionsBox = document.getElementById('searchSuggestionsBox');
        if (suggestionsBox) {
            suggestionsBox.style.display = 'none';
        }
    }

    /**
     * Search & Train Rendering
     */
    async handleSearch(query) {
        this.hideSuggestions();
        const rawQ = (query || '').trim();
        if (!rawQ) {
            this.showSearchError("Please enter a valid train number, name, or route (e.g. 12951, August Kranti, Rajdhani).");
            return;
        }

        this.showSearchLoading(true);
        this.hideSearchError();

        try {
            let targetTrainNumber = rawQ;

            // If query is not a numeric train number, resolve via search API
            if (!/^\d{4,5}$/.test(rawQ)) {
                const searchResults = await window.railwayApi.searchTrains(rawQ, 5);
                if (searchResults && searchResults.length > 0) {
                    targetTrainNumber = searchResults[0].train_number;
                    const searchInput = document.getElementById('trainSearchInput');
                    if (searchInput) searchInput.value = targetTrainNumber;
                } else {
                    this.showSearchLoading(false);
                    this.showSearchError(`No train matching "${rawQ}" found on Indian Railways network.`);
                    return;
                }
            }

            const train = await window.railwayApi.getTrainDetails(targetTrainNumber);
            this.showSearchLoading(false);

            if (train) {
                this.applyTrainData(train);
                window.dataService.saveRecentSearch(train);
                this.renderRecentSearches();
                this.navigateToPassengerScreen('screen-details');
            } else {
                this.showSearchError(`Train "${rawQ}" not found on Indian Railways network.`);
            }
        } catch (err) {
            this.showSearchLoading(false);
            this.showSearchError(err.message || `Unable to fetch train "${rawQ}" from RailRadar API.`);
        }
    }

    showSearchLoading(isLoading) {
        const btn = document.getElementById('btnSearchSubmit');
        const spinner = document.getElementById('searchSpinner');
        if (btn && spinner) {
            btn.disabled = isLoading;
            spinner.style.display = isLoading ? 'inline-block' : 'none';
        }
    }

    showSearchError(msg) {
        const errorEl = document.getElementById('searchErrorMsg');
        if (errorEl) {
            errorEl.textContent = msg;
            errorEl.style.display = 'block';
        }
    }

    hideSearchError() {
        const errorEl = document.getElementById('searchErrorMsg');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }

    renderRecentSearches() {
        const container = document.getElementById('recentSearchesList');
        if (!container) return;

        const list = window.dataService.getRecentSearches();
        if (list.length === 0) {
            container.innerHTML = `<div class="empty-recent-text">No recent searches.</div>`;
            return;
        }

        container.innerHTML = list.map(item => `
            <div class="recent-search-card" onclick="passengerApp.handleSearch('${item.train_number}')">
                <div class="recent-search-left">
                    <i class="fa-solid fa-clock-rotate-left recent-icon"></i>
                    <div>
                        <span class="recent-num">${item.train_number}</span>
                        <span class="recent-name">${item.train_name || `${item.source} → ${item.destination}`}</span>
                    </div>
                </div>
                <i class="fa-solid fa-chevron-right" style="font-size:10px; color:var(--text-light);"></i>
            </div>
        `).join('');
    }

    setupTrainsBetweenSection() {
        const form = document.getElementById('betweenStationsOverviewForm');
        const fromInput = document.getElementById('fromStationOverviewInput');
        const toInput = document.getElementById('toStationOverviewInput');
        const btnSwap = document.getElementById('btnSwapOverviewStations');
        const routeChips = document.querySelectorAll('.btn-between-route-chip');

        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const fromStn = fromInput ? fromInput.value.trim() : '';
                const toStn = toInput ? toInput.value.trim() : '';
                this.searchTrainsBetween(fromStn, toStn);
            });
        }

        if (btnSwap && fromInput && toInput) {
            btnSwap.addEventListener('click', () => {
                const tmp = fromInput.value;
                fromInput.value = toInput.value;
                toInput.value = tmp;
            });
        }

        routeChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const fromVal = chip.getAttribute('data-from');
                const toVal = chip.getAttribute('data-to');
                if (fromInput) fromInput.value = fromVal;
                if (toInput) toInput.value = toVal;
                this.searchTrainsBetween(fromVal, toVal);
            });
        });
    }

    async searchTrainsBetween(fromStn, toStn) {
        const errorBox = document.getElementById('betweenOverviewError');
        const spinner = document.getElementById('betweenSearchSpinner');
        const btnSubmit = document.getElementById('btnSearchBetweenStations');

        if (!fromStn || !toStn) {
            if (errorBox) {
                errorBox.textContent = 'Please enter both source and destination stations.';
                errorBox.style.display = 'block';
            }
            return;
        }

        if (fromStn.toUpperCase() === toStn.toUpperCase()) {
            if (errorBox) {
                errorBox.textContent = 'Source and destination stations cannot be the same.';
                errorBox.style.display = 'block';
            }
            return;
        }

        if (errorBox) errorBox.style.display = 'none';
        if (spinner) spinner.style.display = 'inline-block';
        if (btnSubmit) btnSubmit.disabled = true;

        try {
            const data = await window.railwayApi.getTrainsBetweenStations(fromStn, toStn);
            if (spinner) spinner.style.display = 'none';
            if (btnSubmit) btnSubmit.disabled = false;

            if (data) {
                this.renderAvailableTrains(data);
                this.navigateToPassengerScreen('screen-trains-between');
            }
        } catch (err) {
            if (spinner) spinner.style.display = 'none';
            if (btnSubmit) btnSubmit.disabled = false;
            if (errorBox) {
                errorBox.textContent = err.message || 'Unable to fetch live train data. Please try again.';
                errorBox.style.display = 'block';
            }
        }
    }

    renderAvailableTrains(data) {
        const titleEl = document.getElementById('betweenResultsTitle');
        const fromCodeEl = document.getElementById('betweenSummaryFromCode');
        const fromNameEl = document.getElementById('betweenSummaryFromName');
        const toCodeEl = document.getElementById('betweenSummaryToCode');
        const toNameEl = document.getElementById('betweenSummaryToName');
        const countBadge = document.getElementById('betweenFoundCountBadge');
        const container = document.getElementById('betweenTrainsListContainer');

        const fromCode = data.from_station ? data.from_station.code : 'ORIGIN';
        const fromName = data.from_station ? data.from_station.name : fromCode;
        const toCode = data.to_station ? data.to_station.code : 'DEST';
        const toName = data.to_station ? data.to_station.name : toCode;
        const total = data.total_trains || (data.trains ? data.trains.length : 0);

        if (titleEl) titleEl.textContent = `AVAILABLE TRAINS — ${total}`;
        if (fromCodeEl) fromCodeEl.textContent = fromCode;
        if (fromNameEl) fromNameEl.textContent = fromName;
        if (toCodeEl) toCodeEl.textContent = toCode;
        if (toNameEl) toNameEl.textContent = toName;
        if (countBadge) countBadge.textContent = `${total} Train${total === 1 ? '' : 's'} Available`;

        if (!container) return;

        if (!data.trains || data.trains.length === 0) {
            container.innerHTML = `
                <div class="between-empty-state">
                    <i class="fa-solid fa-train-slash between-empty-icon"></i>
                    <div class="between-empty-title">No trains found for this route.</div>
                    <div class="between-empty-sub">
                        No direct train services found between <strong>${fromName} (${fromCode})</strong> and <strong>${toName} (${toCode})</strong>. Try searching major nearby terminal pairs or interchange hubs.
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = data.trains.map(t => {
            let chipClass = 'chip-running';
            let statusIcon = 'fa-solid fa-circle';
            let cat = (t.status_category || 'running').toLowerCase();

            if (cat === 'completed') {
                chipClass = 'chip-completed';
            } else if (cat === 'not_started') {
                chipClass = 'chip-not-started';
            } else if (cat === 'delayed') {
                chipClass = 'chip-delayed';
            } else if (cat === 'unavailable') {
                chipClass = 'chip-unavailable';
                statusIcon = 'fa-solid fa-info-circle';
            } else {
                chipClass = 'chip-running';
            }

            const delayMins = parseInt(t.delay_mins || 0, 10);
            let delayHtml = `<span class="between-delay-badge on-time">On-time</span>`;
            if (cat === 'unavailable') {
                delayHtml = `<span class="between-delay-badge on-time">Timetable</span>`;
            } else if (delayMins > 0) {
                delayHtml = `<span class="between-delay-badge late">+${delayMins} min delay</span>`;
            }

            const origCode = t.origin_station ? (t.origin_station.code || '') : '';
            const destCode = t.destination_station ? (t.destination_station.code || '') : '';
            const routeTag = origCode && destCode ? `<span class="between-train-type-badge">${origCode} → ${destCode}</span>` : '';
            const durationHtml = t.duration && t.duration !== '--' ? `<span class="between-duration-tag"><i class="fa-regular fa-clock"></i> ${t.duration}</span>` : '';

            const locText = (t.current_location && t.current_location !== '--') 
                ? t.current_location 
                : `${t.from_station_name || t.from_station_code} → ${t.to_station_name || t.to_station_code}`;
            const nextText = t.next_station && t.next_station !== '--' ? `Next: ${t.next_station}` : '';
            const updatedText = t.last_updated_time || (cat === 'unavailable' ? 'Timetable Schedule' : 'Live Real-Time');

            const boardingCode = t.from_station_code || fromCode;
            const arrivalCode = t.to_station_code || toCode;

            return `
                <div class="between-train-card" onclick="passengerApp.handleSelectTrainFromBetween('${t.train_number}')" title="Click to track live running status and dynamic ETA">
                    <div class="between-train-card-header">
                        <div class="between-train-title-wrap">
                            <span class="between-train-no-pill">${t.train_number}</span>
                            <span class="between-train-name-text">${t.train_name}</span>
                            <span class="between-train-type-badge">${t.train_type || 'Superfast Express'}</span>
                            ${routeTag}
                            ${durationHtml}
                        </div>
                        <div class="status-chip ${chipClass}">
                            <i class="${statusIcon}"></i>
                            <span>${t.current_status || 'Scheduled'}</span>
                        </div>
                    </div>

                    <div class="between-times-strip">
                        <div class="between-time-col">
                            <span class="between-time-val">${t.departure_time}</span>
                            <span class="between-time-lbl">Departs ${boardingCode}</span>
                        </div>
                        <div class="between-time-divider">
                            <i class="fa-solid fa-arrow-right-long between-time-arrow"></i>
                            ${delayHtml}
                        </div>
                        <div class="between-time-col" style="text-align:right;">
                            <span class="between-time-val">${t.arrival_time}</span>
                            <span class="between-time-lbl">Arrives ${arrivalCode}</span>
                        </div>
                    </div>

                    <div class="between-meta-strip">
                        <div class="between-meta-left">
                            <div class="between-meta-item">
                                <i class="fa-solid fa-location-dot"></i>
                                <span>${locText}</span>
                            </div>
                            ${nextText ? `
                            <div class="between-meta-item">
                                <i class="fa-solid fa-train"></i>
                                <span>${nextText}</span>
                            </div>` : ''}
                            <div class="between-meta-item">
                                <i class="fa-regular fa-clock"></i>
                                <span>${updatedText}</span>
                            </div>
                        </div>
                        <div class="btn-track-action-link">
                            <span>Track Train</span>
                            <i class="fa-solid fa-arrow-right"></i>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    handleSelectTrainFromBetween(trainNumber) {
        if (!trainNumber) return;
        const searchInput = document.getElementById('trainSearchInput');
        if (searchInput) searchInput.value = trainNumber;
        this.handleSearch(trainNumber);
    }

    navigateToPassengerScreen(screenId) {
        if (screenId !== 'screen-home' && !this.currentTrain) {
            this.handleSearch('12951');
            return;
        }

        const screens = document.querySelectorAll('.app-screen');
        screens.forEach(s => s.classList.remove('active-screen'));

        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active-screen');
            this.currentPassengerScreen = screenId;
        }

        document.querySelectorAll('[data-target-screen]').forEach(btn => {
            if (btn.getAttribute('data-target-screen') === screenId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        if (screenId === 'screen-map' && this.currentTrain) {
            setTimeout(() => {
                if (window.routeMapTracker) {
                    window.routeMapTracker.renderTrainRoute(this.currentTrain || window.selectedTrain);
                }
            }, 100);
        } else if (screenId === 'screen-weather' && this.currentTrain) {
            setTimeout(() => {
                if (window.weatherMapTracker) {
                    window.weatherMapTracker.renderTrainWeatherRoute(this.currentTrain || window.selectedTrain);
                }
            }, 100);
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    renderTrainDetails(train) {
        if (!train) return;

        const setTxt = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        const delayMins = train.current_delay_mins || 0;
        const isDelayed = delayMins > 0;
        const statusCode = (train.current_status_code || train.status || '').toUpperCase();
        const statusRaw = (train.current_status || '').toUpperCase();

        let runningStatusMsg = 'Running on time';
        let pillClassName = 'train-status-badge ontime';

        if (statusCode === 'NOT_STARTED' || statusRaw === 'NOT STARTED' || statusRaw === 'NOT-STARTED') {
            runningStatusMsg = 'NOT STARTED';
            pillClassName = 'train-status-badge not-started';
        } else if (statusCode === 'COMPLETED' || statusRaw === 'COMPLETED') {
            runningStatusMsg = 'Completed';
            pillClassName = 'train-status-badge completed';
        } else if (delayMins > 5 || statusCode === 'DELAYED' || statusRaw.includes('LATE') || statusRaw.includes('DELAYED')) {
            runningStatusMsg = `Running ${delayMins} min late`;
            pillClassName = 'train-status-badge delayed';
        } else {
            runningStatusMsg = isDelayed ? `Running (+${delayMins}m)` : 'Running on time';
            pillClassName = 'train-status-badge ontime';
        }

        // 1. Compact Train Summary Card (Details, Map, Weather & Route Screens)
        setTxt('detailsTrainNo', train.train_number);
        setTxt('detailsRouteSubtitle', `${train.source} → ${train.destination}`);
        setTxt('mapScreenTrainNo', train.train_number);
        setTxt('mapScreenRouteSubtitle', `${train.source} → ${train.destination}`);
        setTxt('weatherScreenTrainNo', train.train_number);
        setTxt('weatherScreenRouteSubtitle', `${train.source} → ${train.destination}`);
        setTxt('routeScreenTrainNo', train.train_number);
        setTxt('routeScreenRouteSubtitle', `${train.source} → ${train.destination}`);
        setTxt('alertsScreenTrainNo', train.train_number);
        setTxt('alertsScreenRouteSubtitle', `${train.source} → ${train.destination}`);
        
        const runningPill = document.getElementById('detailsRunningStatusPill');
        const runningText = document.getElementById('detailsRunningStatusText');
        if (runningText) runningText.textContent = runningStatusMsg;
        if (runningPill) runningPill.className = pillClassName;

        const mapRunningPill = document.getElementById('mapScreenRunningStatusPill');
        const mapRunningText = document.getElementById('mapScreenRunningStatusText');
        if (mapRunningText) mapRunningText.textContent = runningStatusMsg;
        if (mapRunningPill) mapRunningPill.className = pillClassName;

        const routeRunningPill = document.getElementById('routeScreenRunningStatusPill');
        const routeRunningText = document.getElementById('routeScreenRunningStatusText');
        if (routeRunningText) routeRunningText.textContent = runningStatusMsg;
        if (routeRunningPill) routeRunningPill.className = pillClassName;

        const alertsRunningPill = document.getElementById('alertsScreenRunningStatusPill');
        const alertsRunningText = document.getElementById('alertsScreenRunningStatusText');
        if (alertsRunningText) alertsRunningText.textContent = runningStatusMsg;
        if (alertsRunningPill) alertsRunningPill.className = pillClassName;

        // 2. Main Hero ETA Card (Details & Route Screens)
        const predETA = train.predicted_destination_eta || "--:--";
        const schedETA = `vs scheduled ${train.scheduled_destination_eta || '--:--'}`;
        const delayLabel = isDelayed ? `+${delayMins} min` : 'On Time';
        const delayClass = isDelayed ? 'eta-delay-pill' : 'eta-delay-pill ontime';

        setTxt('detailsPredictedETA', predETA);
        setTxt('routePredictedETA', predETA);
        
        const delayTag = document.getElementById('detailsDelayTag');
        if (delayTag) {
            delayTag.textContent = delayLabel;
            delayTag.className = delayClass;
        }
        const routeDelayTag = document.getElementById('routeDelayTag');
        if (routeDelayTag) {
            routeDelayTag.textContent = delayLabel;
            routeDelayTag.className = delayClass;
        }

        setTxt('detailsScheduledETA', schedETA);
        setTxt('routeScheduledETA', schedETA);

        const confPctText = typeof train.confidence_pct === 'number' ? `${train.confidence_pct}%` : (train.confidence_level || '94%');
        const confDisplay = train.arrival_window ? `${confPctText} (${train.arrival_window})` : confPctText;
        const confHtml = `<i class="fa-solid fa-shield-check"></i> <span>Confidence: ${confDisplay}</span>`;
        const lastUpdatedHtml = `<i class="fa-regular fa-clock"></i> Updated just now`;

        const confTextEl = document.getElementById('detailsConfidenceText');
        if (confTextEl) confTextEl.innerHTML = confHtml;
        const routeConfTextEl = document.getElementById('routeConfidenceText');
        if (routeConfTextEl) routeConfTextEl.innerHTML = confHtml;

        const lastUpdatedEl = document.getElementById('detailsLastUpdatedTime');
        if (lastUpdatedEl) lastUpdatedEl.innerHTML = lastUpdatedHtml;
        const routeLastUpdatedEl = document.getElementById('routeLastUpdatedTime');
        if (routeLastUpdatedEl) routeLastUpdatedEl.innerHTML = lastUpdatedHtml;

        // 3. Current Status (3 Compact Blocks for Details, Map & Route Screens)
        const loc = train.current_location || 'En route';
        const shortLoc = loc.split('(')[0].replace('Passing', '').replace('Approaching', '').trim() || loc;
        const speedVal = (typeof train.current_speed_kmh === 'number') ? train.current_speed_kmh : (typeof train.speed === 'number' ? train.speed : 0);
        const currentSpeedText = `${speedVal} km/h`;

        setTxt('detailsCurrentLocation', shortLoc);
        setTxt('detailsCurrentSpeed', currentSpeedText);
        setTxt('mapCurrentLocation', shortLoc);
        setTxt('mapCurrentSpeed', currentSpeedText);
        setTxt('routeCurrentLocation', shortLoc);
        setTxt('routeCurrentSpeed', currentSpeedText);
        setTxt('mapToolbarSpeed', `${currentSpeedText} • GPS`);

        // Update Top Mini Status Banner
        const simStatusTextEl = document.getElementById('simStatusText');
        const simSpeedIndicatorEl = document.getElementById('simSpeedIndicator');
        const isNotStarted = (statusCode === 'NOT_STARTED' || statusRaw === 'NOT STARTED' || statusRaw === 'NOT-STARTED');
        const isCompleted = (statusCode === 'COMPLETED' || statusRaw === 'COMPLETED');

        if (simStatusTextEl) {
            if (isNotStarted) {
                simStatusTextEl.textContent = 'NOT STARTED';
                simStatusTextEl.style.color = '#DC2626';
                simStatusTextEl.style.fontWeight = '700';
            } else if (isCompleted) {
                simStatusTextEl.textContent = 'Journey Completed';
                simStatusTextEl.style.color = '#64748B';
                simStatusTextEl.style.fontWeight = '600';
            } else {
                simStatusTextEl.textContent = 'Live tracking active';
                simStatusTextEl.style.color = '';
                simStatusTextEl.style.fontWeight = '';
            }
        }
        if (simSpeedIndicatorEl) {
            simSpeedIndicatorEl.textContent = isNotStarted ? `${speedVal} km/h • Timetable` : `${speedVal} km/h • GPS`;
        }

        if (train.next_station) {
            const nextETA = `ETA ${train.next_station.expected_eta || '--:--'}`;
            setTxt('detailsNextStationName', train.next_station.name);
            setTxt('detailsNextStationETA', nextETA);
            setTxt('mapNextStationName', train.next_station.name);
            setTxt('mapNextStationDetailETA', nextETA);
            setTxt('routeNextStationName', train.next_station.name);
            setTxt('routeNextStationETA', nextETA);
        }

        // 4. Visual Journey Progress Line
        const srcName = train.source_code || (train.source ? train.source.split('(')[0].trim() : 'ORIGIN');
        const destName = train.destination_code || (train.destination ? train.destination.split('(')[0].trim() : 'DEST');
        setTxt('detailsSourceCode', srcName);
        setTxt('detailsDestCode', destName);
        setTxt('mapSourceCode', srcName);
        setTxt('mapDestCode', destName);
        setTxt('routeScreenSourceCode', srcName);
        setTxt('routeScreenDestCode', destName);

        const pct = typeof train.journey_progress_pct === 'number' ? Math.round(train.journey_progress_pct * 10) / 10 : 0;
        const pctText = `${pct}% completed`;
        setTxt('detailsProgressPct', pctText);
        setTxt('mapProgressPct', pctText);
        setTxt('routeScreenProgressPct', pctText);
        
        const progressFill = document.getElementById('detailsProgressFill');
        if (progressFill) progressFill.style.width = `${pct}%`;

        const progressMarker = document.getElementById('detailsProgressMarker');
        if (progressMarker) progressMarker.style.left = `${pct}%`;

        const totalDist = train.total_distance_km ? Math.round(train.total_distance_km) : 0;
        const coveredDist = train.distance_covered_km !== undefined ? Math.round(train.distance_covered_km) : Math.round((pct / 100) * totalDist);
        const remainingDist = train.distance_remaining_km !== undefined ? Math.round(train.distance_remaining_km) : Math.max(0, totalDist - coveredDist);
        const distMetaText = `${coveredDist} km covered · ${remainingDist} km remaining`;
        setTxt('detailsDistanceMeta', distMetaText);
        setTxt('mapDistanceMeta', distMetaText);
        setTxt('routeScreenDistanceMeta', distMetaText);

        // Render Dynamic Intermediate Stations Route Timeline
        this.renderRouteTimeline(train);

        // Render Complete Vertical Station Timeline on Route Screen
        this.renderCompleteRouteTimeline(train);

        // Render Detailed Timetable Comparison Table on Route Screen
        this.renderRouteTimetableTable(train);

        // 5. Why is ETA changing? Section (Top 2-3 Active Factors)
        this.renderActiveFactors(train);

        // 6. Next Stations Preview (Next 3-4 Stops)
        this.renderNextStationsPreview(train);

        // 7. Smart Conditional Alert (Displayed only when active)
        this.renderSmartAlert(train);

        // 8. Sync Map Screen & Weather Screen Bottom HUD
        const currentDelayVal = typeof train.current_delay_mins === 'number' ? train.current_delay_mins : 0;
        const delayNotice = currentDelayVal > 0 ? ` (+${currentDelayVal} min)` : '';
        setTxt('mapTrainNumber', train.train_number);
        setTxt('mapNextStationText', `Next: ${train.next_station ? train.next_station.name : '--'}`);
        setTxt('mapNextStationETA', `ETA ${train.next_station ? (train.next_station.expected_eta || train.next_station.scheduled_eta || '--') : '--'}${delayNotice}`);
        setTxt('weatherTrainNumber', train.train_number);
        setTxt('weatherNextStationText', `Next: ${train.next_station ? train.next_station.name : '--'}`);
        setTxt('weatherNextStationETA', `ETA ${train.next_station ? train.next_station.expected_eta : '--'}`);

        if (window.routeMapTracker && this.currentPassengerScreen === 'screen-map') {
            window.routeMapTracker.updateTrainPosition(train.current_coordinates, train);
        } else if (window.weatherMapTracker && this.currentPassengerScreen === 'screen-weather') {
            window.weatherMapTracker.updateWeatherForTrain(train);
        }

        // 9. Render Passenger Alerts Feed
        this.renderPassengerAlerts(train);
    }

    renderRouteTimeline(train) {
        const container = document.getElementById('routeTimelineTrackContainer');
        const mapContainer = document.getElementById('mapRouteTimelineTrackContainer');
        const routeProgressContainer = document.getElementById('routeScreenProgressTrackContainer');
        if (!container && !mapContainer && !routeProgressContainer) return;

        let stations = train.stations || [];
        if (stations.length === 0) {
            const emptyMsg = '<div style="padding:10px;text-align:center;font-size:11px;color:var(--text-muted);">Route stations unavailable.</div>';
            if (container) container.innerHTML = emptyMsg;
            if (mapContainer) mapContainer.innerHTML = emptyMsg;
            if (routeProgressContainer) routeProgressContainer.innerHTML = emptyMsg;
            return;
        }

        // Defensive deduplication by station code
        const seenCodes = new Set();
        stations = stations.filter(stn => {
            const code = String(stn.code || '').trim().toUpperCase();
            if (!code || seenCodes.has(code)) return false;
            seenCodes.add(code);
            return true;
        });

        const pct = typeof train.journey_progress_pct === 'number' ? Math.round(train.journey_progress_pct * 10) / 10 : 0;
        const speed = typeof train.current_speed_kmh === 'number' ? train.current_speed_kmh : 0;
        const currentLoc = train.current_location || 'En route';

        // Determine current train position index relative to stations
        let currentTrainBeforeIndex = -1;
        const nextCode = train.next_station ? train.next_station.code : null;
        if (nextCode) {
            currentTrainBeforeIndex = stations.findIndex(s => s.code === nextCode);
        }
        if (currentTrainBeforeIndex === -1) {
            currentTrainBeforeIndex = stations.findIndex(s => s.status === 'approaching' || s.status === 'upcoming');
        }
        if (currentTrainBeforeIndex === -1) {
            currentTrainBeforeIndex = Math.min(stations.length - 1, Math.max(1, Math.floor((pct / 100) * stations.length)));
        }

        const clampRailPct = Math.max(5, Math.min(95, pct));

        // -------------------------------------------------------------
        // 1. DESKTOP HORIZONTAL TIMELINE
        // -------------------------------------------------------------
        let desktopHtml = `
            <div class="route-timeline-desktop">
                <div class="timeline-h-track-wrap">
                    <!-- Base Continuous Rail Track -->
                    <div class="timeline-h-rail-bg">
                        <div class="timeline-h-rail-fill" style="width: ${clampRailPct}%;"></div>
                        
                        <!-- Floating Live Train Pointer Badge -->
                        <div class="timeline-h-train-pointer" style="left: ${clampRailPct}%;">
                            <div class="h-train-marker-badge" title="${currentLoc} (${speed} km/h)">
                                <i class="fa-solid fa-train"></i>
                                <span>LIVE ${speed} km/h</span>
                            </div>
                            <div class="h-train-pointer-arrow"></div>
                            <div class="h-train-pulse-dot"></div>
                        </div>
                    </div>

                    <!-- Station Nodes along the Rail -->
                    <div class="timeline-h-stations-row">
        `;

        stations.forEach((stn, idx) => {
            const isCompleted = idx < currentTrainBeforeIndex;
            const isApproaching = idx === currentTrainBeforeIndex;
            const isUpcoming = idx > currentTrainBeforeIndex;

            let nodeClass = isCompleted ? 'node-completed' : (isApproaching ? 'node-approaching' : 'node-upcoming');
            let bulletContent = isCompleted 
                ? '<i class="fa-solid fa-check"></i>' 
                : (isApproaching ? '<span class="h-approaching-pulse"></span>' : '<span class="h-dot-inner"></span>');
            
            let timeDisplay = stn.predicted_arr && stn.predicted_arr !== 'START' && stn.predicted_arr !== 'DEST' 
                ? stn.predicted_arr 
                : (stn.scheduled_dep && stn.scheduled_dep !== 'DEST' ? stn.scheduled_dep : (stn.scheduled_arr || '--:--'));

            desktopHtml += `
                <div class="h-stn-node ${nodeClass}" style="flex: 1;">
                    <div class="h-node-bullet-wrap">
                        <div class="h-node-bullet" title="${stn.name} (${stn.code})">${bulletContent}</div>
                    </div>
                    <div class="h-node-info">
                        <div class="h-node-name" title="${stn.name}">${stn.name}</div>
                        <div class="h-node-meta">
                            <span class="h-node-code">${stn.code}</span>
                            ${stn.platform ? `<span class="h-node-pf">PF ${stn.platform}</span>` : ''}
                        </div>
                        <div class="h-node-time">${timeDisplay}</div>
                    </div>
                </div>
            `;
        });

        desktopHtml += `
                    </div>
                </div>
            </div>
        `;

        // -------------------------------------------------------------
        // 2. MOBILE VERTICAL TIMELINE
        // -------------------------------------------------------------
        let mobileHtml = `
            <div class="route-timeline-mobile">
                <div class="timeline-v-scroll-container">
                    <div class="timeline-v-track">
        `;

        stations.forEach((stn, idx) => {
            const isCompleted = idx < currentTrainBeforeIndex;
            const isApproaching = idx === currentTrainBeforeIndex;
            const isUpcoming = idx > currentTrainBeforeIndex;

            // Render live train position badge right before the approaching station
            if (idx === currentTrainBeforeIndex) {
                mobileHtml += `
                    <div class="timeline-v-current-indicator">
                        <div class="v-current-badge">
                            <span class="v-current-pulse"></span>
                            <div class="v-current-text-wrap">
                                <div class="v-current-title"><i class="fa-solid fa-train"></i> CURRENT TRAIN POSITION</div>
                                <div class="v-current-sub">${currentLoc} • ${speed} km/h</div>
                            </div>
                        </div>
                    </div>
                `;
            }

            let stnClass = isCompleted ? 'v-stn-completed' : (isApproaching ? 'v-stn-approaching' : 'v-stn-upcoming');
            let bulletContent = isCompleted 
                ? '<i class="fa-solid fa-check"></i>' 
                : (isApproaching ? '<span class="v-node-pulse-ring"></span>' : '');

            let timeDisplay = stn.predicted_arr && stn.predicted_arr !== 'START' && stn.predicted_arr !== 'DEST' 
                ? stn.predicted_arr 
                : (stn.scheduled_dep && stn.scheduled_dep !== 'DEST' ? stn.scheduled_dep : (stn.scheduled_arr || '--:--'));

            let statusTag = isCompleted 
                ? '<span class="v-tag-passed"><i class="fa-solid fa-check"></i> Departed</span>' 
                : (isApproaching ? '<span class="v-tag-approaching"><i class="fa-solid fa-circle-dot"></i> Approaching Next</span>' : '<span class="v-tag-upcoming">Scheduled</span>');

            mobileHtml += `
                <div class="timeline-v-station ${stnClass}">
                    <div class="timeline-v-spine">
                        <div class="v-node-dot">${bulletContent}</div>
                        ${idx < stations.length - 1 ? '<div class="v-node-line"></div>' : ''}
                    </div>
                    <div class="timeline-v-content">
                        <div class="v-stn-top">
                            <span class="v-stn-name">${stn.name}</span>
                            <span class="v-stn-time">${timeDisplay}</span>
                        </div>
                        <div class="v-stn-bottom">
                            <div class="v-stn-meta">
                                <span class="v-stn-code">${stn.code}</span>
                                ${stn.platform ? `<span class="v-stn-pf">PF ${stn.platform}</span>` : ''}
                                ${stn.distance_km ? `<span class="v-stn-dist">${stn.distance_km} km</span>` : ''}
                            </div>
                            ${statusTag}
                        </div>
                    </div>
                </div>
            `;
        });

        mobileHtml += `
                    </div>
                </div>
            </div>
        `;

        const fullTimelineHtml = desktopHtml + mobileHtml;
        if (container) container.innerHTML = fullTimelineHtml;
        if (mapContainer) mapContainer.innerHTML = fullTimelineHtml;
        if (routeProgressContainer) routeProgressContainer.innerHTML = fullTimelineHtml;
    }

    renderCompleteRouteTimeline(train) {
        const container = document.getElementById('routeScreenTimelineContainer');
        if (!container) return;

        let stations = train.stations || [];
        if (stations.length === 0) {
            container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:12px;">Route stations information unavailable.</div>';
            return;
        }

        // Defensive deduplication by station code
        const seenCodes = new Set();
        stations = stations.filter(stn => {
            const code = String(stn.code || '').trim().toUpperCase();
            if (!code || seenCodes.has(code)) return false;
            seenCodes.add(code);
            return true;
        });

        const pct = typeof train.journey_progress_pct === 'number' ? Math.round(train.journey_progress_pct * 10) / 10 : 0;
        const speed = typeof train.current_speed_kmh === 'number' ? train.current_speed_kmh : 0;
        const currentLoc = train.current_location || 'En route';
        const delayMins = train.current_delay_mins || 0;
        const isDelayed = delayMins > 0;
        const statusCode = (train.current_status_code || train.status || '').toUpperCase();
        const statusRaw = (train.current_status || '').toUpperCase();

        // Determine current position index
        let currentTrainBeforeIndex = -1;
        const nextCode = train.next_station ? train.next_station.code : null;
        if (nextCode) {
            currentTrainBeforeIndex = stations.findIndex(s => s.code === nextCode);
        }
        if (currentTrainBeforeIndex === -1) {
            currentTrainBeforeIndex = stations.findIndex(s => s.status === 'approaching' || s.status === 'upcoming');
        }
        if (currentTrainBeforeIndex === -1) {
            currentTrainBeforeIndex = Math.min(stations.length - 1, Math.max(1, Math.floor((pct / 100) * stations.length)));
        }

        let html = '<div class="route-complete-timeline-spine">';

        stations.forEach((stn, idx) => {
            const isCompleted = idx < currentTrainBeforeIndex;
            const isApproaching = idx === currentTrainBeforeIndex;
            const isUpcoming = idx > currentTrainBeforeIndex;

            // Render live train position card right before the approaching station
            if (idx === currentTrainBeforeIndex) {
                const isNotStarted = (statusCode === 'NOT_STARTED' || statusRaw === 'NOT STARTED' || statusRaw === 'NOT-STARTED');
                const posBadgeHtml = isNotStarted 
                    ? `<span class="live-pos-badge not-started" style="background:#FEF2F2; color:#DC2626; border:1px solid #FECACA;">🔴 NOT STARTED</span>`
                    : `<span class="live-pos-badge">🟢 CURRENTLY HERE</span>`;
                const posDelayTag = isNotStarted
                    ? `<span class="live-pos-delay-tag not-started" style="background:#FEF2F2; color:#DC2626; border:1px solid #FECACA;">NOT STARTED</span>`
                    : `<span class="live-pos-delay-tag ${isDelayed ? 'delayed' : 'ontime'}">${isDelayed ? `Running ${delayMins} min late` : 'Running on time'}</span>`;
                const locDisplay = isNotStarted && !currentLoc.startsWith('At') ? `At ${currentLoc}` : currentLoc;

                html += `
                    <div class="route-live-train-position-block">
                        <div class="live-train-pos-card">
                            <div class="live-pos-pulse-wrap">
                                <span class="live-train-pos-pulse" style="${isNotStarted ? 'background:#DC2626; box-shadow: 0 0 0 4px rgba(220,38,38,0.2);' : ''}"></span>
                                <i class="fa-solid fa-train live-train-pos-icon" style="${isNotStarted ? 'color:#DC2626;' : ''}"></i>
                            </div>
                            <div class="live-pos-content">
                                <div class="live-pos-header">
                                    ${posBadgeHtml}
                                    <span class="live-pos-speed">${speed} km/h • ${isNotStarted ? 'Origin Scheduled' : 'GPS'}</span>
                                </div>
                                <div class="live-pos-train-title">
                                    <strong>Train ${train.train_number}</strong> (${train.short_name || train.train_name || 'Express'})
                                </div>
                                <div class="live-pos-meta">
                                    <span><i class="fa-solid fa-location-dot"></i> ${locDisplay}</span>
                                    ${posDelayTag}
                                </div>
                                <div class="live-pos-next-hint">
                                    ${isNotStarted ? 'First Stop' : 'Next Station'}: <strong>${stn.name} (${stn.code})</strong> • Dynamic ETA: <span style="color:#059669; font-weight:800;">${stn.predicted_arr || stn.scheduled_arr || '--:--'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }

            let nodeStateClass = isCompleted ? 'stn-completed' : (isApproaching ? 'stn-approaching' : 'stn-upcoming');
            let bulletContent = isCompleted 
                ? '<i class="fa-solid fa-check"></i>' 
                : (isApproaching ? '<span class="approaching-pulse-dot"></span>' : '<span class="upcoming-dot-inner"></span>');

            const isStart = idx === 0;
            const isEnd = idx === stations.length - 1;

            let stnStatusBadge = isCompleted 
                ? `<span class="stn-status-pill stn-departed"><i class="fa-solid fa-check"></i> Departed</span>`
                : (isApproaching 
                    ? `<span class="stn-status-pill stn-approaching-pill"><i class="fa-solid fa-circle-dot"></i> Approaching Next</span>`
                    : `<span class="stn-status-pill stn-scheduled">Scheduled</span>`);

            let delayBadge = stn.delay_mins > 0 
                ? `<span class="stn-delay-tag delayed">+${stn.delay_mins}m</span>` 
                : `<span class="stn-delay-tag ontime">On Time</span>`;

            let schedTime = stn.scheduled_arr && stn.scheduled_arr !== 'START' ? stn.scheduled_arr : (stn.scheduled_dep || '--:--');
            let predTime = stn.predicted_arr && stn.predicted_arr !== 'START' ? stn.predicted_arr : (stn.predicted_dep || '--:--');

            html += `
                <div class="route-timeline-station-node ${nodeStateClass}">
                    <div class="route-node-spine">
                        <div class="route-node-bullet ${isStart ? 'bullet-start' : (isEnd ? 'bullet-end' : '')}">
                            ${bulletContent}
                        </div>
                        ${idx < stations.length - 1 ? '<div class="route-node-line"></div>' : ''}
                    </div>

                    <div class="route-node-card">
                        <div class="route-node-card-top">
                            <div class="route-node-title-group">
                                <span class="route-node-stn-name">${stn.name}</span>
                                <span class="route-node-stn-code">${stn.code}</span>
                                ${stn.platform ? `<span class="route-node-pf-badge">PF ${stn.platform}</span>` : ''}
                            </div>
                            <div class="route-node-badges-group">
                                ${delayBadge}
                                ${stnStatusBadge}
                            </div>
                        </div>

                        <div class="route-node-times-grid">
                            <div class="time-tile">
                                <span class="time-tile-lbl">Scheduled ${isStart ? 'Departure' : (isEnd ? 'Arrival' : 'Arrival / Dep')}</span>
                                <span class="time-tile-val">${schedTime} ${stn.scheduled_dep && !isStart && !isEnd ? `/ ${stn.scheduled_dep}` : ''}</span>
                            </div>
                            <div class="time-tile highlight-eta">
                                <span class="time-tile-lbl">Dynamic Predicted ETA</span>
                                <span class="time-tile-val eta-val">${predTime}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;

        // Keep backward compatible hooks populated
        const fullList = document.getElementById('fullRouteStationsList');
        if (fullList) fullList.innerHTML = html;
    }

    renderRouteTimetableTable(train) {
        const tbody = document.getElementById('routeTimetableTableBody');
        if (!tbody) return;

        let stations = train.stations || [];
        if (stations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:15px; color:var(--text-muted);">No timetable data available.</td></tr>';
            return;
        }

        // Defensive deduplication by station code
        const seenCodes = new Set();
        stations = stations.filter(stn => {
            const code = String(stn.code || '').trim().toUpperCase();
            if (!code || seenCodes.has(code)) return false;
            seenCodes.add(code);
            return true;
        });

        tbody.innerHTML = stations.map((stn, idx) => {
            const isDeparted = stn.status === 'departed';
            const isApproaching = stn.status === 'approaching';
            
            let statusBadge = isDeparted 
                ? '<span class="tbl-badge tbl-departed"><i class="fa-solid fa-check"></i> Departed</span>'
                : (isApproaching 
                    ? '<span class="tbl-badge tbl-approaching"><i class="fa-solid fa-circle-dot"></i> Approaching</span>'
                    : '<span class="tbl-badge tbl-upcoming">Upcoming</span>');

            let delayText = stn.delay_mins > 0 ? `+${stn.delay_mins}m` : 'On Time';
            let delayClass = stn.delay_mins > 0 ? 'color: #D97706; font-weight: 700;' : 'color: #059669; font-weight: 700;';

            let rowClass = isApproaching ? 'table-row-approaching' : (isDeparted ? 'table-row-departed' : '');

            let schedDisplay = `${stn.scheduled_arr || '--:--'} / ${stn.scheduled_dep || '--:--'}`;
            let predDisplay = stn.predicted_arr || stn.predicted_dep || '--:--';

            return `
                <tr class="${rowClass}">
                    <td class="tbl-stn-cell">
                        <strong>${stn.name}</strong>
                        <span class="tbl-code-sub">${stn.code}</span>
                    </td>
                    <td class="tbl-mono">${schedDisplay}</td>
                    <td class="tbl-mono tbl-eta-highlight"><strong>${predDisplay}</strong></td>
                    <td style="${delayClass}">${delayText}</td>
                    <td><span class="tbl-pf-tag">PF ${stn.platform || '1'}</span></td>
                    <td>${statusBadge}</td>
                </tr>
            `;
        }).join('');
    }

    renderActiveFactors(train) {
        const activeFactors = window.EtaFactorProcessor.getActiveFactors(train);
        const countBadges = [
            document.getElementById('detailsFactorsCountBadge'),
            document.getElementById('mapFactorsCountBadge'),
            document.getElementById('routeFactorsCountBadge')
        ];
        countBadges.forEach(badge => {
            if (badge) badge.textContent = `${activeFactors.length} factors currently affecting ETA`;
        });

        const containers = [
            document.getElementById('detailsActiveFactorsList'),
            document.getElementById('mapActiveFactorsList'),
            document.getElementById('routeActiveFactorsList')
        ];

        let contentHtml = '';
        if (activeFactors.length === 0) {
            contentHtml = `
                <div class="factor-mini-row">
                    <div class="factor-mini-top">
                        <span class="factor-mini-title">Clear Corridor</span>
                        <span class="eta-pill pill-success">Normal</span>
                    </div>
                    <div class="factor-mini-desc">Train is running on schedule with green signal clearance ahead.</div>
                </div>
            `;
        } else {
            const topFactors = activeFactors.slice(0, 3);
            contentHtml = topFactors.map(f => {
                const impactBadge = f.delay_impact_mins > 0
                    ? `<span class="eta-pill pill-high">+${f.delay_impact_mins} min</span>`
                    : window.EtaFactorProcessor.getImpactBadge(f.impact_level);
                return `
                    <div class="factor-mini-row">
                        <div class="factor-mini-top">
                            <span class="factor-mini-title">${f.name}</span>
                            ${impactBadge}
                        </div>
                        <div class="factor-mini-desc">${f.passenger_explanation}</div>
                    </div>
                `;
            }).join('');
        }

        containers.forEach(container => {
            if (container) container.innerHTML = contentHtml;
        });
    }

    renderAllTwelveFactors(train) {
        const containers = [
            document.getElementById('detailsAllTwelveFactorsContainer'),
            document.getElementById('mapAllTwelveFactorsContainer'),
            document.getElementById('routeAllTwelveFactorsContainer')
        ];

        const allTwelve = window.EtaFactorProcessor.getAllTwelveFactors(train);

        const contentHtml = allTwelve.map(f => {
            let impactBadge;
            if (f.is_active && f.delay_impact_mins > 0) {
                impactBadge = `<span class="eta-pill pill-high">+${f.delay_impact_mins} min</span>`;
            } else if (f.is_active) {
                impactBadge = window.EtaFactorProcessor.getImpactBadge(f.impact_level);
            } else {
                impactBadge = `<span class="eta-pill pill-nominal">Normal</span>`;
            }

            return `
                <div class="factor-mini-row">
                    <div class="factor-mini-top">
                        <span class="factor-mini-title">${f.name}</span>
                        ${impactBadge}
                    </div>
                    <div class="factor-mini-desc">${f.passenger_explanation}</div>
                </div>
            `;
        }).join('');

        containers.forEach(container => {
            if (container) container.innerHTML = contentHtml;
        });
    }

    renderNextStationsPreview(train) {
        const containers = [
            document.getElementById('nextStationsPreviewList'),
            document.getElementById('mapNextStationsPreviewList')
        ];
        if (!train.stations) return;

        let stations = train.stations || [];
        const seenCodes = new Set();
        stations = stations.filter(stn => {
            const code = String(stn.code || '').trim().toUpperCase();
            if (!code || seenCodes.has(code)) return false;
            seenCodes.add(code);
            return true;
        });

        // Filter upcoming or approaching stations
        const upcomingStns = stations.filter(s => s.status !== 'departed').slice(0, 3);
        const displayList = upcomingStns.length > 0 ? upcomingStns : stations.slice(-3);

        const contentHtml = displayList.map(stn => `
            <div class="station-preview-item">
                <div class="stn-prev-left">
                    <span class="stn-prev-dot"></span>
                    <span class="stn-prev-name">${stn.name}</span>
                    <span class="stn-prev-pf">PF ${stn.platform || '1'}</span>
                </div>
                <span class="stn-prev-eta">${stn.predicted_arr !== 'START' ? stn.predicted_arr : stn.scheduled_dep}</span>
            </div>
        `).join('');

        containers.forEach(container => {
            if (container) container.innerHTML = contentHtml;
        });
    }

    renderSmartAlert(train) {
        const alertCard = document.getElementById('detailsSmartAlertContainer');
        const routeAlertCard = document.getElementById('routeSmartAlertContainer');

        const alerts = train.passenger_alerts || [];
        if (alerts.length > 0) {
            const firstAlert = alerts[0];
            const titleEl = document.getElementById('detailsAlertTitle');
            const msgEl = document.getElementById('detailsAlertMessage');
            const timeEl = document.getElementById('detailsAlertTime');

            if (titleEl) titleEl.textContent = firstAlert.title;
            if (msgEl) msgEl.textContent = firstAlert.message;
            if (timeEl) timeEl.textContent = firstAlert.time;

            const routeTitleEl = document.getElementById('routeAlertTitle');
            const routeMsgEl = document.getElementById('routeAlertMessage');
            const routeTimeEl = document.getElementById('routeAlertTime');

            if (routeTitleEl) routeTitleEl.textContent = firstAlert.title;
            if (routeMsgEl) routeMsgEl.textContent = firstAlert.message;
            if (routeTimeEl) routeTimeEl.textContent = firstAlert.time;

            if (alertCard) alertCard.style.display = 'flex';
            if (routeAlertCard) routeAlertCard.style.display = 'flex';
        } else {
            if (alertCard) alertCard.style.display = 'none';
            if (routeAlertCard) routeAlertCard.style.display = 'none';
        }
    }

    renderUpcomingStations(train) {
        // Keep for backward compatibility with older test harnesses
        this.renderCompleteRouteTimeline(train);
        this.renderRouteTimetableTable(train);
    }

    renderPassengerAlerts(train) {
        const container = document.getElementById('passengerAlertsList');
        if (!container) return;

        const countBadge = document.getElementById('alertsFeedCountBadge');

        const alerts = train.passenger_alerts || [];
        if (countBadge) {
            countBadge.textContent = alerts.length === 1 ? '1 Bulletin Active' : `${alerts.length} Bulletins Active`;
            countBadge.style.display = alerts.length > 0 ? 'inline-block' : 'none';
        }

        if (alerts.length === 0) {
            container.innerHTML = `
                <div class="alerts-empty-state">
                    <div class="empty-icon"><i class="fa-solid fa-circle-check"></i></div>
                    <div class="empty-title">All Operational Signals Clear</div>
                    <div class="empty-desc">No active delay advisories, speed restrictions, or congestion bulletins reported for this train.</div>
                </div>
            `;
            return;
        }

        container.innerHTML = alerts.map(alert => {
            const severity = (alert.severity || 'info').toLowerCase();
            const iconClass = alert.icon || (severity === 'danger' ? 'fa-triangle-exclamation' : (severity === 'warning' || severity === 'attention' ? 'fa-triangle-exclamation' : 'fa-bell'));
            return `
                <div class="passenger-alert-card alert-severity-${severity}">
                    <div class="alert-icon-box"><i class="fa-solid ${iconClass}"></i></div>
                    <div class="alert-content">
                        <div class="alert-header">
                            <span class="alert-title">${alert.title}</span>
                            <span class="alert-timestamp">${alert.time || 'Live'}</span>
                        </div>
                        <div class="alert-message">${alert.message}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    startSimulationTicker() {
        if (this.simulationTimer) clearInterval(this.simulationTimer);

        this.simulationTimer = setInterval(async () => {
            if (!this.isSimulationRunning) return;

            try {
                if (this.currentTrain && this.currentTrain.train_number) {
                    const res = await window.railwayApi.simulateTrainStep(this.currentTrain.train_number);
                    if (res && res.train) {
                        this.applyTrainData(res.train);

                        const speedSub = document.getElementById('simSpeedIndicator');
                        if (speedSub) {
                            speedSub.textContent = `${res.train.current_speed_kmh} km/h • GPS`;
                        }
                    }
                }
            } catch (e) {
                // Keep current state on network pause
            }
        }, 15000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.passengerApp = new UnifiedGatiSetuApp();
    window.passengerApp.init();
});
