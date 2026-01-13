# Test Scenario: MoTeC Parameter Management Demo

## Demo Files Location
- **Path**: `data/motec/demo/20251205_EThrottle/`
- **Files**: 17 `.ldx` files and 17 `.ld` files
- **Source**: EThrottle test sessions from 2025-12-07

## Test Scenario Overview

This demo will test the complete parameter management workflow:
1. Upload `.ldx` files
2. Auto-populate parameters from files
3. Edit parameters
4. Update associated `.ldx` files
5. Track session history
6. View parameter history

---

## Step 1: Upload Demo LDX Files

### Files to Upload:
1. `S1_#31435_20251207_155835.ldx` (contains MathItems + Details)
2. `S1_#31435_20251207_152010.ldx` (contains Details only)
3. `S1_#31435_20251207_150108.ldx` (contains Details only)

### Expected Parameters Extracted:

#### From `S1_#31435_20251207_155835.ldx`:
- **Details Parameters:**
  - `ldx_details_Total_Laps` = "6"
  - `ldx_details_Fastest_Time` = "0:33.827"
  - `ldx_details_Fastest_Lap` = "4"

- **MathItems:**
  - `ldx_math_IRIMU_V2_IMU_Acceleration_Z_Axis_scale` = "1"
  - `ldx_math_IRIMU_V2_IMU_Acceleration_Z_Axis_offset` = "1.02"

- **Descriptors:**
  - `ldx_desc_IRIMU_V2_IMU_Acceleration_Z_Axis_dps` = "4"

#### From `S1_#31435_20251207_152010.ldx`:
- `ldx_details_Total_Laps` = "10"
- `ldx_details_Fastest_Time` = "0:35.723"
- `ldx_details_Fastest_Lap` = "2"

#### From `S1_#31435_20251207_150108.ldx`:
- `ldx_details_Total_Laps` = "8"
- `ldx_details_Fastest_Time` = "0:36.388"
- `ldx_details_Fastest_Lap` = "6"

---

## Step 2: Verify Parameters Imported

1. Navigate to "All Parameters" tab
2. Filter by "MoTeC" subteam
3. Verify these parameters appear:
   - `ldx_details_Total_Laps`
   - `ldx_details_Fastest_Time`
   - `ldx_details_Fastest_Lap`
   - `ldx_math_IRIMU_V2_IMU_Acceleration_Z_Axis_scale`
   - `ldx_math_IRIMU_V2_IMU_Acceleration_Z_Axis_offset`
   - `ldx_desc_IRIMU_V2_IMU_Acceleration_Z_Axis_dps`

---

## Step 3: Verify Sessions Created

1. Scroll to "Session History" section
2. Verify sessions were created for each uploaded file
3. Each session should show:
   - File name
   - Upload timestamp
   - Performance data (Total Laps, Fastest Time, Fastest Lap)
   - Parameter snapshot count

---

## Step 4: Edit Parameter - Test LDX Update

### Test Case: Edit Fastest Time Parameter

1. Click "Edit" button on `ldx_details_Fastest_Time` parameter
2. Current value should show: "0:33.827" (from first file)
3. Change to: "0:32.500"
4. Add comment: "Test update for demo"
5. Click "Update Parameter"

### Expected Results:
- ✅ Parameter value updated in database
- ✅ Original value "0:33.827" saved in history
- ✅ `S1_#31435_20251207_155835.ldx` file updated
- ✅ Success message shows: "Parameter updated successfully (1 LDX file updated)"

### Verify LDX File Updated:
1. Open `data/motec_files/ldx/S1_#31435_20251207_155835.ldx`
2. Check Details section:
   ```xml
   <String Id="Fastest Time" Value="0:32.500"/>
   ```

---

## Step 5: Edit MathItem Parameter

### Test Case: Edit IMU Offset

1. Click "Edit" on `ldx_math_IRIMU_V2_IMU_Acceleration_Z_Axis_offset`
2. Current value: "1.02"
3. Change to: "1.05"
4. Update parameter

### Expected Results:
- ✅ Database updated
- ✅ LDX file's MathItem updated:
   ```xml
   <MathScaleOffset ... Offset="1.05"/>
   ```

---

## Step 6: Test Parameter History

1. Click "History" button on `ldx_details_Fastest_Time`
2. Verify history shows:
   - Original value: "0:33.827" → "0:32.500"
   - Updated by: (your username)
   - Timestamp
   - Comment: "Test update for demo"

---

## Step 7: Upload Multiple Files with Same Parameter

### Test Case: Upload Second File

1. Upload `S1_#31435_20251207_152010.ldx`
2. This file also has `ldx_details_Fastest_Time` = "0:35.723"

### Expected Behavior:
- Parameter value in database updates to latest upload value
- Both files are tracked in sessions
- Each file maintains its original parameter value snapshot

---

## Step 8: Edit Parameter Linked to Multiple Files

### Test Case: Update Parameter in All Files

1. Edit `ldx_details_Fastest_Time` again
2. Change to: "0:30.000"
3. Update parameter

### Expected Results:
- ✅ Parameter updated in database
- ✅ **ALL** associated `.ldx` files updated:
   - `S1_#31435_20251207_155835.ldx`
   - `S1_#31435_20251207_152010.ldx`
- ✅ Success message: "Parameter updated successfully (2 LDX files updated)"

### Verify Multiple Files Updated:
Check both LDX files show:
```xml
<String Id="Fastest Time" Value="0:30.000"/>
```

---

## Step 9: Test Car Parameters

1. Click "Initialize Car Parameters" button
2. Verify tire pressure parameters appear:
   - `tire_pressure_fl` = 20.0 psi
   - `tire_pressure_fr` = 20.0 psi
   - `tire_pressure_rl` = 20.0 psi
   - `tire_pressure_rr` = 20.0 psi

3. Edit `tire_pressure_fl`:
   - Change from "20.0" to "22.5"
   - Add comment: "Increased pressure for testing"
   - Update

### Expected Results:
- ✅ Car parameter updated (but no LDX files updated since it's not in LDX)
- ✅ History shows change
- ✅ Parameter stored for future session tracking

---

## Step 10: Test Session Comparison

1. Navigate to Sessions section
2. Verify multiple sessions are listed
3. Each session should show:
   - Different performance data (lap times)
   - Parameter snapshots captured at upload time

---

## Step 11: Test Category Filtering

1. Click "Suspension" tab
2. Verify category dropdown appears
3. Select "Tires" category
4. Should show only tire pressure parameters

---

## Validation Checklist

### ✅ Parameter Import
- [ ] Parameters extracted from LDX files
- [ ] Parameters appear in "All Parameters" table
- [ ] Display names show correctly
- [ ] Units show correctly

### ✅ Session Tracking
- [ ] Sessions created for each uploaded file
- [ ] Performance data captured (lap times, total laps)
- [ ] Parameter snapshots stored

### ✅ Parameter Editing
- [ ] Edit modal opens with current values
- [ ] Can update parameter values
- [ ] History preserved
- [ ] Success messages shown

### ✅ LDX File Updates
- [ ] LDX files updated when parameters change
- [ ] Backup files created (.bak)
- [ ] Correct number of files updated reported
- [ ] XML structure preserved

### ✅ Multi-File Updates
- [ ] Parameter updates propagate to all associated files
- [ ] Each file updated correctly
- [ ] No data corruption

---

## Files for Manual Verification

After testing, verify these files were updated:
- `data/motec_files/ldx/S1_#31435_20251207_155835.ldx`
- `data/motec_files/ldx/S1_#31435_20251207_152010.ldx`
- Backup files: `*.ldx.bak` (should exist)

---

## Expected Database State

### Parameters Table:
- All imported LDX parameters
- All car parameters (tire pressure, etc.)
- Current values from latest uploads

### History Table:
- Record of all parameter changes
- Prior values preserved
- Comments and timestamps

### Sessions:
- One record per uploaded file
- Parameter snapshots
- Performance data

---

## Troubleshooting

### If parameters don't import:
1. Check browser console for errors
2. Verify file upload succeeded
3. Check backend logs

### If LDX files don't update:
1. Verify sessions were created
2. Check file permissions
3. Look for backup files (indicates write attempt)

### If history doesn't show:
1. Check database connection
2. Verify parameter was actually updated
3. Check History button functionality

