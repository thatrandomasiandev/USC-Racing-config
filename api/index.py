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

# Import the FastAPI app
# Vercel expects 'handler' to be the ASGI app
try:
    from main import app as handler
except Exception as e:
    # Fallback error handler
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    error_app = FastAPI(title="Error Handler")
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_route(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to initialize application",
                "message": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
    
    handler = error_app
