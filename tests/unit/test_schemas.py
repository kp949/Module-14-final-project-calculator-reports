import pytest
from pydantic import ValidationError

from app.schemas import UserCreate


def test_user_create_accepts_valid_data():
    user = UserCreate(
        username="alice",
        email="alice@example.com",
        password="Password123",
    )

    assert user.username == "alice"
    assert user.email == "alice@example.com"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="not-an-email", password="Password123")


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="alice@example.com", password="short")


def test_user_create_rejects_short_username():
    with pytest.raises(ValidationError):
        UserCreate(username="al", email="alice@example.com", password="Password123")

