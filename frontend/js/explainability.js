
function renderExplainabilityCards(reasons) {
    const container = document.getElementById('explainabilityCards');
    if (!container) return;

    container.innerHTML = '';
    if (!reasons || reasons.length === 0) {
        container.innerHTML = '<div style="color:#64748b; font-size:13px;">No abnormal track impediments detected. Train running on scheduled green corridor.</div>';
        return;
    }

    reasons.forEach(r => {
        const card = document.createElement('div');
        const sevClass = r.severity ? `severity-${r.severity}` : 'severity-info';
        card.className = `reason-card ${sevClass}`;

        const impactSign = r.delay_impact_mins > 0 ? `+${r.delay_impact_mins}m` : (r.delay_impact_mins < 0 ? `${r.delay_impact_mins}m` : '0m');

        card.innerHTML = `
            <div class="reason-top">
                <span class="reason-title">${r.title}</span>
                <span class="reason-delta">${impactSign}</span>
            </div>
            <div class="reason-desc">${r.description}</div>
        `;
        container.appendChild(card);
    });
}
