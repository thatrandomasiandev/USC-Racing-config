# Trackside Reliability & UI Guidelines

This document outlines the reliability and UI requirements for trackside operations.

## Core Principles

**Priority Order:**
1. **Straightforward UI** - No confusion
2. **Reliability** - No crashes, no data corruption
3. **Accuracy** - Correct MoTeC config and mappings
4. **Speed** - Fewest clicks/steps possible

## UI Requirements

### Obvious at a Glance
- Plain language labels (no jargon)
- Short helper text (one sentence)
- Clear visual hierarchy
- Status icons: ✅ Success, ⚠️ Warning, ❌ Error

### Minimal but Powerful
- Show only what's needed right now
- Hide advanced options behind "Advanced" sections
- Avoid overwhelming tables

### Fast to Operate
- Keyboard-friendly controls
- Clear primary actions
- Single-page control surfaces (avoid wizards)

### Consistent
- Same button placements
- Same spacing and typography
- Same patterns for dialogs

## Reliability Requirements

### No Silent Failures
- All failures clearly indicated in UI
- Logged with context
- Provide next steps

### No Destructive Defaults
- Never overwrite without explicit confirmation
- Batch actions require confirmation with description

### Safe Write Patterns
- Use temp files (`*.tmp` then replace)
- Validate before finalizing
- Atomic file operations

### Robust Error Handling
- Catch all exceptions
- Show localized errors
- Keep rest of UI functional
- Never crash entire app

### Clear Status Indicators
- Idle / In Progress / Succeeded / Failed
- Use icons: ✅ ⚠️ ❌
- Include timestamps for operations

## Accuracy Requirements

### Validate Before Committing
- Required channels exist
- Units are consistent
- Paths are valid and writable
- Block writes if validation fails

### Prevent Accidental Misconfiguration
- Show old vs new values
- Warn if disabling/renaming common channels
- Preview before major changes

### Deterministic Behavior
- Same inputs → same outputs
- Document auto-inference
- Avoid "magic" behaviors

## Optimized Trackside Flows

### Attach LD File to Session
1. Select session
2. See suggested LDs
3. Click to attach
4. Show success/error immediately

### Generate/Update LDX
1. Button: "Generate LDX"
2. Optional preview
3. Confirmation if overwriting
4. Clear success + file path

### Edit Channel Mappings
1. Table view
2. Inline or row-based edit
3. Bulk save with validation
4. Show validation errors clearly

### System Health Check
Compact overview showing:
- NAS reachable: Yes/No
- LD discovery OK: Yes/No
- LDX template present: Yes/No
- Config validity: OK/Warnings/Errors

## Design Filter

For every feature, ask:
- **Straightforward?** Enough for a tired engineer at the track?
- **Reliable?** Trustworthy during a live session?
- **Accurate?** MoTeC receives exactly what's intended?

If not all "yes", refine until they are.

## Implementation Examples

### Safe File Writing
```python
# Write to temp file first
temp_path = file_path.with_suffix('.ldx.tmp')
tree.write(temp_path)
# Validate
ET.parse(temp_path)
# Atomic replace
temp_path.replace(file_path)
```

### Error Display
```javascript
// Clear, actionable error messages
showToast('❌ LD file not found. Check path: /mnt/nas/motec/', 'error');
```

### Status Indicators
```html
<!-- Simple, scannable -->
<div class="status-badge enabled">✅ Enabled</div>
<div class="status-item">
    <span>LD Files:</span>
    <span>5</span>
</div>
```

## Forbidden Patterns

❌ Silent failures
❌ Destructive actions without confirmation
❌ Complex multi-step wizards
❌ Unnecessary animations
❌ Jargon without explanation
❌ Overwhelming information density
❌ Magic behaviors (auto-inference without visibility)

## Required Patterns

✅ Clear error messages with next steps
✅ Confirmation dialogs for destructive actions
✅ Status indicators for all operations
✅ Validation before committing
✅ Safe write patterns (temp files)
✅ Simple, scannable UI
✅ Plain language labels
✅ Fast, keyboard-friendly operations


