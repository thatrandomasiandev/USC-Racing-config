# MoTeC UI/UX Configuration Guide

The MoTeC integration includes a complete UI-driven configuration system, allowing all MoTeC settings to be managed through the web interface.

## UI Access

Navigate to the **MoTeC** tab in the trackside interface to access:
- Integration status
- Global settings
- Car profiles management
- Channel mappings
- LD file discovery and session linking

## UI Features

### 1. Status Dashboard

Shows at-a-glance information:
- Integration enabled/disabled status
- Number of LD files found
- Number of cars configured
- Real-time status updates

### 2. Global Settings Form

Editable settings:
- **Enable MoTeC Integration**: Toggle on/off
- **NAS Base Path**: Network storage location
- **LD File Pattern**: File matching pattern (default: `*.ld`)
- **Auto-generate LDX**: Automatically create LDX files for new sessions
- **Overwrite Policy**: How to handle existing LDX files
  - Never: Don't overwrite
  - If Safe: Overwrite if file is older
  - Always: Always overwrite

**Note**: Some settings require server restart to take full effect.

### 3. Car Profiles Management

**View Cars**: Table showing all configured cars with:
- Car ID
- Name
- Class
- Number of channel mappings
- Edit/Delete actions

**Add Car**: Modal form to create new car profile with:
- Car ID (required)
- Name
- Class
- Year
- Default track
- Default driver

**Edit Car**: Same form pre-filled with existing data

**Delete Car**: Confirmation dialog before deletion

### 4. Channel Mappings

**Select Car**: Dropdown to choose which car's mappings to view/edit

**View Mappings**: Table showing:
- Internal channel name
- MoTeC channel name
- Units
- Source (CAN, analog, digital, derived, calculated)
- Enabled status
- Edit/Delete actions

**Add Mapping**: Modal form with:
- Internal name (required)
- MoTeC name (required)
- Units (required)
- Source type (required)
- Math expression (for calculated channels)
- Enabled toggle
- Description

**Edit Mapping**: Same form pre-filled with existing data

**Delete Mapping**: Confirmation before deletion

### 5. LD Files & Sessions

**Scan for LD Files**: Button to discover LD files in configured directories
- Shows file list with validation status
- Displays file size and channel count
- Shows errors if files are invalid

**Discover Sessions**: Button to automatically:
- Scan for LD files
- Extract metadata
- Link to sessions
- Generate LDX files (if auto-generation enabled)

**File Display**: Cards showing:
- File name
- Validation status
- File size
- Channel count
- Error messages (if any)

## UI Workflow

### Adding a New Car with Mappings

1. Click "Add Car" button
2. Fill in car profile form
3. Save car profile
4. Select car from dropdown
5. Click "Add Mapping" for each channel
6. Fill in channel mapping form
7. Save mapping
8. Repeat for all channels

### Linking LD File to Session

1. Click "Scan for LD Files"
2. Review discovered files
3. Click "Discover Sessions" to auto-link
4. Or manually link via API if needed

### Updating Global Settings

1. Modify settings in Global Settings form
2. Click "Save Settings"
3. Review toast notification for success/error
4. Note any settings requiring restart

## API Endpoints Used by UI

- `GET /api/motec/status` - Status and statistics
- `GET /api/motec/config` - Get configuration
- `PATCH /api/motec/config` - Update configuration
- `GET /api/motec/cars` - List all cars
- `POST /api/motec/cars/{car_id}` - Create/update car
- `DELETE /api/motec/cars/{car_id}` - Delete car
- `GET /api/motec/channels/{car_id}` - Get channel mappings
- `POST /api/motec/channels/{car_id}` - Save channel mappings
- `GET /api/motec/ld/files` - List LD files
- `GET /api/motec/sessions/discover` - Auto-discover sessions

## Validation & Error Handling

### Client-Side Validation
- Required fields marked with *
- Form validation before submission
- Disabled states during save operations

### Server-Side Validation
- All API endpoints validate input
- Error messages returned in JSON
- Toast notifications show errors

### Error Display
- Toast notifications for success/error
- Inline error messages in forms
- Status badges for file validation
- Error details in file cards

## Responsive Design

The MoTeC UI adapts to different screen sizes:
- Tables scroll horizontally on mobile
- Forms stack vertically on small screens
- Modals adjust to viewport size
- Navigation collapses on mobile

## Future UI Enhancements

Planned improvements:
- Live preview of LDX structure
- Visual math expression editor
- Auto-suggest mappings from LD files
- Drag-and-drop channel reordering
- Batch operations for multiple cars
- Export/import configuration
- Configuration templates
- Session workflow visualization


