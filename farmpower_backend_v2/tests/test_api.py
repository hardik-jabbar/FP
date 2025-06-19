import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker

# Create test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_seed_dummy_data():
    # Test seeding marketplace data
    response = client.post("/api/marketplace/seed-dummy-data")
    assert response.status_code == 200
    assert response.json()["message"] == "Dummy data seeded successfully"

    # Test seeding diagnostic data
    response = client.post("/api/diagnostic/seed-dummy-data")
    assert response.status_code == 200
    assert response.json()["message"] == "Dummy diagnostic data seeded successfully"

def test_marketplace_endpoints():
    # Test getting tractors
    response = client.get("/api/marketplace/tractors")
    assert response.status_code == 200
    tractors = response.json()
    assert len(tractors) > 0

    # Test getting parts
    response = client.get("/api/marketplace/parts")
    assert response.status_code == 200
    parts = response.json()
    assert len(parts) > 0

    # Test getting featured listings
    response = client.get("/api/marketplace/featured")
    assert response.status_code == 200
    featured = response.json()
    assert len(featured) > 0

def test_diagnostic_endpoints():
    # Test getting diagnostic reports
    response = client.get("/api/diagnostic/reports")
    assert response.status_code == 200
    reports = response.json()
    assert len(reports) > 0

    # Test getting maintenance schedules
    response = client.get("/api/diagnostic/maintenance")
    assert response.status_code == 200
    schedules = response.json()
    assert len(schedules) > 0

def test_filtering():
    # Test filtering tractors
    response = client.get("/api/marketplace/tractors?brand=John%20Deere")
    assert response.status_code == 200
    tractors = response.json()
    assert all(t["brand"] == "John Deere" for t in tractors)

    # Test filtering parts
    response = client.get("/api/marketplace/parts?category=Filters")
    assert response.status_code == 200
    parts = response.json()
    assert all(p["category"] == "Filters" for p in parts)

def test_error_handling():
    # Test invalid tractor ID
    response = client.get("/api/marketplace/tractors/999")
    assert response.status_code == 404

    # Test invalid part ID
    response = client.get("/api/marketplace/parts/999")
    assert response.status_code == 404

    # Test invalid diagnostic report ID
    response = client.get("/api/diagnostic/reports/999")
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__]) 