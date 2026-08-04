from fastapi.testclient import TestClient

from control_plane_api.core.config import Settings
from control_plane_api.main import create_app


def make_client(database_url: str = "") -> TestClient:
    app = create_app(
        Settings(
            app_name="Test Control Plane",
            app_env="test",
            database_url=database_url,
            redis_url="",
        )
    )
    return TestClient(app)


def test_liveness_endpoint() -> None:
    client = make_client()

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "service": "Test Control Plane",
        "environment": "test",
        "status": "ok",
    }


def test_readiness_reports_missing_database_url() -> None:
    client = make_client()

    response = client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["ready"] is False
    assert body["components"][0]["name"] == "postgres"
    assert body["components"][0]["ok"] is False


def test_meta_endpoint_lists_foundation_modules() -> None:
    client = make_client()

    response = client.get("/api/v1/meta")

    assert response.status_code == 200
    body = response.json()
    module_names = {module["name"] for module in body["modules"]}
    assert body["service"] == "Test Control Plane"
    assert "health" in module_names
    assert "policy_engine" in module_names
    assert "auth" in module_names
