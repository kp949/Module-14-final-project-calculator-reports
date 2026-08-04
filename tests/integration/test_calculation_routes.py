import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

connect_args = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def auth_headers(email="krish@example.com"):
    response = client.post(
        "/register",
        json={"email": email, "password": "Password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_add_calculation_route():
    headers = auth_headers()
    response = client.post("/calculations", json={"a": 2, "b": 3, "type": "Add"}, headers=headers)

    data = response.json()

    assert response.status_code == 201
    assert data["a"] == 2
    assert data["b"] == 3
    assert data["type"] == "Add"
    assert data["result"] == 5
    assert data["user_id"] is not None


def test_browse_calculations_route():
    headers = auth_headers()
    client.post("/calculations", json={"a": 2, "b": 3, "type": "Add"}, headers=headers)
    client.post("/calculations", json={"a": 10, "b": 4, "type": "Sub"}, headers=headers)

    response = client.get("/calculations", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_calculation_route():
    headers = auth_headers()
    create_response = client.post(
        "/calculations",
        json={"a": 4, "b": 5, "type": "Multiply"},
        headers=headers,
    )
    calculation_id = create_response.json()["id"]

    response = client.get(f"/calculations/{calculation_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["result"] == 20


def test_edit_calculation_route():
    headers = auth_headers()
    create_response = client.post(
        "/calculations",
        json={"a": 2, "b": 3, "type": "Add"},
        headers=headers,
    )
    calculation_id = create_response.json()["id"]

    response = client.put(
        f"/calculations/{calculation_id}",
        json={"a": 20, "b": 4, "type": "Divide"},
        headers=headers,
    )

    data = response.json()

    assert response.status_code == 200
    assert data["type"] == "Divide"
    assert data["result"] == 5


def test_delete_calculation_route():
    headers = auth_headers()
    create_response = client.post(
        "/calculations",
        json={"a": 2, "b": 3, "type": "Add"},
        headers=headers,
    )
    calculation_id = create_response.json()["id"]

    delete_response = client.delete(f"/calculations/{calculation_id}", headers=headers)
    read_response = client.get(f"/calculations/{calculation_id}", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Calculation deleted"
    assert read_response.status_code == 404


def test_missing_calculation_returns_404():
    response = client.get("/calculations/999", headers=auth_headers())

    assert response.status_code == 404
    assert response.json()["detail"] == "Calculation not found"


def test_invalid_calculation_type_returns_422():
    response = client.post(
        "/calculations",
        json={"a": 2, "b": 3, "type": "Power"},
        headers=auth_headers(),
    )

    assert response.status_code == 422


def test_division_by_zero_returns_422():
    response = client.post(
        "/calculations",
        json={"a": 10, "b": 0, "type": "Divide"},
        headers=auth_headers(),
    )

    assert response.status_code == 422


def test_calculation_routes_require_login():
    response = client.post(
        "/calculations",
        json={"a": 2, "b": 3, "type": "Add"},
    )

    assert response.status_code == 401


def test_user_cannot_read_another_users_calculation():
    first_user_headers = auth_headers("first@example.com")
    second_user_headers = auth_headers("second@example.com")
    create_response = client.post(
        "/calculations",
        json={"a": 9, "b": 3, "type": "Divide"},
        headers=first_user_headers,
    )
    calculation_id = create_response.json()["id"]

    response = client.get(f"/calculations/{calculation_id}", headers=second_user_headers)

    assert response.status_code == 404


def test_browse_only_returns_current_users_calculations():
    first_user_headers = auth_headers("first@example.com")
    second_user_headers = auth_headers("second@example.com")
    client.post("/calculations", json={"a": 1, "b": 2, "type": "Add"}, headers=first_user_headers)
    client.post("/calculations", json={"a": 7, "b": 3, "type": "Sub"}, headers=second_user_headers)

    response = client.get("/calculations", headers=first_user_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["result"] == 3
