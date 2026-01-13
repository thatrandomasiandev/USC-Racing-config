"""
Test user management functionality
"""
import pytest

def test_get_users(admin_session):
    """Test getting all users"""
    response = admin_session.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)

def test_create_user(admin_session):
    """Test creating a new user"""
    response = admin_session.post("/api/users", json={
        "username": "newuser",
        "password": "newpass",
        "role": "user",
        "subteam": "Suspension"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_update_user_role(admin_session):
    """Test updating user role"""
    # Create a user first
    admin_session.post("/api/users", json={
        "username": "roleuser",
        "password": "pass",
        "role": "user",
        "subteam": "Suspension"
    })
    
    # Update role
    response = admin_session.patch("/api/users/roleuser/role?role=admin")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_update_user_subteam(admin_session):
    """Test updating user subteam"""
    # Create a user first
    admin_session.post("/api/users", json={
        "username": "subteamuser",
        "password": "pass",
        "role": "user",
        "subteam": "Suspension"
    })
    
    # Update subteam
    response = admin_session.patch("/api/users/subteamuser/subteam?subteam=Aero")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_delete_user(admin_session):
    """Test deleting a user"""
    # Create a user first
    admin_session.post("/api/users", json={
        "username": "deleteuser",
        "password": "pass",
        "role": "user",
        "subteam": "Suspension"
    })
    
    # Delete user
    response = admin_session.delete("/api/users/deleteuser")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify user is in deleted list
    deleted_response = admin_session.get("/api/users/deleted")
    assert deleted_response.status_code == 200
    deleted_data = deleted_response.json()
    assert any(u["username"] == "deleteuser" for u in deleted_data["deleted_users"])

def test_non_admin_cannot_manage_users(user_session):
    """Test non-admin cannot access user management"""
    response = user_session.get("/api/users")
    assert response.status_code == 403
