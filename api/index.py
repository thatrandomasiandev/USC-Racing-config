"""
Vercel serverless function entry point for FastAPI
Simplified version that handles Vercel's environment
"""
import sys
import os
from pathlib import Path

# Get absolute paths
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
backend_path = project_root / "backend"

# Debug: Print paths (will show in Vercel logs)
print(f"Current file: {current_file}")
print(f"Project root: {project_root}")
print(f"Backend path: {backend_path}")
print(f"Backend exists: {backend_path.exists()}")

# Add all necessary paths
paths_to_add = [
    str(project_root),
    str(backend_path),
    str(backend_path / "internal"),
    str(backend_path / "internal" / "config"),
    str(backend_path / "internal" / "aero"),
    str(backend_path / "internal" / "motec"),
]

for path_str in paths_to_add:
    path = Path(path_str)
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))
        print(f"Added to path: {path}")

print(f"Python path: {sys.path[:5]}")

# Set environment variables
os.environ.setdefault("TEL_HOST", "0.0.0.0")
os.environ.setdefault("TEL_PORT", "8000")
os.environ.setdefault("TEL_CORS_ORIGINS", "*")
os.environ.setdefault("TEL_LOG_ENABLED", "false")

# Try to import with detailed error reporting
try:
    print("Attempting to import main...")
    from main import app
    print("Successfully imported app!")
    handler = app
    
except ImportError as e:
    print(f"ImportError: {e}")
    import traceback
    traceback.print_exc()
    
    # Try alternative import
    try:
        print("Trying alternative import path...")
        sys.path.insert(0, str(backend_path))
        os.chdir(backend_path)
        from main import app
        handler = app
        print("Alternative import succeeded!")
    except Exception as e2:
        print(f"Alternative import also failed: {e2}")
        traceback.print_exc()
        
        # Create minimal error app
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        error_app = FastAPI()
        
        @error_app.get("/")
        @error_app.get("/{path:path}")
        async def error_handler(path: str = ""):
            import traceback
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Import failed",
                    "import_error": str(e),
                    "alternative_error": str(e2),
                    "traceback": traceback.format_exc(),
                    "sys_path": sys.path[:10],
                    "cwd": os.getcwd(),
                    "backend_exists": str(backend_path.exists()),
                    "backend_path": str(backend_path)
                }
            )
        
        handler = error_app
        
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    error_app = FastAPI()
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Unexpected error during initialization",
                "message": str(e),
                "traceback": traceback.format_exc(),
                "sys_path": sys.path[:10]
            }
        )
    
    handler = error_app

print("Handler created successfully")
