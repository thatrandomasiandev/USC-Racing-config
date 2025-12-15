"""
Simple test function to verify Vercel Python is working
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
@app.get("/{path:path}")
async def test_handler(path: str = ""):
    return JSONResponse({
        "status": "ok",
        "message": "Vercel Python function is working!",
        "path": path
    })

handler = app

