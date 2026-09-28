/**
 * GatiSetu - Problem Statement 12-Factor ETA Engine Architecture
 * 
 * Defines the structured schema for all 12 operational railway factors
 * specified in the problem statement. Provides feature processing,
 * confidence range calculation, impact classification, and passenger-friendly
 * explainability translation.
 */

const PS_ETA_FACTORS_SCHEMA = {
    GPS_LOCATION: {
        id: "gps_telemetry",
        code: "F01",
        name: "GPS & Live Telemetry",
        category: "Real-Time Telemetry",
        icon: "fa-satellite-dish",
        defaultImpact: "Nominal",
        defaultText: "Live GPS updates confirmed normal section cruising speed."
    },
    SIGNAL_ASPECTS: {
        id: "signal_aspects",
        code: "F02",
        name: "Signal Aspects & Halts",
        category: "Signaling & Interlocking",
        icon: "fa-traffic-light",
        defaultImpact: "High impact",
        defaultText: "Outer signal aspect holding for track clearance ahead."
    },
    SECTIONAL_RUNTIME: {
        id: "sectional_runtime",
        code: "F03",
        name: "Sectional Running Time",
        category: "Section Performance",
        icon: "fa-gauge-high",
        defaultImpact: "Moderate impact",
        defaultText: "Section running envelope within permissible time bounds."
    },
    WEATHER_CONDITIONS: {
        id: "weather_conditions",
        code: "F04",
        name: "Weather & Track Conditions",
        category: "Environmental",
        icon: "fa-cloud-rain",
        defaultImpact: "Moderate impact",
        defaultText: "Weather conditions along route require regulated speed."
    },
    HISTORICAL_PATTERNS: {
        id: "historical_patterns",
        code: "F05",
        name: "Historical Delay Patterns",
        category: "Historical Intelligence",
        icon: "fa-chart-line",
        defaultImpact: "Low impact",
        defaultText: "Historical statistical delay modeling applied for junction arrivals."
    },
    DOWNSTREAM_CONGESTION: {
        id: "downstream_congestion",
        code: "F06",
        name: "Downstream Track Congestion",
        category: "Traffic Density",
        icon: "fa-network-wired",
        defaultImpact: "High impact",
        defaultText: "High traffic density at downstream junction causing caution signals."
    },
    SPEED_RESTRICTIONS: {
        id: "speed_restrictions",
        code: "F07",
        name: "Speed Restriction (TSR)",
        category: "Track Infrastructure",
        icon: "fa-triangle-exclamation",
        defaultImpact: "Moderate impact",
        defaultText: "Temporary speed restriction active for track maintenance section."
    },
    UNSCHEDULED_STOPPAGES: {
        id: "unscheduled_stoppages",
        code: "F08",
        name: "Unscheduled Stoppages",
        category: "Operational Incidents",
        icon: "fa-hand",
        defaultImpact: "High impact",
        defaultText: "Unscheduled section halt awaiting block clearance."
    },
    PRECEDING_TRAIN_DELAYS: {
        id: "preceding_train_delays",
        code: "F09",
        name: "Preceding Train Delay",
        category: "Traffic Density",
        icon: "fa-train-subway",
        defaultImpact: "Moderate impact",
        defaultText: "Preceding train in section limiting cruising headway."
    },
    MAINTENANCE_BLOCKS: {
        id: "maintenance_blocks",
        code: "F10",
        name: "Temporary Maintenance Blocks",
        category: "Engineering Work",
        icon: "fa-wrench",
        defaultImpact: "Low impact",
        defaultText: "Engineering shadow block active on adjacent loop line."
    },
    LEVEL_CROSSINGS: {
        id: "level_crossings",
        code: "F11",
        name: "Level-Crossing Gate Clearance",
        category: "Interlocking",
        icon: "fa-road-barrier",
        defaultImpact: "Moderate impact",
        defaultText: "Interlocked level-crossing gate clearance operating normally."
    },
    OPERATIONAL_BOTTLENECKS: {
        id: "operational_bottlenecks",
        code: "F12",
        name: "Operational Bottlenecks",
        category: "Junction Capacity",
        icon: "fa-diagram-project",
        defaultImpact: "High impact",
        defaultText: "Junction bottleneck constraints regulating train movement."
    }
};

class EtaFactorProcessor {
    /**
     * Filters active factors for a train.
     */
    static getActiveFactors(train) {
        if (!train || !train.eta_factors) return [];
        return train.eta_factors.filter(f => f.is_active);
    }

    /**
     * Returns a complete list of all 12 Problem Statement factors for a train,
     * merging train-specific active attributes with schema defaults for the rest.
     */
    static getAllTwelveFactors(train) {
        const activeList = this.getActiveFactors(train);
        const activeMap = {};
        activeList.forEach(f => {
            activeMap[f.id] = f;
        });

        return Object.values(PS_ETA_FACTORS_SCHEMA).map(schema => {
            if (activeMap[schema.id]) {
                return {
                    ...schema,
                    ...activeMap[schema.id],
                    is_active: true
                };
            }
            return {
                ...schema,
                is_active: false,
                impact_level: "Nominal / Clear",
                delay_impact_mins: 0,
                passenger_explanation: schema.defaultText
            };
        });
    }

    /**
     * Computes the formatted confidence window string (e.g., "08:41–08:51 AM").
     */
    static getConfidenceRange(predictedEtaStr, confidencePct = 94) {
        if (!predictedEtaStr || predictedEtaStr === "--:--") return "Estimating...";
        
        const parsed = this.parseTime(predictedEtaStr);
        if (!parsed) return predictedEtaStr;

        const varianceMins = confidencePct >= 92 ? 5 : (confidencePct >= 80 ? 8 : 12);
        
        const minDate = new Date(parsed.getTime() - varianceMins * 60000);
        const maxDate = new Date(parsed.getTime() + varianceMins * 60000);

        return `${this.formatTime(minDate)}–${this.formatTime(maxDate)}`;
    }

    /**
     * Formats impact level badge HTML.
     */
    static getImpactBadge(impactLevel) {
        const level = (impactLevel || "Moderate impact").toLowerCase();
        if (level.includes("high")) {
            return `<span class="eta-pill pill-high">High impact</span>`;
        } else if (level.includes("mod")) {
            return `<span class="eta-pill pill-moderate">Moderate impact</span>`;
        } else if (level.includes("low")) {
            return `<span class="eta-pill pill-low">Low impact</span>`;
        } else if (level.includes("saved") || level.includes("positive") || level.includes("recovery")) {
            return `<span class="eta-pill pill-success">Time Saved</span>`;
        }
        return `<span class="eta-pill pill-nominal">Normal</span>`;
    }

    /**
     * Parses time string to Date object for today.
     */
    static parseTime(timeStr) {
        if (!timeStr) return null;
        const clean = timeStr.trim();
        const now = new Date();

        const match12 = clean.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)?$/i);
        if (match12) {
            let hours = parseInt(match12[1], 10);
            const minutes = parseInt(match12[2], 10);
            const period = match12[3] ? match12[3].toUpperCase() : null;

            if (period === "PM" && hours < 12) hours += 12;
            if (period === "AM" && hours === 12) hours = 0;

            const dt = new Date(now);
            dt.setHours(hours, minutes, 0, 0);
            return dt;
        }

        return null;
    }

    /**
     * Formats Date object into HH:MM AM/PM string.
     */
    static formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }
}

// Attach globally
window.PS_ETA_FACTORS_SCHEMA = PS_ETA_FACTORS_SCHEMA;
window.EtaFactorProcessor = EtaFactorProcessor;
