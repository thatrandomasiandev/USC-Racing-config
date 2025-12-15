"""
Vercel serverless function entry point for FastAPI
This file must be in the api/ directory for Vercel to recognize it
"""
import sys
import os
from pathlib import Path

# Vercel's working directory is the project root
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Add backend directory to Python path so we can import main
# This allows main.py to use 'from internal.config.settings import settings'
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Set environment variables BEFORE imports
os.environ.setdefault("TEL_HOST", "0.0.0.0")
os.environ.setdefault("TEL_PORT", "8000")
os.environ.setdefault("TEL_CORS_ORIGINS", "*")
os.environ.setdefault("TEL_LOG_ENABLED", "false")
os.environ.setdefault("TEL_DATA_DIR", "/tmp")
# Disable MoTeC on Vercel (read-only filesystem, no NAS access)
os.environ.setdefault("MOTEC_ENABLED", "false")
os.environ.setdefault("MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP", "false")

# Set paths for templates and static files (Vercel read-only filesystem)
# These should exist in the repo
os.environ.setdefault("TEL_TEMPLATES_DIR", str(PROJECT_ROOT / "frontend" / "templates"))
os.environ.setdefault("TEL_STATIC_DIR", str(PROJECT_ROOT / "frontend" / "static"))

# Import the FastAPI app
# Change to backend directory to ensure relative imports work
# This is important because main.py uses 'from internal.config.settings'
original_cwd = os.getcwd()
try:
    os.chdir(str(BACKEND_DIR))
    # Now import main - it will resolve 'internal' as backend/internal
    from main import app
finally:
    os.chdir(original_cwd)

# Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
from mangum import Mangum

# Export the handler - Mangum wraps FastAPI for serverless
handler = Mangum(app, lifespan="off")
