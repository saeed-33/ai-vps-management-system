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


def test_specialist_agents_require_auth() -> None:
    client = make_client()

    response = client.get("/api/v1/specialist-agents")

    assert response.status_code == 401


def test_specialist_agents_list_returns_foundation_agents() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/specialist-agents", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["agents"]) == 3
    assert body["agents"][0]["id"] == "cpu-memory-specialist"
    assert body["agents"][0]["source"] == "foundation-fixture"


def test_specialist_agents_summary() -> None:
    client = make_client()
    token = login(client)

    response = client.get("/api/v1/specialist-agents/summary", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["active"] == 2
    assert body["draft"] == 1
    assert body["by_domain"]["system"] == 1


def test_specialist_agent_detail() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/specialist-agents/nginx-health-specialist",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "web"
    assert body["trigger_profiles"] == ["profile-nginx-health"]
    assert "Never reload or restart Nginx in this phase." in body["analysis_contract"]


def test_specialist_agent_detail_not_found() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/specialist-agents/missing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
