"""
Test authentication and authorization
"""
import pytest
from fastapi.testclient import TestClient

def test_login_page_loads(client):
    """Test login page is accessible"""
    response = client.get("/login")
    assert response.status_code == 200
    assert "login" in response.text.lower()

def test_login_success(client, test_db):
    """Test successful login"""
    response = client.post("/login", data={
        "username": "admin",
        "password": "admin"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_login_failure(client, test_db):
    """Test failed login"""
    response = client.post("/login", data={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 200
    assert "invalid" in response.text.lower()

def test_logout(admin_session):
    """Test logout"""
    response = admin_session.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

def test_protected_route_requires_auth(client, test_db):
    """Test that protected routes require authentication"""
    response = client.get("/")
    assert response.status_code == 303
    assert "/login" in response.headers["location"]

def test_admin_can_access_all_parameters(admin_session):
    """Test admin can see all parameters"""
    response = admin_session.get("/api/parameters")
    assert response.status_code == 200
    data = response.json()
    assert "parameters" in data

def test_user_can_only_see_own_subteam(user_session):
    """Test regular user can only see their subteam's parameters"""
    response = user_session.get("/api/parameters")
    assert response.status_code == 200
    data = response.json()
    # User should only see Suspension subteam parameters
    for param in data["parameters"]:
        assert param["subteam"] == "Suspension"
