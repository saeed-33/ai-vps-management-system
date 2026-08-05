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
    assert len(body["thresholds"]) == 5
    assert "Treat thresholds as signals, not final decisions." in body["analysis_guidelines"]


def test_monitoring_profile_detail_not_found() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/monitoring-profiles/missing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
