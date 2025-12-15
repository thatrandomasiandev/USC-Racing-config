# MoTeC i2 Integration

The trackside telemetry system includes comprehensive MoTeC i2 integration for LDX (configuration) and LD (logged data) files.

## Overview

The MoTeC integration provides:
- **LDX File Support**: Read, write, and manage MoTeC workspace/configuration files
- **LD File Support**: Discover, validate, and extract metadata from MoTeC log files
- **Channel Mapping**: Map internal telemetry channels to MoTeC i2 channel names
- **Session Linking**: Associate LD files with track sessions
- **Auto-generation**: Automatically generate LDX files from channel mappings

## Configuration

All MoTeC settings are configurable via environment variables:

```bash
# Enable/disable MoTeC integration
MOTEC_ENABLED=true

# NAS base path (optional, for network storage)
MOTEC_NAS_BASE_PATH=/mnt/nas/motec

# LD file discovery
MOTEC_LD_GLOB_PATTERN=*.ld
MOTEC_LD_SCAN_DIR=data/motec/ld

# LDX file management
MOTEC_LDX_TEMPLATE_DIR=config/motec/templates
MOTEC_LDX_OUTPUT_DIR=data/motec/ldx

# Auto-generation settings
MOTEC_AUTO_GENERATE_LDX=false
MOTEC_OVERWRITE_POLICY=ifSafe  # never, ifSafe, always

# Configuration files
MOTEC_CHANNEL_MAPPINGS_FILE=config/motec/channel_mappings.json
MOTEC_CAR_PROFILES_FILE=config/motec/car_profiles.json
```

## Channel Mappings

Channel mappings define how internal telemetry channels map to MoTeC i2 channels.

### Mapping Structure

```json
{
  "car_001": [
    {
      "internal_name": "speed",
      "motec_name": "Speed",
      "units": "mph",
      "source": "CAN",
      "enabled": true,
      "description": "Vehicle speed"
    }
  ]
}
```

### Channel Sources

- `CAN`: CAN bus data
- `analog`: Analog input
- `digital`: Digital input
- `derived`: Derived from other channels
- `calculated`: Calculated using math expressions

### Math Expressions

For calculated channels, use MoTeC math expression syntax:

```json
{
  "internal_name": "cp_port_1",
  "motec_name": "CP Port 1",
  "source": "calculated",
  "math_expression": "(Pressure Port 1 - Pressure Port 8) / (Pressure Port 7 - Pressure Port 8)"
}
```

## API Endpoints

### Status
```bash
GET /api/motec/status
```

Returns MoTeC integration status and statistics.

### LD Files
```bash
GET /api/motec/ld/files?directory=optional
```

List all discovered LD files with metadata.

### LDX Files
```bash
GET /api/motec/ldx/{file_path}
POST /api/motec/ldx/{file_path}
```

Read or write LDX configuration files.

### Channel Mappings
```bash
GET /api/motec/channels/{car_id}
POST /api/motec/channels/{car_id}
```

Get or set channel mappings for a car.

### Session Linking
```bash
POST /api/motec/sessions/link
```

Link an LD file to a track session.

### Session Discovery
```bash
GET /api/motec/sessions/discover?car_id=optional&directory=optional
```

Automatically discover and link LD files to sessions.

### Cars
```bash
GET /api/motec/cars
```

List all configured cars with their profiles and channel counts.

## Usage Examples

### 1. Configure Channel Mappings

```python
# Via API
POST /api/motec/channels/car_001
{
  "channels": [
    {
      "internal_name": "speed",
      "motec_name": "Speed",
      "units": "mph",
      "source": "CAN",
      "enabled": true
    }
  ]
}
```

### 2. Link LD File to Session

```python
POST /api/motec/sessions/link
{
  "ld_file_path": "data/motec/ld/session_001.ld",
  "car_id": "car_001",
  "track_id": "Willow Springs",
  "driver": "Driver 1",
  "date": "2024-12-05"
}
```

### 3. Auto-discover Sessions

```python
GET /api/motec/sessions/discover?car_id=car_001
```

This will:
1. Scan for LD files
2. Extract metadata
3. Link to sessions
4. Auto-generate LDX files if configured

## File Structure

```
config/motec/
├── channel_mappings.json      # Channel mappings per car
├── car_profiles.json          # Car profile configurations
└── templates/                 # LDX template files (optional)

data/motec/
├── ld/                        # LD log files
└── ldx/                       # Generated LDX files
```

## NAS Integration

If `MOTEC_NAS_BASE_PATH` is configured:
- LD files are searched on NAS first
- LDX files can be written to NAS
- Paths are automatically resolved

## Track-Ready Features

- ✅ Non-blocking file operations
- ✅ Graceful fallback if NAS unavailable
- ✅ Configurable overwrite policies
- ✅ Automatic session linking
- ✅ Channel mapping persistence
- ✅ Error handling and validation
- ✅ Production stability

## Future Enhancements

- Support for multiple MoTeC projects/workspaces per car
- UI for channel mapping management
- Background job for auto-scanning NAS
- LD file data extraction and conversion
- Math channel generation from configuration DSL
- Integration with telemetry device for real-time LDX updates


