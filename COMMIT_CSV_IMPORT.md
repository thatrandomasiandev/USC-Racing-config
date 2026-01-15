# Commit CSV Import Feature

Run these commands to commit and push the CSV import feature:

## Commands to Run

```bash
cd "C:\Users\josht\Documents\New folder\USC-Racing-config"

# Check status
git status

# Stage all changes
git add .

# Commit with message
git commit -m "Add link key system and CSV import for car parameter definitions

- Add link_key generation (composite key: subteam_tab_variablename)
- Add tab, inject_type, variable_name, type fields to parameter definitions
- Add get_car_parameter_definition_by_link_key() function
- Create csv_parameter_importer.py module for CSV parsing and import
- Add POST /api/car-parameters/import-csv endpoint (admin only)
- Add GET /api/car-parameters/definitions/link-key/{link_key} endpoint
- Add CarParameterDefinition model to models.py
- Maintain backward compatibility with existing parameter_name lookups"

# Push to GitHub
git push
```

## Files Changed

- `backend/internal/car_parameters.py` - Added link_key support, tab, inject_type fields
- `backend/internal/csv_parameter_importer.py` - New CSV import module
- `backend/internal/models.py` - Added CarParameterDefinition model
- `backend/main.py` - Added CSV import and link_key lookup endpoints
- `test_csv_import.py` - New test script
- `TEST_CSV_IMPORT.md` - New test documentation

## Alternative: Shorter Commit Message

If you prefer a shorter message:

```bash
git commit -m "Add link key system and CSV import for car parameters"
```
