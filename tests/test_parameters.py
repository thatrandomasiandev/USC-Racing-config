"""
Test parameter management functionality
"""
import pytest

def test_get_all_parameters(admin_session):
    """Test getting all parameters"""
    response = admin_session.get("/api/parameters")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["parameters"], list)

def test_create_parameter(admin_session):
    """Test creating a new parameter"""
    response = admin_session.post("/api/parameters", json={
        "parameter_name": "test_param",
        "subteam": "Suspension",
        "new_value": "100",
        "comment": "Test parameter",
        "queue": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["parameter"]["parameter_name"] == "test_param"

def test_update_parameter(admin_session):
    """Test updating an existing parameter"""
    # First create a parameter
    admin_session.post("/api/parameters", json={
        "parameter_name": "test_update",
        "subteam": "Suspension",
        "new_value": "50",
        "queue": False
    })
    
    # Then update it
    response = admin_session.post("/api/parameters", json={
        "parameter_name": "test_update",
        "subteam": "Suspension",
        "new_value": "75",
        "comment": "Updated value",
        "queue": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["parameter"]["current_value"] == "75"

def test_get_parameter_history(admin_session):
    """Test getting parameter history"""
    # Create and update a parameter
    admin_session.post("/api/parameters", json={
        "parameter_name": "test_history",
        "subteam": "Suspension",
        "new_value": "100",
        "queue": False
    })
    admin_session.post("/api/parameters", json={
        "parameter_name": "test_history",
        "subteam": "Suspension",
        "new_value": "200",
        "queue": False
    })
    
    # Get history
    response = admin_session.get("/api/history?parameter=test_history")
    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) >= 2

def test_search_parameters(admin_session):
    """Test searching parameters"""
    # Create a test parameter
    admin_session.post("/api/parameters", json={
        "parameter_name": "searchable_param",
        "subteam": "Suspension",
        "new_value": "100",
        "queue": False
    })
    
    # Search for it
    response = admin_session.get("/api/search?q=searchable")
    assert response.status_code == 200
    data = response.json()
    assert len(data["parameters"]) > 0
    assert any(p["parameter_name"] == "searchable_param" for p in data["parameters"])

def test_queue_parameter_change(admin_session):
    """Test queuing a parameter change"""
    response = admin_session.post("/api/parameters", json={
        "parameter_name": "queued_param",
        "subteam": "Suspension",
        "new_value": "100",
        "comment": "Needs approval",
        "queue": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "form_id" in data

def test_process_queue_item(admin_session):
    """Test processing a queued item"""
    # Add to queue
    queue_response = admin_session.post("/api/parameters", json={
        "parameter_name": "queue_process",
        "subteam": "Suspension",
        "new_value": "100",
        "queue": True
    })
    form_id = queue_response.json()["form_id"]
    
    # Process it
    response = admin_session.post(f"/api/queue/{form_id}/process")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_user_cannot_update_other_subteam(user_session):
    """Test user cannot update parameters from other subteams"""
    # Try to update a parameter from a different subteam
    response = user_session.post("/api/parameters", json={
        "parameter_name": "other_subteam_param",
        "subteam": "Aero",  # User is in Suspension
        "new_value": "100",
        "queue": False
    })
    assert response.status_code == 403
