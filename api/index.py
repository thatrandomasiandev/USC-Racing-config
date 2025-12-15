"""
Vercel serverless function entry point for FastAPI
This file must be in the api/ directory for Vercel to recognize it
"""
import sys
import os
from pathlib import Path

# Vercel's working directory is the project root
# We need to add backend to the path
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Add backend to Python path
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Add internal modules to path
INTERNAL_DIR = BACKEND_DIR / "internal"
if str(INTERNAL_DIR) not in sys.path:
    sys.path.insert(0, str(INTERNAL_DIR))

# Set environment variables
os.environ.setdefault("TEL_HOST", "0.0.0.0")
os.environ.setdefault("TEL_PORT", "8000")
os.environ.setdefault("TEL_CORS_ORIGINS", "*")
os.environ.setdefault("TEL_LOG_ENABLED", "false")
os.environ.setdefault("TEL_DATA_DIR", "/tmp")  # Use /tmp on Vercel (writable)

# Import the FastAPI app
# This must be a simple import - Vercel handles the rest
try:
    # Change to backend directory for imports
    original_cwd = os.getcwd()
    try:
        os.chdir(BACKEND_DIR)
        from main import app
    finally:
        os.chdir(original_cwd)
    
    # Export handler for Vercel
    handler = app
    
except Exception as e:
    # If import fails, create a minimal error handler
    import traceback
    
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    error_app = FastAPI(title="Error Handler")
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_route(path: str = ""):
        error_info = {
            "error": "Failed to initialize application",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "python_path": sys.path[:10],
            "cwd": os.getcwd(),
            "project_root": str(PROJECT_ROOT),
            "backend_dir": str(BACKEND_DIR),
            "backend_exists": BACKEND_DIR.exists(),
            "path": path
        }
        return JSONResponse(status_code=500, content=error_info)
    
    handler = error_app
