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
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_user_returns_public_user_data():
    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "password" not in data
    assert "password_hash" not in data
    assert "created_at" in data


def test_duplicate_username_is_rejected():
    user_data = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password123",
    }
    client.post("/users", json=user_data)

    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice2@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_duplicate_email_is_rejected():
    client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )

    response = client.post(
        "/users",
        json={
            "username": "bob",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_invalid_email_is_rejected():
    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "not-an-email",
            "password": "Password123",
        },
    )

    assert response.status_code == 422


def test_short_password_is_rejected():
    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_read_user_by_id():
    create_response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_read_missing_user_returns_404():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_calculator_endpoint_still_works():
    response = client.post("/add", json={"a": 2, "b": 3})

    assert response.status_code == 200
    assert response.json()["result"] == 5


def test_home_page_loads():
    response = client.get("/")

    assert response.status_code == 200
    assert "Module 14 Calculation BREAD Application" in response.text


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_subtract_endpoint():
    response = client.post("/subtract", json={"a": 10, "b": 4})

    assert response.status_code == 200
    assert response.json()["result"] == 6


def test_multiply_endpoint():
    response = client.post("/multiply", json={"a": 4, "b": 5})

    assert response.status_code == 200
    assert response.json()["result"] == 20


def test_divide_endpoint():
    response = client.post("/divide", json={"a": 20, "b": 4})

    assert response.status_code == 200
    assert response.json()["result"] == 5


def test_divide_by_zero_endpoint_returns_error():
    response = client.post("/divide", json={"a": 10, "b": 0})

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot divide by zero"


def test_register_user_route():
    response = client.post(
        "/users/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "Password123",
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert data["username"] == "charlie"
    assert "password_hash" not in data


def test_login_user_route():
    client.post(
        "/users/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "Password123",
        },
    )

    response = client.post(
        "/users/login",
        json={"username": "charlie", "password": "Password123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert response.json()["user"]["username"] == "charlie"


def test_login_rejects_bad_password():
    client.post(
        "/users/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "Password123",
        },
    )

    response = client.post(
        "/users/login",
        json={"username": "charlie", "password": "WrongPass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
