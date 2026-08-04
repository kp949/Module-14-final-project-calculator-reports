from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_does_not_store_plain_text():
    password = "MyPassword123"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password not in password_hash


def test_verify_password_accepts_correct_password():
    password_hash = hash_password("MyPassword123")

    assert verify_password("MyPassword123", password_hash) is True


def test_verify_password_rejects_wrong_password():
    password_hash = hash_password("MyPassword123")

    assert verify_password("WrongPassword123", password_hash) is False


def test_verify_password_rejects_bad_hash_format():
    assert verify_password("MyPassword123", "not-a-valid-hash") is False


def test_create_access_token_returns_jwt_string():
    token = create_access_token({"sub": "krish@example.com", "user_id": 1})

    assert isinstance(token, str)
    assert token.count(".") == 2


def test_decode_access_token_returns_payload():
    token = create_access_token({"sub": "krish@example.com", "user_id": 1})

    payload = decode_access_token(token)

    assert payload["sub"] == "krish@example.com"
    assert payload["user_id"] == 1
