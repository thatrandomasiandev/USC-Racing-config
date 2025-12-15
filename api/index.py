"""
Vercel serverless function entry point for FastAPI
This file must be in the api/ directory for Vercel to recognize it
"""
import sys
import os
from pathlib import Path
import traceback

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

# Create error handler first (in case imports fail)
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

error_app = FastAPI(title="Error Handler")

@error_app.get("/")
@error_app.get("/{path:path}")
async def error_route(path: str = "", error_msg: str = None, error_type: str = None, error_tb: str = None):
    """Error handler route"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Failed to initialize application",
            "message": error_msg or "Unknown error",
            "type": error_type or "Unknown",
            "traceback": error_tb or "No traceback available",
            "paths": {
                "project_root": str(PROJECT_ROOT),
                "backend_dir": str(BACKEND_DIR),
                "backend_exists": BACKEND_DIR.exists(),
                "sys_path": sys.path[:5]
            }
        }
    )

# Try to import the FastAPI app
# Vercel expects 'handler' to be the ASGI app
handler = None
import_error = None

try:
    from main import app as handler
except Exception as e:
    import_error = e
    # Store error info for error handler
    error_app.state.error_msg = str(e)
    error_app.state.error_type = type(e).__name__
    error_app.state.error_tb = traceback.format_exc()
    handler = error_app

# If handler is still None, use error app
if handler is None:
    handler = error_app
