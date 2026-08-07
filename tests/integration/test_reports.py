import os
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_reports.db")

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


def register_and_login():
    email = f"reportuser{int(time.time() * 1000)}@example.com"

    client.post(
        "/register",
        json={"email": email, "password": "Password123", "username": "reportuser"},
    )

    login_response = client.post(
        "/login",
        json={"email": email, "password": "Password123"},
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_report_summary_requires_login():
    response = client.get("/reports/summary")

    assert response.status_code == 401


def test_report_summary_returns_user_calculation_stats():
    headers = register_and_login()

    client.post(
        "/calculations",
        json={"a": 10, "b": 5, "type": "Add"},
        headers=headers,
    )
    client.post(
        "/calculations",
        json={"a": 20, "b": 4, "type": "Divide"},
        headers=headers,
    )

    response = client.get("/reports/summary", headers=headers)

    assert response.status_code == 200

    report = response.json()

    assert report["total_calculations"] == 2
    assert report["add_count"] == 1
    assert report["divide_count"] == 1
    assert report["average_result"] == 10
    assert report["highest_result"] == 15
    assert report["lowest_result"] == 5
    assert len(report["recent_calculations"]) == 2