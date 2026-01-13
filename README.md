# USC Racing - Parameter Management System

A lightweight parameter management system for USC Racing subteams, optimized for Raspberry Pi deployment.

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or use the convenience script:
   ```bash
   ./run_server.sh
   ```

3. **Access the application:**
   - Main application: http://localhost:8000
   - Login with default credentials: `admin` / `admin`

## Features

- **Parameter Management**: Subteam-specific parameter modification with full audit trail
- **User Management**: Role-based access control (admin/user)
- **Queue System**: Parameter changes can be queued for admin approval
- **Change History**: Complete history of all parameter modifications
- **MoTeC File Support**: Upload and manage .ldx and .ld files
- **Raspberry Pi Optimized**: Lightweight SQLite database, minimal dependencies

## Project Structure

```
USC Racing/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── internal/        # Core modules
│   │   ├── database.py  # SQLite database operations
│   │   ├── models.py    # Pydantic models
│   │   ├── auth.py      # Authentication
│   │   ├── motec_file_manager.py  # MoTeC file handling
│   │   └── ...
│   └── requirements.txt
├── frontend/            # Frontend templates and static files
│   ├── templates/       # HTML templates
│   └── static/          # CSS and JavaScript
├── data/                # Data storage
│   ├── parameters.db    # SQLite database
│   ├── registered_users.json
│   ├── recently_deleted_users.json
│   └── motec_files/     # Uploaded MoTeC files
└── run_server.sh        # Server startup script
```

## Configuration

Environment variables can be set in `.env` file or as system environment variables:

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DATA_DIR`: Data directory path (default: `data/`)
- `CORS_ORIGINS`: CORS allowed origins (default: `*`)

## Requirements

- Python 3.11+
- See `backend/requirements.txt` for Python dependencies

## Network Access

To access the server from other devices on your network, see [NETWORK_ACCESS.md](./NETWORK_ACCESS.md).

## Documentation

- [RUN_LOCAL.md](./RUN_LOCAL.md) - Detailed local development guide
- [README_PARAMETER_MANAGEMENT.md](./README_PARAMETER_MANAGEMENT.md) - Parameter management details
- [CONFIGURATION.md](./CONFIGURATION.md) - Configuration reference
- [TRACKSIDE_RELIABILITY.md](./TRACKSIDE_RELIABILITY.md) - Reliability guidelines
