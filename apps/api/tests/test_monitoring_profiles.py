from fastapi.testclient import TestClient

from control_plane_api.core.config import Settings
from control_plane_api.core.security import hash_password
from control_plane_api.main import create_app
from control_plane_api.modules.monitoring_profiles.service import MEMORY_PROFILE_STORE


def make_client() -> TestClient:
    MEMORY_PROFILE_STORE.clear()
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


def test_monitoring_profiles_require_auth() -> None:
    client = make_client()

    response = client.get("/api/v1/monitoring-profiles")

    assert response.status_code == 401


def test_monitoring_profiles_list_returns_foundation_profiles() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/monitoring-profiles", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["profiles"]) == 2
    assert body["profiles"][0]["id"] == "profile-linux-baseline"
    assert body["profiles"][0]["source"] == "foundation-fixture"


def test_monitoring_profiles_summary() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/monitoring-profiles/summary",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["active"] == 1
    assert body["draft"] == 1
    assert body["by_domain"]["system"] == 1


def test_monitoring_profile_detail() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/monitoring-profiles/profile-linux-baseline",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "system"
    assert len(body["monitoring_instructions"]) == 4
    assert body["monitoring_instructions"][0]["command"] == "uptime"
    assert "Use raw command evidence first" in body["analysis_instructions"][0]


def test_monitoring_profile_create_accepts_execution_instructions() -> None:
    client = make_client()
    token = login(client)

    response = client.post(
        "/api/v1/monitoring-profiles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": "profile-custom-linux",
            "name": "Custom Linux",
            "domain": "system",
            "status": "active",
            "description": "Custom read-only collection profile.",
            "monitoring_instructions": [
                {
                    "id": "custom-uptime",
                    "title": "Collect uptime",
                    "tool_code": "custom_uptime",
                    "command": "uptime",
                    "purpose": "Collect load average evidence.",
                    "parser": "uptime",
                    "expected_evidence": ["load average"],
                    "read_only": True,
                }
            ],
            "analysis_instructions": ["Use raw evidence only."],
            "specialist_agents": [],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "profile-custom-linux"
    assert body["instructions_count"] == 1
    assert body["monitoring_instructions"][0]["command"] == "uptime"


def test_monitoring_profile_detail_not_found() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/monitoring-profiles/missing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
