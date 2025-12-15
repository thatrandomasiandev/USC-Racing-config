"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set environment variables for Vercel
os.environ.setdefault("TEL_HOST", "0.0.0.0")
os.environ.setdefault("TEL_PORT", "8000")

# Import app
from main import app

# Export app for Vercel
handler = app

