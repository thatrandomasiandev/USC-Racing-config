"""
Vercel serverless function entry point for FastAPI
This file must be in the api/ directory for Vercel to recognize it
"""
import sys
import os
import json
from pathlib import Path
import traceback

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

# Import the FastAPI app with comprehensive error handling
app = None
import_error = None

try:
    # Change to backend directory to ensure relative imports work
    # This is important because main.py uses 'from internal.config.settings'
    original_cwd = os.getcwd()
    try:
        os.chdir(str(BACKEND_DIR))
        # Now import main - it will resolve 'internal' as backend/internal
        from main import app
    finally:
        os.chdir(original_cwd)
except Exception as e:
    import_error = {
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc(),
        "cwd": os.getcwd(),
        "backend_dir": str(BACKEND_DIR),
        "backend_exists": BACKEND_DIR.exists(),
        "sys_path": sys.path[:5]  # First 5 entries
    }
    print(f"IMPORT ERROR: {import_error}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)

# If import failed, create error app
if app is None:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    error_app = FastAPI(title="USC Racing - Error")
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to import FastAPI app",
                "details": import_error,
                "message": "Check Vercel function logs for full traceback"
            }
        )
    
    app = error_app

# Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # If Mangum fails, create a simple handler
    print(f"MANGUM ERROR: {str(e)}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    
    def handler(event, context):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Mangum initialization failed",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
        }
