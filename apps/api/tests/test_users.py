from fastapi.testclient import TestClient

from control_plane_api.core.config import Settings
from control_plane_api.core.security import hash_password
from control_plane_api.main import create_app


def make_client() -> TestClient:
    app = create_app(
        Settings(
            app_name="Test Control Plane",
            app_env="test",
            auth_secret_key="test-secret",
            bootstrap_admin_email="admin@example.com",
            bootstrap_admin_password_hash=hash_password("correct-password"),
            database_url="",
            redis_url="",
        )
    )
    return TestClient(app)


def login(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/token",
        json={"email": "admin@example.com", "password": "correct-password"},
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


def test_users_requires_auth() -> None:
    client = make_client()

    response = client.get("/api/v1/users")

    assert response.status_code == 401


def test_users_list_returns_current_bootstrap_user() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["users"]) == 1
    assert body["users"][0]["email"] == "admin@example.com"
    assert body["users"][0]["source"] == "token"


def test_users_me_returns_current_user() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


def test_roles_list_returns_rbac_catalog_summary() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/users/roles", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    role_codes = {role["code"] for role in response.json()["roles"]}
    assert {"owner", "admin", "operator", "viewer", "auditor"}.issubset(role_codes)
