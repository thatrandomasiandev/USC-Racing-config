// USC Racing Trackside Telemetry Display
class TracksideTelemetry {
    constructor() {
        this.ws = null;
        this.updateCount = 0;
        this.lastUpdateTime = Date.now();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.currentHistogramScenario = 'straight';
        this.histogramCanvases = {};
        
        // Manual lap timer
        this.lapTimerRunning = false;
        this.lapTimerStartTime = null;
        this.lapTimerPausedTime = 0; // Accumulated paused time
        this.lapTimerInterval = null;
        this.manualLapTime = false; // Whether to use manual timer or telemetry data
        this.lapTimes = []; // Array of recorded lap times
        this.lapTimesGraphCanvas = null;
        this.lapTimesGraphCtx = null;
        
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.initializeHistograms();
        this.startHistogramUpdates();
        this.setupLapTimerControls();
        this.setupGlobalNavigation();
    }

    setupGlobalNavigation() {
        // Handle navigation for all sections
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.showSection(section);
            });
        });
    }

    showSection(section) {
        // Hide all sections
        document.querySelectorAll('.section-content').forEach(sec => {
            sec.style.display = 'none';
        });

        // Show selected section
        const targetSection = document.getElementById(section);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        // Update nav active state
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.section === section) {
                link.classList.add('active');
            }
        });
        
        // If MoTeC Dashboard section is shown, ensure it's rendered
        if (section === 'motec-dashboard' && window.motecDashboard) {
            // Re-render dashboard to ensure it's visible
            window.motecDashboard.renderDashboard();
            const gridContainer = document.getElementById('channel-values-grid');
            if (gridContainer) {
                gridContainer.style.display = 'grid';
            }
        }
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus(true);
                this.reconnectAttempts = 0;
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.updateDisplay(data);
                    this.updateRate();
                } catch (e) {
                    console.error('Error parsing telemetry data:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
        } catch (e) {
            console.error('Failed to connect WebSocket:', e);
            this.updateConnectionStatus(false);
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
            setTimeout(() => this.connectWebSocket(), delay);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.textContent = connected ? 'Connected' : 'Disconnected';
            statusEl.className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
        }
    }

    updateRate() {
        this.updateCount++;
        const now = Date.now();
        const elapsed = (now - this.lastUpdateTime) / 1000;
        
        if (elapsed >= 1) {
            const rate = Math.round(this.updateCount / elapsed);
            const rateEl = document.getElementById('update-rate');
            if (rateEl) {
                rateEl.textContent = `${rate} Hz`;
            }
            this.updateCount = 0;
            this.lastUpdateTime = now;
        }
    }

    updateDisplay(data) {
        // Store data globally for MoTeC dashboard access
        window.telemetryData = data;

        // Primary metrics
        this.updateMetric('speed', data.speed?.toFixed(1) || '0');
        this.updateMetric('rpm', Math.round(data.rpm || 0).toLocaleString());
        
        // Lap time: use manual timer if running, otherwise use telemetry data
        if (!this.manualLapTime) {
            this.updateMetric('lap-time', data.lap_time || '0:00.000');
        }
        
        // Secondary metrics
        this.updateMetric('throttle', Math.round(data.throttle || 0));
        this.updateMetric('brake', Math.round(data.brake || 0));
        this.updateMetric('oil-temp', Math.round(data.oil_temp || 0));
        this.updateMetric('water-temp', Math.round(data.water_temp || 0));
        this.updateMetric('oil-pressure', Math.round(data.oil_pressure || 0));
        this.updateMetric('fuel-level', Math.round(data.fuel_level || 0));
        this.updateMetric('g-lat', (data.g_force_lat || 0).toFixed(2));
        this.updateMetric('g-long', (data.g_force_long || 0).toFixed(2));
        
        // Info
        this.updateMetric('lap-number', data.lap_number || 0);
        this.updateMetric('sector-time', data.sector_time || '0:00.000');
        this.updateMetric('position', data.position || 0);
        
        // Progress bars
        this.updateBar('throttle-bar', data.throttle || 0);
        this.updateBar('brake-bar', data.brake || 0);
        this.updateBar('fuel-bar', data.fuel_level || 0);
        
        // Aero data
        this.updateAeroData(data);
    }
    
    updateAeroData(data) {
        // Pressure ports (1-8)
        for (let i = 1; i <= 8; i++) {
            const pressure = data[`pressure_port_${i}`];
            if (pressure !== undefined) {
                this.updateMetric(`pressure-port-${i}`, (pressure || 0).toFixed(2));
            }
        }
        
        // Coefficients (Cp for ports 1-6)
        for (let i = 1; i <= 6; i++) {
            const cp = data[`cp_port_${i}`];
            if (cp !== undefined) {
                this.updateMetric(`cp-port-${i}`, (cp || 0).toFixed(3));
            }
        }
        
        // Scenario indicator
        const scenario = data.aero_scenario || 'straight';
        const scenarioEl = document.getElementById('aero-scenario');
        if (scenarioEl) {
            scenarioEl.textContent = this.formatScenario(scenario);
            scenarioEl.className = `scenario-indicator ${scenario}`;
        }
        
        // Scenario averages
        const averages = data.aero_averages || {};
        this.updateScenarioAverages(averages);
    }
    
    formatScenario(scenario) {
        const scenarios = {
            'straight': 'Straight',
            'turn_left': 'Turn Left',
            'turn_right': 'Turn Right'
        };
        return scenarios[scenario] || scenario;
    }
    
    updateScenarioAverages(averages) {
        const scenarios = ['straight', 'turn_left', 'turn_right'];
        
        scenarios.forEach(scenario => {
            const scenarioData = averages[scenario];
            const listEl = document.getElementById(`avg-${scenario}-list`);
            
            if (!listEl) return;
            
            if (!scenarioData || Object.keys(scenarioData).length === 0) {
                listEl.innerHTML = '<div style="color: #666; font-style: italic;">No data</div>';
                return;
            }
            
            let html = '';
            for (let i = 1; i <= 6; i++) {
                const avgKey = `cp_port_${i}_avg`;
                const countKey = `cp_port_${i}_count`;
                
                if (scenarioData[avgKey] !== undefined) {
                    const avg = scenarioData[avgKey].toFixed(3);
                    const stdKey = `cp_port_${i}_std`;
                    const std = scenarioData[stdKey] !== undefined ? scenarioData[stdKey].toFixed(3) : '0.000';
                    const count = scenarioData[countKey] || 0;
                    html += `
                        <div class="avg-item">
                            <span class="avg-label">Port ${i}:</span>
                            <span class="avg-value">${avg} ± ${std} (n=${count})</span>
                        </div>
                    `;
                }
            }
            
            listEl.innerHTML = html || '<div style="color: #666;">No data</div>';
        });
    }

    updateMetric(id, value) {
        const el = document.getElementById(id);
        if (el && el.textContent !== String(value)) {
            el.textContent = value;
            el.classList.add('updated');
            setTimeout(() => el.classList.remove('updated'), 300);
        }
    }

    updateBar(id, value) {
        const el = document.getElementById(id);
        if (el) {
            el.style.width = `${Math.min(100, Math.max(0, value))}%`;
        }
    }

    setupEventListeners() {
        // Handle page visibility
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Page is hidden, could pause updates
            } else {
                // Page is visible, ensure connection
                if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                    this.connectWebSocket();
                }
            }
        });

        // Make telemetry data available globally for MoTeC dashboard
        // This will be updated in updateDisplay()
        window.telemetryData = {};
        
        // Reset aero averages button
        const resetBtn = document.getElementById('reset-aero-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetAeroAverages());
        }
        
        // Histogram scenario selector
        document.querySelectorAll('.hist-scenario-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.hist-scenario-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentHistogramScenario = btn.dataset.scenario;
                this.updateHistograms();
            });
        });
    }

    setupLapTimerControls() {
        const startBtn = document.getElementById('lap-time-start');
        const stopBtn = document.getElementById('lap-time-stop');
        const lapBtn = document.getElementById('lap-time-lap');
        const resetBtn = document.getElementById('lap-time-reset');

        if (startBtn) {
            startBtn.addEventListener('click', () => this.startOrResumeLapTimer());
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopLapTimer());
        }

        if (lapBtn) {
            lapBtn.addEventListener('click', () => this.recordLap());
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetLapTimer());
        }

        // Initialize graph canvas
        const graphCanvas = document.getElementById('lap-times-graph');
        if (graphCanvas) {
            this.lapTimesGraphCanvas = graphCanvas;
            this.lapTimesGraphCtx = graphCanvas.getContext('2d');
        }

        // Keyboard shortcuts for trackside use
        document.addEventListener('keydown', (e) => {
            // Space bar to start/stop (when not typing in input)
            if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                if (this.lapTimerRunning) {
                    this.stopLapTimer();
                } else {
                    this.startOrResumeLapTimer();
                }
            }
            // L key for lap
            if (e.code === 'KeyL' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                if (this.lapTimerRunning) {
                    this.recordLap();
                }
            }
            // R key to reset
            if (e.code === 'KeyR' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                this.resetLapTimer();
            }
        });
    }

    startOrResumeLapTimer() {
        if (this.lapTimerRunning) return;

        this.lapTimerRunning = true;
        this.manualLapTime = true;

        // If resuming, adjust start time to account for paused time
        const now = Date.now();
        if (this.lapTimerStartTime === null) {
            // First start
            this.lapTimerStartTime = now;
            this.lapTimerPausedTime = 0;
        } else {
            // Resuming - adjust start time to account for pause
            const pauseDuration = now - (this.lapTimerStartTime + this.lapTimerPausedTime);
            this.lapTimerPausedTime += pauseDuration;
        }

        const startBtn = document.getElementById('lap-time-start');
        const stopBtn = document.getElementById('lap-time-stop');
        const lapBtn = document.getElementById('lap-time-lap');

        if (startBtn) {
            startBtn.disabled = true;
            startBtn.textContent = 'Running';
        }
        if (stopBtn) stopBtn.disabled = false;
        if (lapBtn) lapBtn.disabled = false;

        // Update timer every 10ms for smooth display
        this.lapTimerInterval = setInterval(() => {
            this.updateLapTimerDisplay();
        }, 10);
    }

    stopLapTimer() {
        if (!this.lapTimerRunning) return;

        this.lapTimerRunning = false;

        const startBtn = document.getElementById('lap-time-start');
        const stopBtn = document.getElementById('lap-time-stop');
        const lapBtn = document.getElementById('lap-time-lap');

        if (startBtn) {
            startBtn.disabled = false;
            startBtn.textContent = 'Resume';
        }
        if (stopBtn) stopBtn.disabled = true;
        if (lapBtn) lapBtn.disabled = true;

        if (this.lapTimerInterval) {
            clearInterval(this.lapTimerInterval);
            this.lapTimerInterval = null;
        }

        // Final update
        this.updateLapTimerDisplay();
    }

    recordLap() {
        if (!this.lapTimerRunning) return;

        const currentTime = this.getCurrentLapTime();
        const lapNumber = this.lapTimes.length + 1;
        
        this.lapTimes.push({
            lap: lapNumber,
            time: currentTime,
            timestamp: Date.now()
        });

        // Show graph container if hidden
        const graphContainer = document.getElementById('lap-times-graph-container');
        if (graphContainer) {
            graphContainer.style.display = 'block';
        }

        // Update graph and list
        this.updateLapTimesGraph();
        this.updateLapTimesList();

        // Flash the lap time display briefly
        const lapTimeEl = document.getElementById('lap-time');
        if (lapTimeEl) {
            lapTimeEl.style.color = 'var(--success)';
            setTimeout(() => {
                lapTimeEl.style.color = '';
            }, 500);
        }
    }

    resetLapTimer() {
        const wasRunning = this.lapTimerRunning;
        
        if (wasRunning) {
            this.stopLapTimer();
        }

        this.lapTimerStartTime = null;
        this.lapTimerPausedTime = 0;
        this.manualLapTime = false;
        this.lapTimes = [];
        this.updateMetric('lap-time', '0:00.000');

        const startBtn = document.getElementById('lap-time-start');
        const stopBtn = document.getElementById('lap-time-stop');
        const lapBtn = document.getElementById('lap-time-lap');
        const graphContainer = document.getElementById('lap-times-graph-container');

        if (startBtn) {
            startBtn.disabled = false;
            startBtn.textContent = 'Start';
        }
        if (stopBtn) stopBtn.disabled = true;
        if (lapBtn) lapBtn.disabled = true;
        if (graphContainer) {
            graphContainer.style.display = 'none';
        }

        // Clear graph
        if (this.lapTimesGraphCtx) {
            this.lapTimesGraphCtx.clearRect(0, 0, this.lapTimesGraphCanvas.width, this.lapTimesGraphCanvas.height);
        }
        
        const lapTimesList = document.getElementById('lap-times-list');
        if (lapTimesList) {
            lapTimesList.innerHTML = '';
        }
    }

    getCurrentLapTime() {
        if (!this.lapTimerStartTime) return 0;
        const now = Date.now();
        const elapsed = now - this.lapTimerStartTime - this.lapTimerPausedTime;
        return Math.max(0, elapsed);
    }

    updateLapTimerDisplay() {
        if (!this.lapTimerStartTime) return;

        const elapsed = this.getCurrentLapTime();
        const formatted = this.formatLapTime(elapsed);
        this.updateMetric('lap-time', formatted);
    }

    formatLapTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        const ms = Math.floor((milliseconds % 1000) / 10); // Show centiseconds (00-99)

        return `${minutes}:${seconds.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
    }

    updateLapTimesGraph() {
        if (!this.lapTimesGraphCtx || this.lapTimes.length === 0) return;

        const canvas = this.lapTimesGraphCanvas;
        const ctx = this.lapTimesGraphCtx;
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        const graphWidth = width - padding * 2;
        const graphHeight = height - padding * 2;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        if (this.lapTimes.length === 0) return;

        // Find min/max times for scaling
        const times = this.lapTimes.map(l => l.time);
        const minTime = Math.min(...times);
        const maxTime = Math.max(...times);
        const timeRange = maxTime - minTime || 1000; // Avoid division by zero

        // Draw axes
        ctx.strokeStyle = '#333333'; // --border color
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();

        // Draw grid lines
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = padding + (graphHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }

        // Draw lap times line
        ctx.strokeStyle = '#990000'; // --primary-color
        ctx.lineWidth = 2;
        ctx.beginPath();

        this.lapTimes.forEach((lapData, index) => {
            const x = padding + (graphWidth / (this.lapTimes.length - 1 || 1)) * index;
            const normalizedTime = (lapData.time - minTime) / timeRange;
            const y = height - padding - (normalizedTime * graphHeight);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();

        // Draw points
        ctx.fillStyle = '#FFB81C'; // --secondary-color
        this.lapTimes.forEach((lapData, index) => {
            const x = padding + (graphWidth / (this.lapTimes.length - 1 || 1)) * index;
            const normalizedTime = (lapData.time - minTime) / timeRange;
            const y = height - padding - (normalizedTime * graphHeight);
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
        });

        // Draw labels
        ctx.fillStyle = '#aaaaaa'; // --text-dim
        ctx.font = '10px monospace';
        ctx.textAlign = 'center';
        
        // X-axis labels (lap numbers)
        this.lapTimes.forEach((lapData, index) => {
            const x = padding + (graphWidth / (this.lapTimes.length - 1 || 1)) * index;
            ctx.fillText(`L${lapData.lap}`, x, height - padding + 15);
        });

        // Y-axis labels (times)
        ctx.textAlign = 'right';
        for (let i = 0; i <= 5; i++) {
            const y = padding + (graphHeight / 5) * i;
            const timeValue = maxTime - (timeRange / 5) * i;
            ctx.fillText(this.formatLapTime(timeValue), padding - 5, y + 3);
        }

        // Title
        ctx.fillStyle = '#ffffff'; // --text-light
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Lap Times', width / 2, 15);
    }

    updateLapTimesList() {
        const listEl = document.getElementById('lap-times-list');
        if (!listEl) return;

        if (this.lapTimes.length === 0) {
            listEl.innerHTML = '';
            return;
        }

        // Find fastest and slowest laps
        const times = this.lapTimes.map(l => l.time);
        const fastestTime = Math.min(...times);
        const slowestTime = Math.max(...times);

        listEl.innerHTML = this.lapTimes.map(lapData => {
            const isFastest = lapData.time === fastestTime;
            const isSlowest = lapData.time === slowestTime && fastestTime !== slowestTime;
            const style = isFastest ? 'color: var(--success); font-weight: bold;' : 
                          isSlowest ? 'color: var(--danger);' : '';
            
            return `<div style="${style} padding: 2px 0;">
                Lap ${lapData.lap}: ${this.formatLapTime(lapData.time)}
                ${isFastest ? ' ⭐' : ''}
            </div>`;
        }).join('');
    }
    
    initializeHistograms() {
        const container = document.getElementById('histograms-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        for (let port = 1; port <= 6; port++) {
            const card = document.createElement('div');
            card.className = 'histogram-card';
            card.innerHTML = `
                <div class="histogram-title">CP${port} (ratio)</div>
                <div class="histogram-stats">
                    <span id="hist-mean-${port}">Mean: --</span>
                    <span id="hist-std-${port}">Std: --</span>
                </div>
                <div class="histogram-canvas-container">
                    <canvas class="histogram-canvas" id="hist-canvas-${port}" width="300" height="200"></canvas>
                </div>
                <div class="histogram-samples" id="hist-samples-${port}">0 Samples</div>
            `;
            container.appendChild(card);
            
            const canvas = document.getElementById(`hist-canvas-${port}`);
            if (canvas) {
                this.histogramCanvases[port] = canvas.getContext('2d');
            }
        }
    }
    
    async updateHistograms() {
        try {
            const response = await fetch(`/api/aero/histograms?scenario=${this.currentHistogramScenario}`);
            if (!response.ok) return;
            
            const data = await response.json();
            const scenarioData = data[this.currentHistogramScenario];
            
            if (!scenarioData) return;
            
            // Also get averages for mean/std display
            const avgResponse = await fetch('/api/aero/averages');
            const averages = await avgResponse.ok ? await avgResponse.json() : {};
            const scenarioAverages = averages[this.currentHistogramScenario] || {};
            
            for (let port = 1; port <= 6; port++) {
                const portKey = `port_${port}`;
                const histData = scenarioData[portKey];
                
                if (histData && histData.bins && histData.bins.length > 0) {
                    this.drawHistogram(port, histData);
                    
                    // Update stats
                    const avgKey = `cp_port_${port}_avg`;
                    const stdKey = `cp_port_${port}_std`;
                    const meanEl = document.getElementById(`hist-mean-${port}`);
                    const stdEl = document.getElementById(`hist-std-${port}`);
                    const samplesEl = document.getElementById(`hist-samples-${port}`);
                    
                    if (meanEl && scenarioAverages[avgKey] !== undefined) {
                        meanEl.textContent = `Mean: ${scenarioAverages[avgKey].toFixed(3)}`;
                    }
                    if (stdEl && scenarioAverages[stdKey] !== undefined) {
                        stdEl.textContent = `Std: ${scenarioAverages[stdKey].toFixed(3)}`;
                    }
                    if (samplesEl) {
                        samplesEl.textContent = `${histData.total_samples} Samples`;
                    }
                }
            }
        } catch (e) {
            console.error('Error updating histograms:', e);
        }
    }
    
    drawHistogram(port, histData) {
        const ctx = this.histogramCanvases[port];
        if (!ctx) return;
        
        const canvas = ctx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        // Clear canvas
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, width, height);
        
        if (!histData.bins || histData.bins.length === 0) return;
        
        const bins = histData.bins;
        const percentages = histData.percentages;
        const maxPercent = Math.max(...percentages, 1);
        
        // Draw axes
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();
        
        // Draw grid lines
        ctx.strokeStyle = '#222';
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // Draw bars
        const barWidth = chartWidth / bins.length;
        ctx.fillStyle = '#990000';
        
        bins.forEach((bin, i) => {
            const barHeight = (percentages[i] / maxPercent) * chartHeight;
            const x = padding + i * barWidth;
            const y = height - padding - barHeight;
            
            ctx.fillRect(x, y, barWidth - 1, barHeight);
        });
        
        // Draw labels
        ctx.fillStyle = '#aaa';
        ctx.font = '10px monospace';
        ctx.textAlign = 'center';
        
        // X-axis labels
        const range = histData.range || [-3, 3];
        for (let i = 0; i <= 4; i++) {
            const value = range[0] + (range[1] - range[0]) * (i / 4);
            const x = padding + (chartWidth / 4) * i;
            ctx.fillText(value.toFixed(1), x, height - padding + 15);
        }
        
        // Y-axis labels
        ctx.textAlign = 'right';
        for (let i = 0; i <= 5; i++) {
            const value = (maxPercent / 5) * (5 - i);
            const y = padding + (chartHeight / 5) * i;
            ctx.fillText(value.toFixed(0) + '%', padding - 5, y + 3);
        }
    }
    
    async startHistogramUpdates() {
        // Get update interval from config
        let updateInterval = 2000; // default 2 seconds
        try {
            const configResponse = await fetch('/api/config');
            if (configResponse.ok) {
                const config = await configResponse.json();
                if (config.aero && config.aero.histogram_update_interval_ms) {
                    updateInterval = config.aero.histogram_update_interval_ms;
                }
            }
        } catch (e) {
            console.warn('Could not fetch config, using default interval');
        }
        
        // Update histograms at configured interval
        setInterval(() => {
            this.updateHistograms();
        }, updateInterval);
        
        // Initial update
        setTimeout(() => this.updateHistograms(), 1000);
    }
    
    async resetAeroAverages() {
        try {
            const response = await fetch('/api/aero/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (response.ok) {
                console.log('Aero averages reset');
                // Clear display
                ['straight', 'turn_left', 'turn_right'].forEach(scenario => {
                    const listEl = document.getElementById(`avg-${scenario}-list`);
                    if (listEl) {
                        listEl.innerHTML = '<div style="color: #666; font-style: italic;">No data</div>';
                    }
                });
            }
        } catch (e) {
            console.error('Failed to reset aero averages:', e);
        }
    }
}

// Section Navigation Handler
function setupSectionNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            
            // Hide all sections
            document.querySelectorAll('.section-content').forEach(sec => {
                sec.style.display = 'none';
            });
            
            // Show selected section
            const targetSection = document.getElementById(section);
            if (targetSection) {
                targetSection.style.display = 'block';
            }
            
            // Update nav active state
            document.querySelectorAll('.nav-link').forEach(l => {
                l.classList.remove('active');
            });
            link.classList.add('active');
        });
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.telemetry = new TracksideTelemetry();
    setupSectionNavigation();
});
