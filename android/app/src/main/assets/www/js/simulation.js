
class SimulationLab {
    constructor(app) {
        this.app = app;
        this.autoTimer = null;
        this.isAutoRunning = false;
        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('btnSimStep').addEventListener('click', () => this.triggerStep());
        document.getElementById('btnSimCongestion').addEventListener('click', () => this.injectCongestion());
        document.getElementById('btnSimTSR').addEventListener('click', () => this.injectTSR());
        document.getElementById('btnSimHalt').addEventListener('click', () => this.injectHalt());
        document.getElementById('btnSimClear').addEventListener('click', () => this.clearEvents());
        document.getElementById('btnSimAuto').addEventListener('click', () => this.toggleAutoSim());
    }

    async triggerStep() {
        try {
            await api.simulateTick(this.app.currentTrainNumber, 0.15);
            this.app.refreshCurrentTrain();
        } catch (err) {
            console.error('Sim step error:', err);
        }
    }

    async injectCongestion() {
        try {
            await api.injectEvent(this.app.currentTrainNumber, 'CONGESTION', null, 6.0);
            this.app.refreshCurrentTrain();
        } catch (err) {
            console.error('Sim congestion error:', err);
        }
    }

    async injectTSR() {
        try {
            await api.injectEvent(this.app.currentTrainNumber, 'TSR', null, 4.0, 30.0);
            this.app.refreshCurrentTrain();
        } catch (err) {
            console.error('Sim TSR error:', err);
        }
    }

    async injectHalt() {
        try {
            await api.injectEvent(this.app.currentTrainNumber, 'UNSCHEDULED_STOP', null, 8.0);
            this.app.refreshCurrentTrain();
        } catch (err) {
            console.error('Sim halt error:', err);
        }
    }

    async clearEvents() {
        try {
            await api.injectEvent(this.app.currentTrainNumber, 'CLEAR');
            this.app.refreshCurrentTrain();
        } catch (err) {
            console.error('Sim clear error:', err);
        }
    }

    toggleAutoSim() {
        this.isAutoRunning = !this.isAutoRunning;
        const statusSpan = document.getElementById('autoSimStatus');
        const btn = document.getElementById('btnSimAuto');

        if (this.isAutoRunning) {
            statusSpan.innerText = 'ON (Every 4s)';
            btn.style.background = '#047857';
            this.autoTimer = setInterval(() => {
                this.triggerStep();
            }, 4000);
        } else {
            statusSpan.innerText = 'OFF';
            btn.style.background = '#0f766e';
            if (this.autoTimer) {
                clearInterval(this.autoTimer);
                this.autoTimer = null;
            }
        }
    }
}
