
class UserProfileManager {
    constructor(app) {
        this.app = app;
        this.currentRole = 'passenger';
        this.profileData = null;
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        const profileBtn = document.getElementById('userProfileAvatarBtn');
        const profileMenu = document.getElementById('profileDropdownMenu');

        if (profileBtn && profileMenu) {
            profileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = profileMenu.classList.contains('show');
                this.closeAllDropdowns();
                if (!isVisible) {
                    profileMenu.classList.add('show');
                }
            });
        }

        document.addEventListener('click', (e) => {
            if (profileMenu && !profileMenu.contains(e.target) && (!profileBtn || !profileBtn.contains(e.target))) {
                profileMenu.classList.remove('show');
            }
        });

        document.querySelectorAll('.role-select-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const role = btn.getAttribute('data-role');
                if (role) {
                    this.switchRole(role);
                    if (profileMenu) profileMenu.classList.remove('show');
                }
            });
        });

        const viewProfileLink = document.getElementById('menuViewProfile');
        if (viewProfileLink) {
            viewProfileLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.app.switchTab('tab-user-profile');
                if (profileMenu) profileMenu.classList.remove('show');
            });
        }
    }

    closeAllDropdowns() {
        const notifPanel = document.getElementById('notifDropdownPanel');
        const profilePanel = document.getElementById('profileDropdownMenu');
        if (notifPanel) notifPanel.classList.remove('show');
        if (profilePanel) profilePanel.classList.remove('show');
    }

    async switchRole(role) {
        this.currentRole = role;
        this.app.currentRole = role;

        document.querySelectorAll('.role-select-btn').forEach(btn => {
            if (btn.getAttribute('data-role') === role) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        await this.loadProfile(role);
        await this.app.notificationManager.loadNotifications(role);

        const currentTab = this.app.activeTabId;
        if (currentTab === 'tab-user-profile') {
            this.renderProfilePane();
        }
    }

    async loadProfile(role = 'passenger') {
        try {
            this.profileData = await api.getUserProfile(role);
            this.updateHeaderProfileWidget();
        } catch (err) {
            console.error('Error loading user profile:', err);
        }
    }

    updateHeaderProfileWidget() {
        if (!this.profileData) return;
        const avatarEl = document.getElementById('navUserAvatar');
        const nameEl = document.getElementById('navUserName');
        const roleBadgeEl = document.getElementById('navUserRoleBadge');

        if (avatarEl) avatarEl.innerText = this.profileData.user_avatar || 'U';
        if (nameEl) nameEl.innerText = this.profileData.user_name || 'User';
        if (roleBadgeEl) roleBadgeEl.innerText = this.profileData.role_name || 'Passenger';

        const dropdownAvatar = document.getElementById('dropdownUserAvatar');
        const dropdownName = document.getElementById('dropdownUserName');
        const dropdownSubtitle = document.getElementById('dropdownUserSubtitle');

        if (dropdownAvatar) dropdownAvatar.innerText = this.profileData.user_avatar || 'U';
        if (dropdownName) dropdownName.innerText = this.profileData.user_name || 'User';
        if (dropdownSubtitle) dropdownSubtitle.innerText = this.profileData.subtitle || '';
    }

    renderProfilePane() {
        const paneContainer = document.getElementById('tab-user-profile');
        if (!paneContainer || !this.profileData) return;

        const p = this.profileData;
        let roleContent = '';

        if (p.role_id === 'passenger') {
            roleContent = this.renderPassengerView(p);
        } else if (p.role_id === 'station_staff') {
            roleContent = this.renderStationStaffView(p);
        } else if (p.role_id === 'control_room') {
            roleContent = this.renderControlRoomView(p);
        }

        const isStaff = p.role_id !== 'passenger';

        paneContainer.innerHTML = `
            <div class="profile-dashboard-layout">
                <div class="profile-header-card">
                    <div class="profile-avatar-large">${p.user_avatar}</div>
                    <div class="profile-info">
                        <div class="profile-role-badge"><i class="fa-solid fa-user-shield"></i> ROLE: ${p.role_name.toUpperCase()}</div>
                        <h2 class="profile-name">${p.user_name}</h2>
                        <p class="profile-sub">${p.subtitle}</p>
                    </div>
                    ${isStaff ? `
                        <button class="btn-staff-logout" onclick="window.gatiApp.logoutStaff(); return false;">
                            <i class="fa-solid fa-right-from-bracket"></i> Logout to Passenger App
                        </button>
                    ` : `
                        <button class="btn-staff-login" onclick="window.gatiApp.openStaffLogin(); return false;">
                            <i class="fa-solid fa-user-shield"></i> Staff Login Portal
                        </button>
                    `}
                </div>

                ${roleContent}
            </div>
        `;

        this.bindPaneInteractiveElements(paneContainer);
    }

    renderPassengerView(p) {
        const savedTrainsHtml = p.saved_trains.map(t => `
            <div class="saved-train-item">
                <div class="st-info">
                    <span class="st-num">${t.train_number}</span>
                    <span class="st-name">${t.train_name}</span>
                    <span class="st-route">${t.route}</span>
                </div>
                <button class="btn-quick-track" data-train="${t.train_number}"><i class="fa-solid fa-crosshairs"></i> Quick Track</button>
            </div>
        `).join('');

        const recentSearchesHtml = p.recent_searches.map(num => `
            <button class="chip-recent-search" data-train="${num}"><i class="fa-solid fa-clock-rotate-left"></i> Train ${num}</button>
        `).join('');

        const recentJourneysHtml = p.recent_journeys.map(j => `
            <div class="journey-log-item">
                <div class="jl-left">
                    <span class="jl-num"><i class="fa-solid fa-train"></i> Train ${j.train_number}</span>
                    <span class="jl-route">${j.from} → ${j.to}</span>
                </div>
                <div class="jl-right">
                    <span class="jl-date">${j.date}</span>
                    <span class="jl-status badge-success">${j.status}</span>
                </div>
            </div>
        `).join('');

        return `
            <div class="profile-grid">
                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-star text-amber"></i> MY TRAINS (FAVOURITES)</div>
                    <div class="saved-trains-list">${savedTrainsHtml}</div>
                </div>

                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-magnifying-glass"></i> RECENT SEARCHES</div>
                    <div class="recent-chips-wrap">${recentSearchesHtml}</div>
                </div>

                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-route"></i> MY JOURNEYS & PNR LOGS</div>
                    <div class="journeys-list">${recentJourneysHtml}</div>
                </div>

                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-bell"></i> NOTIFICATION PREFERENCES</div>
                    <div class="prefs-list">
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.delay_alerts ? 'checked' : ''}><span>Train Delay Alerts (+5m delay triggers)</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.eta_updates ? 'checked' : ''}><span>Dynamic ETA Destination Shifts</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.platform_changes ? 'checked' : ''}><span>Platform Assignment & Shift Notifications</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.journey_reminders ? 'checked' : ''}><span>Journey Departure & Boarding Reminders</span></label>
                    </div>
                </div>
            </div>
        `;
    }

    renderStationStaffView(p) {
        const shortcutsHtml = p.dashboard_shortcuts.map(s => `
            <button class="shortcut-card-btn" data-tab="${s.tab}">
                <div class="sc-icon"><i class="fa-solid ${s.icon}"></i></div>
                <div class="sc-label">${s.label}</div>
            </button>
        `).join('');

        return `
            <div class="profile-grid">
                <div class="profile-section-card highlight-card">
                    <div class="sec-header"><i class="fa-solid fa-building-columns"></i> ASSIGNED STATION DETAILS</div>
                    <div class="station-detail-box">
                        <div class="sd-row"><span>Assigned Junction:</span> <strong>${p.assigned_station}</strong></div>
                        <div class="sd-row"><span>Station Code:</span> <strong>${p.station_code}</strong></div>
                        <div class="sd-row"><span>Railway Zone:</span> <strong>${p.zone}</strong></div>
                        <div class="sd-row"><span>Duty Shift:</span> <strong>${p.duty_shift}</strong></div>
                    </div>
                </div>

                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-bolt"></i> STATION DASHBOARD SHORTCUTS</div>
                    <div class="shortcuts-grid">${shortcutsHtml}</div>
                </div>

                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-sliders"></i> STATION STAFF NOTIFICATION PREFERENCES</div>
                    <div class="prefs-list">
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.arrival_departure ? 'checked' : ''}><span>Live Arrival & Departure Waypoint Alerts</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.platform_change_alerts ? 'checked' : ''}><span>Platform Track Conflict & Shift Warnings</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.signal_operational_alerts ? 'checked' : ''}><span>Outer Signal Holding & Caution Orders</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.downstream_eta_changes ? 'checked' : ''}><span>Downstream Dynamic ETA Calculation Shifts</span></label>
                    </div>
                </div>
            </div>
        `;
    }

    renderControlRoomView(p) {
        const shortcutsHtml = p.dashboard_shortcuts.map(s => `
            <button class="shortcut-card-btn" data-tab="${s.tab}">
                <div class="sc-icon"><i class="fa-solid ${s.icon}"></i></div>
                <div class="sc-label">${s.label}</div>
            </button>
        `).join('');

        return `
            <div class="profile-grid">
                <div class="profile-section-card highlight-card">
                    <div class="sec-header"><i class="fa-solid fa-tower-observation"></i> CONTROL CENTER JURISDICTION</div>
                    <div class="station-detail-box">
                        <div class="sd-row"><span>Control Center:</span> <strong>${p.assigned_zone}</strong></div>
                        <div class="sd-row"><span>Corridor Jurisdiction:</span> <strong>${p.section_jurisdiction}</strong></div>
                        <div class="sd-row"><span>Controller ID:</span> <strong>${p.operator_id}</strong></div>
                    </div>
                </div>

                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-gauge-high"></i> CONTROL ROOM SHORTCUTS</div>
                    <div class="shortcuts-grid">${shortcutsHtml}</div>
                </div>

                <div class="profile-section-card">
                    <div class="sec-header"><i class="fa-solid fa-shield-halved"></i> OCC ALERT PREFERENCES</div>
                    <div class="prefs-list">
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.critical_delays ? 'checked' : ''}><span>Critical Delay Cascading (&gt;15 min delay)</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.network_congestion ? 'checked' : ''}><span>Junction Track Congestion & Yard Load Spikes</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.speed_restrictions ? 'checked' : ''}><span>Temporary Speed Restrictions (TSR) Imposed</span></label>
                        <label class="pref-toggle"><input type="checkbox" ${p.preferences.signal_issues ? 'checked' : ''}><span>Automatic Signaling & Interlocking Disruption</span></label>
                    </div>
                </div>
            </div>
        `;
    }

    bindPaneInteractiveElements(container) {
        container.querySelectorAll('.btn-quick-track, .chip-recent-search').forEach(btn => {
            btn.addEventListener('click', () => {
                const trainNum = btn.getAttribute('data-train');
                if (trainNum) {
                    this.app.selectTrain(trainNum);
                    this.app.switchTab('tab-dashboard');
                }
            });
        });

        container.querySelectorAll('.shortcut-card-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.getAttribute('data-tab');
                if (targetTab) {
                    this.app.switchTab(targetTab);
                }
            });
        });
    }
}
