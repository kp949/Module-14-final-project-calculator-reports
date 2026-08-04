import os
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_jwt.db")

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


def unique_email():
    return f"krish{int(time.time() * 1000)}@example.com"


def test_jwt_register_returns_token_and_public_user():
    response = client.post(
        "/register",
        json={"email": unique_email(), "password": "Password123"},
    )

    data = response.json()

    assert response.status_code == 201
    assert data["message"] == "Registration successful"
    assert data["token_type"] == "bearer"
    assert data["access_token"].count(".") == 2
    assert "password_hash" not in data["user"]


def test_jwt_register_rejects_duplicate_email():
    email = unique_email()
    client.post("/register", json={"email": email, "password": "Password123"})

    response = client.post("/register", json={"email": email, "password": "Password123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_jwt_login_returns_token_for_correct_password():
    email = unique_email()
    client.post("/register", json={"email": email, "password": "Password123"})

    response = client.post("/login", json={"email": email, "password": "Password123"})

    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Login successful"
    assert data["access_token"].count(".") == 2


def test_jwt_login_rejects_wrong_password():
    email = unique_email()
    client.post("/register", json={"email": email, "password": "Password123"})

    response = client.post("/login", json={"email": email, "password": "WrongPass123"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_static_auth_pages_load():
    register_response = client.get("/static/register.html")
    login_response = client.get("/static/login.html")
    calculations_response = client.get("/static/calculations.html")

    assert register_response.status_code == 200
    assert "Create Account" in register_response.text
    assert login_response.status_code == 200
    assert "Log In" in login_response.text
    assert calculations_response.status_code == 200
    assert "Saved Calculations" in calculations_response.text
