# Aerodynamics Telemetry System

The trackside telemetry system includes comprehensive aerodynamics support for pressure data analysis.

## Overview

The aero system processes data from 8 pressure ports:
- **Ports 1-6**: Measurement ports for aerodynamic analysis
- **Port 7**: Dynamic reference pressure
- **Port 8**: Static reference pressure

## Calculations

### Coefficient of Pressure (Cp)

For each measurement port (1-6), the system calculates:

```
Cp = (P_port - P_static) / (P_dynamic - P_static)
```

Where:
- `P_port` = Pressure at measurement port (1-6)
- `P_static` = Static reference pressure (Port 8)
- `P_dynamic` = Dynamic reference pressure (Port 7)

### Coefficient of Total Pressure (Cpt)

Similar calculation for total pressure coefficient (currently same as Cp).

## Scenario Detection

The system automatically detects car scenarios based on:
- **Steering angle**: Detects turning vs. straight
- **Lateral G-force**: Confirms turning direction

Scenarios:
- **Straight**: Low steering angle and lateral G
- **Turn Left**: Positive steering or lateral G
- **Turn Right**: Negative steering or lateral G

### Configuration

Thresholds are configurable via environment variables:
- `AERO_STRAIGHT_THRESHOLD` (default: 0.1)
- `AERO_TURN_THRESHOLD` (default: 0.3)
- `AERO_LATERAL_G_THRESHOLD` (default: 0.2)

## Scenario Averaging

The system maintains rolling averages for each scenario:
- Separate averages for straight, turn left, and turn right
- Configurable window size (default: 100 samples)
- Real-time display of average Cp values per port

### Accessing Averages

**API Endpoint:**
```bash
GET /api/aero/averages
```

Returns:
```json
{
  "straight": {
    "cp_port_1_avg": 0.523,
    "cp_port_1_count": 150,
    "cp_port_2_avg": -0.234,
    ...
  },
  "turn_left": { ... },
  "turn_right": { ... }
}
```

**Reset Averages:**
```bash
POST /api/aero/reset?scenario=straight  # Reset specific scenario
POST /api/aero/reset                    # Reset all scenarios
```

## Data Format

### Input (from telemetry device)

```json
{
  "pressure_port_1": 14.7,
  "pressure_port_2": 14.5,
  "pressure_port_3": 14.6,
  "pressure_port_4": 14.8,
  "pressure_port_5": 14.4,
  "pressure_port_6": 14.9,
  "pressure_port_7": 15.0,  // Dynamic reference
  "pressure_port_8": 14.5,  // Static reference
  "steering": 0.2,
  "g_force_lat": 0.5
}
```

### Output (calculated coefficients)

```json
{
  "cp_port_1": 0.400,
  "cp_port_2": 0.000,
  "cp_port_3": 0.200,
  "cp_port_4": 0.600,
  "cp_port_5": -0.200,
  "cp_port_6": 0.800,
  "aero_scenario": "turn_left",
  "aero_averages": {
    "straight": { ... },
    "turn_left": { ... },
    "turn_right": { ... }
  }
}
```

## Configuration

Add to your `.env` file:

```bash
# Aero Configuration
AERO_REF_DYNAMIC_PORT=7
AERO_REF_STATIC_PORT=8
AERO_NUM_PORTS=8
AERO_STRAIGHT_THRESHOLD=0.1
AERO_TURN_THRESHOLD=0.3
AERO_LATERAL_G_THRESHOLD=0.2
AERO_AVG_WINDOW_SIZE=100
```

## Frontend Display

The trackside interface displays:
1. **Pressure Ports**: Real-time pressure values for all 8 ports
2. **Coefficients**: Current Cp values for ports 1-6
3. **Scenario Indicator**: Current detected scenario (color-coded)
4. **Scenario Averages**: Average Cp values with sample counts for each scenario

## Usage

1. **Configure pressure ports** in your telemetry device to send:
   - `pressure_port_1` through `pressure_port_8`
   - `steering` angle
   - `g_force_lat` (lateral G-force)

2. **Send data** via POST to `/api/telemetry` or through WebSocket

3. **View results** in real-time on the trackside display

4. **Access averages** via API or frontend reset button

## Track-Ready Features

- ✅ No hardcoded values - all configurable
- ✅ Real-time coefficient calculations
- ✅ Automatic scenario detection
- ✅ Rolling averages per scenario
- ✅ WebSocket updates for live display
- ✅ Data logging includes all aero calculations


