import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_create_equipment_without_auth(client: TestClient):
    equipment_data = {
        "name": "Test Tractor",
        "type": "tractor",
        "description": "A test tractor",
        "manufacturer": "John Deere",
        "model": "Test Model",
        "year": 2023,
        "hours_used": 100.5,
        "price_per_day": 150.00,
        "location": "Test Location"
    }
    response = client.post(
        f"{settings.API_V1_STR}/equipment/",
        json=equipment_data
    )
    assert response.status_code == 401

def test_update_others_equipment(client: TestClient, user_token_headers: dict, test_superuser: dict):
    # Create equipment as first user
    equipment_data = {
        "name": "Test Tractor",
        "type": "tractor",
        "description": "A test tractor",
        "manufacturer": "John Deere",
        "model": "Test Model",
        "year": 2023,
        "hours_used": 100.5,
        "price_per_day": 150.00,
        "location": "Test Location"
    }
    response = client.post(
        f"{settings.API_V1_STR}/equipment/",
        headers=user_token_headers,
        json=equipment_data
    )
    equipment_id = response.json()["id"]
    
    # Try to update as another user
    login_data = {
        "username": test_superuser["email"],
        "password": test_superuser["password"],
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    other_user_token = {"Authorization": f"Bearer {r.json()['access_token']}"}
    
    update_data = {
        "name": "Updated Tractor",
        "type": "tractor",
        "description": "An updated test tractor",
        "manufacturer": "John Deere",
        "model": "Updated Model",
        "year": 2024,
        "hours_used": 200.5,
        "price_per_day": 200.00,
        "location": "Updated Location"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/equipment/{equipment_id}",
        headers=other_user_token,
        json=update_data
    )
    assert response.status_code == 403

def test_delete_others_equipment(client: TestClient, user_token_headers: dict, test_superuser: dict):
    # Create equipment as first user
    equipment_data = {
        "name": "Test Tractor",
        "type": "tractor",
        "description": "A test tractor",
        "manufacturer": "John Deere",
        "model": "Test Model",
        "year": 2023,
        "hours_used": 100.5,
        "price_per_day": 150.00,
        "location": "Test Location"
    }
    response = client.post(
        f"{settings.API_V1_STR}/equipment/",
        headers=user_token_headers,
        json=equipment_data
    )
    equipment_id = response.json()["id"]
    
    # Try to delete as another user
    login_data = {
        "username": test_superuser["email"],
        "password": test_superuser["password"],
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    other_user_token = {"Authorization": f"Bearer {r.json()['access_token']}"}
    
    response = client.delete(
        f"{settings.API_V1_STR}/equipment/{equipment_id}",
        headers=other_user_token
    )
    assert response.status_code == 403

def test_list_equipment_no_auth_required(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/equipment/")
    assert response.status_code == 200

def test_get_equipment_details_no_auth_required(client: TestClient, user_token_headers: dict):
    # First create an equipment
    equipment_data = {
        "name": "Test Tractor",
        "type": "tractor",
        "description": "A test tractor",
        "manufacturer": "John Deere",
        "model": "Test Model",
        "year": 2023,
        "hours_used": 100.5,
        "price_per_day": 150.00,
        "location": "Test Location"
    }
    response = client.post(
        f"{settings.API_V1_STR}/equipment/",
        headers=user_token_headers,
        json=equipment_data
    )
    equipment_id = response.json()["id"]
    
    # Try to get details without authentication
    response = client.get(f"{settings.API_V1_STR}/equipment/{equipment_id}")
    assert response.status_code == 200