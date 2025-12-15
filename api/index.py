"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os
from pathlib import Path

# Get the project root (parent of api directory)
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"

# Add paths to sys.path
paths_to_add = [
    str(project_root),
    str(backend_path),
    str(backend_path / "internal"),
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Set environment variables for Vercel
os.environ.setdefault("TEL_HOST", "0.0.0.0")
os.environ.setdefault("TEL_PORT", "8000")
os.environ.setdefault("TEL_CORS_ORIGINS", "*")
os.environ.setdefault("TEL_LOG_ENABLED", "false")  # Disable logging on Vercel

# Import with better error handling
try:
    # Change to backend directory temporarily for imports
    original_cwd = os.getcwd()
    os.chdir(backend_path)
    
    try:
        from main import app
    finally:
        os.chdir(original_cwd)
    
    # Export app for Vercel
    handler = app
    
except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    
    # Create a minimal error handler
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
                "traceback": error_trace,
                "path": path,
                "sys_path": sys.path[:5],  # First 5 paths
                "cwd": os.getcwd()
            }
        )
    
    handler = error_app

