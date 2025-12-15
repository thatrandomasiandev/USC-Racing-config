"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variables for Vercel (if not already set)
os.environ.setdefault("TEL_HOST", "0.0.0.0")
os.environ.setdefault("TEL_PORT", "8000")
os.environ.setdefault("TEL_CORS_ORIGINS", "*")

# Change to backend directory for relative imports
os.chdir(backend_path)

try:
    # Import app from backend
    from main import app
    
    # Export app for Vercel
    handler = app
    
except Exception as e:
    # Create a minimal error handler if import fails
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    error_app = FastAPI()
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Serverless function initialization failed",
                "message": str(e),
                "path": path
            }
        )
    
    handler = error_app

