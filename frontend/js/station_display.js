
async function loadStationDisplayBoard(stationCode) {
    try {
        const data = await api.getStationDisplay(stationCode);
        document.getElementById('fidsStationHeading').innerText = `${data.station_name.toUpperCase()} (${data.station_code}) - PASSENGER INFORMATION DISPLAY SYSTEM`;
        
        const tbody = document.getElementById('fidsTableBody');
        tbody.innerHTML = '';

        const seen = new Set();
        const uniqueArrivals = (data.arrivals || []).filter(a => {
            const key = String(a.train_number || '').trim();
            if (!key || seen.has(key)) return false;
            seen.add(key);
            return true;
        });

        if (uniqueArrivals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:30px; color:#9ca3af;">No trains scheduled at this station in current window.</td></tr>';
            return;
        }

        uniqueArrivals.forEach(a => {
            const tr = document.createElement('tr');
            const isDelayed = a.delay_mins > 3;
            const statusCode = (a.status_code || a.current_status_code || '').toUpperCase();
            const rawStatus = (a.status || a.current_status || '').toUpperCase();

            let statusClass = isDelayed ? 'fids-status-delayed' : 'fids-status-ontime';
            let statusText = a.status || 'On Time';

            if (statusCode === 'NOT_STARTED' || rawStatus === 'NOT STARTED' || rawStatus === 'NOT-STARTED' || rawStatus === 'NOT_STARTED') {
                statusClass = 'fids-status-not-started';
                statusText = 'NOT STARTED';
            } else if (statusCode === 'COMPLETED' || rawStatus === 'COMPLETED' || rawStatus === 'ARRIVED') {
                statusClass = 'fids-status-departed';
                statusText = 'Completed';
            }

            tr.innerHTML = `
                <td class="col-train-no" style="font-weight:800; color:#38bdf8;">${a.train_number}</td>
                <td class="col-train-name">${a.train_name}</td>
                <td class="col-source">${a.source}</td>
                <td class="col-dest">${a.destination}</td>
                <td class="col-sch">${a.scheduled_arrival}</td>
                <td class="col-eta" style="font-size:1.15rem; font-weight:800; color:#34d399;">${a.expected_arrival}</td>
                <td class="col-delay">${a.delay_mins > 0 ? '+' + a.delay_mins + 'm' : '0m'}</td>
                <td class="col-pf"><span class="fids-pf-badge">${a.platform}</span></td>
                <td class="col-status ${statusClass}">${statusText}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error('Error loading FIDS board:', err);
    }
}
