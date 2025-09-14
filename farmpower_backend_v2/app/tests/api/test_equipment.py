import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.core.config import settings

def test_create_equipment(client: TestClient, user_token_headers: dict):
    equipment_data = {
        "name": "Test Tractor",
        "type": "tractor",
        "description": "A test tractor for agriculture",
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
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == equipment_data["name"]
    assert content["type"] == equipment_data["type"]
    assert "id" in content
    return content

def test_read_equipment(client: TestClient, user_token_headers: dict):
    # First create an equipment
    equipment = test_create_equipment(client, user_token_headers)
    
    response = client.get(
        f"{settings.API_V1_STR}/equipment/{equipment['id']}",
        headers=user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == equipment["name"]
    assert content["type"] == equipment["type"]

def test_list_equipment(client: TestClient, user_token_headers: dict):
    # Create multiple equipment
    test_create_equipment(client, user_token_headers)
    test_create_equipment(client, user_token_headers)
    
    response = client.get(
        f"{settings.API_V1_STR}/equipment/",
        headers=user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2

def test_update_equipment(client: TestClient, user_token_headers: dict):
    # First create an equipment
    equipment = test_create_equipment(client, user_token_headers)
    
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
        f"{settings.API_V1_STR}/equipment/{equipment['id']}",
        headers=user_token_headers,
        json=update_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == update_data["name"]
    assert content["description"] == update_data["description"]

def test_delete_equipment(client: TestClient, user_token_headers: dict):
    # First create an equipment
    equipment = test_create_equipment(client, user_token_headers)
    
    response = client.delete(
        f"{settings.API_V1_STR}/equipment/{equipment['id']}",
        headers=user_token_headers
    )
    assert response.status_code == 200
    
    # Verify equipment is deleted
    response = client.get(
        f"{settings.API_V1_STR}/equipment/{equipment['id']}",
        headers=user_token_headers
    )
    assert response.status_code == 404

def test_filter_equipment(client: TestClient, user_token_headers: dict):
    # Create equipment with different types
    tractor_data = {
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
    harvester_data = {
        "name": "Test Harvester",
        "type": "harvester",
        "description": "A test harvester",
        "manufacturer": "Case IH",
        "model": "Test Model",
        "year": 2023,
        "hours_used": 50.5,
        "price_per_day": 200.00,
        "location": "Test Location"
    }
    
    client.post(
        f"{settings.API_V1_STR}/equipment/",
        headers=user_token_headers,
        json=tractor_data
    )
    client.post(
        f"{settings.API_V1_STR}/equipment/",
        headers=user_token_headers,
        json=harvester_data
    )
    
    # Test type filter
    response = client.get(
        f"{settings.API_V1_STR}/equipment/?type=tractor",
        headers=user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert all(item["type"] == "tractor" for item in content)
    
    # Test price filter
    response = client.get(
        f"{settings.API_V1_STR}/equipment/?min_price=175",
        headers=user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert all(item["price_per_day"] >= 175 for item in content)

def test_create_booking(client: TestClient, user_token_headers: dict):
    # First create an equipment
    equipment = test_create_equipment(client, user_token_headers)
    
    booking_data = {
        "equipment_id": equipment["id"],
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=3)).isoformat()
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/equipment/{equipment['id']}/bookings",
        headers=user_token_headers,
        json=booking_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["equipment_id"] == equipment["id"]
    assert "total_price" in content

def test_list_equipment_bookings(client: TestClient, user_token_headers: dict):
    # First create an equipment and a booking
    equipment = test_create_equipment(client, user_token_headers)
    test_create_booking(client, user_token_headers)
    
    response = client.get(
        f"{settings.API_V1_STR}/equipment/{equipment['id']}/bookings",
        headers=user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 1
    assert all(booking["equipment_id"] == equipment["id"] for booking in content)

def test_create_maintenance_record(client: TestClient, user_token_headers: dict):
    # First create an equipment
    equipment = test_create_equipment(client, user_token_headers)
    
    maintenance_data = {
        "equipment_id": equipment["id"],
        "service_date": datetime.utcnow().isoformat(),
        "description": "Regular maintenance",
        "cost": 500.00,
        "next_service_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/equipment/{equipment['id']}/maintenance",
        headers=user_token_headers,
        json=maintenance_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["equipment_id"] == equipment["id"]
    assert content["description"] == maintenance_data["description"]