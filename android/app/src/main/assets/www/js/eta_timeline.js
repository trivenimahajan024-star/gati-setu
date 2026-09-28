
function renderDynamicETATimeline(etaData, routeData) {
    const tableBody = document.getElementById('etaTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    const stations = routeData.stations;
    const currentIdx = routeData.current_section_index;

    const predMap = {};
    if (etaData.section_predictions) {
        etaData.section_predictions.forEach(p => {
            predMap[p.to_station_code] = p;
        });
    }

    stations.forEach((stn, idx) => {
        const tr = document.createElement('tr');
        const isPassed = idx < currentIdx;
        const isCurrent = idx === currentIdx;
        const isUpcoming = idx > currentIdx;

        if (isPassed) tr.className = 'row-passed';
        else if (isCurrent) tr.className = 'row-current';

        let statusBadge = '<span class="stn-badge badge-upcoming">Upcoming</span>';
        if (isPassed) statusBadge = '<span class="stn-badge badge-passed"><i class="fa-solid fa-check"></i> Passed</span>';
        else if (isCurrent) statusBadge = '<span class="stn-badge badge-current"><span class="pulse-dot" style="width:6px;height:6px;"></span> Current</span>';

        const stnName = `<strong>${stn.station_name}</strong> <span style="color:#64748b; font-size:11px;">(${stn.station_code})</span>`;
        const distText = `${stn.distance_km} km`;
        const schText = `<span class="mono-time">${stn.scheduled_arrival}</span> / <span class="mono-time">${stn.scheduled_departure}</span>`;

        let predText = '-';
        let deltaText = '-';
        let condText = '<span class="cond-badge cond-low">Clear Corridor</span>';
        let confText = '-';

        if (isPassed) {
            predText = `<span class="mono-time text-muted">${stn.scheduled_arrival}</span>`;
            deltaText = `<span class="badge-delta delta-zero">0m</span>`;
            confText = `100%`;
        } else if (isCurrent) {
            predText = `<span class="eta-pred-time">At Section Block</span>`;
            deltaText = `<span class="badge-delta ${etaData.current_delay_mins > 5 ? 'delta-plus' : 'delta-zero'}">+${etaData.current_delay_mins}m</span>`;
            confText = `98% (±2m)`;
        } else {
            const pred = predMap[stn.station_code];
            if (pred) {
                predText = `<span class="eta-pred-time">${pred.predicted_arrival}</span>`;
                const d = pred.accumulated_delay_mins;
                const deltaClass = d > 5 ? 'delta-plus' : (d > 0 ? 'delta-zero' : 'delta-minus');
                deltaText = `<span class="badge-delta ${deltaClass}">${d >= 0 ? '+' : ''}${d}m</span>`;

                if (pred.tsr_active) {
                    condText = `<span class="cond-badge cond-tsr"><i class="fa-solid fa-triangle-exclamation"></i> TSR Active</span>`;
                } else if (pred.congestion_level === 'HIGH' || pred.congestion_level === 'SEVERE') {
                    condText = `<span class="cond-badge cond-high"><i class="fa-solid fa-traffic-light"></i> ${pred.congestion_level} Congestion</span>`;
                } else if (pred.expected_recovery_mins > 0) {
                    condText = `<span class="cond-badge cond-low"><i class="fa-solid fa-bolt"></i> Recovering -${pred.expected_recovery_mins}m</span>`;
                }

                confText = `<strong>${pred.confidence_percent}%</strong> <span style="font-size:11px; color:#64748b;">(±${pred.prediction_window_mins}m)</span>`;
            }
        }

        tr.innerHTML = `
            <td>${statusBadge}</td>
            <td>${stnName}</td>
            <td>${distText}</td>
            <td>${schText}</td>
            <td>${predText}</td>
            <td>${deltaText}</td>
            <td>${condText}</td>
            <td>${confText}</td>
        `;
        tableBody.appendChild(tr);
    });
}
