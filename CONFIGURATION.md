# Configuration Guide

The trackside telemetry system is fully configurable with no hardcoded values. All settings can be configured via environment variables or a `.env` file.

## Quick Start

1. Copy the example configuration:
   ```bash
   cp config.example.env .env
   ```

2. Edit `.env` with your settings

3. Run the server - it will automatically load your configuration

## Configuration Options

### Server Configuration

- `TEL_HOST` - Server host (default: `0.0.0.0`)
- `TEL_PORT` - Server port (default: `8000`)
- `TEL_RELOAD` - Enable auto-reload for development (default: `false`)
- `TEL_LOG_LEVEL` - Logging level: `debug`, `info`, `warning`, `error` (default: `info`)

### CORS Configuration

- `TEL_CORS_ORIGINS` - Allowed origins, comma-separated or `*` for all (default: `*`)

### WebSocket Configuration

- `TEL_WS_UPDATE_RATE` - WebSocket update rate in Hz (default: `10.0`)

### Data Logging

- `TEL_DATA_DIR` - Directory for storing telemetry logs (default: `data`)
- `TEL_LOG_ENABLED` - Enable data logging (default: `true`)
- `TEL_LOG_PREFIX` - Prefix for log files (default: `telemetry`)

### Telemetry Device

- `TEL_DEVICE_PORT` - Serial port for telemetry device (e.g., `/dev/ttyUSB0` or `COM3`)
- `TEL_DEVICE_BAUD` - Baud rate for serial communication (default: `115200`)
- `TEL_DEVICE_UPDATE_RATE` - Device update rate in Hz (default: `10.0`)
- `TEL_API_URL` - API server URL (default: `http://localhost:8000`)

### Telemetry Schema

- `TEL_SCHEMA_FILE` - Path to JSON file defining telemetry data schema (optional)

## Telemetry Schema

You can define a custom telemetry schema by creating a JSON file. See `config/telemetry_schema.example.json` for the format.

The schema allows you to:
- Define all telemetry fields
- Set default values
- Specify units and ranges
- Add descriptions

## Environment Variables vs .env File

Settings are loaded in this order (later overrides earlier):
1. Default values in code
2. `.env` file (if exists)
3. Environment variables

## Example Configuration

```bash
# Production trackside setup
TEL_HOST=0.0.0.0
TEL_PORT=8000
TEL_RELOAD=false
TEL_LOG_LEVEL=info
TEL_CORS_ORIGINS=*
TEL_WS_UPDATE_RATE=20.0
TEL_LOG_ENABLED=true
TEL_DEVICE_PORT=/dev/ttyUSB0
TEL_DEVICE_BAUD=115200
TEL_DEVICE_UPDATE_RATE=20.0
```

## Running with Custom Configuration

### Server
```bash
# Using .env file (automatic)
python3 backend/main.py

# Using environment variables
TEL_PORT=9000 TEL_WS_UPDATE_RATE=20.0 python3 backend/main.py
```

### Telemetry Device
```bash
# Using .env file
python3 backend/internal/telemetry_device.py

# Using command line arguments
python3 backend/internal/telemetry_device.py /dev/ttyUSB0 --rate 20.0

# Using environment variables
TEL_DEVICE_PORT=/dev/ttyUSB0 TEL_DEVICE_UPDATE_RATE=20.0 python3 backend/internal/telemetry_device.py
```

### Aero Configuration

- `AERO_REF_DYNAMIC_PORT` - Dynamic reference pressure port (default: `7`)
- `AERO_REF_STATIC_PORT` - Static reference pressure port (default: `8`)
- `AERO_NUM_PORTS` - Total number of pressure ports (default: `8`)
- `AERO_STRAIGHT_THRESHOLD` - Steering threshold for straight detection (default: `0.1`)
- `AERO_TURN_THRESHOLD` - Steering threshold for turn detection (default: `0.3`)
- `AERO_LATERAL_G_THRESHOLD` - Lateral G-force threshold (default: `0.2`)
- `AERO_AVG_WINDOW_SIZE` - Averaging window size for scenarios (default: `100`)
- `AERO_HISTOGRAM_BINS` - Number of histogram bins (default: `20`)
- `AERO_HISTOGRAM_RANGE` - Histogram range as "min,max" (default: `-3.0,3.0`)
- `AERO_HISTOGRAM_UPDATE_INTERVAL_MS` - Frontend histogram update interval in ms (default: `2000`)

## Track-Ready Checklist

- [x] All hardcoded values removed ✓
- [x] Configuration via environment variables ✓
- [x] Telemetry schema configurable ✓
- [x] Update rates configurable ✓
- [x] Ports and hosts configurable ✓
- [x] Data logging configurable ✓
- [x] CORS origins configurable ✓
- [x] Aero settings configurable ✓
- [x] Histogram settings configurable ✓

