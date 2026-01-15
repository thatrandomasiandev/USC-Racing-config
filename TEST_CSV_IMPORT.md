# Testing CSV Import

## Quick Test Steps

### 1. Start the Server

```bash
cd backend
python main.py
# or use the run script:
# ./run_server.sh (or run_server.bat on Windows)
```

### 2. Access the API Docs

Open in browser: `http://localhost:8000/docs`

### 3. Import CSV via API

1. Navigate to the `POST /api/car-parameters/import-csv` endpoint in the API docs
2. Click "Try it out"
3. Upload your CSV file (`Config Variables - Sheet1.csv`)
4. Optionally set `overwrite_existing` to `true` if you want to update existing definitions
5. Click "Execute"

### 4. Check Results

The response will show:
- `created`: Number of new definitions created
- `updated`: Number of existing definitions updated
- `skipped`: Number of rows skipped (duplicates or invalid)
- `total_rows`: Total rows processed
- `errors`: List of any errors encountered

### 5. Verify Import

Test the lookup endpoint:
- GET `/api/car-parameters/definitions` - See all definitions
- GET `/api/car-parameters/definitions/link-key/{link_key}` - Look up by link key
  - Example: `/api/car-parameters/definitions/link-key/suspension_damper_fl_hs_rebound`

## Example Link Keys

Based on your CSV, these link keys should be generated:

- `suspension_damper_fl_hs_rebound` (Suspension > Damper > FL HS Rebound)
- `suspension_cct_fl_toe` (Suspension > CCT > FL Toe)
- `powertrain_fuel_added` (Powertrain > (empty tab) > Fuel added)
- `ergo_brake_bias` (Ergo > (empty tab) > Brake Bias)

## Testing with curl (if API docs don't work)

```bash
curl -X POST "http://localhost:8000/api/car-parameters/import-csv" \
  -H "Cookie: your_session_cookie" \
  -F "file=@C:\Users\josht\Downloads\Config Variables - Sheet1.csv" \
  -F "overwrite_existing=false"
```

**Note**: You'll need to login first to get a session cookie, or the endpoint requires admin role authentication.

## Expected Behavior

1. CSV should parse correctly
2. Link keys should be generated for each row
3. Definitions should be created/updated in `data/car_parameters.json`
4. Existing definitions without link_keys remain unchanged (backward compatible)
