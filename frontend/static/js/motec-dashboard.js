// MoTeC Dashboard - Display and configure LDX/LD file data
class MotecDashboard {
    constructor() {
        this.displayConfig = {
            layout: 'standard', // standard, compact, custom
            showGear: true,
            showRpmGauge: true,
            showLapTimes: true,
            channels: [], // Empty = show all default channels
            colors: {
                normal: '#ffffff',
                warning: '#ffaa00',
                danger: '#ff0000',
                success: '#00ff00'
            }
        };
        this.channelValues = {};
        this.updateInterval = null;
        this.defaultChannels = this.getDefaultChannels();
        this.init();
    }

    getDefaultChannels() {
        // Default MoTeC-style channels to display
        return [
            { name: 'ENGINE OIL TMP', internal: 'oil_temp', unit: '°F', type: 'temp' },
            { name: 'WATER TMP', internal: 'water_temp', unit: '°F', type: 'temp' },
            { name: 'OIL PRESS', internal: 'oil_pressure', unit: 'psi', type: 'pressure' },
            { name: 'FUEL PRESS', internal: 'fuel_pressure', unit: 'psi', type: 'pressure' },
            { name: 'GBOX OIL TMP', internal: 'gbox_oil_temp', unit: '°F', type: 'temp' },
            { name: 'DIFF OIL TMP', internal: 'diff_oil_temp', unit: '°F', type: 'temp' },
            { name: 'Speed', internal: 'speed', unit: 'mph', type: 'speed' },
            { name: 'RPMx1000', internal: 'rpm', unit: 'rpm', type: 'rpm' },
            { name: 'Throttle', internal: 'throttle', unit: '%', type: 'percentage' },
            { name: 'Brake', internal: 'brake', unit: '%', type: 'percentage' },
            { name: 'Lateral G', internal: 'g_force_lat', unit: 'g', type: 'gforce' },
            { name: 'Longitudinal G', internal: 'g_force_long', unit: 'g', type: 'gforce' }
        ];
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardConfig();
        this.renderDashboard();
        this.startDataUpdates();
    }


    setupEventListeners() {
        const configBtn = document.getElementById('configure-dashboard-btn');
        if (configBtn) {
            configBtn.addEventListener('click', () => this.showConfigModal());
        }

        const saveConfigBtn = document.getElementById('save-dashboard-config-btn');
        if (saveConfigBtn) {
            saveConfigBtn.addEventListener('click', () => this.saveDashboardConfig());
        }
    }


    renderDashboard() {
        const container = document.getElementById('motec-display-main');
        const gridContainer = document.getElementById('channel-values-grid');
        if (!container) return;

        // Determine which channels to show
        const channelsToShow = this.displayConfig.channels.length > 0
            ? this.defaultChannels.filter(ch => this.displayConfig.channels.includes(ch.name))
            : this.defaultChannels;

        // Initialize channel values
        this.channelValues = {};
        channelsToShow.forEach(ch => {
            this.channelValues[ch.name] = {
                value: 0,
                unit: ch.unit,
                label: ch.name,
                internal: ch.internal,
                type: ch.type
            };
        });

        // Render main display
        let html = `
            <div class="motec-display-header">
                <div class="motec-display-title">MoTeC Dashboard</div>
                <div style="font-size: 0.8rem; color: var(--text-dim);">
                    Live Telemetry Display
                </div>
            </div>
        `;

        // Gear display (if enabled)
        if (this.displayConfig.showGear) {
            html += `
                <div class="motec-display-gear-label">RACE</div>
                <div class="motec-display-gear" id="dashboard-gear">N</div>
            `;
        }

        // RPM Gauge (if enabled)
        if (this.displayConfig.showRpmGauge) {
            html += `
                <div class="rpm-gauge">
                    <canvas id="rpm-gauge-canvas" width="200" height="200"></canvas>
                </div>
            `;
        }

        // Channel rows - show configured channels
        html += '<div class="channels-section">';
        channelsToShow.forEach(ch => {
            html += `
                <div class="channel-row" data-channel="${this.escapeHtml(ch.name)}">
                    <span class="channel-label">${this.escapeHtml(ch.name)}</span>
                    <span class="channel-value" id="channel-${this.escapeHtml(ch.name)}">0 ${this.escapeHtml(ch.unit)}</span>
                </div>
            `;
        });
        html += '</div>';

        // Lap times (if enabled)
        if (this.displayConfig.showLapTimes) {
            html += `
                <div class="lap-time-display">
                    <div class="lap-time-item">
                        <div class="lap-time-label">REFERENCE LAP</div>
                        <div class="lap-time-value" id="dashboard-ref-lap">0:00.000</div>
                    </div>
                    <div class="lap-time-item">
                        <div class="lap-time-label">RUNNING LAP</div>
                        <div class="lap-time-value" id="dashboard-running-lap">0:00.000</div>
                    </div>
                    <div class="lap-time-item">
                        <div class="lap-time-label">GAIN/LOSS</div>
                        <div class="lap-time-value gain-loss" id="dashboard-gain-loss">0.000</div>
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;

        // Render channel grid - always show cards with formatted values
        if (gridContainer) {
            gridContainer.style.display = 'grid';
            gridContainer.style.visibility = 'visible';
            gridContainer.innerHTML = channelsToShow.map(ch => {
                // Format initial value based on channel type
                let initialValue = '0';
                if (ch.type === 'temp' || ch.type === 'pressure') {
                    initialValue = '0.0';
                } else if (ch.type === 'percentage') {
                    initialValue = '0%';
                } else if (ch.type === 'speed') {
                    initialValue = '0.0';
                }
                
                return `
                    <div class="channel-card" data-channel="${this.escapeHtml(ch.name)}">
                        <div class="channel-card-header">
                            <span class="channel-card-label">${this.escapeHtml(ch.name)}</span>
                            <span class="channel-card-unit">${this.escapeHtml(ch.unit)}</span>
                        </div>
                        <div class="channel-card-value" id="grid-channel-${this.escapeHtml(ch.name)}">${initialValue}</div>
                    </div>
                `;
            }).join('');
        }
        
        console.log('MoTeC Dashboard rendered:', channelsToShow.length, 'channels');

        // Initialize RPM gauge if enabled
        if (this.displayConfig.showRpmGauge) {
            this.initRpmGauge();
        }
    }

    initRpmGauge() {
        const canvas = document.getElementById('rpm-gauge-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 80;

        // Draw gauge background
        ctx.strokeStyle = '#333333';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 0);
        ctx.stroke();

        // Draw RPM scale
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.font = '10px monospace';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';

        for (let i = 0; i <= 6; i++) {
            const angle = Math.PI - (Math.PI / 6) * i;
            const x1 = centerX + Math.cos(angle) * radius;
            const y1 = centerY - Math.sin(angle) * radius;
            const x2 = centerX + Math.cos(angle) * (radius + 10);
            const y2 = centerY - Math.sin(angle) * (radius + 10);

            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();

            // Label
            const labelX = centerX + Math.cos(angle) * (radius + 20);
            const labelY = centerY - Math.sin(angle) * (radius + 20);
            ctx.fillText(i.toString(), labelX, labelY + 3);
        }

        // Label
        ctx.font = 'bold 12px monospace';
        ctx.fillText('RPMx1000', centerX, centerY + 10);
    }

    updateRpmGauge(rpm) {
        const canvas = document.getElementById('rpm-gauge-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 80;

        // Clear previous needle
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        this.initRpmGauge();

        // Draw needle
        const rpmNormalized = Math.min(6, Math.max(0, rpm / 1000));
        const angle = Math.PI - (Math.PI / 6) * rpmNormalized;
        const needleLength = radius - 10;

        ctx.strokeStyle = '#FFB81C'; // Yellow/orange needle
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(
            centerX + Math.cos(angle) * needleLength,
            centerY - Math.sin(angle) * needleLength
        );
        ctx.stroke();
    }

    startDataUpdates() {
        // Clear existing interval
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        // Update from telemetry data (if available via WebSocket)
        // For now, simulate updates - in production this would come from actual telemetry
        this.updateInterval = setInterval(() => {
            this.updateChannelValues();
        }, 100); // Update 10 times per second
    }

    updateChannelValues() {
        // Update channel values from telemetry data
        if (window.telemetryData) {
            const data = window.telemetryData;
            
            // Update each channel using internal key mapping
            Object.keys(this.channelValues).forEach(chName => {
                const channel = this.channelValues[chName];
                const internalKey = channel.internal;
                
                if (internalKey && data[internalKey] !== undefined) {
                    channel.value = data[internalKey];
                    this.updateChannelDisplay(chName, data[internalKey], channel);
                } else {
                    // Try direct mapping if internal key doesn't exist
                    const directKey = chName.toLowerCase().replace(/\s+/g, '_');
                    if (data[directKey] !== undefined) {
                        channel.value = data[directKey];
                        this.updateChannelDisplay(chName, data[directKey], channel);
                    }
                }
            });

            // Update RPM gauge
            if (this.displayConfig.showRpmGauge && data.rpm !== undefined) {
                this.updateRpmGauge(data.rpm);
            }

            // Update lap times
            if (this.displayConfig.showLapTimes) {
                if (data.lap_time) {
                    const lapEl = document.getElementById('dashboard-running-lap');
                    if (lapEl) lapEl.textContent = data.lap_time;
                }
                
                // Update reference lap if available
                if (data.reference_lap) {
                    const refEl = document.getElementById('dashboard-ref-lap');
                    if (refEl) refEl.textContent = data.reference_lap;
                }
                
                // Calculate gain/loss if both available
                if (data.lap_time && data.reference_lap) {
                    const gainLoss = this.calculateGainLoss(data.lap_time, data.reference_lap);
                    const gainEl = document.getElementById('dashboard-gain-loss');
                    if (gainEl) {
                        gainEl.textContent = gainLoss >= 0 ? `+${gainLoss.toFixed(3)}` : gainLoss.toFixed(3);
                        gainEl.className = 'lap-time-value gain-loss ' + (gainLoss < 0 ? 'positive' : 'negative');
                    }
                }
            }
        }
    }

    calculateGainLoss(runningLap, referenceLap) {
        // Convert lap time strings (M:SS.mmm) to seconds
        const runningSec = this.lapTimeToSeconds(runningLap);
        const referenceSec = this.lapTimeToSeconds(referenceLap);
        return runningSec - referenceSec; // Positive = slower (loss), Negative = faster (gain)
    }

    lapTimeToSeconds(lapTime) {
        // Convert "M:SS.mmm" to seconds
        const parts = lapTime.split(':');
        if (parts.length === 2) {
            const minutes = parseInt(parts[0]) || 0;
            const secondsParts = parts[1].split('.');
            const seconds = parseInt(secondsParts[0]) || 0;
            const milliseconds = parseInt(secondsParts[1]) || 0;
            return minutes * 60 + seconds + milliseconds / 1000;
        }
        return 0;
    }

    updateChannelDisplay(channelName, value, channel) {
        if (!channel) {
            channel = this.channelValues[channelName];
        }
        if (!channel) return;

        const formattedValue = this.formatChannelValue(value, channel.unit);
        const valueClass = this.getValueClass(value, channel);
        
        // Update main display
        const mainEl = document.getElementById(`channel-${channelName}`);
        if (mainEl) {
            mainEl.textContent = `${formattedValue} ${channel.unit}`;
            mainEl.className = 'channel-value ' + valueClass;
        }

        // Update grid display
        const gridEl = document.getElementById(`grid-channel-${channelName}`);
        if (gridEl) {
            gridEl.textContent = formattedValue;
            gridEl.className = 'channel-card-value ' + valueClass;
        }
    }

    formatChannelValue(value, unit) {
        if (value === null || value === undefined) return '0';
        
        if (unit === '°F' || unit === '°C') {
            return Math.round(value).toString();
        }
        if (unit === 'psi' || unit === 'bar') {
            return Math.round(value).toString();
        }
        if (unit === '%') {
            return Math.round(value).toString();
        }
        if (unit === 'mph' || unit === 'km/h') {
            return value.toFixed(1);
        }
        if (unit === 'rpm') {
            return Math.round(value).toLocaleString();
        }
        
        return value.toFixed(2);
    }

    getValueClass(value, channel) {
        if (!channel) return '';
        
        // Determine if value should be warning/danger based on channel type
        const type = channel.type || '';
        
        if (type === 'temp') {
            if (value > 250) return 'danger';
            if (value > 200) return 'warning';
        }
        if (type === 'pressure') {
            if (value < 20) return 'danger';
            if (value < 40) return 'warning';
        }
        if (type === 'percentage') {
            if (value > 95) return 'warning';
        }
        if (type === 'gforce') {
            if (Math.abs(value) > 3) return 'warning';
            if (Math.abs(value) > 4) return 'danger';
        }
        
        return '';
    }

    showConfigModal() {
        const modal = document.getElementById('motec-modal-overlay');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');

        if (!modal || !title || !body) return;

        title.textContent = 'Configure Dashboard Display';
        body.innerHTML = this.getConfigModalHTML();
        modal.style.display = 'flex';

        // Setup form handlers
        this.setupConfigForm();
    }

    getConfigModalHTML() {
        const channels = this.defaultChannels;
        
        return `
            <form id="dashboard-config-form" class="config-form">
                <div class="form-group">
                    <label>Layout</label>
                    <select id="config-layout" name="layout">
                        <option value="standard" ${this.displayConfig.layout === 'standard' ? 'selected' : ''}>Standard</option>
                        <option value="compact" ${this.displayConfig.layout === 'compact' ? 'selected' : ''}>Compact</option>
                        <option value="custom" ${this.displayConfig.layout === 'custom' ? 'selected' : ''}>Custom</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" id="config-show-gear" ${this.displayConfig.showGear ? 'checked' : ''}>
                        Show Gear Display
                    </label>
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" id="config-show-rpm" ${this.displayConfig.showRpmGauge ? 'checked' : ''}>
                        Show RPM Gauge
                    </label>
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" id="config-show-lap-times" ${this.displayConfig.showLapTimes ? 'checked' : ''}>
                        Show Lap Times
                    </label>
                </div>

                <div class="form-group">
                    <label>Channels to Display</label>
                    <p style="font-size: 0.85rem; color: var(--text-dim); margin-bottom: 8px;">
                        Select which telemetry channels to display
                    </p>
                    <div style="max-height: 300px; overflow-y: auto; border: 1px solid var(--border); padding: 10px; border-radius: 4px;">
                        ${channels.map((ch) => `
                            <label style="display: block; padding: 5px 0;">
                                <input type="checkbox" name="channels" value="${this.escapeHtml(ch.name)}" 
                                       ${this.displayConfig.channels.length === 0 || this.displayConfig.channels.includes(ch.name) ? 'checked' : ''}>
                                ${this.escapeHtml(ch.name)} (${this.escapeHtml(ch.unit)})
                            </label>
                        `).join('')}
                    </div>
                    <small>Select channels to display on dashboard. Leave all unchecked to show all channels.</small>
                </div>

                <div class="form-actions">
                    <button type="button" class="btn-primary" onclick="motecDashboard.applyConfig()">Apply</button>
                    <button type="button" class="btn-secondary" onclick="document.getElementById('motec-modal-overlay').style.display='none'">Cancel</button>
                </div>
            </form>
        `;
    }

    setupConfigForm() {
        // Form is set up in getConfigModalHTML with onclick handlers
    }

    applyConfig() {
        const form = document.getElementById('dashboard-config-form');
        if (!form) return;

        // Get layout
        this.displayConfig.layout = document.getElementById('config-layout')?.value || 'standard';

        // Get checkboxes
        this.displayConfig.showGear = document.getElementById('config-show-gear')?.checked || false;
        this.displayConfig.showRpmGauge = document.getElementById('config-show-rpm')?.checked || false;
        this.displayConfig.showLapTimes = document.getElementById('config-show-lap-times')?.checked || false;

        // Get selected channels
        const channelCheckboxes = form.querySelectorAll('input[name="channels"]:checked');
        this.displayConfig.channels = Array.from(channelCheckboxes).map(cb => cb.value);

        // Re-render dashboard
        this.renderDashboard();

        // Show save button
        const saveBtn = document.getElementById('save-dashboard-config-btn');
        if (saveBtn) {
            saveBtn.style.display = 'inline-block';
        }

        // Close modal
        document.getElementById('motec-modal-overlay').style.display = 'none';
        this.showToast('Configuration applied', 'success');
    }

    saveDashboardConfig() {
        // Save configuration to localStorage or backend
        try {
            localStorage.setItem('motec_dashboard_config', JSON.stringify(this.displayConfig));
            this.showToast('Configuration saved', 'success');
        } catch (e) {
            console.error('Error saving config:', e);
            this.showToast('Error saving configuration', 'error');
        }
    }

    loadDashboardConfig() {
        try {
            const saved = localStorage.getItem('motec_dashboard_config');
            if (saved) {
                this.displayConfig = { ...this.displayConfig, ...JSON.parse(saved) };
            }
        } catch (e) {
            console.error('Error loading config:', e);
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            'success': '✅',
            'error': '❌',
            'info': 'ℹ️',
            'warning': '⚠️'
        };
        
        toast.textContent = `${icons[type] || ''} ${message}`;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        const duration = type === 'error' ? 6000 : 4000;
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize MoTeC Dashboard when DOM is ready
let motecDashboard;
document.addEventListener('DOMContentLoaded', () => {
    // Always initialize - dashboard will render when section is shown
    motecDashboard = new MotecDashboard();
    window.motecDashboard = motecDashboard; // Make available globally
});

