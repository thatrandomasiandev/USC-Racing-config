# USC Racing - Cursor Development Guidelines

This document provides detailed guidelines for AI-assisted development on the USC Racing trackside telemetry system.

## Philosophy

**Build on top, never replace.**

This project is a production trackside telemetry system. All development must:
- Preserve existing functionality
- Extend rather than replace
- Maintain backwards compatibility
- Support configuration-driven customization
- Ensure production stability

## Architecture Overview

### Current System Structure

```
USC Racing/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── internal/
│   │   ├── config/
│   │   │   └── settings.py        # Centralized configuration
│   │   ├── aero/
│   │   │   └── calculations.py   # Aero calculations engine
│   │   └── telemetry_device.py   # Device interface
│   └── requirements.txt
├── frontend/
│   ├── templates/
│   │   └── index.html            # Main UI template
│   └── static/
│       ├── css/style.css         # Styling
│       └── js/app.js             # Frontend logic
├── data/                          # Telemetry data storage
├── config/                        # Configuration examples
└── .env                          # Environment configuration
```

### Key Technologies

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Real-time**: WebSocket
- **Data**: JSONL logging
- **Configuration**: Environment variables + .env files

## Development Rules

### Rule 1: Always Audit First

Before making any changes:

1. **Read existing code** related to your change
2. **Identify integration points** where new code will connect
3. **Check for existing similar functionality** that could be extended
4. **Review configuration structure** to see where new settings belong
5. **Understand data flow** (telemetry → processing → display)

### Rule 2: Extend Configuration System

All new features must be configurable:

1. **Add to `settings.py`**:
   ```python
   NEW_SETTING: type = os.getenv("NEW_SETTING", "default")
   ```

2. **Update `config.example.env`**:
   ```bash
   NEW_SETTING=default_value
   ```

3. **Document in `CONFIGURATION.md`**

4. **Never hardcode** values

### Rule 3: Preserve API Contracts

When modifying endpoints:

- **Add new endpoints** rather than modifying existing ones
- **Maintain request/response formats** for existing endpoints
- **Add optional fields** to responses, don't remove required ones
- **Version endpoints** if breaking changes are necessary

### Rule 4: Frontend Additive Changes

When updating the UI:

- **Add new sections** to HTML, don't replace entire templates
- **Extend JavaScript classes**, don't replace them
- **Add CSS classes**, preserve existing styling
- **Maintain WebSocket connection** logic

### Rule 5: Aero System Extensions

When working with aero calculations:

- **Extend `AeroCalculations` class** with new methods
- **Preserve existing calculations** (Cp, Cpt, scenario detection)
- **Maintain histogram functionality**
- **Keep standard deviation calculations**

## Common Patterns

### Adding a New Telemetry Field

1. **Schema Extension**:
   ```python
   # In settings.py - get_initial_telemetry_data()
   data["new_field"] = 0.0
   ```

2. **Backend Processing**:
   ```python
   # In main.py - update_telemetry()
   # Field automatically handled if in schema
   ```

3. **Frontend Display**:
   ```html
   <!-- In index.html -->
   <div class="metric-card">
       <div class="metric-label">New Field</div>
       <div class="metric-value" id="new-field">0</div>
   </div>
   ```
   ```javascript
   // In app.js - updateDisplay()
   this.updateMetric('new-field', data.new_field || 0);
   ```

### Adding a New API Endpoint

```python
# In main.py
@app.get("/api/new-endpoint")
async def new_endpoint():
    """New endpoint description"""
    return {"data": "value"}
```

### Adding Configuration

```python
# In settings.py
NEW_CONFIG: str = os.getenv("NEW_CONFIG", "default")

# In config.example.env
NEW_CONFIG=default_value
```

## Testing Checklist

After any changes:

- [ ] Existing telemetry fields still display
- [ ] WebSocket connection works
- [ ] Configuration loads correctly
- [ ] Aero calculations still function
- [ ] Histograms update properly
- [ ] Data logging continues
- [ ] No console errors
- [ ] Server starts without errors

## Production Considerations

All changes must consider:

1. **Uptime**: System runs 24/7 during track sessions
2. **Performance**: Real-time updates at 10Hz+
3. **Data Integrity**: All telemetry must be logged
4. **Error Handling**: Graceful degradation, no crashes
5. **Configuration**: Easy adjustment without code changes
6. **Monitoring**: Health checks and status endpoints

## Migration Notes Format

When introducing changes that require migration:

```markdown
## Migration Notes

### Configuration Updates
- Add `NEW_SETTING=value` to your `.env` file
- Restart server to apply changes

### Data Format Changes
- Existing data remains compatible
- New fields will default to 0 if not present

### API Changes
- New endpoint: `/api/new-endpoint`
- Existing endpoints unchanged
```

## Forbidden Actions

❌ **Never**:
- Delete existing telemetry fields
- Replace the FastAPI app structure
- Hardcode configuration values
- Remove existing functionality
- Break WebSocket real-time updates
- Remove aero calculation features
- Replace frontend UI structure
- Delete data logging

## Required Actions

✅ **Always**:
- Extend existing code
- Add configuration for new features
- Preserve API contracts
- Maintain backwards compatibility
- Test existing functionality
- Document new features
- Follow existing patterns
- Consider production use

## Example: Complete Feature Addition

### Scenario: Add wind speed telemetry

1. **Audit**: Check existing telemetry schema, frontend display, config system

2. **Extend Schema**:
   ```python
   # settings.py
   data["wind_speed"] = 0.0
   ```

3. **Add Config** (if needed):
   ```python
   # settings.py
   WIND_SENSOR_ENABLED: bool = os.getenv("WIND_SENSOR_ENABLED", "false").lower() == "true"
   ```

4. **Extend Frontend**:
   ```html
   <!-- index.html - add to secondary metrics -->
   <div class="metric-card">
       <div class="metric-label">Wind Speed</div>
       <div class="metric-value" id="wind-speed">0</div>
       <div class="metric-unit">mph</div>
   </div>
   ```
   ```javascript
   // app.js - updateDisplay()
   this.updateMetric('wind-speed', (data.wind_speed || 0).toFixed(1));
   ```

5. **Update Config Example**:
   ```bash
   # config.example.env
   WIND_SENSOR_ENABLED=false
   ```

6. **Document**:
   ```markdown
   # CONFIGURATION.md
   - WIND_SENSOR_ENABLED: Enable wind speed sensor (default: false)
   ```

7. **Test**: Verify existing metrics work, new metric displays, WebSocket updates

## Getting Help

When unsure about how to implement something:

1. Check existing similar functionality
2. Review configuration system
3. Look at how aero calculations are structured
4. Examine frontend update patterns
5. Review API endpoint patterns

Remember: **Extend, don't replace. Configure, don't hardcode. Test, don't assume.**


