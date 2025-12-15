# MoTeC Dashboard Workflow

## Complete Workflow: NAS → Scan → Select → Parse → Display

### Step 1: Connect to NAS (MoTeC Config)

1. Navigate to **MoTeC Config** section
2. In **Global Settings**, configure:
   - **NAS Base Path**: Enter your NAS mount path (e.g., `/mnt/nas/motec`)
   - Enable **MoTeC Integration**
3. Click **"Save Settings"**
4. Click **"Rescan"** button in NAS Status section
5. System will auto-discover NAS and scan for files

**Status Indicators:**
- ✅ Green: NAS connected and accessible
- ❌ Red: NAS not found or not accessible
- Shows: LD Files count, LDX Files count

### Step 2: Scan for .ldx/.ld Files

**Automatic Scanning:**
- NAS is scanned automatically on startup (if enabled)
- Auto-scans every 30 seconds (configurable)
- Files are discovered and cached

**Manual Scanning:**
1. Click **"Rescan"** button in NAS Status
2. Or click **"Scan NAS for Files"** in File Selection section
3. System discovers all `.ldx` and `.ld` files on NAS

**What Gets Scanned:**
- Configured NAS base path
- Subdirectories (recursive)
- Pattern matching: `*.ldx` and `*.ld`

### Step 3: Select .ldx/.ld Files

**In MoTeC Config Section:**
1. Scroll to **"Select Files for Dashboard"** card
2. Click **"Scan NAS for Files"** (if not already scanned)
3. Files appear in a grid with:
   - File name
   - File type badge (LDX/LD)
   - Path, size, modified date
   - Checkbox for selection

**Selection Methods:**
- **Click file card**: Loads immediately to dashboard
- **Checkbox**: Select multiple files (future: batch operations)
- **"Load Selected to Dashboard"**: Loads selected files

**In MoTeC Dashboard Section:**
1. Use dropdown **"Select LDX file..."**
2. Select from discovered files
3. Click **"Load File"** button

### Step 4: Parse .ldx/.ld Files

**LDX Files (XML):**
- Parsed via API endpoint: `GET /api/motec/ldx/{file_path}`
- Extracts:
  - Workspace name
  - Project/Car name
  - Channel definitions (name, units, source, scaling, math)
  - Worksheets
  - Metadata

**LD Files (Binary):**
- Metadata parsed via: `GET /api/motec/ld/files`
- Extracts:
  - File size
  - Sample count
  - Sample rate
  - Channel names (from header)
  - File validity

**Parsing Backend:**
- **Primary**: Python XML parser (ElementTree for LDX)
- **Optional**: Rust parser (10-100x faster, if installed)
- Automatic fallback if Rust parser unavailable

### Step 5: Display Parsed Information on MoTeC Dashboard

**Dashboard Auto-Population:**
- If LDX file loaded: Shows channels from LDX file
- If no file loaded: Shows default MoTeC channels
- Real-time updates from telemetry data

**Display Components:**

1. **Main Display (MoTeC-style)**
   - Black background, white text
   - Workspace/Car/Project header
   - Gear display (large number)
   - RPM gauge (semi-circular with needle)
   - Channel rows (name + value)
   - Lap times (Reference, Running, Gain/Loss)

2. **Channel Grid**
   - Card-based layout
   - Each channel in own card
   - Shows: Label, Value, Unit
   - Color-coded warnings (temp/pressure thresholds)

3. **Real-Time Updates**
   - Pulls from `window.telemetryData`
   - Updates 10 times per second
   - Maps MoTeC channel names to telemetry fields
   - Color coding based on thresholds

**Configuration:**
- Click **"Configure Display"** to:
  - Select which channels to show
  - Toggle gear/RPM/lap times
  - Choose layout style
- Settings persist in localStorage

## Complete User Flow Example

1. **Setup NAS**:
   ```
   MoTeC Config → Global Settings → NAS Base Path: /mnt/nas/motec → Save
   ```

2. **Discover Files**:
   ```
   MoTeC Config → NAS Status → Click "Rescan"
   → Shows: "Found 15 LDX files, 42 LD files"
   ```

3. **Select File**:
   ```
   MoTeC Config → Select Files for Dashboard → Click file card
   OR
   MoTeC Dashboard → Select from dropdown → Click "Load File"
   ```

4. **View Dashboard**:
   ```
   MoTeC Dashboard → See parsed channels displayed
   → Real-time values updating from telemetry
   ```

## Integration Points

### Backend APIs Used:
- `GET /api/motec/nas/status` - NAS connection status
- `POST /api/motec/nas/scan` - Trigger file scan
- `GET /api/motec/nas/files` - Get discovered files
- `GET /api/motec/ldx/{path}` - Parse LDX file
- `GET /api/motec/ld/files` - Get LD file list/metadata

### Frontend Components:
- **MoTeC Config** (`motec.js`): NAS connection, file discovery, selection
- **MoTeC Dashboard** (`motec-dashboard.js`): Display, configuration, updates
- **Shared State**: `window.telemetryData` for real-time values

## Troubleshooting

**NAS Not Connecting:**
- Check NAS path is correct
- Verify NAS is mounted/accessible
- Check network connectivity
- Review NAS Status section for error messages

**Files Not Found:**
- Click "Rescan" to force new scan
- Check file patterns match (`*.ldx`, `*.ld`)
- Verify files exist on NAS
- Check file permissions

**Dashboard Not Updating:**
- Verify telemetry WebSocket is connected
- Check browser console for errors
- Ensure `window.telemetryData` is populated
- Try reloading the page

**LDX Parse Errors:**
- Verify file is valid XML
- Check file isn't corrupted
- Try Rust parser (if installed) for better error messages

