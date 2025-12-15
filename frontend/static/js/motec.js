// MoTeC Configuration UI Manager
class MotecConfigUI {
    constructor() {
        this.currentCarId = null;
        this.cars = [];
        this.channels = [];
        this.ldFiles = [];
        this.currentLdxFile = null;
        this.currentLdxPath = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStatus();
        this.loadGlobalConfig();
        this.loadCars();
        this.setupNavigation();
        this.loadNasStatus();
        this.startAutoRefresh();
    }

    setupNavigation() {
        // Handle section navigation
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
    }

    setupEventListeners() {
        // Global settings form
        const globalForm = document.getElementById('motec-global-form');
        if (globalForm) {
            globalForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveGlobalConfig();
            });
        }

        // Car management
        const addCarBtn = document.getElementById('add-car-btn');
        if (addCarBtn) {
            addCarBtn.addEventListener('click', () => this.showAddCarModal());
        }

        // Channel management
        const carSelect = document.getElementById('motec-car-select');
        if (carSelect) {
            carSelect.addEventListener('change', (e) => {
                this.currentCarId = e.target.value;
                this.loadChannels(this.currentCarId);
            });
        }

        const addChannelBtn = document.getElementById('add-channel-btn');
        if (addChannelBtn) {
            addChannelBtn.addEventListener('click', () => this.showAddChannelModal());
        }

        const syncChannelsToLdxBtn = document.getElementById('sync-channels-to-ldx-btn');
        if (syncChannelsToLdxBtn) {
            syncChannelsToLdxBtn.addEventListener('click', () => this.syncChannelsToLdx());
        }

        const syncCarToLdxBtn = document.getElementById('sync-car-to-ldx-btn');
        if (syncCarToLdxBtn) {
            syncCarToLdxBtn.addEventListener('click', () => this.syncCarProfileToLdx());
        }

        // LD file operations
        const scanBtn = document.getElementById('scan-ld-files-btn');
        if (scanBtn) {
            scanBtn.addEventListener('click', () => this.scanLdFiles());
        }

        const discoverBtn = document.getElementById('discover-sessions-btn');
        if (discoverBtn) {
            discoverBtn.addEventListener('click', () => this.discoverSessions());
        }
        
        // NAS rescan
        const rescanNasBtn = document.getElementById('rescan-nas-btn');
        if (rescanNasBtn) {
            rescanNasBtn.addEventListener('click', () => this.rescanNas());
        }

        // LDX file operations
        const loadLdxBtn = document.getElementById('load-ldx-btn');
        if (loadLdxBtn) {
            loadLdxBtn.addEventListener('click', () => this.loadLdxFile());
        }

        const scanLdxBtn = document.getElementById('scan-ldx-files-btn');
        if (scanLdxBtn) {
            scanLdxBtn.addEventListener('click', () => this.scanLdxFiles());
        }

        const saveLdxBtn = document.getElementById('save-ldx-btn');
        if (saveLdxBtn) {
            saveLdxBtn.addEventListener('click', () => this.saveLdxFile());
        }

        const reloadLdxBtn = document.getElementById('reload-ldx-btn');
        if (reloadLdxBtn) {
            reloadLdxBtn.addEventListener('click', () => this.reloadLdxFile());
        }

        const addLdxChannelBtn = document.getElementById('add-ldx-channel-btn');
        if (addLdxChannelBtn) {
            addLdxChannelBtn.addEventListener('click', () => this.showAddLdxChannelModal());
        }

        // LDX file path input - allow Enter key
        const ldxPathInput = document.getElementById('ldx-file-path-input');
        if (ldxPathInput) {
            ldxPathInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.loadLdxFile();
                }
            });
        }

        // Recommendations
        const analyzeBtn = document.getElementById('analyze-recommendations-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeRecommendations());
        }

        const applyBtn = document.getElementById('apply-recommendations-btn');
        if (applyBtn) {
            applyBtn.addEventListener('click', () => this.applyRecommendations());
        }

        const recCarSelect = document.getElementById('recommendations-car-select');
        if (recCarSelect) {
            recCarSelect.addEventListener('change', (e) => {
                // Update car select when cars are loaded
            });
        }

        // File selection for dashboard
        const scanAllFilesBtn = document.getElementById('scan-all-files-btn');
        if (scanAllFilesBtn) {
            scanAllFilesBtn.addEventListener('click', () => this.scanAllFilesForDashboard());
        }

        const loadSelectedBtn = document.getElementById('load-selected-to-dashboard-btn');
        if (loadSelectedBtn) {
            loadSelectedBtn.addEventListener('click', () => this.loadSelectedFilesToDashboard());
        }

        // Modal close
        const modalClose = document.getElementById('modal-close-btn');
        const modalOverlay = document.getElementById('motec-modal-overlay');
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                modalOverlay.style.display = 'none';
            });
        }
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    modalOverlay.style.display = 'none';
                }
            });
        }
    }

    async loadStatus() {
        try {
            const response = await fetch('/api/motec/status');
            const data = await response.json();
            
            const badge = document.getElementById('motec-status-badge');
            const details = document.getElementById('motec-status-details');
            
            if (badge) {
                // Trackside requirement: Clear status with icon
                const statusText = data.enabled ? '✅ Enabled' : '❌ Disabled';
                badge.textContent = statusText;
                badge.className = `status-badge ${data.enabled ? 'enabled' : 'disabled'}`;
            }
            
            if (details) {
                // Trackside requirement: Simple, scannable status
                details.innerHTML = `
                    <div class="status-item">
                        <span class="status-label">LD Files:</span>
                        <span class="status-value">${data.ld_files_found || 0}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Cars:</span>
                        <span class="status-value">${data.cars_configured || 0}</span>
                    </div>
                    ${data.reason ? `
                    <div class="status-item">
                        <span class="status-label">Status:</span>
                        <span class="status-value" style="color: var(--warning);">${data.reason}</span>
                    </div>
                    ` : ''}
                `;
            }
        } catch (e) {
            console.error('Error loading MoTeC status:', e);
            // Trackside requirement: Show error in UI, don't fail silently
            const details = document.getElementById('motec-status-details');
            if (details) {
                details.innerHTML = `
                    <div class="status-item" style="color: var(--danger);">
                        ⚠️ Could not load status. Check server connection.
                    </div>
                `;
            }
        }
    }
    
    async loadNasStatus() {
        try {
            const response = await fetch('/api/motec/nas/status');
            const data = await response.json();
            
            // Update NAS status in UI if element exists
            const nasStatusEl = document.getElementById('nas-status-display');
            if (nasStatusEl) {
                if (data.nas && data.nas.connected) {
                    nasStatusEl.innerHTML = `
                        <div class="status-item">
                            <span class="status-label">NAS:</span>
                            <span class="status-value" style="color: var(--success);">✅ ${data.nas.path}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">LD Files:</span>
                            <span class="status-value">${data.ld_files_count || 0}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">LDX Files:</span>
                            <span class="status-value">${data.ldx_files_count || 0}</span>
                        </div>
                    `;
                } else {
                    nasStatusEl.innerHTML = `
                        <div class="status-item">
                            <span class="status-label">NAS:</span>
                            <span class="status-value" style="color: var(--danger);">❌ ${data.nas?.error || 'Not connected'}</span>
                        </div>
                    `;
                }
            }
            
            // Auto-populate LD files if enabled
            if (data.auto_populate_enabled) {
                this.loadNasFiles();
            }
        } catch (e) {
            console.error('Error loading NAS status:', e);
        }
    }
    
    async loadNasFiles() {
        try {
            const response = await fetch('/api/motec/nas/files');
            const data = await response.json();
            
            if (data.ld_files && data.ld_files.length > 0) {
                // Auto-populate LD files section
                this.ldFiles = data.ld_files;
                this.renderLdFiles();
            }
        } catch (e) {
            console.error('Error loading NAS files:', e);
        }
    }
    
    startAutoRefresh() {
        // Auto-refresh NAS status every 30 seconds (non-blocking)
        setInterval(() => {
            this.loadNasStatus();
        }, 30000);
    }

    async loadGlobalConfig() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            if (config.motec) {
                const motec = config.motec;
                
                // Populate form
                const enabled = document.getElementById('motec-enabled');
                if (enabled) enabled.checked = motec.enabled;
                
                const nasPath = document.getElementById('motec-nas-path');
                if (nasPath) nasPath.value = motec.nas_base_path || '';
                
                const ldPattern = document.getElementById('motec-ld-pattern');
                if (ldPattern) ldPattern.value = motec.ld_glob_pattern || '*.ld';
                
                const autoLdx = document.getElementById('motec-auto-ldx');
                if (autoLdx) autoLdx.checked = motec.auto_generate_ldx || false;
                
                const overwritePolicy = document.getElementById('motec-overwrite-policy');
                if (overwritePolicy) overwritePolicy.value = motec.overwrite_policy || 'ifSafe';
            }
        } catch (e) {
            console.error('Error loading global config:', e);
        }
    }

    async saveGlobalConfig() {
        const form = document.getElementById('motec-global-form');
        const formData = new FormData(form);
        
        // Trackside safety: Validate before submitting
        const nasPath = formData.get('nas_base_path');
        if (nasPath && !nasPath.startsWith('/') && !nasPath.match(/^[A-Z]:/)) {
            this.showToast('NAS path must be absolute (start with / or drive letter)', 'error');
            return;
        }
        
        const config = {
            enabled: formData.get('enabled') === 'on',
            nas_base_path: nasPath || '',
            ld_glob_pattern: formData.get('ld_glob_pattern') || '*.ld',
            auto_generate_ldx: formData.get('auto_generate_ldx') === 'on',
            overwrite_policy: formData.get('overwrite_policy') || 'ifSafe'
        };

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        try {
            const response = await fetch('/api/motec/config', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showToast('Settings saved successfully', 'success');
                this.loadStatus();
            } else {
                this.showToast(`Error: ${result.error || result.message || 'Failed to save'}`, 'error');
            }
        } catch (e) {
            console.error('Error saving config:', e);
            this.showToast('Network error: Could not save settings. Check connection.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    async loadCars() {
        try {
            const response = await fetch('/api/motec/cars');
            const data = await response.json();
            
            this.cars = data.cars || [];
            this.renderCarsTable();
            this.updateCarSelect();
        } catch (e) {
            console.error('Error loading cars:', e);
        }
    }

    renderCarsTable() {
        const tbody = document.getElementById('cars-table-body');
        if (!tbody) return;

        if (this.cars.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No cars configured</td></tr>';
            return;
        }

        tbody.innerHTML = this.cars.map(car => `
            <tr>
                <td>${car.car_id}</td>
                <td>${car.profile?.name || '-'}</td>
                <td>${car.profile?.class || '-'}</td>
                <td>${car.channel_count || 0}</td>
                <td>
                    <button class="btn-small" onclick="motecUI.editCar('${car.car_id}')">Edit</button>
                    <button class="btn-small btn-danger" onclick="motecUI.deleteCar('${car.car_id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    }

    updateCarSelect() {
        const select = document.getElementById('motec-car-select');
        if (!select) return;

        select.innerHTML = '<option value="">Select a car...</option>' +
            this.cars.map(car => 
                `<option value="${car.car_id}">${car.car_id}${car.profile?.name ? ' - ' + car.profile.name : ''}</option>`
            ).join('');

        // Also update recommendations car select
        const recSelect = document.getElementById('recommendations-car-select');
        if (recSelect) {
            recSelect.innerHTML = '<option value="">Select a car...</option>' +
                this.cars.map(car => 
                    `<option value="${car.car_id}">${car.car_id}${car.profile?.name ? ' - ' + car.profile.name : ''}</option>`
                ).join('');
        }
    }

    async loadChannels(carId) {
        if (!carId) {
            const tbody = document.getElementById('channels-table-body');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="6">Select a car to view mappings</td></tr>';
            }
            return;
        }

        try {
            const response = await fetch(`/api/motec/channels/${carId}`);
            const data = await response.json();
            
            this.channels = data.channels || [];
            this.renderChannelsTable();
        } catch (e) {
            console.error('Error loading channels:', e);
        }
    }

    renderChannelsTable() {
        const tbody = document.getElementById('channels-table-body');
        if (!tbody) return;

        if (this.channels.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No channel mappings</td></tr>';
            return;
        }

        tbody.innerHTML = this.channels.map((ch, idx) => `
            <tr>
                <td>${ch.internal_name}</td>
                <td>${ch.motec_name}</td>
                <td>${ch.units}</td>
                <td>${ch.source}</td>
                <td>${ch.enabled ? '✓' : '✗'}</td>
                <td>
                    <button class="btn-small" onclick="motecUI.editChannel(${idx})">Edit</button>
                    <button class="btn-small btn-danger" onclick="motecUI.deleteChannel('${ch.internal_name}')">Delete</button>
                </td>
            </tr>
        `).join('');
    }

    showAddCarModal() {
        this.showModal('Add Car Profile', this.getCarFormHTML());
        const form = document.getElementById('car-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveCar();
            });
        }
    }

    getCarFormHTML(car = null) {
        return `
            <form id="car-form" class="config-form">
                <div class="form-group">
                    <label for="car-id">Car ID *</label>
                    <input type="text" id="car-id" name="car_id" value="${car?.car_id || ''}" required>
                </div>
                <div class="form-group">
                    <label for="car-name">Name</label>
                    <input type="text" id="car-name" name="name" value="${car?.profile?.name || ''}">
                </div>
                <div class="form-group">
                    <label for="car-class">Class</label>
                    <input type="text" id="car-class" name="class" value="${car?.profile?.class || ''}">
                </div>
                <div class="form-group">
                    <label for="car-year">Year</label>
                    <input type="number" id="car-year" name="year" value="${car?.profile?.year || ''}">
                </div>
                <div class="form-group">
                    <label for="car-default-track">Default Track</label>
                    <input type="text" id="car-default-track" name="default_track" value="${car?.profile?.default_track || ''}">
                </div>
                <div class="form-group">
                    <label for="car-default-driver">Default Driver</label>
                    <input type="text" id="car-default-driver" name="default_driver" value="${car?.profile?.default_driver || ''}">
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-primary">Save</button>
                    <button type="button" class="btn-secondary" onclick="document.getElementById('motec-modal-overlay').style.display='none'">Cancel</button>
                </div>
            </form>
        `;
    }

    async saveCar() {
        const form = document.getElementById('car-form');
        const formData = new FormData(form);
        
        const carId = formData.get('car_id');
        const profile = {
            name: formData.get('name') || '',
            class: formData.get('class') || '',
            year: formData.get('year') ? parseInt(formData.get('year')) : null,
            default_track: formData.get('default_track') || '',
            default_driver: formData.get('default_driver') || ''
        };

        try {
            const response = await fetch(`/api/motec/cars/${carId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profile)
            });

            if (response.ok) {
                this.showToast('Car profile saved', 'success');
                document.getElementById('motec-modal-overlay').style.display = 'none';
                this.loadCars();
            } else {
                const error = await response.json();
                this.showToast(`Error: ${error.error || 'Failed to save'}`, 'error');
            }
        } catch (e) {
            console.error('Error saving car:', e);
            this.showToast('Error saving car profile', 'error');
        }
    }

    editCar(carId) {
        const car = this.cars.find(c => c.car_id === carId);
        this.showModal('Edit Car Profile', this.getCarFormHTML(car));
        const form = document.getElementById('car-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveCar();
            });
        }
    }

    async deleteCar(carId) {
        if (!confirm(`Delete car profile for ${carId}?`)) return;

        try {
            const response = await fetch(`/api/motec/cars/${carId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Car profile deleted', 'success');
                this.loadCars();
            } else {
                this.showToast('Error deleting car', 'error');
            }
        } catch (e) {
            console.error('Error deleting car:', e);
            this.showToast('Error deleting car', 'error');
        }
    }

    showAddChannelModal() {
        if (!this.currentCarId) {
            this.showToast('Please select a car first', 'error');
            return;
        }
        this.showModal('Add Channel Mapping', this.getChannelFormHTML());
        const form = document.getElementById('channel-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveChannel();
            });
        }
    }

    getChannelFormHTML(channel = null) {
        return `
            <form id="channel-form" class="config-form">
                <div class="form-group">
                    <label for="channel-internal">Internal Name *</label>
                    <input type="text" id="channel-internal" name="internal_name" 
                           value="${channel?.internal_name || ''}" required>
                </div>
                <div class="form-group">
                    <label for="channel-motec">MoTeC Name *</label>
                    <input type="text" id="channel-motec" name="motec_name" 
                           value="${channel?.motec_name || ''}" required>
                </div>
                <div class="form-group">
                    <label for="channel-units">Units *</label>
                    <input type="text" id="channel-units" name="units" 
                           value="${channel?.units || ''}" required>
                </div>
                <div class="form-group">
                    <label for="channel-source">Source *</label>
                    <select id="channel-source" name="source" required>
                        <option value="CAN" ${channel?.source === 'CAN' ? 'selected' : ''}>CAN</option>
                        <option value="analog" ${channel?.source === 'analog' ? 'selected' : ''}>Analog</option>
                        <option value="digital" ${channel?.source === 'digital' ? 'selected' : ''}>Digital</option>
                        <option value="derived" ${channel?.source === 'derived' ? 'selected' : ''}>Derived</option>
                        <option value="calculated" ${channel?.source === 'calculated' ? 'selected' : ''}>Calculated</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="channel-math">Math Expression</label>
                    <textarea id="channel-math" name="math_expression" rows="3" 
                              placeholder="e.g., (A - B) / (C - D)">${channel?.math_expression || ''}</textarea>
                    <small>Required for calculated channels</small>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="channel-enabled" name="enabled" 
                               ${channel?.enabled !== false ? 'checked' : ''}>
                        Enabled
                    </label>
                </div>
                <div class="form-group">
                    <label for="channel-description">Description</label>
                    <input type="text" id="channel-description" name="description" 
                           value="${channel?.description || ''}">
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-primary">Save</button>
                    <button type="button" class="btn-secondary" onclick="document.getElementById('motec-modal-overlay').style.display='none'">Cancel</button>
                </div>
            </form>
        `;
    }

    async saveChannel() {
        if (!this.currentCarId) return;

        const form = document.getElementById('channel-form');
        const formData = new FormData(form);
        
        const channel = {
            internal_name: formData.get('internal_name'),
            motec_name: formData.get('motec_name'),
            units: formData.get('units'),
            source: formData.get('source'),
            math_expression: formData.get('math_expression') || null,
            enabled: formData.get('enabled') === 'on',
            description: formData.get('description') || null
        };

        try {
            // Get existing channels
            const response = await fetch(`/api/motec/channels/${this.currentCarId}`);
            const data = await response.json();
            const channels = data.channels || [];
            
            // Update or add channel
            const existingIdx = channels.findIndex(ch => ch.internal_name === channel.internal_name);
            if (existingIdx >= 0) {
                channels[existingIdx] = channel;
            } else {
                channels.push(channel);
            }

            // Save all channels
            const saveResponse = await fetch(`/api/motec/channels/${this.currentCarId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(channels)
            });

            if (saveResponse.ok) {
                this.showToast('Channel mapping saved', 'success');
                document.getElementById('motec-modal-overlay').style.display = 'none';
                this.loadChannels(this.currentCarId);
            } else {
                const error = await saveResponse.json();
                this.showToast(`Error: ${error.error || 'Failed to save'}`, 'error');
            }
        } catch (e) {
            console.error('Error saving channel:', e);
            this.showToast('Error saving channel mapping', 'error');
        }
    }

    editChannel(idx) {
        const channel = this.channels[idx];
        this.showModal('Edit Channel Mapping', this.getChannelFormHTML(channel));
        const form = document.getElementById('channel-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveChannel();
            });
        }
    }

    async deleteChannel(internalName) {
        if (!this.currentCarId) return;
        if (!confirm(`Delete channel mapping for ${internalName}?`)) return;

        try {
            const response = await fetch(`/api/motec/channels/${this.currentCarId}`, {
                method: 'GET'
            });
            const data = await response.json();
            const channels = data.channels.filter(ch => ch.internal_name !== internalName);

            const saveResponse = await fetch(`/api/motec/channels/${this.currentCarId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(channels)
            });

            if (saveResponse.ok) {
                this.showToast('Channel mapping deleted', 'success');
                this.loadChannels(this.currentCarId);
            } else {
                this.showToast('Error deleting channel', 'error');
            }
        } catch (e) {
            console.error('Error deleting channel:', e);
            this.showToast('Error deleting channel', 'error');
        }
    }

    async scanLdFiles() {
        const btn = document.getElementById('scan-ld-files-btn');
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = 'Scanning...';
        
        try {
            // Use NAS discovery if available, otherwise fall back to direct scan
            const nasResponse = await fetch('/api/motec/nas/files');
            if (nasResponse.ok) {
                const nasData = await nasResponse.json();
                if (nasData.ld_files && nasData.ld_files.length > 0) {
                    this.ldFiles = nasData.ld_files;
                    this.renderLdFiles();
                    this.showToast(`Found ${this.ldFiles.length} LD files from NAS`, 'success');
                    return;
                }
            }
            
            // Fallback to direct scan
            const response = await fetch('/api/motec/ld/files');
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Scan failed');
            }
            
            this.ldFiles = data.files || [];
            this.renderLdFiles();
            
            const validCount = this.ldFiles.filter(f => f.valid).length;
            const invalidCount = this.ldFiles.length - validCount;
            
            if (invalidCount > 0) {
                this.showToast(`Found ${validCount} valid, ${invalidCount} invalid LD files`, 'info');
            } else {
                this.showToast(`Found ${this.ldFiles.length} LD files`, 'success');
            }
        } catch (e) {
            console.error('Error scanning LD files:', e);
            this.showToast(`Error: ${e.message || 'Could not scan LD files. Check NAS connection.'}`, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }
    
    async rescanNas() {
        const btn = document.getElementById('rescan-nas-btn');
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = 'Scanning...';
        
        try {
            const response = await fetch('/api/motec/nas/scan?force=true', { method: 'POST' });
            const data = await response.json();
            
            if (response.ok) {
                this.showToast(data.message || 'NAS scan completed', 'success');
                this.loadNasStatus();
                this.loadNasFiles();
                
                // Notify dashboard to refresh file list
                if (window.motecDashboard) {
                    window.motecDashboard.scanFilesForDashboard();
                }
            } else {
                this.showToast(`Scan error: ${data.error || 'Unknown error'}`, 'error');
            }
        } catch (e) {
            console.error('Error rescanning NAS:', e);
            this.showToast('Error rescanning NAS. Check connection.', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }

    async scanAllFilesForDashboard() {
        const btn = document.getElementById('scan-all-files-btn');
        const originalText = btn?.textContent;
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Scanning...';
        }

        try {
            // Trigger NAS scan
            const scanResponse = await fetch('/api/motec/nas/scan?force=true', { method: 'POST' });
            const scanData = await scanResponse.json();

            // Get files
            const filesResponse = await fetch('/api/motec/nas/files');
            const filesData = await filesResponse.json();

            if (filesResponse.ok) {
                this.displayFileSelection(filesData);
                this.showToast(`Found ${(filesData.ldx_files || []).length} LDX files, ${(filesData.ld_files || []).length} LD files`, 'success');
            } else {
                this.showToast('Error scanning files', 'error');
            }
        } catch (e) {
            console.error('Error scanning files:', e);
            this.showToast(`Error: ${e.message || 'Could not scan files'}`, 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        }
    }

    displayFileSelection(filesData) {
        const container = document.getElementById('file-selection-container');
        if (!container) return;

        const ldxFiles = filesData.ldx_files || [];
        const ldFiles = filesData.ld_files || [];
        const allFiles = [...ldxFiles, ...ldFiles];

        if (allFiles.length === 0) {
            container.innerHTML = '<p style="color: var(--text-dim);">No files found. Check NAS connection.</p>';
            return;
        }

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px;">
                ${allFiles.map(file => {
                    const isLdx = file.path.toLowerCase().endsWith('.ldx');
                    const fileName = file.name || file.path.split('/').pop();
                    return `
                        <div class="file-selection-card" style="border: 1px solid var(--border); padding: 15px; border-radius: 4px; cursor: pointer; background: var(--card-bg);"
                             onclick="motecUI.selectFileForDashboard('${this.escapeHtml(file.path)}', ${isLdx})">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                                <div>
                                    <strong>${this.escapeHtml(fileName)}</strong>
                                    <span style="margin-left: 8px; padding: 2px 6px; background: ${isLdx ? 'var(--primary-color)' : 'var(--secondary-color)'}; border-radius: 3px; font-size: 0.8rem;">
                                        ${isLdx ? 'LDX' : 'LD'}
                                    </span>
                                </div>
                                <input type="checkbox" class="file-checkbox" data-file-path="${this.escapeHtml(file.path)}" 
                                       onclick="event.stopPropagation(); motecUI.toggleFileSelection('${this.escapeHtml(file.path)}')">
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-dim);">
                                <div>Path: ${this.escapeHtml(file.path)}</div>
                                ${file.modified ? `<div>Modified: ${new Date(file.modified).toLocaleString()}</div>` : ''}
                                ${file.size ? `<div>Size: ${(file.size / 1024).toFixed(2)} KB</div>` : ''}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        // Show load button if files available
        const loadBtn = document.getElementById('load-selected-to-dashboard-btn');
        if (loadBtn) {
            loadBtn.style.display = 'inline-block';
        }
    }

    selectedFiles = new Set();

    toggleFileSelection(filePath) {
        if (this.selectedFiles.has(filePath)) {
            this.selectedFiles.delete(filePath);
        } else {
            this.selectedFiles.add(filePath);
        }
    }

    selectFileForDashboard(filePath, isLdx) {
        // Direct selection - load immediately
        if (window.motecDashboard) {
            if (isLdx) {
                window.motecDashboard.loadLdxToDashboard(filePath);
            } else {
                window.motecDashboard.loadLdToDashboard(filePath);
            }
        }
    }

    async loadSelectedFilesToDashboard() {
        if (this.selectedFiles.size === 0) {
            this.showToast('Please select at least one file', 'error');
            return;
        }

        // For now, load the first selected file
        // Could be extended to load multiple files
        const firstFile = Array.from(this.selectedFiles)[0];
        const isLdx = firstFile.toLowerCase().endsWith('.ldx');

        if (window.motecDashboard) {
            if (isLdx) {
                await window.motecDashboard.loadLdxToDashboard(firstFile);
            } else {
                await window.motecDashboard.loadLdToDashboard(firstFile);
            }
            this.showToast('File loaded to dashboard', 'success');
        }
    }

    renderLdFiles() {
        const container = document.getElementById('ld-files-container');
        if (!container) return;

        if (this.ldFiles.length === 0) {
            container.innerHTML = '<p>No LD files found. Click "Scan for LD Files" or wait for auto-discovery.</p>';
            return;
        }

        container.innerHTML = this.ldFiles.map(file => `
            <div class="ld-file-card">
                <div class="file-header">
                    <span class="file-name">${file.name || file.file_path.split('/').pop()}</span>
                    <span class="file-status ${file.valid !== false ? 'valid' : 'invalid'}">
                        ${file.valid !== false ? '✓ Valid' : '✗ Invalid'}
                    </span>
                </div>
                <div class="file-details">
                    <div>Size: ${file.size ? (file.size / 1024).toFixed(2) + ' KB' : 'Unknown'}</div>
                    <div>Modified: ${file.modified ? new Date(file.modified).toLocaleString() : 'Unknown'}</div>
                    ${file.suggested_session ? `
                    <div class="suggestion">
                        💡 Suggested session: <strong>${file.suggested_session}</strong>
                        <button class="btn-small" onclick="motecUI.attachLdToSession('${file.file_path}', '${file.suggested_session}')">Attach</button>
                    </div>
                    ` : ''}
                    ${file.suggested_car ? `
                    <div class="suggestion">
                        💡 Suggested car: <strong>${file.suggested_car}</strong>
                    </div>
                    ` : ''}
                    ${file.error ? `<div class="error">❌ ${file.error}</div>` : ''}
                </div>
            </div>
        `).join('');
    }
    
    async attachLdToSession(ldFilePath, sessionId) {
        // Trackside safety: Confirm before attaching
        if (!confirm(`Attach LD file to session "${sessionId}"?`)) {
            return;
        }
        
        try {
            const response = await fetch('/api/motec/sessions/link', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ld_file_path: ldFilePath,
                    car_id: sessionId.split('_')[0] || 'default',
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showToast('LD file attached to session', 'success');
                this.scanLdFiles(); // Refresh
            } else {
                this.showToast(`Error: ${data.error || data.message || 'Failed to attach'}`, 'error');
            }
        } catch (e) {
            console.error('Error attaching LD file:', e);
            this.showToast('Error attaching LD file', 'error');
        }
    }

    async discoverSessions() {
        // Trackside safety: Confirm before batch operation
        if (!confirm('Discover and link all LD files to sessions? This may generate LDX files.')) {
            return;
        }
        
        const btn = document.getElementById('discover-sessions-btn');
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = 'Discovering...';
        
        try {
            const response = await fetch('/api/motec/sessions/discover');
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Discovery failed');
            }
            
            const count = data.count || 0;
            if (count > 0) {
                this.showToast(`Discovered ${count} sessions`, 'success');
            } else {
                this.showToast('No new sessions discovered', 'info');
            }
            
            this.scanLdFiles(); // Refresh LD files list
        } catch (e) {
            console.error('Error discovering sessions:', e);
            this.showToast(`Error: ${e.message || 'Could not discover sessions'}`, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }

    showModal(title, content) {
        const overlay = document.getElementById('motec-modal-overlay');
        const titleEl = document.getElementById('modal-title');
        const bodyEl = document.getElementById('modal-body');
        
        if (titleEl) titleEl.textContent = title;
        if (bodyEl) bodyEl.innerHTML = content;
        if (overlay) overlay.style.display = 'flex';
    }

    showToast(message, type = 'info') {
        // Simple, straightforward toast notification
        // Trackside requirement: Clear, visible, non-intrusive
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        // Add icon for quick visual recognition
        const icons = {
            'success': '✅',
            'error': '❌',
            'info': 'ℹ️',
            'warning': '⚠️'
        };
        
        toast.textContent = `${icons[type] || ''} ${message}`;
        document.body.appendChild(toast);
        
        // Show immediately
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Auto-dismiss after 4 seconds (longer for errors)
        const duration = type === 'error' ? 6000 : 4000;
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

    async loadLdxFile() {
        const pathInput = document.getElementById('ldx-file-path-input');
        const filePath = pathInput?.value.trim();
        
        if (!filePath) {
            this.showToast('Please enter an LDX file path', 'error');
            return;
        }

        const loadBtn = document.getElementById('load-ldx-btn');
        const originalText = loadBtn?.textContent;
        if (loadBtn) {
            loadBtn.disabled = true;
            loadBtn.textContent = 'Loading...';
        }

        try {
            // URL encode the file path
            const encodedPath = encodeURIComponent(filePath);
            const response = await fetch(`/api/motec/ldx/${encodedPath}`);
            const data = await response.json();

            if (data.error) {
                this.showToast(`Error loading LDX: ${data.error}`, 'error');
                return;
            }

            this.currentLdxFile = data;
            this.currentLdxPath = filePath;
            this.displayLdxFile(data);
            this.showToast('LDX file loaded successfully', 'success');
        } catch (e) {
            console.error('Error loading LDX file:', e);
            this.showToast(`Error: ${e.message || 'Could not load LDX file'}`, 'error');
        } finally {
            if (loadBtn) {
                loadBtn.disabled = false;
                loadBtn.textContent = originalText;
            }
        }
    }

    displayLdxFile(ldxData) {
        const container = document.getElementById('ldx-display-container');
        if (!container) return;

        container.style.display = 'block';

        // Display header info
        document.getElementById('ldx-workspace-name').textContent = `Workspace: ${ldxData.workspace_name || '-'}`;
        document.getElementById('ldx-project-name').textContent = ldxData.project_name || '-';
        document.getElementById('ldx-car-name').textContent = ldxData.car_name || '-';
        
        const modifiedTime = ldxData.modified ? new Date(ldxData.modified).toLocaleString() : '-';
        document.getElementById('ldx-modified-time').textContent = modifiedTime;

        // Display channels
        this.displayLdxChannels(ldxData.channels || []);

        // Display worksheets
        this.displayLdxWorksheets(ldxData.worksheets || []);

        // Display metadata
        this.displayLdxMetadata(ldxData.metadata || {});
    }

    displayLdxChannels(channels) {
        const tbody = document.getElementById('ldx-channels-tbody');
        if (!tbody) return;

        if (channels.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No channels configured</td></tr>';
            return;
        }

        tbody.innerHTML = channels.map((ch, idx) => `
            <tr data-channel-index="${idx}">
                <td>
                    <input type="text" class="ldx-channel-field" data-field="name" 
                           value="${this.escapeHtml(ch.name || '')}" 
                           style="width: 100%; border: none; background: transparent; padding: 4px;">
                </td>
                <td>
                    <input type="text" class="ldx-channel-field" data-field="units" 
                           value="${this.escapeHtml(ch.units || '')}" 
                           style="width: 100%; border: none; background: transparent; padding: 4px;">
                </td>
                <td>
                    <select class="ldx-channel-field" data-field="source" 
                            style="width: 100%; border: none; background: transparent; padding: 4px;">
                        <option value="CAN" ${ch.source === 'CAN' ? 'selected' : ''}>CAN</option>
                        <option value="analog" ${ch.source === 'analog' ? 'selected' : ''}>Analog</option>
                        <option value="digital" ${ch.source === 'digital' ? 'selected' : ''}>Digital</option>
                        <option value="derived" ${ch.source === 'derived' ? 'selected' : ''}>Derived</option>
                        <option value="calculated" ${ch.source === 'calculated' ? 'selected' : ''}>Calculated</option>
                    </select>
                </td>
                <td>
                    <input type="text" class="ldx-channel-field" data-field="scaling" 
                           value="${this.escapeHtml(ch.scaling || '')}" 
                           placeholder="e.g., 0.1" 
                           style="width: 100%; border: none; background: transparent; padding: 4px;">
                </td>
                <td>
                    <input type="text" class="ldx-channel-field" data-field="math" 
                           value="${this.escapeHtml(ch.math || '')}" 
                           placeholder="e.g., (A - B) / C" 
                           style="width: 100%; border: none; background: transparent; padding: 4px;">
                </td>
                <td>
                    <button class="btn-small btn-danger" onclick="motecUI.deleteLdxChannel(${idx})">Delete</button>
                </td>
            </tr>
        `).join('');

        // Add change listeners to mark as modified
        tbody.querySelectorAll('.ldx-channel-field').forEach(field => {
            field.addEventListener('change', () => {
                this.markLdxModified();
            });
        });
    }

    displayLdxWorksheets(worksheets) {
        const container = document.getElementById('ldx-worksheets-container');
        if (!container) return;

        if (worksheets.length === 0) {
            container.innerHTML = '<p>No worksheets configured</p>';
            return;
        }

        container.innerHTML = worksheets.map((ws, idx) => `
            <div class="worksheet-card" style="border: 1px solid var(--border); padding: 10px; margin: 10px 0; border-radius: 4px;">
                <h5>${this.escapeHtml(ws.name || 'Unnamed')}</h5>
                <div>Type: ${this.escapeHtml(ws.type || '-')}</div>
                <div>Channels: ${(ws.channels || []).join(', ') || 'None'}</div>
            </div>
        `).join('');
    }

    displayLdxMetadata(metadata) {
        const container = document.getElementById('ldx-metadata-container');
        if (!container) return;

        if (Object.keys(metadata).length === 0) {
            container.innerHTML = '<p>No metadata</p>';
            return;
        }

        container.innerHTML = Object.entries(metadata).map(([key, value]) => `
            <div class="metadata-item" style="display: flex; gap: 10px; margin: 5px 0;">
                <label style="min-width: 100px; font-weight: bold;">${this.escapeHtml(key)}:</label>
                <input type="text" class="ldx-metadata-field" data-key="${this.escapeHtml(key)}" 
                       value="${this.escapeHtml(String(value))}" 
                       style="flex: 1; border: 1px solid var(--border); padding: 4px; border-radius: 4px;">
            </div>
        `).join('');

        // Add change listeners
        container.querySelectorAll('.ldx-metadata-field').forEach(field => {
            field.addEventListener('change', () => {
                this.markLdxModified();
            });
        });
    }

    markLdxModified() {
        const saveBtn = document.getElementById('save-ldx-btn');
        if (saveBtn) {
            saveBtn.classList.add('modified');
            saveBtn.textContent = 'Save Changes *';
        }
    }

    async saveLdxFile() {
        if (!this.currentLdxFile || !this.currentLdxPath) {
            this.showToast('No LDX file loaded', 'error');
            return;
        }

        // Collect channel data from table
        const channels = [];
        const tbody = document.getElementById('ldx-channels-tbody');
        if (tbody) {
            tbody.querySelectorAll('tr[data-channel-index]').forEach(row => {
                const idx = parseInt(row.dataset.channelIndex);
                const nameField = row.querySelector('[data-field="name"]');
                const unitsField = row.querySelector('[data-field="units"]');
                const sourceField = row.querySelector('[data-field="source"]');
                const scalingField = row.querySelector('[data-field="scaling"]');
                const mathField = row.querySelector('[data-field="math"]');

                if (nameField && nameField.value.trim()) {
                    channels.push({
                        name: nameField.value.trim(),
                        units: unitsField?.value.trim() || '',
                        source: sourceField?.value || 'CAN',
                        scaling: scalingField?.value.trim() || null,
                        math: mathField?.value.trim() || null
                    });
                }
            });
        }

        // Collect metadata
        const metadata = {};
        const metadataContainer = document.getElementById('ldx-metadata-container');
        if (metadataContainer) {
            metadataContainer.querySelectorAll('.ldx-metadata-field').forEach(field => {
                const key = field.dataset.key;
                const value = field.value.trim();
                if (key && value) {
                    metadata[key] = value;
                }
            });
        }

        // Prepare LDX data
        const ldxData = {
            workspace_name: this.currentLdxFile.workspace_name,
            project_name: this.currentLdxFile.project_name,
            car_name: this.currentLdxFile.car_name,
            channels: channels,
            worksheets: this.currentLdxFile.worksheets || [],
            metadata: metadata
        };

        // Trackside safety: Confirm overwrite
        const overwrite = confirm('Save changes to LDX file? This will overwrite the existing file.');

        const saveBtn = document.getElementById('save-ldx-btn');
        const originalText = saveBtn?.textContent;
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
        }

        try {
            const encodedPath = encodeURIComponent(this.currentLdxPath);
            const response = await fetch(`/api/motec/ldx/${encodedPath}?overwrite=${overwrite}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ldxData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showToast('LDX file saved successfully', 'success');
                this.currentLdxFile = ldxData;
                if (saveBtn) {
                    saveBtn.classList.remove('modified');
                    saveBtn.textContent = 'Save Changes';
                }
            } else {
                if (result.requires_confirmation) {
                    this.showToast('File exists. Set overwrite=true to overwrite.', 'warning');
                } else {
                    this.showToast(`Error: ${result.error || 'Failed to save'}`, 'error');
                }
            }
        } catch (e) {
            console.error('Error saving LDX file:', e);
            this.showToast(`Error: ${e.message || 'Could not save LDX file'}`, 'error');
        } finally {
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.textContent = originalText;
            }
        }
    }

    async reloadLdxFile() {
        if (!this.currentLdxPath) {
            this.showToast('No file loaded', 'error');
            return;
        }
        await this.loadLdxFile();
    }

    async scanLdxFiles() {
        const btn = document.getElementById('scan-ldx-files-btn');
        const originalText = btn?.textContent;
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Scanning...';
        }

        try {
            // Scan for LDX files in configured directories
            const response = await fetch('/api/motec/nas/files');
            const data = await response.json();

            const ldxFiles = data.ldx_files || [];
            this.displayLdxFilesList(ldxFiles);

            this.showToast(`Found ${ldxFiles.length} LDX files`, 'success');
        } catch (e) {
            console.error('Error scanning LDX files:', e);
            this.showToast(`Error: ${e.message || 'Could not scan for LDX files'}`, 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        }
    }

    displayLdxFilesList(files) {
        const container = document.getElementById('ldx-files-list-container');
        if (!container) return;

        if (files.length === 0) {
            container.innerHTML = '<p>No LDX files found</p>';
            container.style.display = 'block';
            return;
        }

        container.innerHTML = files.map(file => `
            <div class="ldx-file-card" style="border: 1px solid var(--border); padding: 10px; margin: 10px 0; border-radius: 4px; cursor: pointer;"
                 onclick="motecUI.loadLdxFromList('${this.escapeHtml(file.path)}')">
                <div class="file-header">
                    <strong>${this.escapeHtml(file.name || file.path.split('/').pop())}</strong>
                </div>
                <div class="file-details" style="font-size: 0.9em; color: var(--text-secondary); margin-top: 5px;">
                    <div>Path: ${this.escapeHtml(file.path)}</div>
                    ${file.modified ? `<div>Modified: ${new Date(file.modified).toLocaleString()}</div>` : ''}
                </div>
            </div>
        `).join('');

        container.style.display = 'block';
    }

    loadLdxFromList(filePath) {
        const pathInput = document.getElementById('ldx-file-path-input');
        if (pathInput) {
            pathInput.value = filePath;
        }
        this.loadLdxFile();
    }

    deleteLdxChannel(idx) {
        if (!confirm('Delete this channel?')) return;

        const tbody = document.getElementById('ldx-channels-tbody');
        if (!tbody) return;

        const row = tbody.querySelector(`tr[data-channel-index="${idx}"]`);
        if (row) {
            row.remove();
            this.markLdxModified();
            
            // Re-index remaining rows
            tbody.querySelectorAll('tr[data-channel-index]').forEach((r, i) => {
                r.dataset.channelIndex = i;
            });
        }
    }

    showAddLdxChannelModal() {
        this.showModal('Add Channel to LDX', this.getLdxChannelFormHTML());
        const form = document.getElementById('ldx-channel-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addLdxChannel();
            });
        }
    }

    getLdxChannelFormHTML() {
        return `
            <form id="ldx-channel-form" class="config-form">
                <div class="form-group">
                    <label for="ldx-ch-name">Channel Name *</label>
                    <input type="text" id="ldx-ch-name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="ldx-ch-units">Units *</label>
                    <input type="text" id="ldx-ch-units" name="units" required>
                </div>
                <div class="form-group">
                    <label for="ldx-ch-source">Source *</label>
                    <select id="ldx-ch-source" name="source" required>
                        <option value="CAN">CAN</option>
                        <option value="analog">Analog</option>
                        <option value="digital">Digital</option>
                        <option value="derived">Derived</option>
                        <option value="calculated">Calculated</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="ldx-ch-scaling">Scaling</label>
                    <input type="text" id="ldx-ch-scaling" name="scaling" placeholder="e.g., 0.1">
                </div>
                <div class="form-group">
                    <label for="ldx-ch-math">Math Expression</label>
                    <textarea id="ldx-ch-math" name="math" rows="3" placeholder="e.g., (A - B) / (C - D)"></textarea>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-primary">Add Channel</button>
                    <button type="button" class="btn-secondary" onclick="document.getElementById('motec-modal-overlay').style.display='none'">Cancel</button>
                </div>
            </form>
        `;
    }

    addLdxChannel() {
        const form = document.getElementById('ldx-channel-form');
        const formData = new FormData(form);

        const channel = {
            name: formData.get('name'),
            units: formData.get('units'),
            source: formData.get('source'),
            scaling: formData.get('scaling') || null,
            math: formData.get('math') || null
        };

        // Add to current LDX file
        if (!this.currentLdxFile) {
            this.showToast('No LDX file loaded', 'error');
            return;
        }

        if (!this.currentLdxFile.channels) {
            this.currentLdxFile.channels = [];
        }

        this.currentLdxFile.channels.push(channel);
        this.displayLdxChannels(this.currentLdxFile.channels);
        this.markLdxModified();

        document.getElementById('motec-modal-overlay').style.display = 'none';
        this.showToast('Channel added', 'success');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async analyzeRecommendations() {
        const carSelect = document.getElementById('recommendations-car-select');
        const carId = carSelect?.value || 'default';

        const analyzeBtn = document.getElementById('analyze-recommendations-btn');
        const originalText = analyzeBtn?.textContent;
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
        }

        try {
            const response = await fetch(`/api/motec/recommendations/${carId}`);
            const data = await response.json();

            if (data.error) {
                this.showToast(`Error: ${data.error}`, 'error');
                return;
            }

            this.displayRecommendations(data);
            const applyBtn = document.getElementById('apply-recommendations-btn');
            if (applyBtn) {
                applyBtn.style.display = 'inline-block';
                applyBtn.dataset.carId = carId;
            }

            this.showToast(`Analysis complete. Confidence: ${data.confidence}`, 'success');
        } catch (e) {
            console.error('Error analyzing recommendations:', e);
            this.showToast(`Error: ${e.message || 'Could not analyze files'}`, 'error');
        } finally {
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = originalText;
            }
        }
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendations-container');
        const content = document.getElementById('recommendations-content');
        if (!container || !content) return;

        container.style.display = 'block';

        let html = `
            <div class="recommendations-header" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>Confidence Level:</strong> 
                        <span class="confidence-badge confidence-${recommendations.confidence}" 
                              style="padding: 4px 8px; border-radius: 4px; margin-left: 8px;">
                            ${recommendations.confidence.toUpperCase()}
                        </span>
                    </div>
                    <div style="font-size: 0.9rem; color: var(--text-dim);">
                        Analyzed ${recommendations.data_quality?.ld_files_count || 0} LD files, 
                        ${recommendations.data_quality?.ldx_files_count || 0} LDX files
                    </div>
                </div>
            </div>
        `;

        // Channel Mappings Recommendations
        if (recommendations.channel_mappings && recommendations.channel_mappings.length > 0) {
            html += `
                <div class="recommendation-section" style="margin-bottom: 20px;">
                    <h4 style="margin-bottom: 10px;">Recommended Channel Mappings</h4>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Internal</th>
                                    <th>MoTeC Name</th>
                                    <th>Units</th>
                                    <th>Source</th>
                                    <th>Confidence</th>
                                    <th>Reason</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${recommendations.channel_mappings.map(ch => `
                                    <tr>
                                        <td>${this.escapeHtml(ch.internal_name)}</td>
                                        <td>${this.escapeHtml(ch.motec_name)}</td>
                                        <td>${this.escapeHtml(ch.units)}</td>
                                        <td>${this.escapeHtml(ch.source)}</td>
                                        <td>
                                            <span class="confidence-badge confidence-${ch.confidence}">
                                                ${ch.confidence}
                                            </span>
                                        </td>
                                        <td style="font-size: 0.85rem; color: var(--text-dim);">
                                            ${this.escapeHtml(ch.reason || '')}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // Car Profile Recommendations
        if (recommendations.car_profile) {
            const profile = recommendations.car_profile;
            html += `
                <div class="recommendation-section" style="margin-bottom: 20px;">
                    <h4 style="margin-bottom: 10px;">Recommended Car Profile</h4>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                        <div><strong>Car ID:</strong> ${this.escapeHtml(profile.car_id || '')}</div>
                        <div><strong>Name:</strong> ${this.escapeHtml(profile.name || 'Not detected')}</div>
                        <div><strong>Class:</strong> ${this.escapeHtml(profile.class || 'Not detected')}</div>
                        <div><strong>Year:</strong> ${profile.year || 'Not detected'}</div>
                    </div>
                </div>
            `;
        }

        // Missing Channels
        if (recommendations.missing_channels && recommendations.missing_channels.length > 0) {
            html += `
                <div class="recommendation-section" style="margin-bottom: 20px;">
                    <h4 style="margin-bottom: 10px; color: var(--warning);">⚠️ Missing Channels</h4>
                    <p style="color: var(--text-dim); margin-bottom: 8px;">
                        These channels are recommended but not found in your LDX files:
                    </p>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${recommendations.missing_channels.map(ch => `
                            <span style="background: var(--card-bg); padding: 4px 8px; border-radius: 4px; border: 1px solid var(--warning);">
                                ${this.escapeHtml(ch)}
                            </span>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Data Quality
        if (recommendations.data_quality) {
            const quality = recommendations.data_quality;
            html += `
                <div class="recommendation-section" style="margin-bottom: 20px;">
                    <h4 style="margin-bottom: 10px;">Data Quality Assessment</h4>
                    <div style="margin-bottom: 10px;">
                        <strong>Quality Score:</strong> ${quality.score}/100
                        <div style="width: 200px; height: 20px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 4px; margin-top: 5px; overflow: hidden;">
                            <div style="width: ${quality.score}%; height: 100%; background: ${quality.score >= 70 ? 'var(--success)' : quality.score >= 40 ? 'var(--warning)' : 'var(--danger)'};"></div>
                        </div>
                    </div>
                    ${quality.issues && quality.issues.length > 0 ? `
                        <div style="color: var(--danger); margin-top: 10px;">
                            <strong>Issues:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                ${quality.issues.map(issue => `<li>${this.escapeHtml(issue)}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${quality.warnings && quality.warnings.length > 0 ? `
                        <div style="color: var(--warning); margin-top: 10px;">
                            <strong>Warnings:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                ${quality.warnings.map(warning => `<li>${this.escapeHtml(warning)}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        // Optimal Settings
        if (recommendations.optimal_settings) {
            const settings = recommendations.optimal_settings;
            html += `
                <div class="recommendation-section">
                    <h4 style="margin-bottom: 10px;">Optimal Settings</h4>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                        <div><strong>Auto-generate LDX:</strong> ${settings.auto_generate_ldx ? '✅ Recommended' : '❌ Not needed'}</div>
                        <div><strong>Overwrite Policy:</strong> ${settings.overwrite_policy}</div>
                        <div><strong>Update Rate:</strong> ${settings.suggested_update_rate} Hz</div>
                        <div><strong>Channels Found:</strong> ${settings.channel_count}</div>
                    </div>
                </div>
            `;
        }

        content.innerHTML = html;
    }

    async syncChannelsToLdx() {
        const carSelect = document.getElementById('motec-car-select');
        const carId = carSelect?.value;

        if (!carId) {
            this.showToast('Please select a car first', 'error');
            return;
        }

        // Prompt for LDX file path
        const ldxPath = prompt(`Enter LDX file path to sync channel mappings for car "${carId}":\n\n(Leave empty to use default path)`);
        if (ldxPath === null) return; // User cancelled

        try {
            // Get current channel mappings
            const mappingsResponse = await fetch(`/api/motec/channels/${carId}`);
            const mappingsData = await mappingsResponse.json();
            
            if (!mappingsResponse.ok) {
                throw new Error(mappingsData.error || 'Failed to get channel mappings');
            }

            // Get car profile
            const carResponse = await fetch(`/api/motec/cars/${carId}`);
            const carData = await carResponse.json();
            
            if (!carResponse.ok) {
                throw new Error(carData.error || 'Failed to get car profile');
            }

            // Load existing LDX or create new one
            let ldxData;
            if (ldxPath) {
                try {
                    const ldxResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(ldxPath)}`);
                    const ldxResponseData = await ldxResponse.json();
                    if (ldxResponse.ok) {
                        ldxData = ldxResponseData;
                    }
                } catch (e) {
                    // File doesn't exist, create new
                }
            }

            // Create/update LDX with channel mappings
            if (!ldxData) {
                ldxData = {
                    workspace_name: carData.profile?.name || carId,
                    project_name: carData.profile?.class || '',
                    car_name: carData.profile?.name || carId,
                    channels: [],
                    worksheets: [],
                    metadata: {}
                };
            }

            // Update channels from mappings
            ldxData.channels = mappingsData.mappings
                .filter(m => m.enabled)
                .map(m => ({
                    name: m.motec_name,
                    units: m.units || '',
                    source: m.source || 'CAN',
                    scaling: null,
                    math: null
                }));

            // Write LDX file
            const writePath = ldxPath || `${carId}_workspace.ldx`;
            const writeResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(writePath)}?overwrite=true`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ldxData)
            });

            const writeData = await writeResponse.json();
            
            if (writeResponse.ok) {
                this.showToast(`Channel mappings synced to LDX: ${writePath}`, 'success');
            } else {
                throw new Error(writeData.error || 'Failed to write LDX file');
            }
        } catch (e) {
            console.error('Error syncing channels to LDX:', e);
            this.showToast(`Error: ${e.message || 'Failed to sync to LDX'}`, 'error');
        }
    }

    async syncCarProfileToLdx() {
        const carSelect = document.getElementById('motec-car-select');
        const carId = carSelect?.value;

        if (!carId) {
            this.showToast('Please select a car first', 'error');
            return;
        }

        // Prompt for LDX file path
        const ldxPath = prompt(`Enter LDX file path to sync car profile for "${carId}":\n\n(Leave empty to use default path)`);
        if (ldxPath === null) return; // User cancelled

        try {
            // Get car profile
            const carResponse = await fetch(`/api/motec/cars/${carId}`);
            const carData = await carResponse.json();
            
            if (!carResponse.ok) {
                throw new Error(carData.error || 'Failed to get car profile');
            }

            const profile = carData.profile || {};

            // Load existing LDX or create new one
            let ldxData;
            if (ldxPath) {
                try {
                    const ldxResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(ldxPath)}`);
                    const ldxResponseData = await ldxResponse.json();
                    if (ldxResponse.ok) {
                        ldxData = ldxResponseData;
                    }
                } catch (e) {
                    // File doesn't exist, create new
                }
            }

            // Create/update LDX with car profile
            if (!ldxData) {
                ldxData = {
                    workspace_name: profile.name || carId,
                    project_name: profile.class || '',
                    car_name: profile.name || carId,
                    channels: [],
                    worksheets: [],
                    metadata: {}
                };
            } else {
                // Update existing LDX with car profile info
                ldxData.workspace_name = profile.name || ldxData.workspace_name || carId;
                ldxData.project_name = profile.class || ldxData.project_name || '';
                ldxData.car_name = profile.name || ldxData.car_name || carId;
            }

            // Write LDX file
            const writePath = ldxPath || `${carId}_workspace.ldx`;
            const writeResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(writePath)}?overwrite=true`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ldxData)
            });

            const writeData = await writeResponse.json();
            
            if (writeResponse.ok) {
                this.showToast(`Car profile synced to LDX: ${writePath}`, 'success');
            } else {
                throw new Error(writeData.error || 'Failed to write LDX file');
            }
        } catch (e) {
            console.error('Error syncing car profile to LDX:', e);
            this.showToast(`Error: ${e.message || 'Failed to sync to LDX'}`, 'error');
        }
    }

    async syncChannelsToLdx() {
        const carSelect = document.getElementById('motec-car-select');
        const carId = carSelect?.value;

        if (!carId) {
            this.showToast('Please select a car first', 'error');
            return;
        }

        // Prompt for LDX file path
        const ldxPath = prompt(`Enter LDX file path to sync channel mappings for car "${carId}":\n\n(Leave empty to use default path)`);
        if (ldxPath === null) return; // User cancelled

        try {
            // Get current channel mappings
            const mappingsResponse = await fetch(`/api/motec/channels/${carId}`);
            const mappingsData = await mappingsResponse.json();
            
            if (!mappingsResponse.ok) {
                throw new Error(mappingsData.error || 'Failed to get channel mappings');
            }

            // Get car profile
            const carResponse = await fetch(`/api/motec/cars/${carId}`);
            const carData = await carResponse.json();
            
            if (!carResponse.ok) {
                throw new Error(carData.error || 'Failed to get car profile');
            }

            // Load existing LDX or create new one
            let ldxData;
            if (ldxPath) {
                try {
                    const ldxResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(ldxPath)}`);
                    const ldxResponseData = await ldxResponse.json();
                    if (ldxResponse.ok) {
                        ldxData = ldxResponseData;
                    }
                } catch (e) {
                    // File doesn't exist, create new
                }
            }

            // Create/update LDX with channel mappings
            if (!ldxData) {
                ldxData = {
                    workspace_name: carData.profile?.name || carId,
                    project_name: carData.profile?.class || '',
                    car_name: carData.profile?.name || carId,
                    channels: [],
                    worksheets: [],
                    metadata: {}
                };
            }

            // Update channels from mappings
            ldxData.channels = mappingsData.mappings
                .filter(m => m.enabled)
                .map(m => ({
                    name: m.motec_name,
                    units: m.units || '',
                    source: m.source || 'CAN',
                    scaling: null,
                    math: null
                }));

            // Write LDX file
            const writePath = ldxPath || `${carId}_workspace.ldx`;
            const writeResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(writePath)}?overwrite=true`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ldxData)
            });

            const writeData = await writeResponse.json();
            
            if (writeResponse.ok) {
                this.showToast(`Channel mappings synced to LDX: ${writePath}`, 'success');
            } else {
                throw new Error(writeData.error || 'Failed to write LDX file');
            }
        } catch (e) {
            console.error('Error syncing channels to LDX:', e);
            this.showToast(`Error: ${e.message || 'Failed to sync to LDX'}`, 'error');
        }
    }

    async syncCarProfileToLdx() {
        const carSelect = document.getElementById('motec-car-select');
        const carId = carSelect?.value;

        if (!carId) {
            this.showToast('Please select a car first', 'error');
            return;
        }

        // Prompt for LDX file path
        const ldxPath = prompt(`Enter LDX file path to sync car profile for "${carId}":\n\n(Leave empty to use default path)`);
        if (ldxPath === null) return; // User cancelled

        try {
            // Get car profile
            const carResponse = await fetch(`/api/motec/cars/${carId}`);
            const carData = await carResponse.json();
            
            if (!carResponse.ok) {
                throw new Error(carData.error || 'Failed to get car profile');
            }

            const profile = carData.profile || {};

            // Load existing LDX or create new one
            let ldxData;
            if (ldxPath) {
                try {
                    const ldxResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(ldxPath)}`);
                    const ldxResponseData = await ldxResponse.json();
                    if (ldxResponse.ok) {
                        ldxData = ldxResponseData;
                    }
                } catch (e) {
                    // File doesn't exist, create new
                }
            }

            // Create/update LDX with car profile
            if (!ldxData) {
                ldxData = {
                    workspace_name: profile.name || carId,
                    project_name: profile.class || '',
                    car_name: profile.name || carId,
                    channels: [],
                    worksheets: [],
                    metadata: {}
                };
            } else {
                // Update existing LDX with car profile info
                ldxData.workspace_name = profile.name || ldxData.workspace_name || carId;
                ldxData.project_name = profile.class || ldxData.project_name || '';
                ldxData.car_name = profile.name || ldxData.car_name || carId;
            }

            // Write LDX file
            const writePath = ldxPath || `${carId}_workspace.ldx`;
            const writeResponse = await fetch(`/api/motec/ldx/${encodeURIComponent(writePath)}?overwrite=true`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ldxData)
            });

            const writeData = await writeResponse.json();
            
            if (writeResponse.ok) {
                this.showToast(`Car profile synced to LDX: ${writePath}`, 'success');
            } else {
                throw new Error(writeData.error || 'Failed to write LDX file');
            }
        } catch (e) {
            console.error('Error syncing car profile to LDX:', e);
            this.showToast(`Error: ${e.message || 'Failed to sync to LDX'}`, 'error');
        }
    }

    async applyRecommendations() {
        const applyBtn = document.getElementById('apply-recommendations-btn');
        const carId = applyBtn?.dataset.carId || 'default';

        if (!confirm(`Apply recommendations to car "${carId}"? This will update channel mappings and car profile.`)) {
            return;
        }

        const originalText = applyBtn?.textContent;
        if (applyBtn) {
            applyBtn.disabled = true;
            applyBtn.textContent = 'Applying...';
        }

        try {
            const response = await fetch(`/api/motec/recommendations/${carId}/apply?auto_apply=true`, {
                method: 'POST'
            });
            const data = await response.json();

            if (data.error) {
                this.showToast(`Error: ${data.error}`, 'error');
                return;
            }

            if (data.results?.applied) {
                const results = data.results;
                this.showToast(
                    `✅ Applied ${results.channels_applied} channel mappings${results.profile_applied ? ' and car profile' : ''}`,
                    'success'
                );
                
                // Refresh cars and channels
                this.loadCars();
                if (this.currentCarId === carId) {
                    this.loadChannels(carId);
                }
            } else {
                this.showToast('Failed to apply recommendations', 'error');
            }
        } catch (e) {
            console.error('Error applying recommendations:', e);
            this.showToast(`Error: ${e.message || 'Could not apply recommendations'}`, 'error');
        } finally {
            if (applyBtn) {
                applyBtn.disabled = false;
                applyBtn.textContent = originalText;
            }
        }
    }
}

// Initialize MoTeC UI when DOM is ready
let motecUI;
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if MoTeC section exists
    if (document.getElementById('motec')) {
        motecUI = new MotecConfigUI();
        window.motecUI = motecUI; // Make available globally for onclick handlers
    }
});

