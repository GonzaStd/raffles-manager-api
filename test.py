# test_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from main import app
from database.connection import get_db, Base
from core.config_loader import settings
from models.users import User
from auth.utils import create_access_token, get_password_hash

# Test database setup
TEST_DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI).replace(
    settings.MARIADB_DATABASE,
    f"test_{settings.MARIADB_DATABASE}"
)

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Global test data dictionary
test_data = {
    "buyer_id": None,
    "project_id": None,
    "raffleset_id": None,
    "raffle_number": None,
    "access_token": None,
    "test_user_id": None
}

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database before all tests and cleanup after."""
    # Create system engine for database operations
    sys_engine = create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}")

    # Drop and create test database
    with sys_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS test_{settings.MARIADB_DATABASE}"))
        conn.execute(text(f"CREATE DATABASE test_{settings.MARIADB_DATABASE}"))
        conn.commit()

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create a test user for authentication
    db = TestingSessionLocal()
    test_user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        is_active=True
    )
    db.add(test_user)
    db.commit()

    # Store user data for tests
    test_data["test_user_id"] = test_user.id

    # Create access token for tests
    test_data["access_token"] = create_access_token(subject=test_user.username)

    db.close()

    yield

    # Cleanup after all tests - drop test database
    with sys_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS test_{settings.MARIADB_DATABASE}"))
        conn.commit()

def get_auth_headers():
    """Get authentication headers for requests."""
    return {"Authorization": f"Bearer {test_data['access_token']}"}

def test_create_project():
    """Test project creation endpoint."""
    response = client.post("/project",
        json={
            "name": "Test Project",
            "description": "Test project description"
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test project description"
    assert "id" in data

    test_data["project_id"] = data["id"]

def test_get_project():
    """Test get single project endpoint."""
    assert test_data["project_id"] is not None

    response = client.get(f"/project?id={test_data['project_id']}", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_data["project_id"]
    assert data["name"] == "Test Project"

def test_get_projects():
    """Test get all projects endpoint."""
    response = client.get("/projects", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_create_buyer():
    """Test buyer creation endpoint."""
    response = client.post("/buyer",
        json={
            "name": "John Doe",
            "phone": "+1234567890",
            "email": "john@example.com"
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["phone"] == "+1234567890"
    assert data["email"] == "john@example.com"
    assert "id" in data

    test_data["buyer_id"] = data["id"]

def test_get_buyer():
    """Test get single buyer endpoint."""
    assert test_data["buyer_id"] is not None

    response = client.get(f"/buyer?id={test_data['buyer_id']}", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_data["buyer_id"]
    assert data["name"] == "John Doe"

def test_get_buyers():
    """Test get all buyers endpoint."""
    response = client.get("/buyers", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_create_raffleset():
    """Test raffleset creation endpoint."""
    assert test_data["project_id"] is not None

    response = client.post("/raffleset",
        json={
            "project_id": test_data["project_id"],
            "name": "Test Raffle Set",
            "type": "online",
            "requested_count": 10,
            "unit_price": 1000
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert "raffleset" in data
    assert "range" in data
    assert data["raffleset"]["name"] == "Test Raffle Set"

    test_data["raffleset_id"] = data["raffleset"]["id"]
    # Extract first raffle number from range
    range_str = data["range"]
    test_data["raffle_number"] = int(range_str.split("-")[0])

def test_get_raffleset():
    """Test get single raffleset endpoint."""
    assert test_data["raffleset_id"] is not None

    response = client.get(f"/raffleset/{test_data['raffleset_id']}", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_data["raffleset_id"]

def test_get_rafflesets():
    """Test get all rafflesets endpoint."""
    response = client.get("/rafflesets", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_raffle():
    """Test get single raffle endpoint."""
    assert test_data["raffle_number"] is not None

    response = client.get(f"/raffle?number={test_data['raffle_number']}", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert data["number"] == test_data["raffle_number"]

def test_get_raffles():
    """Test get all raffles endpoint."""
    response = client.get("/raffles", headers=get_auth_headers())
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

# Move update tests before delete tests
def test_update_buyer():
    """Test buyer update endpoint."""
    assert test_data["buyer_id"] is not None

    response = client.patch("/buyer",
        json={
            "id": test_data["buyer_id"],
            "name": "John Smith",
            "email": "johnsmith@example.com"
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["email"] == "johnsmith@example.com"

def test_update_project():
    """Test project update endpoint."""
    assert test_data["project_id"] is not None

    response = client.patch("/project",
        json={
            "id": test_data["project_id"],
            "name": "Updated Test Project",
            "description": "Updated description"
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Project"

def test_update_raffle():
    """Test raffle update endpoint."""
    assert test_data["raffle_number"] is not None

    response = client.patch("/raffle",
        json={
            "number": test_data["raffle_number"],
            "state": "reserved"
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["state"] == "reserved"

def test_pay_raffle():
    """Test raffle payment endpoint."""
    assert test_data["raffle_number"] is not None
    assert test_data["buyer_id"] is not None

    response = client.post("/raffle/pay",
        json={
            "number": test_data["raffle_number"],
            "buyer_id": test_data["buyer_id"]
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["number"] == test_data["raffle_number"]
    assert data["buyer_id"] == test_data["buyer_id"]
    assert data["state"] == "paid"

def test_delete_raffleset():
    """Test raffleset deletion endpoint."""
    assert test_data["raffleset_id"] is not None

    response = client.request(
        "DELETE",
        "/raffleset",
        json={"id": test_data["raffleset_id"]},
        headers=get_auth_headers()
    )

    assert response.status_code == 200

def test_delete_buyer():
    """Test buyer deletion endpoint."""
    assert test_data["buyer_id"] is not None

    response = client.request(
        "DELETE",
        "/buyer",
        json={"id": test_data["buyer_id"]},
        headers=get_auth_headers()
    )

    assert response.status_code == 200

def test_delete_project():
    """Test project deletion endpoint."""
    assert test_data["project_id"] is not None

    response = client.request(
        "DELETE",
        "/project",
        json={"id": test_data["project_id"]},
        headers=get_auth_headers()
    )

    assert response.status_code == 200

def test_get_nonexistent_project():
    """Test get nonexistent project endpoint."""
    response = client.get("/project?id=99999", headers=get_auth_headers())
    assert response.status_code == 404

def test_get_nonexistent_buyer():
    """Test get nonexistent buyer endpoint."""
    response = client.get("/buyer?id=99999", headers=get_auth_headers())
    assert response.status_code == 404

def test_get_nonexistent_raffle():
    """Test get nonexistent raffle endpoint."""
    response = client.get("/raffle?number=99999", headers=get_auth_headers())
    assert response.status_code == 404

def test_create_duplicate_project():
    """Test creating duplicate project."""
    response = client.post("/project",
        json={
            "name": "Test Project",
            "description": "Duplicate project"
        },
        headers=get_auth_headers()
    )
    # Should allow duplicate names but with different IDs
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
