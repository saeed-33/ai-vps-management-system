from fastapi.testclient import TestClient

from control_plane_api.core.config import Settings
from control_plane_api.core.security import hash_password
from control_plane_api.main import create_app
from control_plane_api.modules.servers.service import MEMORY_SERVER_STORE, SSH_ACCESS_STORE


def make_client() -> TestClient:
    SSH_ACCESS_STORE.clear()
    MEMORY_SERVER_STORE.clear()
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


def test_server_create_adds_memory_fallback_server() -> None:
    client = make_client()
    token = login(client)

    response = client.post(
        "/api/v1/servers",
        json={
            "name": "prod-app-01",
            "hostname": "prod-app-01.example.com",
            "ip_address": "10.0.0.20",
            "environment": "production",
            "assigned_monitoring_profiles": ["profile-linux-baseline"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "srv-prod-app-01"
    assert body["source"] == "memory-fallback"
    assert body["assigned_monitoring_profiles"] == ["profile-linux-baseline"]

    list_response = client.get("/api/v1/servers", headers={"Authorization": f"Bearer {token}"})
    assert len(list_response.json()["servers"]) == 2


def test_server_update_changes_memory_fallback_server() -> None:
    client = make_client()
    token = login(client)

    client.post(
        "/api/v1/servers",
        json={"name": "stage-db-01", "hostname": "stage-db-01.example.com", "environment": "staging"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.put(
        "/api/v1/servers/srv-stage-db-01",
        json={"status": "maintenance", "os_family": "linux"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "maintenance"
    assert body["os_family"] == "linux"


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


def test_server_ssh_access_update_requires_auth() -> None:
    client = make_client()

    response = client.put(
        "/api/v1/servers/srv-foundation-001/ssh-access",
        json={"enabled": True, "host": "127.0.0.1", "username": "root"},
    )

    assert response.status_code == 401


def test_server_ssh_access_update_masks_secret() -> None:
    client = make_client()
    token = login(client)

    response = client.put(
        "/api/v1/servers/srv-foundation-001/ssh-access",
        json={
            "enabled": True,
            "host": "127.0.0.1",
            "port": 22,
            "username": "root",
            "password": "secret-password",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert body["auth_method"] == "password"
    assert body["has_password"] is True
    assert "password" not in body


def test_server_ssh_access_test_reports_disabled_configuration() -> None:
    client = make_client()
    token = login(client)

    response = client.post(
        "/api/v1/servers/srv-foundation-001/ssh-access/test",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["detail"] == "SSH access is not enabled for this server."


def test_server_ssh_access_test_not_found() -> None:
    client = make_client()
    token = login(client)

    response = client.post(
        "/api/v1/servers/missing/ssh-access/test",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_server_detail_includes_masked_ssh_access() -> None:
    client = make_client()
    token = login(client)

    client.put(
        "/api/v1/servers/srv-foundation-001/ssh-access",
        json={
            "enabled": True,
            "host": "10.0.0.10",
            "port": 2222,
            "username": "ubuntu",
            "private_key_path": "C:/keys/id_rsa",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        "/api/v1/servers/srv-foundation-001",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    ssh_access = response.json()["ssh_access"]
    assert ssh_access["enabled"] is True
    assert ssh_access["host"] == "10.0.0.10"
    assert ssh_access["auth_method"] == "private_key"
