# test_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from main import app
from database.connection import get_db, Base
from core.config_loader import settings
from models.users import User

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

# Global variables for test data
test_data = {
    "buyer_id": None,
    "project_id": None,
    "raffleset_id": None,
    "raffle_number": None
}


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database before all tests and cleanup after."""
    # Create test database
    sys_engine = create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}")

    with sys_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS test_{settings.MARIADB_DATABASE}"))
        conn.execute(text(f"CREATE DATABASE test_{settings.MARIADB_DATABASE}"))
        conn.commit()

    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Create a test user for foreign key relationships
    db = TestingSessionLocal()
    test_user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword123",  # Fixed field name
        is_active=True
    )
    db.add(test_user)
    db.commit()
    db.close()

    yield

    # Cleanup after all tests
    with sys_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS test_{settings.MARIADB_DATABASE}"))
        conn.commit()


def test_create_project():
    """Test project creation endpoint."""
    response = client.post("/project", json={
        "name": "Test Project",
        "description": "Test project description"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test project description"
    assert "id" in data

    test_data["project_id"] = data["id"]


def test_get_project():
    """Test get single project endpoint."""
    assert test_data["project_id"] is not None

    response = client.get(f"/project?id={test_data['project_id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_data["project_id"]
    assert data["name"] == "Test Project"


def test_get_projects():
    """Test get all projects endpoint."""
    response = client.get("/projects")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_create_buyer():
    """Test buyer creation endpoint."""
    response = client.post("/buyer", json={
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john@example.com"
    })

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

    response = client.get(f"/buyer?id={test_data['buyer_id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_data["buyer_id"]
    assert data["name"] == "John Doe"


def test_get_buyers():
    """Test get all buyers endpoint."""
    response = client.get("/buyers")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_create_raffleset():
    """Test raffleset creation endpoint."""
    assert test_data["project_id"] is not None

    response = client.post("/raffleset", json={
        "project_id": test_data["project_id"],
        "name": "Test Raffle Set",
        "type": "online",
        "requested_count": 10,
        "unit_price": 1000
    })

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

    response = client.get(f"/raffleset/{test_data['raffleset_id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_data["raffleset_id"]
    assert data["name"] == "Test Raffle Set"


def test_get_rafflesets():
    """Test get all rafflesets endpoint."""
    response = client.get("/rafflesets")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_raffle():
    """Test get single raffle endpoint."""
    assert test_data["raffle_number"] is not None

    response = client.get(f"/raffle?number={test_data['raffle_number']}")
    assert response.status_code == 200

    data = response.json()
    assert data["number"] == test_data["raffle_number"]
    assert data["state"] == "available"


def test_get_raffles():
    """Test get all raffles endpoint."""
    response = client.get("/raffles")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10  # We created 10 raffles


def test_pay_raffle():
    """Test raffle payment endpoint."""
    assert test_data["raffle_number"] is not None
    assert test_data["buyer_id"] is not None

    response = client.post("/raffle/pay", json={
        "number": test_data["raffle_number"],
        "buyer_id": test_data["buyer_id"],
        "payment_method": "card",
        "state": "sold"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["number"] == test_data["raffle_number"]
    assert data["buyer_id"] == test_data["buyer_id"]
    assert data["state"] == "sold"
    assert data["payment_method"] == "card"


def test_update_buyer():
    """Test buyer update endpoint."""
    assert test_data["buyer_id"] is not None

    response = client.patch("/buyer", json={
        "id": test_data["buyer_id"],
        "name": "John Smith",
        "email": "johnsmith@example.com"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["email"] == "johnsmith@example.com"


def test_update_project():
    """Test project update endpoint."""
    assert test_data["project_id"] is not None

    response = client.patch("/project", json={
        "id": test_data["project_id"],
        "description": "Updated project description"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated project description"


def test_update_raffle():
    """Test raffle update endpoint."""
    assert test_data["raffle_number"] is not None

    response = client.patch("/raffle", json={
        "number": test_data["raffle_number"],
        "state": "reserved"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["state"] == "reserved"


def test_delete_raffleset():
    """Test raffleset deletion endpoint."""
    assert test_data["raffleset_id"] is not None

    response = client.delete(f"/raffleset/{test_data['raffleset_id']}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "deleted successfully" in data["message"]


def test_delete_buyer():
    """Test buyer deletion endpoint."""
    assert test_data["buyer_id"] is not None

    # Use proper JSON parameter for DELETE request - FastAPI can handle this
    response = client.request(
        "DELETE",
        "/buyer",
        json={"id": test_data["buyer_id"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "deleted successfully" in data["message"]


def test_delete_project():
    """Test project deletion endpoint."""
    assert test_data["project_id"] is not None

    response = client.delete(f"/project?id={test_data['project_id']}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "deleted successfully" in data["message"]


# Error handling tests
def test_get_nonexistent_project():
    """Test getting a non-existent project returns 404."""
    response = client.get("/project?id=99999")
    assert response.status_code == 404


def test_get_nonexistent_buyer():
    """Test getting a non-existent buyer returns 404."""
    response = client.get("/buyer?id=99999")
    assert response.status_code == 404


def test_get_nonexistent_raffle():
    """Test getting a non-existent raffle returns 404."""
    response = client.get("/raffle?number=99999")
    assert response.status_code == 404


def test_create_duplicate_project():
    """Test creating a project with duplicate name returns 400."""
    # Create first project
    client.post("/project", json={
        "name": "Duplicate Test",
        "description": "First project"
    })

    # Try to create duplicate
    response = client.post("/project", json={
        "name": "Duplicate Test",
        "description": "Second project"
    })

    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
