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


def test_allowed_tools_require_auth() -> None:
    client = make_client()

    response = client.get("/api/v1/allowed-tools")

    assert response.status_code == 401


def test_allowed_tools_list_returns_foundation_tools() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/allowed-tools", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["tools"]) == 5
    assert body["tools"][0]["code"] == "uptime"
    assert body["tools"][0]["read_only"] is True


def test_allowed_tools_summary() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/allowed-tools/summary", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert body["active"] == 4
    assert body["draft"] == 1
    assert body["read_only"] == 5
    assert body["by_scope"]["server_readonly"] == 5


def test_allowed_tool_detail_by_code() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/allowed-tools/systemctl_status", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "tool-systemctl-status"
    assert "Disallow start, stop, restart, reload, enable, and disable." in [
        guardrail["rule"] for guardrail in body["guardrails"]
    ]


def test_allowed_tool_detail_not_found() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/allowed-tools/missing", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
