"""
Pytest configuration and fixtures for USC Racing Parameter Management System
"""
import pytest
import asyncio
import aiosqlite
from pathlib import Path
import tempfile
import shutil
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test_parameters.db"
    
    # Create data directory structure
    (temp_dir / "motec_files" / "ldx").mkdir(parents=True)
    (temp_dir / "motec_files" / "ld").mkdir(parents=True)
    
    # Set environment variable to use temp database
    import os
    original_data_dir = os.environ.get("DATA_DIR")
    os.environ["DATA_DIR"] = str(temp_dir)
    
    yield db_path
    
    # Cleanup
    if original_data_dir:
        os.environ["DATA_DIR"] = original_data_dir
    else:
        os.environ.pop("DATA_DIR", None)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="function")
def client(temp_db):
    """Create a test client with temporary database"""
    return TestClient(app)

@pytest.fixture(scope="function")
async def test_db(temp_db):
    """Initialize test database"""
    from internal.database import init_db
    await init_db()
    return temp_db

@pytest.fixture(scope="function")
def admin_session(client, test_db):
    """Create an admin session"""
    # Login as admin
    response = client.post("/login", data={
        "username": "admin",
        "password": "admin"
    })
    assert response.status_code == 303  # Redirect
    return client

@pytest.fixture(scope="function")
def user_session(client, test_db):
    """Create a regular user session"""
    # First create a test user
    from internal.database import create_user
    import asyncio
    asyncio.run(create_user("testuser", "testpass", "user", "Suspension"))
    
    # Login
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 303
    return client
