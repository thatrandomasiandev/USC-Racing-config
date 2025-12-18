/**
 * Parameter Management System - Frontend JavaScript
 * Lightweight and efficient for Raspberry Pi
 */

// Form submission (removed - using Edit button on each parameter instead)

// Filter by subteam (old dropdown - tabs are primary now)
const filterSubteam = document.getElementById('filter-subteam');
if (filterSubteam) {
    filterSubteam.addEventListener('change', (e) => {
        const subteam = e.target.value;
        if (subteam) {
            switchSubteamTab(subteam);
            // Also update tab button
            const tab = document.querySelector(`.tab-button[data-subteam="${subteam}"]`);
            if (tab) {
                document.querySelectorAll('.tab-button').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
            }
        } else {
            switchSubteamTab('');
        }
    });
}

// Search parameters
let searchTimeout;
document.getElementById('search').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();
    
        searchTimeout = setTimeout(() => {
            if (query.length > 0) {
                searchParameters(query);
            } else {
                // Reload with current active tab
                loadParameters(activeSubteamTab || null);
            }
        }, 300);
});

// Load parameters from API
async function loadParameters(subteam = null) {
    try {
        // First, ensure car parameters are initialized in the database
        try {
            await fetch('/api/car-parameters/initialize', {
                method: 'POST'
            });
        } catch (e) {
            // Silently fail if already initialized or not authenticated
            console.log('Car parameters may already be initialized');
        }
        
        const url = subteam ? `/api/parameters?subteam=${encodeURIComponent(subteam)}` : '/api/parameters';
        const response = await fetch(url);
        const data = await response.json();
        
        // Load car parameter definitions to get display names and units
        await loadCarParameterDefinitions();
        
        updateTable(data.parameters);
        loadSessions(); // Also load sessions
        
        // Update subteam view summary if a subteam is active
        if (activeSubteamTab) {
            updateSubteamViewSummary(activeSubteamTab);
        }
    } catch (error) {
        console.error('Error loading parameters:', error);
    }
}

// Car parameter definitions cache
let carParameterDefinitions = {};

// Load car parameter definitions
async function loadCarParameterDefinitions() {
    try {
        const response = await fetch('/api/car-parameters/definitions');
        const data = await response.json();
        
        // Build lookup map
        carParameterDefinitions = {};
        if (data.definitions) {
            data.definitions.forEach(def => {
                carParameterDefinitions[def.parameter_name] = def;
            });
        }
        
        // Update existing rows if page already loaded
        updateExistingRows();
        
        // Update category dropdown if we have an active subteam
        if (activeSubteamTab) {
            updateCategoryDropdown(activeSubteamTab);
        }
    } catch (error) {
        console.error('Error loading car parameter definitions:', error);
    }
}

// Autocomplete functionality removed - using Edit button on each parameter instead

// Get user subteam from page (set by template)
let userSubteam = null;
let userRole = null;

// Initialize user info from page
function initUserInfo() {
    // Try to get user subteam from a hidden element or meta tag
    const subteamMeta = document.querySelector('meta[name="user-subteam"]');
    const roleMeta = document.querySelector('meta[name="user-role"]');
    if (subteamMeta) {
        userSubteam = subteamMeta.getAttribute('content') || null;
    }
    if (roleMeta) {
        userRole = roleMeta.getAttribute('content') || null;
    }
}

// Search parameters with fuzzy matching
function searchParameters(query) {
    const queryLower = query.toLowerCase().trim();
    if (queryLower.length === 0) return [];
    
    const matches = [];
    
    // Map common words to abbreviations
    const wordAbbreviations = {
        'front': 'f',
        'rear': 'r',
        'left': 'l',
        'right': 'r',
        'fl': 'fl',
        'fr': 'fr',
        'rl': 'rl',
        'rr': 'rr'
    };
    
    // Expand abbreviations in query (e.g., "front left" -> "fl", "front" -> "f")
    let expandedQuery = queryLower;
    Object.keys(wordAbbreviations).forEach(word => {
        if (word.length > 1) { // Only replace full words
            const regex = new RegExp('\\b' + word + '\\b', 'gi');
            expandedQuery = expandedQuery.replace(regex, wordAbbreviations[word]);
        }
    });
    
    // Normalize query: remove common words and split
    const queryWords = expandedQuery.split(/\s+/).filter(word => 
        word.length > 0 && !['the', 'a', 'an', 'is', 'are', 'and', 'or'].includes(word)
    );
    
    // Also create word combinations (e.g., "front left" -> "fl")
    const wordCombinations = [];
    for (let i = 0; i < queryWords.length - 1; i++) {
        const combo = queryWords[i] + queryWords[i + 1];
        if (combo.length <= 3) { // Only short combinations (FL, FR, etc.)
            wordCombinations.push(combo);
        }
    }
    queryWords.push(...wordCombinations);
    
    // Search through all parameter definitions
    Object.values(carParameterDefinitions).forEach(def => {
        // Filter by user subteam if not admin
        if (userRole !== 'admin' && userSubteam) {
            if (def.subteam !== userSubteam) {
                return; // Skip parameters not in user's subteam
            }
        }
        const paramName = def.parameter_name.toLowerCase();
        const displayName = (def.display_name || '').toLowerCase();
        
        // Create searchable text combinations
        const searchTexts = [
            displayName,
            paramName,
            displayName.replace(/\s+/g, ''), // No spaces (e.g., "FL Camber" -> "flcamber")
            paramName.replace(/_/g, ''), // No underscores (e.g., "camber_fl" -> "camberfl")
            displayName.replace(/\s+/g, ' '), // Normalized display name
            paramName.replace(/_/g, ' '), // Parameter name with spaces instead of underscores
        ];
        
        let score = 0;
        let matchedText = '';
        
        // Check for exact matches
        if (displayName === queryLower || paramName === queryLower) {
            score = 1000;
            matchedText = def.display_name;
        }
        // Check for starts with
        else if (displayName.startsWith(queryLower) || paramName.startsWith(queryLower)) {
            score = 500;
            matchedText = def.display_name;
        }
        // Check for contains
        else if (displayName.includes(queryLower) || paramName.includes(queryLower)) {
            score = 300;
            matchedText = def.display_name;
        }
        // Fuzzy matching: check if all query words appear in any order
        else {
            const allWordsMatch = queryWords.every(word => {
                return searchTexts.some(text => text.includes(word));
            });
            
            if (allWordsMatch) {
                // Count how many words matched
                const matchedWords = queryWords.filter(word => {
                    return searchTexts.some(text => text.includes(word));
                }).length;
                score = 100 + (matchedWords * 10);
                matchedText = def.display_name;
            }
            // Check individual word matches for partial scoring
            else {
                const wordMatches = queryWords.filter(word => {
                    return searchTexts.some(text => text.includes(word));
                }).length;
                if (wordMatches > 0) {
                    score = wordMatches * 5;
                    matchedText = def.display_name;
                }
            }
        }
        
        if (score > 0) {
            matches.push({
                parameter_name: def.parameter_name,
                display_name: def.display_name || def.parameter_name,
                subteam: def.subteam || '',
                unit: def.unit || '',
                score: score,
                matched_text: matchedText
            });
        }
    });
    
    // Sort by score (highest first) and return top 10
    matches.sort((a, b) => b.score - a.score);
    return matches.slice(0, 10);
}

// Autocomplete functions removed - no longer needed since top form was removed

// Load sessions
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        
        if (data.sessions && data.sessions.length > 0) {
            document.getElementById('sessions-section').style.display = 'block';
            updateSessionsTable(data.sessions);
        } else {
            document.getElementById('sessions-section').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
        document.getElementById('sessions-tbody').innerHTML = 
            '<tr><td colspan="6" style="text-align: center; color: var(--text-dim);">No sessions found</td></tr>';
    }
}

// Update sessions table
function updateSessionsTable(sessions) {
    const tbody = document.getElementById('sessions-tbody');
    tbody.innerHTML = '';
    
    if (sessions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim);">No sessions uploaded yet</td></tr>';
        return;
    }
    
    sessions.forEach(session => {
        const row = document.createElement('tr');
        
        // Format upload date
        const uploadDate = new Date(session.uploaded_at);
        const dateStr = uploadDate.toLocaleDateString() + ' ' + uploadDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // Extract performance data
        const perf = session.session_data || {};
        let perfDisplay = '-';
        if (perf.fastest_time) {
            perfDisplay = `⏱️ ${perf.fastest_time}`;
            if (perf.total_laps) {
                perfDisplay += ` (${perf.total_laps} laps)`;
            }
        } else if (perf.session_date) {
            perfDisplay = `📅 ${perf.session_date}`;
        }
        
        const paramCount = session.parameters_snapshot ? session.parameters_snapshot.length : 0;
        
        row.innerHTML = `
            <td><strong>${escapeHtml(session.session_id.split('_').slice(-1)[0])}</strong></td>
            <td><code style="font-size: 0.85em;">${escapeHtml(session.filename)}</code></td>
            <td>${escapeHtml(dateStr)}</td>
            <td>${escapeHtml(perfDisplay)}</td>
            <td>${paramCount} parameters</td>
            <td>
                <button class="btn-small btn-secondary" onclick="viewSessionDetails('${escapeHtml(session.session_id)}')">
                    View
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// View session details
async function viewSessionDetails(sessionId) {
    // Find session and show details
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        const session = data.sessions.find(s => s.session_id === sessionId);
        
        if (!session) {
            showMessage('Session not found', 'error');
            return;
        }
        
        // Build details display
        let details = `Session: ${session.filename}\n\n`;
        details += `Uploaded: ${new Date(session.uploaded_at).toLocaleString()}\n\n`;
        
        if (session.session_data) {
            details += `Performance Data:\n`;
            Object.entries(session.session_data).forEach(([key, value]) => {
                if (key !== 'all_details' && value) {
                    details += `  ${key}: ${value}\n`;
                }
            });
            details += '\n';
        }
        
        if (session.parameters_snapshot && session.parameters_snapshot.length > 0) {
            details += `Parameters at upload time:\n`;
            session.parameters_snapshot.forEach(param => {
                const def = carParameterDefinitions[param.parameter_name];
                const displayName = def ? def.display_name : param.parameter_name;
                const unit = def ? def.unit : '';
                details += `  ${displayName}: ${param.current_value}${unit ? ' ' + unit : ''}\n`;
            });
        }
        
        alert(details);
    } catch (error) {
        console.error('Error loading session details:', error);
        showMessage('Error loading session details', 'error');
    }
}

// Initialize car parameters manually
async function initializeCarParameters() {
    try {
        const response = await fetch('/api/car-parameters/initialize', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`Initialized ${data.count} car parameters: ${data.initialized.join(', ')}`, 'success');
            // Reload parameters to show the new ones
            loadParameters();
        } else {
            showMessage(data.detail || 'Error initializing car parameters', 'error');
        }
    } catch (error) {
        showMessage('Error initializing car parameters: ' + error.message, 'error');
    }
}

// Toggle parameter details (ID)
function toggleParameterDetails(toggleElement) {
    const detailsContent = toggleElement.nextElementSibling;
    const isShowing = detailsContent.classList.contains('show');
    
    if (isShowing) {
        detailsContent.classList.remove('show');
        toggleElement.textContent = 'Show ID';
    } else {
        detailsContent.classList.add('show');
        toggleElement.textContent = 'Hide ID';
    }
}

// Make function globally accessible
window.initializeCarParameters = initializeCarParameters;
window.viewSessionDetails = viewSessionDetails;
window.toggleParameterDetails = toggleParameterDetails;

// Update parameters table
function updateTable(parameters) {
    const tbody = document.getElementById('parameters-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (parameters.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-dim);">No parameters found</td></tr>';
        return;
    }
    
    parameters.forEach(param => {
        const row = document.createElement('tr');
        row.setAttribute('data-parameter', param.parameter_name);
        row.setAttribute('data-subteam', param.subteam);
        // Add category attribute if available
        if (param.category) {
            row.setAttribute('data-category', param.category);
        } else if (carParameterDefinitions[param.parameter_name]?.category) {
            row.setAttribute('data-category', carParameterDefinitions[param.parameter_name].category);
        }
        
        const date = param.updated_at && param.updated_at.length > 19 ? param.updated_at.substring(0, 19) : (param.updated_at || '-');
        
        // Get car parameter definition if available
        const def = carParameterDefinitions[param.parameter_name];
        const displayName = def ? def.display_name : param.parameter_name;
        const unit = def ? def.unit : '-';
        
        // Add indicator for car parameters
        const isCarParam = def ? ' 🚗' : '';
        
        row.innerHTML = `
            <td>
                <strong id="display-${escapeHtml(param.parameter_name)}">${escapeHtml(displayName)}${isCarParam}</strong>
                <div class="parameter-details">
                    <span class="parameter-details-toggle" onclick="toggleParameterDetails(this)">Show ID</span>
                    <div class="parameter-details-content">${escapeHtml(param.parameter_name)}</div>
                </div>
            </td>
            <td>${escapeHtml(param.subteam)}</td>
            <td><strong>${escapeHtml(param.current_value)}</strong></td>
            <td id="unit-${escapeHtml(param.parameter_name)}">${escapeHtml(unit)}</td>
            <td>${escapeHtml(date)}</td>
            <td>${escapeHtml(param.updated_by || '-')}</td>
            <td>
                <button class="btn-small btn-primary" onclick="editParameter('${escapeHtml(param.parameter_name)}')" style="margin-right: 0.5rem;">
                    Edit
                </button>
                <button class="btn-small btn-secondary" onclick="showHistory('${escapeHtml(param.parameter_name)}')">
                    History
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Also update any existing rows from server-side rendering
    updateExistingRows();
    
    // Update category dropdown if we have an active subteam tab
    if (activeSubteamTab) {
        updateCategoryDropdown(activeSubteamTab);
        // Re-apply category filter
        if (activeCategory) {
            switchCategory(activeCategory);
        }
    }
}

// Update existing server-rendered rows with display names and units
function updateExistingRows() {
    const rows = document.querySelectorAll('#parameters-tbody tr[data-parameter]');
    rows.forEach(row => {
        const paramName = row.getAttribute('data-parameter');
        const def = carParameterDefinitions[paramName];
        
        if (def) {
            // Update display name
            const displayCell = row.querySelector(`#display-${paramName}`);
            if (displayCell) {
                displayCell.innerHTML = `${escapeHtml(def.display_name)} 🚗`;
            }
            
            // Update unit
            const unitCell = row.querySelector(`#unit-${paramName}`);
            if (unitCell) {
                unitCell.textContent = def.unit || '-';
            }
            
            // Add category attribute if not present
            if (def.category && !row.getAttribute('data-category')) {
                row.setAttribute('data-category', def.category);
            }
        }
    });
}

// Current active subteam tab and category
let activeSubteamTab = '';
let activeCategory = '';

// Switch subteam tab
function switchSubteamTab(subteam) {
    activeSubteamTab = subteam;
    activeCategory = ''; // Reset category when switching tabs
    
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab-button');
    tabs.forEach(tab => {
        if (tab.getAttribute('data-subteam') === subteam) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Show/hide subteam view summary
    const summaryDiv = document.getElementById('subteam-view-summary');
    if (subteam && summaryDiv) {
        summaryDiv.style.display = 'block';
        updateSubteamViewSummary(subteam);
    } else if (summaryDiv) {
        summaryDiv.style.display = 'none';
    }
    
    // Update category dropdown
    updateCategoryDropdown(subteam);
    
    // Reload parameters with subteam filter
    if (subteam) {
        loadParameters(subteam);
    } else {
        loadParameters(null);
    }
}

// Update subteam view summary with statistics
function updateSubteamViewSummary(subteam) {
    // Get all parameters for this subteam
    fetch('/api/parameters')
        .then(response => response.json())
        .then(data => {
            const subteamParams = data.parameters.filter(p => p.subteam === subteam);
            
            // Update total parameters
            const totalEl = document.getElementById('subteam-total-params');
            if (totalEl) {
                totalEl.textContent = subteamParams.length;
            }
            
            // Count unique categories
            const categories = new Set();
            subteamParams.forEach(param => {
                const def = carParameterDefinitions[param.parameter_name];
                if (def && def.category) {
                    categories.add(def.category);
                }
            });
            const categoriesEl = document.getElementById('subteam-categories');
            if (categoriesEl) {
                categoriesEl.textContent = categories.size;
            }
            
            // Count recently updated (last 7 days)
            const recentDate = new Date();
            recentDate.setDate(recentDate.getDate() - 7);
            const recentUpdates = subteamParams.filter(param => {
                if (!param.updated_at) return false;
                const updateDate = new Date(param.updated_at);
                return updateDate >= recentDate;
            }).length;
            const recentEl = document.getElementById('subteam-recent-updates');
            if (recentEl) {
                recentEl.textContent = recentUpdates;
            }
        })
        .catch(error => {
            console.error('Error updating subteam view summary:', error);
        });
}

// Update category dropdown based on active subteam
function updateCategoryDropdown(subteam) {
    const categoryFilter = document.getElementById('category-filter');
    const categorySelect = document.getElementById('category-select');
    
    if (!subteam) {
        // Hide category filter for "All" tab
        categoryFilter.style.display = 'none';
        return;
    }
    
    // Show category filter
    categoryFilter.style.display = 'flex';
    
    // Clear existing options
    categorySelect.innerHTML = '<option value="">All Categories</option>';
    
    // Get unique categories for this subteam from loaded parameters
    const rows = document.querySelectorAll('#parameters-tbody tr[data-category]');
    const categories = new Set();
    rows.forEach(row => {
        if (row.getAttribute('data-subteam') === subteam) {
            const cat = row.getAttribute('data-category');
            if (cat) categories.add(cat);
        }
    });
    
    // If no rows loaded yet, try to get categories from carParameterDefinitions
    if (categories.size === 0 && Object.keys(carParameterDefinitions).length > 0) {
        Object.values(carParameterDefinitions).forEach(def => {
            if (def.subteam === subteam && def.category) {
                categories.add(def.category);
            }
        });
    }
    
    // Add category options
    Array.from(categories).sort().forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categorySelect.appendChild(option);
    });
    
    // Reset to "All Categories"
    categorySelect.value = '';
}

// Switch category
function switchCategory(category) {
    activeCategory = category || '';
    
    // Filter rows by both subteam and category
    const rows = document.querySelectorAll('#parameters-tbody tr');
    rows.forEach(row => {
        const rowSubteam = row.getAttribute('data-subteam');
        const rowCategory = row.getAttribute('data-category');
        
        const subteamMatch = !activeSubteamTab || rowSubteam === activeSubteamTab;
        const categoryMatch = !activeCategory || rowCategory === activeCategory;
        
        if (subteamMatch && categoryMatch) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Make function globally accessible
window.switchSubteamTab = switchSubteamTab;
window.switchCategory = switchCategory;

// Edit Parameter
async function editParameter(parameterName) {
    try {
        // Get parameter data
        const response = await fetch('/api/parameters');
        const data = await response.json();
        const param = data.parameters.find(p => p.parameter_name === parameterName);
        
        if (!param) {
            showMessage('Parameter not found', 'error');
            return;
        }
        
        // Get parameter definition for validation info
        const def = carParameterDefinitions[parameterName];
        const displayName = def ? def.display_name : parameterName;
        
        // Populate form with autofill
        document.getElementById('edit-parameter-name').value = parameterName;
        document.getElementById('edit-subteam').value = param.subteam || '';
        document.getElementById('edit-display-name').value = displayName;
        document.getElementById('edit-current-value').value = param.current_value || '';
        
        // Autofill new value with current value (user can modify)
        const newValueInput = document.getElementById('edit-new-value');
        newValueInput.value = param.current_value || '';
        newValueInput.placeholder = `Enter new value (current: ${param.current_value || 'none'})`;
        
        // Clear comment and queue checkbox
        document.getElementById('edit-comment').value = '';
        document.getElementById('edit-queue').checked = false;
        
        // Set unit and range hints
        const unit = def ? def.unit : '';
        document.getElementById('edit-value-unit').textContent = unit ? `Unit: ${unit}` : '';
        
        let rangeText = '';
        if (def) {
            if (def.min_value && def.max_value) {
                rangeText = `Range: ${def.min_value} - ${def.max_value}`;
                if (unit) rangeText += ` ${unit}`;
            } else if (def.min_value) {
                rangeText = `Min: ${def.min_value}`;
                if (unit) rangeText += ` ${unit}`;
            } else if (def.max_value) {
                rangeText = `Max: ${def.max_value}`;
                if (unit) rangeText += ` ${unit}`;
            }
        }
        document.getElementById('edit-value-range').textContent = rangeText;
        
        // Show modal and focus on new value field (don't select text so user can see the value)
        document.getElementById('edit-parameter-modal').style.display = 'block';
        // Focus at the end of the text so user can see the full value
        newValueInput.focus();
        newValueInput.setSelectionRange(newValueInput.value.length, newValueInput.value.length);
    } catch (error) {
        console.error('Error loading parameter:', error);
        showMessage('Error loading parameter details', 'error');
    }
}

// Close edit parameter modal
function closeEditParameter() {
    document.getElementById('edit-parameter-modal').style.display = 'none';
    document.getElementById('edit-parameter-message').textContent = '';
}

// Make functions globally accessible
window.editParameter = editParameter;
window.closeEditParameter = closeEditParameter;

// Make function globally accessible
window.switchSubteamTab = switchSubteamTab;

// Filter table by subteam (and optionally category)
function filterTable(subteam, category = null) {
    const rows = document.querySelectorAll('#parameters-tbody tr');
    rows.forEach(row => {
        const rowSubteam = row.getAttribute('data-subteam');
        const rowCategory = row.getAttribute('data-category');
        
        const subteamMatch = !subteam || rowSubteam === subteam;
        const categoryMatch = !category || rowCategory === category;
        
        if (subteamMatch && categoryMatch) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Search parameters
async function searchParameters(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        // When searching, show all results but filter by active tab and category if selected
        updateTable(data.parameters);
        
        // If there's an active tab or category, filter the results
        if (activeSubteamTab || activeCategory) {
            filterTable(activeSubteamTab, activeCategory);
        }
    } catch (error) {
        console.error('Error searching parameters:', error);
    }
}

// Show parameter history
async function showHistory(parameterName) {
    try {
        const response = await fetch(`/api/history?parameter=${encodeURIComponent(parameterName)}`);
        const data = await response.json();
        
        document.getElementById('history-parameter-name').textContent = parameterName;
        const content = document.getElementById('history-content');
        
        if (data.history.length === 0) {
            content.innerHTML = '<p style="color: var(--text-dim);">No history available for this parameter.</p>';
        } else {
            content.innerHTML = data.history.map(item => {
                const date = item.updated_at.length > 19 ? item.updated_at.substring(0, 19) : item.updated_at;
                const formLink = item.form_id ? `<a href="#" onclick="showFormHistory('${escapeHtml(item.form_id)}'); return false;" style="color: var(--primary-color);">Form ${escapeHtml(item.form_id.substring(0, 8))}</a>` : '';
                return `
                    <div class="history-item">
                        <div class="history-item-header">
                            <strong>${escapeHtml(item.updated_by)}</strong>
                            <span style="color: var(--text-dim);">${escapeHtml(date)}</span>
                            ${formLink}
                        </div>
                        <div class="history-item-value">
                            ${item.prior_value ? `
                                <span class="value-change old">${escapeHtml(item.prior_value)}</span>
                                →
                            ` : '<span style="color: var(--text-dim);">Initial</span> → '}
                            <span class="value-change new">${escapeHtml(item.new_value)}</span>
                        </div>
                        ${item.comment ? `<div style="margin-top: 0.5rem; color: var(--text-dim); font-style: italic;">Comment: ${escapeHtml(item.comment)}</div>` : ''}
                    </div>
                `;
            }).join('');
        }
        
        document.getElementById('history-modal').style.display = 'block';
    } catch (error) {
        console.error('Error loading history:', error);
        alert('Error loading parameter history');
    }
}

// Show form history by form_id
async function showFormHistory(formId) {
    try {
        const response = await fetch(`/api/history?form_id=${encodeURIComponent(formId)}`);
        const data = await response.json();
        
        document.getElementById('history-parameter-name').textContent = `Form: ${formId.substring(0, 8)}...`;
        const content = document.getElementById('history-content');
        
        if (data.history.length === 0) {
            content.innerHTML = '<p style="color: var(--text-dim);">No history found for this form.</p>';
        } else {
            content.innerHTML = data.history.map(item => {
                const date = item.updated_at.length > 19 ? item.updated_at.substring(0, 19) : item.updated_at;
                return `
                    <div class="history-item">
                        <div class="history-item-header">
                            <strong>${escapeHtml(item.parameter_name)}</strong>
                            <span style="color: var(--text-dim);">${escapeHtml(date)}</span>
                        </div>
                        <div class="history-item-value">
                            ${item.prior_value ? `
                                <span class="value-change old">${escapeHtml(item.prior_value)}</span>
                                →
                            ` : '<span style="color: var(--text-dim);">Initial</span> → '}
                            <span class="value-change new">${escapeHtml(item.new_value)}</span>
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <span style="color: var(--text-dim);">By: ${escapeHtml(item.updated_by)}</span>
                            ${item.comment ? `<span style="margin-left: 1rem; color: var(--text-dim); font-style: italic;">Comment: ${escapeHtml(item.comment)}</span>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        document.getElementById('history-modal').style.display = 'block';
    } catch (error) {
        console.error('Error loading form history:', error);
        alert('Error loading form history');
    }
}

// Close history modal
function closeHistory() {
    document.getElementById('history-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const historyModal = document.getElementById('history-modal');
    const usersModal = document.getElementById('users-modal');
    if (event.target === historyModal) {
        closeHistory();
    }
    if (usersModal && event.target === usersModal) {
        closeUserManagement();
    }
}

// Show message
function showMessage(text, type) {
    const messageEl = document.getElementById('form-message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    
    setTimeout(() => {
        messageEl.className = 'message';
    }, 5000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Queue management functions
async function loadQueue() {
    try {
        const response = await fetch('/api/queue?status=pending');
        const data = await response.json();
        updateQueueTable(data.queue);
    } catch (error) {
        console.error('Error loading queue:', error);
    }
}

function updateQueueTable(queueItems) {
    const tbody = document.getElementById('queue-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (queueItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-dim);">No pending queue items</td></tr>';
        return;
    }
    
    queueItems.forEach(item => {
        const row = document.createElement('tr');
        row.setAttribute('data-form-id', item.form_id);
        const date = item.submitted_at.length > 19 ? item.submitted_at.substring(0, 19) : item.submitted_at;
        
        row.innerHTML = `
            <td><strong>${escapeHtml(item.parameter_name)}</strong></td>
            <td>${escapeHtml(item.subteam)}</td>
            <td>
                <span class="value-change old">${escapeHtml(item.current_value || "N/A")}</span>
                →
                <span class="value-change new">${escapeHtml(item.new_value)}</span>
            </td>
            <td>${escapeHtml(item.submitted_by)}</td>
            <td>${escapeHtml(item.comment || "-")}</td>
            <td>${escapeHtml(date)}</td>
            <td>
                <button class="btn-small btn-primary" onclick="processQueueItem('${escapeHtml(item.form_id)}')">Approve</button>
                <button class="btn-small btn-secondary" onclick="rejectQueueItem('${escapeHtml(item.form_id)}')">Reject</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

async function processQueueItem(formId) {
    if (!confirm('Approve this parameter change?')) return;
    
    try {
        const response = await fetch(`/api/queue/${encodeURIComponent(formId)}/process`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Queue item processed successfully', 'success');
            loadQueue();
            loadParameters();
        } else {
            showMessage(data.detail || 'Error processing queue item', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

async function rejectQueueItem(formId) {
    if (!confirm('Reject this parameter change?')) return;
    
    try {
        const response = await fetch(`/api/queue/${encodeURIComponent(formId)}/reject`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Queue item rejected', 'success');
            loadQueue();
        } else {
            showMessage(data.detail || 'Error rejecting queue item', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

// User management functions
async function showUserManagement() {
    try {
        const [usersResponse, deletedResponse] = await Promise.all([
            fetch('/api/users'),
            fetch('/api/users/deleted')
        ]);
        
        const usersData = await usersResponse.json();
        const deletedData = await deletedResponse.json();
        
        const users = usersData.users;
        const subteams = usersData.subteams || [];
        const deletedUsers = deletedData.deleted_users || [];
        
        const content = document.getElementById('users-content');
        content.innerHTML = `
            <div style="margin-bottom: 1rem;">
                <h3>Create New User</h3>
                <form id="create-user-form" style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr auto; gap: 0.5rem; align-items: end;">
                    <input type="text" id="new-username" placeholder="Username" required>
                    <input type="password" id="new-password" placeholder="Password" required>
                    <select id="new-role">
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                    </select>
                    <select id="new-subteam" required>
                        <option value="">Select Subteam</option>
                        ${subteams.map(st => `<option value="${escapeHtml(st)}">${escapeHtml(st)}</option>`).join('')}
                    </select>
                    <button type="submit" class="btn-primary">Create</button>
                </form>
            </div>
            <h3>Existing Users</h3>
            <div class="table-container">
                <table class="parameters-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Password</th>
                            <th>Role</th>
                            <th>Subteam</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="users-tbody">
                        ${users.map(user => {
                            const date = user.created_at.length > 19 ? user.created_at.substring(0, 19) : user.created_at;
                            // Get password from registered users JSON
                            const password = user.password || 'N/A';
                            const subteam = user.subteam || '';
                            return `
                                <tr>
                                    <td><strong>${escapeHtml(user.username)}</strong></td>
                                    <td><code style="background: var(--card-bg); padding: 0.25rem 0.5rem; border-radius: 4px;">${escapeHtml(password)}</code></td>
                                    <td>
                                        <select onchange="updateUserRole('${escapeHtml(user.username)}', this.value)" style="padding: 0.25rem;">
                                            <option value="user" ${user.role === 'user' ? 'selected' : ''}>User</option>
                                            <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                                        </select>
                                    </td>
                                    <td>
                                        <select onchange="updateUserSubteam('${escapeHtml(user.username)}', this.value)" style="padding: 0.25rem;">
                                            <option value="">No Subteam</option>
                                            ${subteams.map(st => `<option value="${escapeHtml(st)}" ${subteam === st ? 'selected' : ''}>${escapeHtml(st)}</option>`).join('')}
                                        </select>
                                    </td>
                                    <td>${escapeHtml(date)}</td>
                                    <td>
                                        <button class="btn-small btn-danger" onclick="deleteUser('${escapeHtml(user.username)}')">Delete</button>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 2rem;">
                <h3>Recently Deleted Users</h3>
                <p style="color: var(--text-dim); margin-bottom: 1rem;">
                    These users are denied login access. Remove them permanently to allow re-creation.
                </p>
                <div class="table-container">
                    <table class="parameters-table">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Role</th>
                                <th>Subteam</th>
                                <th>Deleted At</th>
                                <th>Deleted By</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${deletedUsers.length === 0 ? `
                                <tr>
                                    <td colspan="6" style="text-align: center; color: var(--text-dim);">No deleted users</td>
                                </tr>
                            ` : deletedUsers.map(user => {
                                const date = user.deleted_at ? (user.deleted_at.length > 19 ? user.deleted_at.substring(0, 19) : user.deleted_at) : 'Unknown';
                                const subteam = user.subteam || 'N/A';
                                return `
                                    <tr>
                                        <td><strong>${escapeHtml(user.username)}</strong></td>
                                        <td><span class="role-badge role-${escapeHtml(user.role)}">${escapeHtml(user.role)}</span></td>
                                        <td>${escapeHtml(subteam)}</td>
                                        <td>${escapeHtml(date)}</td>
                                        <td>${escapeHtml(user.deleted_by || 'Unknown')}</td>
                                        <td>
                                            <button class="btn-small btn-secondary" onclick="permanentlyRemoveDeletedUser('${escapeHtml(user.username)}')">Remove Permanently</button>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Add form handler
        document.getElementById('create-user-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('new-username').value.trim();
            const password = document.getElementById('new-password').value;
            const role = document.getElementById('new-role').value;
            const subteam = document.getElementById('new-subteam').value;
            
            // Validate subteam is required
            if (!subteam || subteam.trim() === '') {
                showMessage('Subteam is required. Please select a subteam.', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, role, subteam })
                });
                
                const data = await response.json();
                if (response.ok) {
                    showMessage('User created successfully', 'success');
                    showUserManagement(); // Reload
                } else {
                    showMessage(data.detail || 'Error creating user', 'error');
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, 'error');
            }
        });
        
        document.getElementById('users-modal').style.display = 'block';
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Error loading users');
    }
}

async function updateUserRole(username, role) {
    try {
        const response = await fetch(`/api/users/${encodeURIComponent(username)}/role?role=${encodeURIComponent(role)}`, {
            method: 'PATCH'
        });
        
        const data = await response.json();
        if (response.ok) {
            showMessage(`User ${username} role updated to ${role}`, 'success');
        } else {
            showMessage(data.detail || 'Error updating role', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

async function updateUserSubteam(username, subteam) {
    try {
        const subteamParam = subteam ? `?subteam=${encodeURIComponent(subteam)}` : '?subteam=';
        const response = await fetch(`/api/users/${encodeURIComponent(username)}/subteam${subteamParam}`, {
            method: 'PATCH'
        });
        
        const data = await response.json();
        if (response.ok) {
            const subteamText = subteam || 'None';
            showMessage(`User ${username} subteam updated to ${subteamText}`, 'success');
        } else {
            showMessage(data.detail || 'Error updating subteam', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

// Make updateUserSubteam globally accessible
window.updateUserSubteam = updateUserSubteam;

// Make deleteUser globally accessible
window.deleteUser = async function(username) {
    // Get current user from page header
    const usernameElement = document.querySelector('.username strong');
    const currentUser = usernameElement ? usernameElement.textContent.trim() : '';
    
    // Check if user being deleted is an admin by looking at the role in the table
    let isAdmin = false;
    const userRows = document.querySelectorAll('#users-tbody tr');
    userRows.forEach(row => {
        const nameCell = row.querySelector('td:first-child strong');
        if (nameCell && nameCell.textContent.trim() === username) {
            const roleSelect = row.querySelector('select');
            if (roleSelect && roleSelect.value === 'admin') {
                isAdmin = true;
            }
        }
    });
    
    // Prevent self-deletion
    if (username === currentUser) {
        alert('⚠️ ERROR: You cannot delete your own account! Ask another admin to delete it.');
        return;
    }
    
    // Build warning message for admin deletion
    const warning = isAdmin ? '\n\n⚠️ WARNING: This user is an admin. Are you sure you want to delete them?' : '';
    
    if (!confirm(`Delete user "${username}"? This will move them to recently deleted users and deny login access.${warning}`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${encodeURIComponent(username)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (response.ok) {
            showMessage(`User ${username} deleted successfully`, 'success');
            showUserManagement(); // Reload to show updated list
        } else {
            showMessage(data.detail || 'Error deleting user', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

// Make permanentlyRemoveDeletedUser globally accessible
window.permanentlyRemoveDeletedUser = async function(username) {
    if (!confirm(`Permanently remove "${username}" from deleted users list? This will allow them to be recreated.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/deleted/${encodeURIComponent(username)}/remove`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (response.ok) {
            showMessage(`User ${username} permanently removed from deleted list`, 'success');
            showUserManagement(); // Reload to show updated list
        } else {
            showMessage(data.detail || 'Error removing user', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

function closeUserManagement() {
    const modal = document.getElementById('users-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Load queue on page load if admin
if (document.getElementById('queue-tbody')) {
    loadQueue();
}

// Setup edit parameter form submission
document.addEventListener('DOMContentLoaded', () => {
    const editForm = document.getElementById('edit-parameter-form');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(editForm);
            const updateData = {
                parameter_name: formData.get('parameter_name'),
                subteam: formData.get('subteam'),
                new_value: formData.get('new_value'),
                comment: formData.get('comment') || null,
                queue: formData.get('queue') === 'on'
            };
            
            try {
                const response = await fetch('/api/parameters', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updateData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    if (data.status === 'queued') {
                        showMessage('Parameter change added to queue for admin approval', 'success');
                    } else {
                        let message = `Parameter "${updateData.parameter_name}" updated successfully`;
                        const ldxCount = data.ldx_files_updated !== undefined ? data.ldx_files_updated : 0;
                        console.log(`[Parameter Update] Parameter: ${updateData.parameter_name}, LDX files updated: ${ldxCount}`);
                        
                        if (ldxCount > 0) {
                            message += ` (${ldxCount} LDX file${ldxCount > 1 ? 's' : ''} updated)`;
                        } else if (updateData.parameter_name.startsWith('ldx_')) {
                            message += ` (No LDX files found containing this parameter)`;
                            console.warn(`[Parameter Update] No LDX files were found/updated for parameter: ${updateData.parameter_name}`);
                        } else {
                            message += ` (Note: This parameter type is not stored in LDX files)`;
                        }
                        showMessage(message, 'success');
                    }
                    
                    // Close modal
                    closeEditParameter();
                    
                    // Reload parameters
                    loadParameters(activeSubteamTab || null);
                } else {
                    const msgEl = document.getElementById('edit-parameter-message');
                    msgEl.textContent = data.detail || 'Error updating parameter';
                    msgEl.style.color = 'var(--danger)';
                }
            } catch (error) {
                const msgEl = document.getElementById('edit-parameter-message');
                msgEl.textContent = 'Network error: ' + error.message;
                msgEl.style.color = 'var(--danger)';
            }
        });
    }
});

// MoTeC Files Management and Page Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize user info from page meta tags
    initUserInfo();
    
    // Load car parameter definitions first, then update existing rows
    loadCarParameterDefinitions().then(() => {
        updateExistingRows();
    });
    
    // Load parameters to refresh table with API data (which will use definitions)
    if (document.getElementById('parameters-tbody')) {
        loadParameters();
    }
    
    // Load MoTeC files on page load
    if (document.getElementById('motec-files-tbody')) {
        loadMotecFiles();
        
        // Setup upload form
        const uploadForm = document.getElementById('motec-upload-form');
        if (uploadForm) {
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await uploadMotecFile();
            });
        }
    }
});

async function loadMotecFiles() {
    const tbody = document.getElementById('motec-files-tbody');
    if (!tbody) return;
    
    // Set loading state
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim);">Loading...</td></tr>';
    
    try {
        // Add timeout to prevent infinite loading
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        const response = await fetch('/api/motec/files', {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.files || !Array.isArray(data.files)) {
            throw new Error('Invalid response format');
        }
        
        if (data.files.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim);">No MoTeC files uploaded yet</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.files.map(file => {
            const size = file.file_size ? formatFileSize(file.file_size) : 'Unknown';
            const uploaded = file.uploaded_at ? (file.uploaded_at.length > 19 ? file.uploaded_at.substring(0, 19) : file.uploaded_at) : 'Unknown';
            const details = [];
            
            // LDX file details
            if (file.file_type === 'ldx') {
                if (file['Total Laps']) details.push(`Laps: ${file['Total Laps']}`);
                if (file['Fastest Time']) details.push(`Fastest: ${file['Fastest Time']}`);
                if (file['Fastest Lap']) details.push(`Lap #${file['Fastest Lap']}`);
                if (file.total_markers) details.push(`Markers: ${file.total_markers}`);
            }
            
            // LD file details
            if (file.file_type === 'ld') {
                if (file.date) details.push(`Date: ${file.date}`);
                if (file.time) details.push(`Time: ${file.time}`);
                if (file.driver_name) details.push(`Driver: ${file.driver_name}`);
                if (file.device_name) details.push(`Device: ${file.device_name}`);
                if (file.track_name) details.push(`Track: ${file.track_name}`);
            }
            
            const detailsText = details.length > 0 ? details.join('<br>') : '-';
            
            return `
                <tr>
                    <td><strong>${escapeHtml(file.filename || 'Unknown')}</strong></td>
                    <td><span style="text-transform: uppercase;">${escapeHtml(file.file_type || 'unknown')}</span></td>
                    <td>${escapeHtml(size)}</td>
                    <td>${escapeHtml(uploaded)}</td>
                    <td style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.4;">${detailsText}</td>
                    <td>
                        <button class="btn-small btn-secondary" onclick="parseMotecFile('${escapeHtml(file.id || '')}')">Parse</button>
                        <button class="btn-small btn-primary" onclick="downloadMotecFile('${escapeHtml(file.id || '')}')">Download</button>
                        <button class="btn-small btn-danger" onclick="deleteMotecFile('${escapeHtml(file.id || '')}', '${escapeHtml(file.filename || 'Unknown')}')">Delete</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading MoTeC files:', error);
        let errorMessage = 'Error loading files';
        
        if (error.name === 'AbortError') {
            errorMessage = 'Request timed out. Please refresh the page.';
        } else if (error.message) {
            errorMessage = `Error: ${error.message}`;
        }
        
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--danger);">${escapeHtml(errorMessage)}</td></tr>`;
    }
}

async function uploadMotecFile() {
    const fileInput = document.getElementById('motec-file-input');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        showMessage('Please select a file to upload', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    // Determine file type
    const fileType = file.name.toLowerCase().endsWith('.ldx') ? 'ldx' : 'ld';
    formData.append('file_type', fileType);
    
    try {
        const response = await fetch('/api/motec/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (response.ok && data) {
            let message = `File ${file.name} uploaded successfully`;
            
            // Show session information if available
            if (data.session) {
                const session = data.session;
                if (session.parameters_captured !== undefined) {
                    message += ` - Session captured with ${session.parameters_captured} parameters`;
                }
                if (session.performance_data && session.performance_data.fastest_time) {
                    message += ` | Fastest: ${session.performance_data.fastest_time}`;
                }
            }
            
            showMessage(message, 'success');
            fileInput.value = ''; // Clear input
            loadMotecFiles(); // Reload list
            loadSessions(); // Reload sessions
            loadParameters(); // Reload parameters in case new ones were added
        } else {
            const errorMsg = (data && data.detail) ? data.detail : 'Error uploading file';
            showMessage(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showMessage('Network error: ' + error.message, 'error');
    }
}

function downloadMotecFile(fileId) {
    window.open(`/api/motec/files/${encodeURIComponent(fileId)}/download`, '_blank');
}

async function parseMotecFile(fileId) {
    try {
        const response = await fetch(`/api/motec/files/${encodeURIComponent(fileId)}/parse`);
        const data = await response.json();
        
        if (response.ok) {
            // Display parsed data in a modal or alert
            const parsedData = data.parsed_data;
            let content = `<h3>Parsed Data: ${escapeHtml(parsedData.filename)}</h3><pre style="max-height: 500px; overflow: auto; background: var(--card-bg); padding: 1rem; border-radius: 4px;">${escapeHtml(JSON.stringify(parsedData, null, 2))}</pre>`;
            
            // Create a simple modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 800px;">
                    <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
                    ${content}
                    <button class="btn-primary" onclick="this.closest('.modal').remove()" style="margin-top: 1rem;">Close</button>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Close on outside click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
        } else {
            showMessage(data.detail || 'Error parsing file', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

async function deleteMotecFile(fileId, filename) {
    if (!confirm(`Delete file "${filename}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/motec/files/${encodeURIComponent(fileId)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (response.ok) {
            showMessage(`File ${filename} deleted successfully`, 'success');
            loadMotecFiles(); // Reload list
        } else {
            showMessage(data.detail || 'Error deleting file', 'error');
        }
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
