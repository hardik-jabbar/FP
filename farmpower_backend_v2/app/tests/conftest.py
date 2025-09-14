import os
import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
from pathlib import Path

# Import test database configuration
from app.tests.test_engine import (
    engine,
    TestingSessionLocal,
    setup_test_db,
    teardown_test_db,
)

# Import app modules
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from main import app

# Create temp directory for uploads
TEMP_DIR = tempfile.mkdtemp()
os.environ["UPLOAD_DIR"] = TEMP_DIR

# Override environment variables for testing
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Set up
    setup_test_db()
    yield
    # Clean up
    teardown_test_db()
    if os.path.exists("test.db"):
        os.remove("test.db")
    if os.path.exists(TEMP_DIR):
        for file in Path(TEMP_DIR).glob("*"):
            file.unlink()
        os.rmdir(TEMP_DIR)

@pytest.fixture
def db():
    """Return a SQLAlchemy session for testing."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """Return a FastAPI TestClient for testing."""
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client) -> Dict[str, str]:
    """Create a test user and return their credentials."""
    user_data = {
        "email": "test@example.com",
        "password": "test123",
        "full_name": "Test User"
    }
    response = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
    assert response.status_code == 200
    return user_data

@pytest.fixture
def user_token_headers(client, test_user) -> Dict[str, str]:
    """Create authentication headers for the test user."""
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}

# Use SQLite for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client: TestClient) -> Dict[str, str]:
    user_data = {
        "email": "test@example.com",
        "password": "test123",
        "full_name": "Test User"
    }
    response = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
    assert response.status_code == 200
    return user_data

@pytest.fixture
def test_superuser(client: TestClient) -> Dict[str, str]:
    user_data = {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "Admin User",
        "is_superuser": True
    }
    response = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
    assert response.status_code == 200
    return user_data

@pytest.fixture
def user_token_headers(client: TestClient, test_user: Dict[str, str]) -> Dict[str, str]:
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"],
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}