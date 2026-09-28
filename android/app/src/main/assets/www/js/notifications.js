
class NotificationManager {
    constructor(app) {
        this.app = app;
        this.currentFilter = 'all';
        this.notifications = [];
        this.unreadCount = 0;
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        const bellBtn = document.getElementById('notifBellBtn');
        const notifPanel = document.getElementById('notifDropdownPanel');

        if (bellBtn && notifPanel) {
            bellBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = notifPanel.classList.contains('show');
                this.closeAllDropdowns();
                if (!isVisible) {
                    notifPanel.classList.add('show');
                }
            });
        }

        document.addEventListener('click', (e) => {
            if (notifPanel && !notifPanel.contains(e.target) && (!bellBtn || !bellBtn.contains(e.target))) {
                notifPanel.classList.remove('show');
            }
        });

        const filterBtns = document.querySelectorAll('.notif-filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFilter = btn.getAttribute('data-filter') || 'all';
                this.render();
            });
        });

        const markAllBtn = document.getElementById('btnMarkAllRead');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', async () => {
                await this.markAllRead();
            });
        }

        const clearAllBtn = document.getElementById('btnClearNotifs');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', async () => {
                await this.clearAll();
            });
        }
    }

    closeAllDropdowns() {
        const notifPanel = document.getElementById('notifDropdownPanel');
        const profilePanel = document.getElementById('profileDropdownMenu');
        if (notifPanel) notifPanel.classList.remove('show');
        if (profilePanel) profilePanel.classList.remove('show');
    }

    async loadNotifications(role) {
        try {
            const data = await api.getNotifications(role);
            this.notifications = data.notifications || [];
            this.unreadCount = data.unread_count || 0;
            this.updateBadge();
            this.render();
        } catch (err) {
            console.error('Error fetching notifications:', err);
        }
    }

    updateBadge() {
        const badge = document.getElementById('notifBadge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.innerText = this.unreadCount;
                badge.style.display = 'inline-flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    async markAsRead(notifId) {
        const role = this.app.currentRole || 'passenger';
        await api.markNotificationRead(role, notifId);
        await this.loadNotifications(role);
    }

    async markAllRead() {
        const role = this.app.currentRole || 'passenger';
        await api.markNotificationRead(role, 'all');
        await this.loadNotifications(role);
    }

    async clearAll() {
        const role = this.app.currentRole || 'passenger';
        await api.clearNotifications(role);
        await this.loadNotifications(role);
    }

    render() {
        const listContainer = document.getElementById('notifList');
        if (!listContainer) return;

        let filtered = this.notifications;
        if (this.currentFilter === 'unread') {
            filtered = this.notifications.filter(n => !n.read);
        } else if (this.currentFilter === 'alerts') {
            filtered = this.notifications.filter(n => n.severity === 'WARNING' || n.severity === 'CRITICAL');
        }

        if (filtered.length === 0) {
            listContainer.innerHTML = `
                <div class="notif-empty">
                    <i class="fa-solid fa-bell-slash"></i>
                    <p>No notifications available</p>
                </div>
            `;
            return;
        }

        listContainer.innerHTML = '';
        filtered.forEach(n => {
            const item = document.createElement('div');
            item.className = `notif-item ${n.read ? 'read' : 'unread'} severity-${n.severity.toLowerCase()}`;

            let iconClass = n.icon || 'fa-bell';
            let badgeClass = 'badge-info';
            if (n.severity === 'SUCCESS') badgeClass = 'badge-success';
            if (n.severity === 'WARNING') badgeClass = 'badge-warning';
            if (n.severity === 'CRITICAL') badgeClass = 'badge-critical';

            item.innerHTML = `
                <div class="notif-icon-col"><i class="fa-solid ${iconClass}"></i></div>
                <div class="notif-content-col">
                    <div class="notif-title-row">
                        <span class="notif-title">${n.title}</span>
                        <span class="notif-tag ${badgeClass}">${n.severity}</span>
                    </div>
                    <div class="notif-desc">${n.description}</div>
                    <div class="notif-meta">
                        <span class="notif-time"><i class="fa-regular fa-clock"></i> ${n.time_ago} (${n.timestamp})</span>
                        ${n.train_number ? `<span class="notif-train-link" data-train="${n.train_number}"><i class="fa-solid fa-train"></i> Train ${n.train_number}</span>` : ''}
                    </div>
                </div>
                ${!n.read ? `<button class="btn-mark-read" data-id="${n.id}" title="Mark as read"><i class="fa-solid fa-check"></i></button>` : ''}
            `;

            const markBtn = item.querySelector('.btn-mark-read');
            if (markBtn) {
                markBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.markAsRead(n.id);
                });
            }

            const trainLink = item.querySelector('.notif-train-link');
            if (trainLink) {
                trainLink.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const tNum = trainLink.getAttribute('data-train');
                    this.app.selectTrain(tNum);
                    document.getElementById('notifDropdownPanel').classList.remove('show');
                });
            }

            listContainer.appendChild(item);
        });
    }
}
