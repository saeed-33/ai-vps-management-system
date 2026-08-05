from fastapi.testclient import TestClient

from control_plane_api.core.config import Settings
from control_plane_api.core.security import hash_password
from control_plane_api.main import create_app
from control_plane_api.modules.periodic_monitoring.analysis import analyze_server_report
from control_plane_api.modules.periodic_monitoring.persistence import database_uuid, stable_uuid
from control_plane_api.modules.periodic_monitoring.service import RECENT_CYCLES, stop_periodic_monitoring_scheduler
from control_plane_api.schemas.periodic_monitoring import MonitoringMetricSample, ServerSubAgentReport


def make_client() -> TestClient:
    RECENT_CYCLES.clear()
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


def test_periodic_monitoring_requires_auth() -> None:
    client = make_client()

    response = client.post("/api/v1/periodic-monitoring/cycles")

    assert response.status_code == 401


def test_stable_uuid_maps_text_ids_consistently() -> None:
    first = stable_uuid("srv-foundation-001")
    second = stable_uuid("srv-foundation-001")

    assert first == second
    assert first.version == 5


def test_database_uuid_preserves_existing_uuid_values() -> None:
    value = "95502c32-9d2e-589d-b58e-334e97eeb99b"

    assert str(database_uuid(value)) == value


def test_latest_cycle_not_found_before_run() -> None:
    client = make_client()
    token = login(client)

    response = client.get(
        "/api/v1/periodic-monitoring/cycles/latest",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_periodic_monitoring_cycle_produces_analyzed_report() -> None:
    client = make_client()
    token = login(client)

    response = client.post(
        "/api/v1/periodic-monitoring/cycles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["trigger"] == "manual"
    assert body["servers_planned"] == 1
    assert body["servers_checked"] == 1
    assert body["reports_count"] == 1
    assert "Control plane analysis" in body["scope_note"]
    report = body["reports"][0]
    assert report["sub_agent_id"] == "server-sub-agent-srv-foundation-001"
    assert len(report["metrics"]) == 5
    assert report["analysis"]["status"] == "no_issue"
    assert report["analysis"]["severity"] == "info"
    assert report["analysis"]["findings"] == []


def test_periodic_monitoring_analysis_flags_critical_metrics() -> None:
    report = ServerSubAgentReport(
        sub_agent_id="server-sub-agent-srv-1",
        server_id="srv-1",
        server_name="server-one",
        status="completed",
        started_at="2026-08-05T10:00:00Z",
        completed_at="2026-08-05T10:00:01Z",
        monitoring_profiles=["profile-linux-baseline"],
        metrics=[
            MonitoringMetricSample(
                metric="memory_usage_percent",
                value=93,
                unit="%",
                domain="memory",
                source_tool="free",
                collected_at="2026-08-05T10:00:01Z",
            )
        ],
        raw_snapshot={},
        collection_summary="Baseline metrics collected successfully by periodic monitoring agent.",
    )

    analysis = analyze_server_report(report)

    assert analysis.status == "confirmed_issue"
    assert analysis.severity == "critical"
    assert analysis.findings[0].code == "memory_usage_percent_critical"


def test_periodic_monitoring_lists_created_reports() -> None:
    client = make_client()
    token = login(client)

    client.post(
        "/api/v1/periodic-monitoring/cycles",
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        "/api/v1/periodic-monitoring/reports",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["reports"]) >= 1
    assert body["reports"][0]["collection_summary"] == "Baseline metrics collected successfully by periodic monitoring agent."


def test_periodic_monitoring_scheduler_start_status_and_stop() -> None:
    with make_client() as client:
        token = login(client)

        start_response = client.post(
            "/api/v1/periodic-monitoring/scheduler/start",
            json={"interval_seconds": 60},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert start_response.status_code == 200
        start_body = start_response.json()
        assert start_body["enabled"] is True
        assert start_body["interval_seconds"] == 60
        assert start_body["runs_count"] == 1

        status_response = client.get(
            "/api/v1/periodic-monitoring/scheduler/status",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert status_response.status_code == 200
        assert status_response.json()["enabled"] is True

        stop_response = client.post(
            "/api/v1/periodic-monitoring/scheduler/stop",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert stop_response.status_code == 200
        assert stop_response.json()["enabled"] is False

    try:
        import asyncio

        asyncio.run(stop_periodic_monitoring_scheduler())
    except RuntimeError:
        pass
