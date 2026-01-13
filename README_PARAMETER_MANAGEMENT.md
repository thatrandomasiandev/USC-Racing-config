# USC Racing Parameter Management System

Lightweight parameter management system for subteams. Optimized for Raspberry Pi.

## Features

- **Parameter Management**: Update parameters via web form
- **Subteam Organization**: Organize parameters by subteam (Aero, Engine, Suspension, etc.)
- **Alphabetical Sorting**: All parameters sorted alphabetically
- **Audit Trail**: Complete history of all parameter changes
- **User Tracking**: Track who modified each parameter
- **Date Tracking**: Track when each parameter was modified
- **Prior Value Tracking**: See what the value was before each change

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server

```bash
python main.py
```

Or use the run script:
```bash
./run_server.sh
```

### 3. Access Application

- **Main App**: http://localhost:8000
- **Login**: http://localhost:8000/login

### Default Login Credentials

- Username: `admin`, Password: `admin`
- Username: `aero`, Password: `aero`
- Username: `engine`, Password: `engine`
- Username: `suspension`, Password: `suspension`
- Username: `electronics`, Password: `electronics`

## Database

SQLite database stored at: `data/parameters.db`

### Tables

- **parameters**: Current parameter values
- **parameter_history**: Complete audit trail

## API Endpoints

- `GET /` - Main parameter management page
- `GET /login` - Login page
- `POST /login` - Handle login
- `POST /logout` - Logout
- `GET /api/parameters` - Get all parameters (alphabetical)
- `GET /api/parameters?subteam={name}` - Filter by subteam
- `GET /api/parameters/{name}` - Get specific parameter
- `POST /api/parameters` - Update parameter
- `GET /api/history?parameter={name}` - Get parameter history
- `GET /api/search?q={query}` - Search parameters
- `GET /api/subteams` - Get all subteams

## Default Subteams

- Aero
- Engine
- Suspension
- Electronics
- Chassis
- Powertrain

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: SQLite (lightweight, file-based)
- **Frontend**: HTML/CSS/JavaScript (vanilla, no frameworks)
- **Authentication**: Session-based (simple, lightweight)

## Raspberry Pi Optimization

- SQLite (no separate database server)
- Minimal dependencies
- Efficient queries with indexes
- Lightweight frontend (no heavy frameworks)
- Low memory footprint

## File Structure

```
backend/
  main.py              # FastAPI application
  internal/
    database.py        # SQLite database operations
    models.py          # Pydantic models
    auth.py            # Authentication
frontend/
  templates/
    index.html         # Main parameter management page
    login.html         # Login page
  static/
    css/style.css      # Styles
    js/app.js          # Frontend JavaScript
data/
  parameters.db        # SQLite database (created automatically)
```

## Usage

1. Login with your credentials
2. Fill out the form:
   - Select subteam
   - Enter parameter name
   - Enter new value
3. Click "Update Parameter"
4. View all parameters in the table (sorted alphabetically)
5. Click "History" to see change history for any parameter
6. Filter by subteam or search by name

## Notes

- All parameter changes are logged with full audit trail
- Parameters are automatically sorted alphabetically
- History shows: prior value, new value, who changed it, when it was changed
- Database is created automatically on first run

