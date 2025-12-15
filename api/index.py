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

# Add paths to sys.path BEFORE any imports
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "internal"))

# Set environment variables BEFORE imports
os.environ.setdefault("TEL_HOST", "0.0.0.0")
os.environ.setdefault("TEL_PORT", "8000")
os.environ.setdefault("TEL_CORS_ORIGINS", "*")
os.environ.setdefault("TEL_LOG_ENABLED", "false")
os.environ.setdefault("TEL_DATA_DIR", "/tmp")
# Disable MoTeC on Vercel (read-only filesystem, no NAS access)
os.environ.setdefault("MOTEC_ENABLED", "false")
os.environ.setdefault("MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP", "false")

# Import the FastAPI app directly
# Vercel expects 'handler' to be the ASGI app (FastAPI instance)
from main import app

# Export the FastAPI app as 'handler' - this is what Vercel looks for
handler = app
