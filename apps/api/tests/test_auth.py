from datetime import timedelta

from fastapi.testclient import TestClient

from control_plane_api.core.config import Settings
from control_plane_api.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from control_plane_api.main import create_app


def make_client(*, password_hash: str = "", secret_key: str = "test-secret") -> TestClient:
    app = create_app(
        Settings(
            app_name="Test Control Plane",
            app_env="test",
            auth_secret_key=secret_key,
            bootstrap_admin_email="admin@example.com",
            bootstrap_admin_password_hash=password_hash,
            database_url="",
            redis_url="",
        )
    )
    return TestClient(app)


def test_password_hash_round_trip() -> None:
    password_hash = hash_password("correct-password")

    assert verify_password("correct-password", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_access_token_round_trip() -> None:
    token = create_access_token(
        subject="admin@example.com",
        secret_key="test-secret",
        expires_delta=timedelta(minutes=5),
        claims={"email": "admin@example.com", "roles": ["owner"]},
    )

    payload = decode_access_token(token, secret_key="test-secret")

    assert payload["sub"] == "admin@example.com"
    assert payload["email"] == "admin@example.com"
    assert payload["roles"] == ["owner"]


def test_access_token_rejects_wrong_secret() -> None:
    token = create_access_token(
        subject="admin@example.com",
        secret_key="test-secret",
        expires_delta=timedelta(minutes=5),
    )

    try:
        decode_access_token(token, secret_key="wrong-secret")
    except TokenError as exc:
        assert "signature" in str(exc)
    else:
        raise AssertionError("TokenError was not raised")


def test_login_requires_bootstrap_configuration() -> None:
    client = make_client(password_hash="", secret_key="")

    response = client.post(
        "/api/v1/auth/token",
        json={"email": "admin@example.com", "password": "correct-password"},
    )

    assert response.status_code == 503


def test_login_and_current_principal() -> None:
    client = make_client(password_hash=hash_password("correct-password"))

    token_response = client.post(
        "/api/v1/auth/token",
        json={"email": "admin@example.com", "password": "correct-password"},
    )

    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    body = me_response.json()
    assert body["email"] == "admin@example.com"
    assert body["roles"] == ["owner"]
    assert "servers.read" in body["permissions"]


def test_current_principal_requires_bearer_token() -> None:
    client = make_client(password_hash=hash_password("correct-password"))

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_rbac_catalog_requires_auth() -> None:
    client = make_client(password_hash=hash_password("correct-password"))

    response = client.get("/api/v1/auth/rbac")

    assert response.status_code == 401
