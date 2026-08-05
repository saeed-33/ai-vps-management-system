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


def test_servers_requires_auth() -> None:
    client = make_client()

    response = client.get("/api/v1/servers")

    assert response.status_code == 401


def test_servers_list_returns_foundation_server() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/servers", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["servers"]) == 1
    assert body["servers"][0]["id"] == "srv-foundation-001"
    assert body["servers"][0]["source"] == "foundation-fixture"


def test_servers_summary() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/servers/summary", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["active"] == 1
    assert body["by_environment"]["development"] == 1


def test_server_detail() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/servers/srv-foundation-001",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["hostname"] == "foundation-vps.local"


def test_server_detail_not_found() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/servers/missing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
