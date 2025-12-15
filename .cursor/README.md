# Cursor Configuration for USC Racing

This directory contains Cursor-specific configuration and guidelines.

## Active Configuration

The `.cursorrules` file in the project root is automatically loaded by Cursor and contains:
- Architecture preservation rules
- Project-specific patterns
- Development workflow guidelines
- Forbidden/required actions

## Quick Start for AI Development

When working on this project, Cursor will:

1. **Always audit** existing code before making changes
2. **Extend** rather than replace functionality
3. **Add configuration** for all new features
4. **Preserve** existing API contracts and data structures
5. **Test** that existing functionality still works

## Key Files to Know

- **Configuration**: `backend/internal/config/settings.py`
- **Aero Engine**: `backend/internal/aero/calculations.py`
- **Main Server**: `backend/main.py`
- **Frontend**: `frontend/templates/index.html` + `frontend/static/js/app.js`
- **Config Examples**: `config.example.env`

## Common Tasks

### Add New Telemetry Field
→ Extend `settings.get_initial_telemetry_data()`
→ Add display in frontend template
→ Add update in `app.js`

### Add New Aero Calculation
→ Add method to `AeroCalculations` class
→ Use existing reference ports from config
→ Preserve existing calculation methods

### Add New Configuration
→ Add to `settings.py` with `os.getenv()`
→ Update `config.example.env`
→ Document in `CONFIGURATION.md`

### Add New API Endpoint
→ Add route to `main.py`
→ Use settings for config values
→ Maintain JSON response format

## Testing After Changes

Always verify:
- [ ] Server starts without errors
- [ ] WebSocket connection works
- [ ] Existing telemetry displays
- [ ] Aero calculations function
- [ ] Histograms update
- [ ] Configuration loads
- [ ] No console errors

## Need Help?

See `CURSOR_GUIDELINES.md` for detailed examples and patterns.


