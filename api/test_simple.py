"""
Minimal test handler for Vercel
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Vercel"}

handler = app

